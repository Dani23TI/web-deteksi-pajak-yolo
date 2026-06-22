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

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="AutoTax Intelligence | Kelompok 4",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ADVANCED UI/UX STYLING ENGINE ---
# --- LOAD CSS STYLING ---
def load_css(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")


# --- LAZY-LOAD MODEL & OCR ---
from utils import load_yolo, load_ocr, ocr_and_predict, extract_data, cek_status_pajak, conf_class, annotate_frame


# --- HISTORI DETEKSI (SESSION STATE) ---
if "riwayat_deteksi" not in st.session_state:
    st.session_state.riwayat_deteksi = []   # list of dict — satu entri per kendaraan terdeteksi

if "riwayat_detail_idx" not in st.session_state:
    st.session_state.riwayat_detail_idx = None  # index riwayat yang sedang dilihat detailnya


def catat_riwayat(sumber, plat, masa, status, conf_yolo, conf_ocr, raw_ocr="-"):
    """
    Simpan satu hasil deteksi ke histori global (session_state).
    Dipanggil otomatis setiap kali deteksi pajak berhasil dijalankan
    dari tab Gambar, Video, atau Kamera Real-time.
    """
    entry = {
        "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sumber": sumber,          # "Gambar" / "Video" / "Kamera"
        "plat": plat,
        "masa": masa,
        "status": status,
        "conf_yolo": conf_yolo,
        "conf_ocr": conf_ocr,
        "raw_ocr": raw_ocr,
    }
    st.session_state.riwayat_deteksi.append(entry)


# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div class='sidebar-brand'>
            <div class='sidebar-logo-ring'>🛡️</div>
            <div class='sidebar-title'>AUTOTAX INTEL</div>
            <div class='sidebar-sub'>SISTEM DETEKSI PAJAK KENDARAAN</div>
        </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "MENU",
        [
            "👥 Pengenalan Kelompok",
            "📖 Deskripsi & Latar Belakang",
            "⚙️ Mesin Deteksi Pajak",
            "🗂️ Histori Deteksi",
        ],
        label_visibility="collapsed"
    )

    st.markdown("<div class='road-divider'></div>", unsafe_allow_html=True)

    st.markdown("""
        <div class='sidebar-footer'>
            ⚡ YOLOv11 &nbsp;·&nbsp; EasyOCR<br>
            Kelompok 4 &nbsp;·&nbsp; 3 TI B<br>
            PCR TA 2025/2026
        </div>
    """, unsafe_allow_html=True)


# ==========================================
# HALAMAN 1: PENGENALAN KELOMPOK
# ==========================================
if page == "👥 Pengenalan Kelompok":
    st.markdown("""
        <div class='page-header'>
            <div class='page-eyebrow'>// KELOMPOK 4</div>
            <div class='main-title'>Tim <span class='title-accent'>Pengembang</span></div>
            <div class='subtitle'>Personel di balik dashboard AutoTax Intelligence</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class='info-card card-amber'>
            <span class='info-card-icon'>🎯</span>
            <div class='info-card-title'>Visi Dashboard</div>
            <div class='info-card-body'>
                Dashboard ini dirancang sebagai sistem pemantauan lalu lintas otomatis (<i>Smart Traffic Surveillance</i>) terintegrasi.
                Memanfaatkan model deteksi objek YOLOv11 dan Optical Character Recognition (OCR), sistem ini ditargetkan untuk
                menyokong program digitalisasi penegakan hukum pajak kendaraan bermotor daerah secara otomatis dan efisien.
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-label'>Anggota Inti</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class='member-card m-blue'>
            <div class='member-avatar avatar-blue'>👨‍💻</div>
            <div class='member-name'>Dani Raditya M.</div>
            <div class='member-nim'>NIM: 2355301042</div>
            <span class='member-role role-blue'>Website Engineer</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='member-card m-green'>
            <div class='member-avatar avatar-green'>👩‍💻</div>
            <div class='member-name'>Elsha Amara Davia</div>
            <div class='member-nim'>NIM: 2355301056</div>
            <span class='member-role role-green'>AI Engineer</span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class='member-card m-amber'>
            <div class='member-avatar avatar-amber'>👨‍🔧</div>
            <div class='member-name'>M. Rizal Wahyu</div>
            <div class='member-nim'>NIM: 2355301xxx</div>
            <span class='member-role role-amber'>Data Architect</span>
        </div>
        """, unsafe_allow_html=True)


