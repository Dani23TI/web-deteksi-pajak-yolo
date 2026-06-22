import streamlit as st
import cv2
import numpy as np
import re
import calendar
import tempfile
import os
import threading
import time
from datetime import datetime
from pathlib import Path

# --- LAZY-LOAD MODEL & OCR ---
@st.cache_resource
def load_yolo():
    from ultralytics import YOLO
    model_path = Path("best.onnx")
    if not model_path.exists():
        st.error("File 'best.onnx' tidak ditemukan di folder proyek!")
        st.stop()
    return YOLO(str(model_path), task="detect")

@st.cache_resource
def load_ocr():
    import easyocr
    import torch
    return easyocr.Reader(["en"], gpu=torch.cuda.is_available(), model_storage_directory="./easyocr_models")


# --- HELPER FUNCTIONS ---
# Catatan: Logika OCR, ekstraksi data, dan pengecekan status pajak di bawah ini
# disesuaikan 1:1 dengan notebook referensi "dataset2_sesuai_jurnal.ipynb"
# (model 1 kelas 'plat_nomor', tanpa preprocessing OpenCV tambahan,
# parsing huruf/angka manual, dan aturan status AKTIF/MATI berbasis bulan & tahun).

_OCR_MAX_WIDTH = 200  # px — downscale large crops for speed
_OCR_ALLOWLIST = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "

def ocr_and_predict(crop_bgr, reader=None):
    """
    OCR plat — identik dengan ocr_plate() pada notebook referensi.
    EasyOCR dijalankan langsung pada crop tanpa preprocessing tambahan
    (tidak ada CLAHE/threshold/sharpening) agar perilaku deteksi sama
    persis dengan hasil training/notebook.
    Optimasi: crop di-resize ke maks 200px lebar sebelum OCR, dan
    allowlist dibatasi pada karakter plat nomor untuk mempercepat inferensi.
    Return (text_gabungan, confidence_rata_rata_persen).
    """
    if reader is None:
        reader = load_ocr()

    if crop_bgr is None or crop_bgr.size == 0:
        return "", 0.0

    # --- Resize crop agar OCR lebih cepat ---
    h, w = crop_bgr.shape[:2]
    if w > _OCR_MAX_WIDTH:
        scale = _OCR_MAX_WIDTH / w
        crop_bgr = cv2.resize(crop_bgr, (_OCR_MAX_WIDTH, int(h * scale)),
                              interpolation=cv2.INTER_AREA)

    try:
        result = reader.readtext(
            crop_bgr, detail=1,
            paragraph=False,
            allowlist=_OCR_ALLOWLIST,
        )
    except Exception:
        return "", 0.0

    if not result:
        return "", 0.0

    text = " ".join([res[1] for res in result])
    confs = [res[2] for res in result]
    avg_conf = (sum(confs) / len(confs)) * 100 if confs else 0.0

    return text, round(avg_conf, 1)


def extract_data(text):
    """
    Ekstraksi nomor plat + bulan/tahun pajak — identik dengan extract_info()
    pada notebook referensi: bersihkan teks, pisahkan token huruf vs angka,
    lalu susun ulang sebagai plat (depan-nomor-belakang) dan cari pasangan
    bulan(1-12)/tahun(>=20) dari deretan angka kecil.
    """
    text = text.upper()
    text = re.sub(r'[^A-Z0-9]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    parts = text.split()

    huruf = [p for p in parts if p.isalpha()]
    angka = [p for p in parts if p.isdigit()]

    # ===== BARIS 1 (PLAT) =====
    depan = huruf[0] if len(huruf) > 0 else ""
    nomor = max(angka, key=len) if len(angka) > 0 else ""
    belakang = huruf[1][:2] if len(huruf) > 1 else ""

    plat_gabungan = f"{depan} {nomor} {belakang}".strip()
    nomor_plat = plat_gabungan if plat_gabungan else "Tidak Terbaca"

    # ===== BARIS 2 (BULAN/TAHUN) =====
    bulan, tahun = None, None
    angka_kecil = [int(a) for a in angka if len(a) <= 2 and int(a) != 0]

    for i in range(len(angka_kecil) - 1):
        b = angka_kecil[i]
        t = angka_kecil[i + 1]
        if 1 <= b <= 12 and t >= 20:
            bulan = b
            tahun = 2000 + t
            break

    return nomor_plat, bulan, tahun


def cek_status_pajak(bln, thn):
    """
    Status pajak — identik dengan cek_status() pada notebook referensi:
    AKTIF jika (tahun > tahun_sekarang) atau (tahun == tahun_sekarang DAN
    bulan >= bulan_sekarang). Selain itu MATI. Jika data tidak lengkap,
    TIDAK TERBACA.
    Return (status_str, color_rgb) — color_rgb dipertahankan untuk
    kompatibilitas dengan kode anotasi bounding box yang sudah ada.
    """
    if bln is None or thn is None:
        return "TIDAK TERBACA", (252, 205, 23)

    now = datetime.now()

    if (thn > now.year) or (thn == now.year and bln >= now.month):
        return "PAJAK AKTIF", (3, 114, 114)
    else:
        return "PAJAK MATI", (255, 168, 0)


def conf_class(conf):
    """Kelas CSS warna berdasarkan nilai confidence (0-100)."""
    if conf >= 80:
        return "conf-high"
    elif conf >= 50:
        return "conf-mid"
    return "conf-low"


def annotate_frame(frame_rgb, boxes, frame_bgr):
    """Jalankan OCR + annotasi pada satu frame. Return (frame_rgb_annotated, list_detections)."""
    detections = []
    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        crop = frame_bgr[y1:y2, x1:x2]
        if crop.size == 0:
            continue

        conf_yolo = float(box.conf[0]) * 100
        raw_text, conf_ocr = ocr_and_predict(crop)
        plat, bln, thn = extract_data(raw_text)
        status, color_rgb = cek_status_pajak(bln, thn)

        cv2.rectangle(frame_rgb, (x1, y1), (x2, y2), color_rgb, 3)
        cv2.rectangle(frame_rgb, (x1, max(y1 - 34, 0)), (x2, y1), color_rgb, -1)
        masa_str = f"{bln:02d}/{thn}" if bln and thn else "N/A"
        label = f"{plat}  {masa_str}  ({conf_ocr:.0f}%)"
        cv2.putText(frame_rgb, label, (x1 + 8, max(y1 - 10, 14)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)

        detections.append({
            "plat": plat,
            "raw": raw_text if raw_text else "Tidak Ada Teks",
            "masa": f"{bln:02d} / {thn}" if bln and thn else "Gagal Parsing",
            "status": status,
            "conf_yolo": conf_yolo,
            "conf_ocr": conf_ocr,
        })
    return frame_rgb, detections