# ==========================================
# HALAMAN 2: DESKRIPSI & LATAR BELAKANG
# ==========================================
elif page == "📖 Deskripsi & Latar Belakang":
    st.markdown("""
        <div class='page-header'>
            <div class='page-eyebrow'>// LATAR BELAKANG</div>
            <div class='main-title'>Mengapa <span class='title-accent'>AutoTax?</span></div>
            <div class='subtitle'>Transformasi penegakan hukum pajak via Computer Vision</div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown("""
        <div class='info-card card-red'>
            <span class='info-card-icon'>❌</span>
            <div class='info-card-title'>Hambatan Operasional Lapangan</div>
            <div class='info-card-body'>
                Pengecekan pajak konvensional yang mengandalkan razia fisik di jalan arteri terbukti menciptakan kemacetan besar
                dan gesekan sosial dengan pengendara. Keterbatasan personel polisi dan dinas pendapatan daerah membuat intensitas
                pengawasan tidak merata dan mudah dihindari.
            </div>
        </div>
        <div class='info-card card-blue'>
            <span class='info-card-icon'>🚀</span>
            <div class='info-card-title'>Pipeline Kecerdasan Buatan AutoTax</div>
            <div class='info-card-body'>
                Sistem AutoTax meniadakan kebutuhan penghentian laju kendaraan. Citra kendaraan ditangkap via CCTV,
                diproses instan menggunakan model <b>YOLOv11 ONNX</b> untuk mengunci citra plat,
                lalu diserahkan ke mesin <b>EasyOCR</b> untuk penentuan tanggal kedaluwarsa pajak.
            </div>
        </div>
        <div class='info-card card-green'>
            <span class='info-card-icon'>⚡</span>
            <div class='info-card-title'>Tumpukan Teknologi (Tech Stack)</div>
            <div class='info-card-body' style='display: flex; flex-direction: column; gap: 10px; margin-top: 10px;'>
                <div style='display: flex; align-items: center; gap: 10px;'>
                    <span style='background: #fef3c7; color: #d97706; padding: 4px 10px; border-radius: 6px; font-family: monospace; font-size: 0.78rem; font-weight: 700; min-width: 110px; text-align: center;'>YOLOv11 ONNX</span>
                    <span style='font-size: 0.85rem; font-weight: 500;'>Deteksi objek plat nomor presisi tinggi</span>
                </div>
                <div style='display: flex; align-items: center; gap: 10px;'>
                    <span style='background: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 6px; font-family: monospace; font-size: 0.78rem; font-weight: 700; min-width: 110px; text-align: center;'>EasyOCR</span>
                    <span style='font-size: 0.85rem; font-weight: 500;'>Ekstraksi teks plat & tanggal kedaluwarsa</span>
                </div>
                <div style='display: flex; align-items: center; gap: 10px;'>
                    <span style='background: #d1fae5; color: #047857; padding: 4px 10px; border-radius: 6px; font-family: monospace; font-size: 0.78rem; font-weight: 700; min-width: 110px; text-align: center;'>Streamlit</span>
                    <span style='font-size: 0.85rem; font-weight: 500;'>Dashboard monitoring interaktif</span>
                </div>
                <div style='display: flex; align-items: center; gap: 10px;'>
                    <span style='background: #f1f5f9; color: #475569; padding: 4px 10px; border-radius: 6px; font-family: monospace; font-size: 0.78rem; font-weight: 700; min-width: 110px; text-align: center;'>OpenCV</span>
                    <span style='font-size: 0.85rem; font-weight: 500;'>Pre-processing citra & rendering frame</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)
        st.image(
            "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&w=600&q=80",
            caption="// Ilustrasi implementasi smart traffic camera",
            use_container_width=True
        )
        st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# HALAMAN 3: MESIN DETEKSI PAJAK
# ==========================================
elif page == "⚙️ Mesin Deteksi Pajak":
    st.markdown("""
        <div class='page-header'>
            <div class='page-eyebrow'>// INFERENCE ENGINE</div>
            <div class='main-title'>Mesin <span class='title-accent'>Deteksi</span> Pajak</div>
            <div class='subtitle'>Pipeline YOLOv11-Nano · EasyOCR · Analisis Kedaluwarsa Pajak</div>
        </div>
    """, unsafe_allow_html=True)

    # --- TAB: Gambar / Video / Kamera ---
    tab_img, tab_vid, tab_cam = st.tabs([
        "🖼️  Gambar Statis",
        "🎬  Rekaman Video",
        "📷  Kamera Real-time",
    ])

    # ======================================
    # TAB 1 — GAMBAR STATIS (tidak diubah)
    # ======================================
    with tab_img:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>Unggah Citra Kendaraan</div>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Seret file ke sini atau klik untuk memilih (JPG, JPEG, PNG)",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if uploaded_file is not None:
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            img_bgr = cv2.imdecode(file_bytes, 1)
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

            with st.spinner("⚡ Menjalankan inferensi deep learning..."):
                model = load_yolo()
                results = model(img_bgr, conf=0.35, verbose=False)
                boxes = results[0].boxes

                annotated_img = img_rgb.copy()
                detections_data = []
                total_aktif = 0
                total_mati = 0

                for box in boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    crop = img_bgr[y1:y2, x1:x2]

                    if crop.size > 0:
                        conf_yolo = float(box.conf[0]) * 100
                        raw_text, conf_ocr = ocr_and_predict(crop)
                        plat, bln, thn = extract_data(raw_text)
                        status, color_rgb = cek_status_pajak(bln, thn)

                        if status == "PAJAK AKTIF":
                            total_aktif += 1
                        elif status == "PAJAK MATI":
                            total_mati += 1

                        cv2.rectangle(annotated_img, (x1, y1), (x2, y2), color_rgb, 3)
                        cv2.rectangle(annotated_img, (x1, max(y1 - 34, 0)), (x2, y1), color_rgb, -1)
                        cv2.putText(annotated_img, f"{plat}  ({conf_ocr:.0f}%)", (x1 + 8, max(y1 - 10, 14)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

                        masa_fmt = f"{bln:02d} / {str(thn)}" if bln and thn else "Gagal Parsing"

                        detections_data.append({
                            "plat": plat,
                            "raw": raw_text if raw_text else "Tidak Ada Teks",
                            "masa": masa_fmt,
                            "status": status,
                            "conf_yolo": conf_yolo,
                            "conf_ocr": conf_ocr,
                        })

                        # --- Catat otomatis ke Histori Deteksi ---
                        catat_riwayat(
                            sumber="Gambar",
                            plat=plat,
                            masa=masa_fmt,
                            status=status,
                            conf_yolo=conf_yolo,
                            conf_ocr=conf_ocr,
                            raw_ocr=raw_text if raw_text else "Tidak Ada Teks",
                        )

            st.markdown(f"""
            <div class='metric-row'>
                <div class='metric-box m-total'>
                    <div class='metric-label'>Kendaraan Terdeteksi</div>
                    <div class='metric-value'>{len(detections_data)}<span class='metric-unit'>unit</span></div>
                </div>
                <div class='metric-box m-active'>
                    <div class='metric-label'><span class='tl-dot tl-green'></span>Pajak Aktif</div>
                    <div class='metric-value'>{total_aktif}<span class='metric-unit'>unit</span></div>
                </div>
                <div class='metric-box m-dead'>
                    <div class='metric-label'><span class='tl-dot tl-red'></span>Pajak Mati</div>
                    <div class='metric-value'>{total_mati}<span class='metric-unit'>unit</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_img, col_res = st.columns([1.2, 1])

            with col_img:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<div class='section-label'>Hasil Anotasi Bounding Box</div>", unsafe_allow_html=True)
                st.image(annotated_img, caption="// Output YOLOv11 inference pipeline", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_res:
                st.markdown("<div class='section-label'>Log Inspeksi Kendaraan</div>", unsafe_allow_html=True)

                if not detections_data:
                    st.markdown("""
                    <div class='result-card rc-expired'>
                        <div class='result-header'>
                            <div class='result-vehicle-id'>Zero Detection</div>
                            <span class='badge badge-expired'>Gagal</span>
                        </div>
                        <div style='font-size:0.85rem; color:#5a6090; line-height:1.7;'>
                            Model tidak berhasil mendeteksi plat nomor. Periksa pencahayaan dan resolusi gambar input.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    for idx, det in enumerate(detections_data):
                        if det["status"] == "PAJAK AKTIF":
                            rc_class = "rc-active"
                            badge = "<span class='badge badge-active'>Aktif</span>"
                        elif det["status"] == "PAJAK MATI":
                            rc_class = "rc-expired"
                            badge = "<span class='badge badge-expired'>Kedaluwarsa</span>"
                        else:
                            rc_class = "rc-unknown"
                            badge = "<span class='badge badge-unknown'>Tidak Terbaca</span>"

                        st.markdown(f"""
                        <div class='result-card {rc_class}'>
                            <div class='result-header'>
                                <div class='result-vehicle-id'>Kendaraan #{idx+1:02d}</div>
                                {badge}
                            </div>
                            <div class='data-row'>
                                <span class='data-key'>Nomor Plat</span>
                                <span class='data-val plate-num'>{det['plat']}</span>
                            </div>
                            <div class='data-row'>
                                <span class='data-key'>Masa Berlaku</span>
                                <span class='data-val'>{det['masa']}</span>
                            </div>
                            <div class='data-row'>
                                <span class='data-key'>Confidence Deteksi (YOLO)</span>
                                <span class='data-val {conf_class(det['conf_yolo'])}'>{det['conf_yolo']:.1f}%</span>
                            </div>
                            <div class='data-row'>
                                <span class='data-key'>Confidence OCR</span>
                                <span class='data-val {conf_class(det['conf_ocr'])}'>{det['conf_ocr']:.1f}%</span>
                            </div>
                            <div class='data-row'>
                                <span class='data-key'>Raw OCR Token</span>
                                <span class='data-val mono'>{det['raw']}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        if det["status"] == "PAJAK AKTIF":
                            st.toast(f"Unit {det['plat']} — Terverifikasi patuh.", icon="🟢")
                        elif det["status"] == "PAJAK MATI":
                            st.toast(f"Unit {det['plat']} — Pelanggaran terdeteksi!", icon="🔴")
        else:
            st.markdown("""
            <div class='card'>
                <div class='empty-state'>
                    <span class='empty-icon'>🚦</span>
                    <div class='empty-title'>Sistem Siap Menerima Input</div>
                    <div class='empty-body'>Unggah foto kendaraan atau area plat nomor untuk memulai analisis inferensi otomatis.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ======================================
    # TAB 2 — REKAMAN VIDEO (frame-by-frame live)
    # ======================================
    with tab_vid:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>Unggah Berkas Video</div>", unsafe_allow_html=True)
        uploaded_video = st.file_uploader(
            "Seret file video ke sini atau klik untuk memilih (MP4, AVI, MOV)",
            type=["mp4", "avi", "mov"],
            key="video_upload",
            label_visibility="collapsed"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Slider skip frame — makin besar makin cepat tapi deteksi lebih jarang
        skip_n = st.slider(
            "Proses setiap N frame (lebih besar = lebih cepat, deteksi lebih jarang)",
            min_value=1, max_value=10, value=3, step=1
        )

        if uploaded_video is not None:
            # Simpan ke file sementara agar OpenCV bisa buka via path
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            tfile.write(uploaded_video.read())
            tfile.flush()
            tfile.close()

            cap = cv2.VideoCapture(tfile.name)
            try:
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps_video    = cap.get(cv2.CAP_PROP_FPS) or 25

                model = load_yolo()

                # Layout: video kiri, log kanan
                col_vid, col_log = st.columns([1.3, 1])

                with col_vid:
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown("<div class='section-label'>Live Annotated Stream</div>", unsafe_allow_html=True)
                    # Placeholder progress info
                    progress_info = st.empty()
                    # Placeholder frame video
                    frame_holder = st.empty()
                    st.markdown("</div>", unsafe_allow_html=True)

                with col_log:
                    st.markdown("<div class='section-label'>Real-time Log Scanning</div>", unsafe_allow_html=True)
                    # Placeholder metric ringkasan
                    metric_holder = st.empty()
                    # Placeholder log kartu
                    log_holder = st.empty()

                # State untuk log & metric
                detected_history = {}   # plat -> {masa, status, timestamp}
                total_aktif_v = 0
                total_mati_v  = 0

                frame_idx  = 0
                last_boxes = []         # cache boxes dari frame sebelumnya
                box_labels = {}         # cache OCR label untuk bounding boxes

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # Jalankan inferensi YOLO hanya setiap skip_n frame
                    if frame_idx % skip_n == 0:
                        res = model(frame, conf=0.35, verbose=False)
                        last_boxes = res[0].boxes
                        box_labels.clear()

                        # OCR & annotasi hanya pada frame yang diinfer
                        for bi, box in enumerate(last_boxes):
                            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                            crop = frame[y1:y2, x1:x2]
                            if crop.size == 0:
                                continue

                            conf_yolo = float(box.conf[0]) * 100
                            raw_text, conf_ocr = ocr_and_predict(crop)
                            plat, bln, thn = extract_data(raw_text)
                            status, color_rgb = cek_status_pajak(bln, thn)

                            box_labels[bi] = {
                                "plat": plat,
                                "status": status,
                                "color": color_rgb,
                                "label_txt": f"{plat} ({status})" if plat != "Tidak Terbaca" else "Tidak Terbaca"
                            }

                            # Simpan ke history hanya jika plat baru & berhasil dibaca
                            if plat != "Tidak Terbaca" and plat not in detected_history:
                                if status == "PAJAK AKTIF":
                                    total_aktif_v += 1
                                elif status == "PAJAK MATI":
                                    total_mati_v += 1

                                masa_fmt_v = f"{bln:02d} / {thn}" if bln and thn else "Gagal Parsing"

                                detected_history[plat] = {
                                    "masa": masa_fmt_v,
                                    "status": status,
                                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                                    "conf_yolo": conf_yolo,
                                    "conf_ocr": conf_ocr,
                                }

                                # --- Catat otomatis ke Histori Deteksi ---
                                catat_riwayat(
                                    sumber="Video",
                                    plat=plat,
                                    masa=masa_fmt_v,
                                    status=status,
                                    conf_yolo=conf_yolo,
                                    conf_ocr=conf_ocr,
                                    raw_ocr=raw_text if raw_text else "Tidak Ada Teks",
                                )

                    # Gambar bounding box dari cache last_boxes di SETIAP frame
                    # supaya anotasi tetap muncul di frame yang di-skip
                    for bi, box in enumerate(last_boxes):
                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        info = box_labels.get(bi, None)
                        if info:
                            color = info["color"]
                            label_txt = info["label_txt"]
                        else:
                            color = (180, 180, 180)
                            label_txt = "Scanning..."

                        cv2.rectangle(frame_rgb, (x1, y1), (x2, y2), color, 3)
                        cv2.rectangle(frame_rgb, (x1, max(y1 - 30, 0)), (x2, y1), color, -1)
                        cv2.putText(frame_rgb, label_txt, (x1 + 6, max(y1 - 8, 14)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)

                # Overlay info frame di pojok kiri atas
                pct = int(100 * frame_idx / total_frames) if total_frames > 0 else 0
                cv2.putText(frame_rgb,
                            f"Frame {frame_idx}/{total_frames}  |  {pct}%",
                            (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(frame_rgb,
                            f"Plat unik: {len(detected_history)}",
                            (10, 54), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 230, 225), 2, cv2.LINE_AA)

                # --- Render frame ke Streamlit ---
                frame_holder.image(frame_rgb, use_container_width=True)

                # --- Progress bar ---
                progress_info.markdown(f"""
                <div class='video-info-row'>
                    <span>Frame {frame_idx} / {total_frames}</span>
                    <span>{pct}%</span>
                </div>
                <div class='video-progress-wrap'>
                    <div class='video-progress-bar' style='width:{pct}%;'></div>
                </div>
                """, unsafe_allow_html=True)

                # --- Metric ringkasan ---
                metric_holder.markdown(f"""
                <div class='metric-row' style='margin-bottom:14px;'>
                    <div class='metric-box m-total'>
                        <div class='metric-label'>Plat Unik</div>
                        <div class='metric-value'>{len(detected_history)}<span class='metric-unit'>unit</span></div>
                    </div>
                    <div class='metric-box m-active'>
                        <div class='metric-label'><span class='tl-dot tl-green'></span>Aktif</div>
                        <div class='metric-value'>{total_aktif_v}<span class='metric-unit'>unit</span></div>
                    </div>
                    <div class='metric-box m-dead'>
                        <div class='metric-label'><span class='tl-dot tl-red'></span>Mati</div>
                        <div class='metric-value'>{total_mati_v}<span class='metric-unit'>unit</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # --- Log kartu real-time ---
                log_html = "<div style='max-height:420px; overflow-y:auto;'>"
                if not detected_history:
                    log_html += "<p style='color:#7A928C; font-size:0.85rem; padding:12px 0;'>Menunggu kendaraan terdeteksi...</p>"
                else:
                    for plate_no, data in reversed(list(detected_history.items())):
                        if data["status"] == "PAJAK AKTIF":
                            rc_c = "rc-active"; bc = "badge-active"; bl = "Aktif"
                        elif data["status"] == "PAJAK MATI":
                            rc_c = "rc-expired"; bc = "badge-expired"; bl = "Kedaluwarsa"
                        else:
                            rc_c = "rc-unknown"; bc = "badge-unknown"; bl = "Tidak Terbaca"

                        log_html += f"""
                        <div class='result-card {rc_c}' style='margin-bottom:10px;'>
                            <div class='result-header'>
                                <div class='result-vehicle-id'>⏱ {data['timestamp']}</div>
                                <span class='badge {bc}'>{bl}</span>
                            </div>
                            <div class='data-row'>
                                <span class='data-key'>No. Plat</span>
                                <span class='data-val plate-num'>{plate_no}</span>
                            </div>
                            <div class='data-row'>
                                <span class='data-key'>Berlaku s/d</span>
                                <span class='data-val'>{data['masa']}</span>
                            </div>
                            <div class='data-row'>
                                <span class='data-key'>Confidence Deteksi</span>
                                <span class='data-val {conf_class(data['conf_yolo'])}'>{data['conf_yolo']:.1f}%</span>
                            </div>
                            <div class='data-row'>
                                <span class='data-key'>Confidence OCR</span>
                                <span class='data-val {conf_class(data['conf_ocr'])}'>{data['conf_ocr']:.1f}%</span>
                            </div>
                        </div>"""
                log_html += "</div>"
                log_holder.markdown(log_html, unsafe_allow_html=True)

                frame_idx += 1

            finally:
                cap.release()
                try:
                    os.unlink(tfile.name)   # Hapus file sementara
                except Exception:
                    pass

            st.success(f"🎉 Pemrosesan selesai — {len(detected_history)} plat unik teridentifikasi dari {total_frames} frame.")

        else:
            st.markdown("""
            <div class='card'>
                <div class='empty-state'>
                    <span class='empty-icon'>📹</span>
                    <div class='empty-title'>Sistem Siap Menerima Input Video</div>
                    <div class='empty-body'>Unggah file video rekaman CCTV/jalan raya. Deteksi plat dan pengecekan pajak berjalan langsung per frame secara real-time.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ======================================
    # TAB 3 — KAMERA REAL-TIME (REPLACEMENT)
    # ======================================
    with tab_cam:
        st.markdown("""
        <div class='info-card card-blue' style='margin-bottom:18px;'>
            <span class='info-card-icon'>📷</span>
            <div class='info-card-title'>Kamera Real-time Terintegrasi (Smart-Mirror Mode)</div>
            <div class='info-card-body'>
                Mode ini menangkap stream video langsung dari kamera lokal/webcam Anda menggunakan engine OpenCV. 
                Sistem akan membalikkan stream agar gerakan Anda terasa natural seperti cermin, namun tulisan plat nomor 
                tetap diproses secara normal oleh model YOLO dan EasyOCR untuk fungsionalitas akurat tanpa lag internal WebRTC.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Kontrol interaksi Kamera
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>Kontrol Kamera</div>", unsafe_allow_html=True)
        
        col_btn1, col_btn2, col_slider = st.columns([1, 1, 2])
        with col_btn1:
            start_cam = st.button("▶ Mulai Kamera", use_container_width=True, type="primary")
        with col_btn2:
            stop_cam = st.button("⏹ Hentikan Kamera", use_container_width=True)
        with col_slider:
            skip_n_cam = st.slider(
                "Proses setiap N frame kamera (lebih besar = stream lebih lancar)",
                min_value=1, max_value=10, value=4, step=1, key="cam_skip_slider"
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # Inisialisasi Layout / Placeholder (Sama persis dengan konsep Video)
        col_cam_stream, col_cam_log = st.columns([1.3, 1])

        with col_cam_stream:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-label'>Live Camera Stream (Mirror)</div>", unsafe_allow_html=True)
            frame_holder_cam = st.empty()
            st.markdown("</div>", unsafe_allow_html=True)

        with col_cam_log:
            st.markdown("<div class='section-label'>Real-time Camera Scanning Log</div>", unsafe_allow_html=True)
            metric_holder_cam = st.empty()
            log_holder_cam = st.empty()

        # Logic Execution Loop Kamera — THREADED (Non-Blocking)
        if start_cam and not stop_cam:
            cap_cam = cv2.VideoCapture(0)
            try:
                # Atur resolusi agar ringan saat pemrosesan OCR
                cap_cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap_cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

                model = load_yolo()
                reader_thread = load_ocr()

                # State storage (shared between threads via mutable containers)
                cam_history = {}  # plat -> {masa, status, timestamp, conf_yolo, conf_ocr}
                total_aktif_c = [0]   # list agar bisa diubah dari dalam thread
                total_mati_c  = [0]

                # Shared state for the AI inference thread
                ai_lock = threading.Lock()
                ai_boxes = []        # bounding boxes dari hasil YOLO terakhir
                ai_labels = {}       # box_idx -> {plat, status, color, label_txt}
                ai_busy = [False]    # list agar bisa diubah dari dalam thread
                ai_frame = [None]    # frame yang sedang/akan diproses AI
                ai_stop = [False]    # signal stop ke thread
                ai_new_detections = [] # queue of detections to record on main thread

                def ai_worker():
                    """Background thread: jalankan YOLO + OCR tanpa memblokir main loop."""
                    while not ai_stop[0]:
                        # Tunggu sampai ada frame baru untuk diproses
                        if ai_frame[0] is None:
                            time.sleep(0.01)
                            continue

                        with ai_lock:
                            frame_to_process = ai_frame[0].copy()
                            ai_frame[0] = None  # tandai sudah diambil
                            ai_busy[0] = True

                        try:
                            res = model(frame_to_process, conf=0.35, verbose=False)
                            boxes = res[0].boxes
                            new_boxes = []
                            new_labels = {}
                            pending_detections = []

                            for bi, box in enumerate(boxes):
                                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                                crop = frame_to_process[y1:y2, x1:x2]
                                if crop.size == 0:
                                    continue

                                conf_yolo = float(box.conf[0]) * 100
                                raw_text, conf_ocr = ocr_and_predict(crop, reader=reader_thread)
                                plat, bln, thn = extract_data(raw_text)
                                status, _ = cek_status_pajak(bln, thn)

                                # Warna berdasarkan status
                                if status == "PAJAK AKTIF":
                                    color = (3, 114, 114)
                                elif status == "PAJAK MATI":
                                    color = (255, 168, 0)
                                else:
                                    color = (252, 205, 23)

                                new_boxes.append((x1, y1, x2, y2))
                                new_labels[bi] = {
                                    "plat": plat, "status": status,
                                    "color": color,
                                    "label_txt": f"{plat} ({status})",
                                }

                                # Simpan ke pending jika plat valid dan belum tercatat
                                if plat != "Tidak Terbaca":
                                    pending_detections.append({
                                        "plat": plat,
                                        "bln": bln,
                                        "thn": thn,
                                        "status": status,
                                        "conf_yolo": conf_yolo,
                                        "conf_ocr": conf_ocr,
                                        "raw_text": raw_text
                                    })

                            # Simpan hasil ke shared state
                            with ai_lock:
                                ai_boxes.clear()
                                ai_boxes.extend(new_boxes)
                                ai_labels.clear()
                                ai_labels.update(new_labels)

                                for det in pending_detections:
                                    plat = det["plat"]
                                    if plat not in cam_history:
                                        status = det["status"]
                                        if status == "PAJAK AKTIF":
                                            total_aktif_c[0] += 1
                                        elif status == "PAJAK MATI":
                                            total_mati_c[0] += 1

                                        bln, thn = det["bln"], det["thn"]
                                        masa_fmt_c = f"{bln:02d} / {thn}" if bln and thn else "Gagal Parsing"

                                        cam_history[plat] = {
                                            "masa": masa_fmt_c,
                                            "status": status,
                                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                                            "conf_yolo": det["conf_yolo"],
                                            "conf_ocr": det["conf_ocr"],
                                        }

                                        # Catat untuk diproses oleh main thread
                                        ai_new_detections.append({
                                            "plat": plat,
                                            "masa": masa_fmt_c,
                                            "status": status,
                                            "conf_yolo": det["conf_yolo"],
                                            "conf_ocr": det["conf_ocr"],
                                            "raw_ocr": det["raw_text"] if det["raw_text"] else "Tidak Ada Teks",
                                        })
                        except Exception:
                            pass
                        finally:
                            ai_busy[0] = False

                # Mulai thread AI di background
                ai_thread = threading.Thread(target=ai_worker, daemon=True)
                ai_thread.start()

                frame_idx_cam = 0

                while cap_cam.isOpened():
                    ret, frame = cap_cam.read()
                    if not ret:
                        st.error("Gagal mendapatkan gambar dari kamera. Pastikan kamera tidak digunakan aplikasi lain.")
                        break

                    frame_ai = frame.copy()

                    # Kirim frame ke thread AI setiap N frame (hanya jika thread tidak sedang sibuk)
                    if frame_idx_cam % skip_n_cam == 0 and not ai_busy[0]:
                        with ai_lock:
                            ai_frame[0] = frame.copy()

                    # Gambar bounding box dari hasil AI terakhir (non-blocking)
                    with ai_lock:
                        current_boxes = list(ai_boxes)
                        current_labels = dict(ai_labels)

                    for bi, (x1, y1, x2, y2) in enumerate(current_boxes):
                        info = current_labels.get(bi, None)
                        if info:
                            color = info["color"]
                            label_txt = info["label_txt"]
                        else:
                            color = (180, 180, 180)
                            label_txt = "Scanning..."

                        cv2.rectangle(frame_ai, (x1, y1), (x2, y2), color, 3)
                        cv2.rectangle(frame_ai, (x1, max(y1 - 30, 0)), (x2, y1), color, -1)
                        cv2.putText(frame_ai, label_txt, (x1 + 6, max(y1 - 8, 14)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                    # Efek Cermin (Mirror) hanya untuk tampilan UI
                    frame_final = cv2.flip(frame_ai, 1)
                    frame_rgb = cv2.cvtColor(frame_final, cv2.COLOR_BGR2RGB)

                    # Process any new detections from background thread in the main thread (thread-safe)
                    with ai_lock:
                        local_new_dets = list(ai_new_detections)
                        ai_new_detections.clear()

                    for det in local_new_dets:
                        catat_riwayat(
                            sumber="Kamera",
                            plat=det["plat"],
                            masa=det["masa"],
                            status=det["status"],
                            conf_yolo=det["conf_yolo"],
                            conf_ocr=det["conf_ocr"],
                            raw_ocr=det["raw_ocr"]
                        )

                    # Thread-safe read for counts and history
                    with ai_lock:
                        cnt_total = len(cam_history)
                        cnt_aktif = total_aktif_c[0]
                        cnt_mati  = total_mati_c[0]
                        local_cam_history = dict(cam_history)

                    # Overlay Info Statis
                    status_text = "LIVE" if not ai_busy[0] else "SCANNING..."
                    status_color = (0, 255, 0) if not ai_busy[0] else (0, 200, 255)
                    cv2.putText(frame_rgb, status_text, (10, 28), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.55, status_color, 2, cv2.LINE_AA)
                    cv2.putText(frame_rgb, f"Plat Unik: {cnt_total}", (10, 54), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                    # 1. Render Stream ke UI
                    frame_holder_cam.image(frame_rgb, use_container_width=True)

                    # 2. Render Ringkasan Metric
                    metric_holder_cam.markdown(f"""
                    <div class='metric-row' style='margin-bottom:14px;'>
                        <div class='metric-box m-total'>
                            <div class='metric-label'>Total Plat</div>
                            <div class='metric-value'>{cnt_total}<span class='metric-unit'>unit</span></div>
                        </div>
                        <div class='metric-box m-active'>
                            <div class='metric-label'><span class='tl-dot tl-green'></span>Aktif</div>
                            <div class='metric-value'>{cnt_aktif}<span class='metric-unit'>unit</span></div>
                        </div>
                        <div class='metric-box m-dead'>
                            <div class='metric-label'><span class='tl-dot tl-red'></span>Mati</div>
                            <div class='metric-value'>{cnt_mati}<span class='metric-unit'>unit</span></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # 3. Render Log Kartu Inspeksi Real-time
                    log_html = "<div style='max-height:380px; overflow-y:auto;'>"
                    if not local_cam_history:
                        log_html += "<p style='color:#64748b; font-size:0.85rem; padding:12px 0;'>Menghadapkan plat kendaraan ke kamera...</p>"
                    else:
                        for plate_no, data in reversed(list(local_cam_history.items())):
                            if data["status"] == "PAJAK AKTIF":
                                rc_c = "rc-active"; bc = "badge-active"; bl = "Aktif"
                            elif data["status"] == "PAJAK MATI":
                                rc_c = "rc-expired"; bc = "badge-expired"; bl = "Kedaluwarsa"
                            else:
                                rc_c = "rc-unknown"; bc = "badge-unknown"; bl = "Tidak Terbaca"

                            log_html += f"""
                            <div class='result-card {rc_c}' style='margin-bottom:10px;'>
                                <div class='result-header'>
                                    <div class='result-vehicle-id'>⏱ {data['timestamp']}</div>
                                    <span class='badge {bc}'>{bl}</span>
                                </div>
                                <div class='data-row'>
                                    <span class='data-key'>No. Plat</span>
                                    <span class='data-val plate-num'>{plate_no}</span>
                                </div>
                                <div class='data-row'>
                                    <span class='data-key'>Berlaku s/d</span>
                                    <span class='data-val'>{data['masa']}</span>
                                </div>
                                <div class='data-row'>
                                    <span class='data-key'>Confidence YOLO</span>
                                    <span class='data-val {conf_class(data['conf_yolo'])}'>{data['conf_yolo']:.1f}%</span>
                                </div>
                                <div class='data-row'>
                                    <span class='data-key'>Confidence OCR</span>
                                    <span class='data-val {conf_class(data['conf_ocr'])}'>{data['conf_ocr']:.1f}%</span>
                                </div>
                            </div>"""
                    log_html += "</div>"
                    log_holder_cam.markdown(log_html, unsafe_allow_html=True)

                    frame_idx_cam += 1
            finally:
                ai_stop[0] = True
                try:
                    ai_thread.join(timeout=2)
                except Exception:
                    pass
                cap_cam.release()
        else:
            st.markdown("""
            <div class='card'>
                <div class='empty-state'>
                    <span class='empty-icon'>🎥</span>
                    <div class='empty-title'>Kamera Nonaktif</div>
                    <div class='empty-body'>Klik tombol <b>Mulai Kamera</b> di atas untuk menghidupkan webcam dan memulai pemindaian plat secara live.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ==========================================
# HALAMAN 4: HISTORI DETEKSI (BARU)
# ==========================================
elif page == "🗂️ Histori Deteksi":
    st.markdown("""
        <div class='page-header'>
            <div class='page-eyebrow'>// RECORD KEEPING</div>
            <div class='main-title'>Histori <span class='title-accent'>Deteksi</span></div>
            <div class='subtitle'>Rekam jejak seluruh hasil pemindaian pajak dari Gambar, Video, dan Kamera Real-time</div>
        </div>
    """, unsafe_allow_html=True)

    riwayat = st.session_state.riwayat_deteksi

    # --- Jika sedang melihat detail salah satu entri ---
    if st.session_state.riwayat_detail_idx is not None and 0 <= st.session_state.riwayat_detail_idx < len(riwayat):
        idx_detail = st.session_state.riwayat_detail_idx
        item = riwayat[idx_detail]

        if st.button("← Kembali ke Daftar Histori"):
            st.session_state.riwayat_detail_idx = None
            st.rerun()

        if item["status"] == "PAJAK AKTIF":
            badge_detail = "<span class='badge badge-active'>Aktif</span>"
        elif item["status"] == "PAJAK MATI":
            badge_detail = "<span class='badge badge-expired'>Kedaluwarsa</span>"
        else:
            badge_detail = "<span class='badge badge-unknown'>Tidak Terbaca</span>"

        st.markdown(f"""
        <div class='detail-banner'>
            <div style='font-size:0.72rem; letter-spacing:2px; text-transform:uppercase; opacity:0.85; margin-bottom:6px;'>
                Detail Entri Histori #{idx_detail + 1:04d}
            </div>
            <div class='detail-plate-big'>{item['plat']}</div>
        </div>
        """, unsafe_allow_html=True)

        col_d1, col_d2 = st.columns([1, 1])

        with col_d1:
            st.markdown(f"""
            <div class='result-card { "rc-active" if item["status"]=="PAJAK AKTIF" else ("rc-expired" if item["status"]=="PAJAK MATI" else "rc-unknown") }'>
                <div class='result-header'>
                    <div class='result-vehicle-id'>Status Pajak</div>
                    {badge_detail}
                </div>
                <div class='data-row'>
                    <span class='data-key'>Nomor Plat</span>
                    <span class='data-val plate-num'>{item['plat']}</span>
                </div>
                <div class='data-row'>
                    <span class='data-key'>Masa Berlaku</span>
                    <span class='data-val'>{item['masa']}</span>
                </div>
                <div class='data-row'>
                    <span class='data-key'>Sumber Deteksi</span>
                    <span class='data-val'><span class='history-source-tag'>{item['sumber']}</span></span>
                </div>
                <div class='data-row'>
                    <span class='data-key'>Waktu Pencatatan</span>
                    <span class='data-val mono'>{item['waktu']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_d2:
            st.markdown(f"""
            <div class='result-card rc-unknown'>
                <div class='result-header'>
                    <div class='result-vehicle-id'>Detail Confidence Pipeline</div>
                </div>
                <div class='data-row'>
                    <span class='data-key'>Confidence Deteksi (YOLO)</span>
                    <span class='data-val {conf_class(item['conf_yolo'])}'>{item['conf_yolo']:.1f}%</span>
                </div>
                <div class='data-row'>
                    <span class='data-key'>Confidence OCR</span>
                    <span class='data-val {conf_class(item['conf_ocr'])}'>{item['conf_ocr']:.1f}%</span>
                </div>
                <div class='data-row'>
                    <span class='data-key'>Raw OCR Token</span>
                    <span class='data-val mono'>{item['raw_ocr']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class='info-card' style='margin-top:6px;'>
            <div class='info-card-body' style='font-size:0.82rem;'>
                💡 Confidence YOLO menunjukkan tingkat keyakinan model dalam mengenali lokasi plat nomor pada citra,
                sedangkan Confidence OCR menunjukkan tingkat keyakinan mesin EasyOCR dalam membaca karakter teks pada plat tersebut.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- Tampilan daftar histori (default) ---
    else:
        if not riwayat:
            st.markdown("""
            <div class='card'>
                <div class='empty-state'>
                    <span class='empty-icon'>🗂️</span>
                    <div class='empty-title'>Histori Masih Kosong</div>
                    <div class='empty-body'>Belum ada deteksi yang tercatat. Lakukan deteksi pajak melalui tab Gambar, Video, atau Kamera Real-time pada menu "Mesin Deteksi Pajak" — setiap hasil akan otomatis tersimpan di sini.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            total_riwayat = len(riwayat)
            total_aktif_r = sum(1 for r in riwayat if r["status"] == "PAJAK AKTIF")
            total_mati_r  = sum(1 for r in riwayat if r["status"] == "PAJAK MATI")

            st.markdown(f"""
            <div class='metric-row'>
                <div class='metric-box m-total'>
                    <div class='metric-label'>Total Tercatat</div>
                    <div class='metric-value'>{total_riwayat}<span class='metric-unit'>entri</span></div>
                </div>
                <div class='metric-box m-active'>
                    <div class='metric-label'><span class='tl-dot tl-green'></span>Pajak Aktif</div>
                    <div class='metric-value'>{total_aktif_r}<span class='metric-unit'>entri</span></div>
                </div>
                <div class='metric-box m-dead'>
                    <div class='metric-label'><span class='tl-dot tl-red'></span>Pajak Mati</div>
                    <div class='metric-value'>{total_mati_r}<span class='metric-unit'>entri</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # --- Toolbar: filter sumber + tombol bersihkan ---
            col_f1, col_f2 = st.columns([3, 1])
            with col_f1:
                filter_sumber = st.multiselect(
                    "Filter berdasarkan sumber deteksi",
                    options=["Gambar", "Video", "Kamera"],
                    default=["Gambar", "Video", "Kamera"],
                )
            with col_f2:
                st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
                if st.button("🗑️ Bersihkan Histori", use_container_width=True):
                    st.session_state.riwayat_deteksi = []
                    st.rerun()

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-label'>Daftar Riwayat Deteksi (terbaru di atas)</div>", unsafe_allow_html=True)

            st.markdown("""
            <div class='history-table-head'>
                <span>Waktu</span>
                <span>Nomor Plat</span>
                <span>Masa Berlaku</span>
                <span>Status</span>
                <span>Sumber</span>
                <span>Detail</span>
            </div>
            """, unsafe_allow_html=True)

            # Tampilkan terbaru di atas, simpan index asli untuk keperluan detail
            indexed_riwayat = list(enumerate(riwayat))
            indexed_riwayat_filtered = [
                (i, r) for i, r in indexed_riwayat if r["sumber"] in filter_sumber
            ]
            indexed_riwayat_filtered.reverse()

            if not indexed_riwayat_filtered:
                st.markdown("""
                <p style='color:#7A928C; font-size:0.85rem; padding:14px 4px;'>
                    Tidak ada entri yang cocok dengan filter sumber yang dipilih.
                </p>
                """, unsafe_allow_html=True)
            else:
                for i, item in indexed_riwayat_filtered:
                    if item["status"] == "PAJAK AKTIF":
                        badge_row = "<span class='badge badge-active'>Aktif</span>"
                    elif item["status"] == "PAJAK MATI":
                        badge_row = "<span class='badge badge-expired'>Kedaluwarsa</span>"
                    else:
                        badge_row = "<span class='badge badge-unknown'>Tidak Terbaca</span>"

                    col_r1, col_r2, col_r3, col_r4, col_r5, col_r6 = st.columns([1.1, 1.3, 1, 1, 1, 1])
                    with col_r1:
                        st.markdown(f"<span style='font-family:JetBrains Mono, monospace; font-size:0.78rem; color:#64748b;'>{item['waktu']}</span>", unsafe_allow_html=True)
                    with col_r2:
                        st.markdown(f"<span class='data-val plate-num' style='font-size:0.85rem;'>{item['plat']}</span>", unsafe_allow_html=True)
                    with col_r3:
                        st.markdown(f"<span style='font-size:0.8rem; color:#64748b;'>{item['masa']}</span>", unsafe_allow_html=True)
                    with col_r4:
                        st.markdown(badge_row, unsafe_allow_html=True)
                    with col_r5:
                        st.markdown(f"<span class='history-source-tag'>{item['sumber']}</span>", unsafe_allow_html=True)
                    with col_r6:
                        st.markdown("<div class='history-row-btn'>", unsafe_allow_html=True)
                        if st.button("🔍 Lihat", key=f"lihat_riwayat_{i}", use_container_width=True):
                            st.session_state.riwayat_detail_idx = i
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)