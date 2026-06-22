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
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    /* Global styling */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #f8fafc !important;
        color: #1e293b !important;
    }

    /* Titles and headings styling */
    h1, h2, h3, .main-title {
        font-family: 'Outfit', sans-serif !important;
    }

    /* Sidebar Glassmorphism */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #090d16 0%, #0f172a 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        box-shadow: 10px 0 30px rgba(0,0,0,0.2) !important;
    }
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }

    .sidebar-brand {
        padding: 32px 24px 20px 24px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        margin-bottom: 24px;
        text-align: center;
    }
    
    /* Shield logo animation */
    .sidebar-logo-ring {
        width: 64px; height: 64px;
        background: linear-gradient(135deg, #0d9488, #10b981);
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.8rem;
        margin: 0 auto 16px auto;
        box-shadow: 0 0 20px rgba(13, 148, 136, 0.4);
        position: relative;
        animation: pulseLogo 3s infinite alternate;
    }
    
    @keyframes pulseLogo {
        0% { box-shadow: 0 0 10px rgba(13, 148, 136, 0.3); transform: scale(1); }
        100% { box-shadow: 0 0 25px rgba(16, 185, 129, 0.6); transform: scale(1.04); }
    }

    .sidebar-title {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 800;
        font-size: 1.15rem;
        letter-spacing: 2px;
        color: #ffffff !important;
    }
    .sidebar-sub {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 500;
        font-size: 0.75rem;
        color: #06b6d4 !important;
        letter-spacing: 1px;
        margin-top: 4px;
    }

    .road-divider {
        height: 4px;
        background: repeating-linear-gradient(
            90deg,
            rgba(255, 255, 255, 0.1) 0px, rgba(255, 255, 255, 0.1) 15px,
            transparent 15px, transparent 30px
        );
        border-radius: 2px;
        margin: 20px 24px;
        opacity: 0.6;
    }

    /* Radio button custom look (sidebar navigation) */
    div[data-testid="stRadio"] > div {
        gap: 8px !important;
        padding: 0 12px;
    }
    div[data-testid="stRadio"] label {
        background-color: rgba(255, 255, 255, 0.03) !important;
        padding: 12px 18px !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.04) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        color: #94a3b8 !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        display: flex !important;
        align-items: center !important;
    }
    div[data-testid="stRadio"] label:hover {
        background: rgba(255, 255, 255, 0.08) !important;
        border-color: rgba(13, 148, 136, 0.4) !important;
        color: #ffffff !important;
        transform: translateX(4px);
    }
    div[data-testid="stRadio"] [data-checked="true"] label {
        background: linear-gradient(90deg, rgba(13, 148, 136, 0.2) 0%, rgba(16, 185, 129, 0.1) 100%) !important;
        border: 1px solid #0d9488 !important;
        border-left: 5px solid #10b981 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(13, 148, 136, 0.15);
    }
    div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] {
        margin-left: 0px !important;
    }

    .sidebar-footer {
        padding: 20px 24px;
        font-size: 0.72rem;
        color: #64748b !important;
        text-align: center;
        line-height: 1.8;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        margin-top: 40px;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Page Header */
    .page-header { margin-bottom: 35px; }
    .page-eyebrow {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 4px;
        color: #0d9488;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -1px;
        color: #0f172a;
        line-height: 1.1;
        margin-bottom: 8px;
    }
    .title-accent {
        background: linear-gradient(135deg, #0d9488 0%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        font-size: 1.05rem;
        color: #475569;
        font-weight: 400;
        margin-bottom: 35px;
    }

    /* Card styling - Glassmorphism Light */
    .card {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(226, 232, 240, 0.8) !important;
        border-radius: 16px !important;
        padding: 28px 30px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.02), 0 8px 10px -6px rgba(15, 23, 42, 0.02) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .card:hover {
        border-color: rgba(13, 148, 136, 0.3) !important;
        box-shadow: 0 20px 30px -5px rgba(13, 148, 136, 0.06) !important;
        transform: translateY(-2px);
    }
    .card-title {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #0d9488;
        margin-bottom: 16px;
    }

    .card-amber  { border-left: 5px solid #f59e0b !important; }
    .card-red    { border-left: 5px solid #f43f5e !important; }
    .card-blue   { border-left: 5px solid #0284c7 !important; }
    .card-green  { border-left: 5px solid #10b981 !important; }

    /* Metrics display */
    .metric-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }
    .metric-box {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 16px;
        padding: 22px 24px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.01), 0 4px 6px -4px rgba(0, 0, 0, 0.01);
        transition: all 0.3s ease;
    }
    .metric-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 20px 25px -5px rgba(13, 148, 136, 0.05);
    }
    .metric-box::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 5px;
    }
    .metric-box.m-total::before  { background: linear-gradient(90deg, #0ea5e9, #0284c7); }
    .metric-box.m-active::before { background: linear-gradient(90deg, #10b981, #059669); }
    .metric-box.m-dead::before   { background: linear-gradient(90deg, #f43f5e, #e11d48); }
    
    .metric-label {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #64748b;
        margin-bottom: 12px;
    }
    .metric-value {
        font-family: 'Outfit', sans-serif;
        font-size: 2.4rem;
        font-weight: 800;
        line-height: 1;
        color: #0f172a;
        display: flex;
        align-items: baseline;
    }
    .metric-unit {
        font-size: 0.95rem;
        font-weight: 500;
        color: #94a3b8;
        margin-left: 6px;
    }

    /* Custom high-tech badges */
    .badge {
        display: inline-block;
        padding: 5px 14px;
        border-radius: 30px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
    }
    .badge-active  { 
        background: rgba(16, 185, 129, 0.1) !important; 
        color: #059669 !important; 
        border: 1px solid rgba(16, 185, 129, 0.2) !important; 
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.05);
    }
    .badge-expired { 
        background: rgba(244, 63, 94, 0.1) !important; 
        color: #e11d48 !important; 
        border: 1px solid rgba(244, 63, 94, 0.2) !important; 
        box-shadow: 0 2px 8px rgba(244, 63, 94, 0.05);
    }
    .badge-unknown { 
        background: rgba(245, 158, 11, 0.1) !important; 
        color: #d97706 !important; 
        border: 1px solid rgba(245, 158, 11, 0.2) !important;
        box-shadow: 0 2px 8px rgba(245, 158, 11, 0.05);
    }

    .conf-high { color: #059669 !important; font-weight: 700; }
    .conf-mid  { color: #d97706 !important; font-weight: 700; }
    .conf-low  { color: #e11d48 !important; font-weight: 700; }

    /* Result list cards style */
    .result-card {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 14px;
        padding: 22px 24px;
        margin-bottom: 18px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.01), 0 2px 4px -1px rgba(0, 0, 0, 0.01);
        transition: all 0.25s ease;
    }
    .result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px -5px rgba(15, 23, 42, 0.04);
        border-color: rgba(203, 213, 225, 1);
    }
    .result-card.rc-active  { border-left: 5px solid #10b981; }
    .result-card.rc-expired { border-left: 5px solid #f43f5e; }
    .result-card.rc-unknown { border-left: 5px solid #f59e0b; }

    .result-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        border-bottom: 1px dashed rgba(226, 232, 240, 0.8);
        padding-bottom: 12px;
    }
    .result-vehicle-id {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 0.95rem;
        color: #334155;
    }

    .data-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #f1f5f9;
    }
    .data-row:last-child { border-bottom: none; }
    .data-key {
        font-size: 0.82rem;
        color: #64748b;
        font-weight: 500;
    }
    .data-val {
        font-size: 0.9rem;
        color: #1e293b;
        font-weight: 600;
        text-align: right;
    }
    .data-val.mono {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: #0ea5e9;
        font-weight: 600;
        background: #f0f9ff;
        padding: 2px 8px;
        border-radius: 6px;
    }
    .data-val.plate-num {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.15rem;
        color: #0f172a;
        letter-spacing: 2px;
        background: #f8fafc;
        padding: 4px 12px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        display: inline-block;
        font-weight: 700;
    }

    /* Member Cards (Team Page) */
    .member-card {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 20px;
        padding: 35px 24px;
        text-align: center;
        box-shadow: 0 10px 20px -10px rgba(0, 0, 0, 0.02);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .member-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 30px -10px rgba(13, 148, 136, 0.12);
    }
    .member-card::after {
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 4px;
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    .member-card:hover::after {
        transform: scaleX(1);
    }
    .member-card.m-blue:hover::after  { background: linear-gradient(90deg, #0ea5e9, #0284c7); }
    .member-card.m-green:hover::after { background: linear-gradient(90deg, #10b981, #059669); }
    .member-card.m-amber:hover::after { background: linear-gradient(90deg, #f59e0b, #d97706); }

    .member-avatar {
        width: 80px; height: 80px;
        border-radius: 50%;
        margin: 0 auto 20px auto;
        display: flex; align-items: center; justify-content: center;
        font-size: 2.2rem;
        transition: all 0.3s ease;
    }
    .member-card:hover .member-avatar {
        transform: scale(1.1) rotate(5deg);
    }
    .avatar-blue   { background: linear-gradient(135deg, #e0f2fe, #bae6fd); box-shadow: 0 8px 16px rgba(14, 165, 233, 0.15); }
    .avatar-green  { background: linear-gradient(135deg, #d1fae5, #a7f3d0); box-shadow: 0 8px 16px rgba(16, 185, 129, 0.15); }
    .avatar-amber  { background: linear-gradient(135deg, #fef3c7, #fde68a); box-shadow: 0 8px 16px rgba(245, 158, 11, 0.15); }
    
    .member-name {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 1.15rem;
        color: #0f172a;
        margin-bottom: 6px;
    }
    .member-nim {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: #64748b;
        margin-bottom: 20px;
    }
    .member-role {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 30px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        border: 1px solid transparent;
    }
    .role-blue  { background: #e0f2fe; color: #0369a1; border-color: #bae6fd; }
    .role-green { background: #d1fae5; color: #047857; border-color: #a7f3d0; }
    .role-amber { background: #fef3c7; color: #b45309; border-color: #fde68a; }

    /* Info card layout */
    .info-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px 26px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.01);
    }
    .info-card-icon {
        font-size: 1.6rem;
        margin-bottom: 12px;
        display: block;
    }
    .info-card-title {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 1rem;
        color: #0f172a;
        margin-bottom: 10px;
    }
    .info-card-body {
        font-size: 0.88rem;
        color: #475569;
        line-height: 1.8;
        text-align: justify;
    }

    /* File Uploader override styling */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.6) !important;
        border: 2px dashed #cbd5e1 !important;
        border-radius: 16px !important;
        padding: 28px !important;
        transition: all 0.25s ease !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #0d9488 !important;
        background: rgba(13, 148, 136, 0.02) !important;
    }

    /* Empty states */
    .empty-state {
        text-align: center;
        padding: 50px 20px;
        color: #94a3b8;
    }
    .empty-icon { font-size: 3.8rem; margin-bottom: 20px; display: block; }
    .empty-title { font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1.2rem; color: #475569; margin-bottom: 8px; }
    .empty-body  { font-size: 0.9rem; color: #94a3b8; max-width: 380px; margin: 0 auto; line-height: 1.7; }

    /* Timeline dots */
    .tl-dot {
        width: 10px; height: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
    .tl-red   { background: #f43f5e; box-shadow: 0 0 8px #f43f5e; }
    .tl-amber { background: #f59e0b; box-shadow: 0 0 8px #f59e0b; }
    .tl-green { background: #10b981; box-shadow: 0 0 8px #10b981; }

    /* Sections division */
    .section-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #64748b;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .section-label::after {
        content: '';
        flex: 1;
        height: 1px;
        background: #e2e8f0;
    }

    [data-testid="stImage"] p {
        color: #64748b !important;
        font-size: 0.8rem !important;
        text-align: center;
        font-family: 'JetBrains Mono', monospace;
        margin-top: 8px;
    }

    footer { visibility: hidden; }

    /* Header styling with blurred transparency */
    header {
        visibility: visible !important;
        background-color: rgba(248, 250, 252, 0.8) !important;
        backdrop-filter: blur(12px) !important;
        border-bottom: 1px solid rgba(226, 232, 240, 0.8) !important;
    }
    [data-testid="stHeader"] button,
    [data-testid="stHeader"] svg,
    [data-testid="stHeader"] * {
        color: #0f172a !important;
        fill: #0f172a !important;
    }

    /* Video & camera progress styling */
    .video-progress-wrap {
        background: #e2e8f0;
        border-radius: 99px;
        height: 8px;
        margin: 12px 0 18px 0;
        overflow: hidden;
    }
    .video-progress-bar {
        height: 8px;
        background: linear-gradient(90deg, #0d9488, #10b981);
        border-radius: 99px;
        transition: width 0.15s linear;
    }
    .video-info-row {
        display: flex;
        justify-content: space-between;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #64748b;
        margin-bottom: 6px;
    }

    /* Tabs Styling - Make them gorgeous */
    button[data-testid="stTabBarTab"] {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 10px 24px !important;
        border-radius: 12px 12px 0 0 !important;
        transition: all 0.25s ease !important;
    }
    button[data-testid="stTabBarTab"]:hover {
        color: #0d9488 !important;
        background: rgba(13, 148, 136, 0.04) !important;
    }
    button[data-testid="stTabBarTab"][aria-selected="true"] {
        color: #0d9488 !important;
        border-bottom: 3px solid #0d9488 !important;
        font-weight: 700 !important;
    }

    /* Primary buttons */
    button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #0d9488 0%, #10b981 100%) !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 14px rgba(13, 148, 136, 0.3) !important;
        transition: all 0.2s ease !important;
        border-radius: 12px !important;
        padding: 8px 20px !important;
        font-weight: 600 !important;
    }
    button[data-testid="baseButton-primary"]:hover {
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Secondary buttons */
    button[data-testid="baseButton-secondary"] {
        border-radius: 12px !important;
        border: 1px solid #cbd5e1 !important;
        color: #334155 !important;
        background: #ffffff !important;
        transition: all 0.2s ease !important;
        font-weight: 600 !important;
    }
    button[data-testid="baseButton-secondary"]:hover {
        border-color: #0d9488 !important;
        color: #0d9488 !important;
        background: rgba(13, 148, 136, 0.02) !important;
    }

    /* History table design */
    .history-row-btn button {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
        color: #334155 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.78rem !important;
        text-align: center !important;
        justify-content: center !important;
        padding: 6px 12px !important;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    }
    .history-row-btn button:hover {
        border-color: #0d9488 !important;
        background: rgba(13, 148, 136, 0.04) !important;
        color: #0d9488 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(13, 148, 136, 0.1) !important;
    }
    
    .history-table-head {
        display: grid;
        grid-template-columns: 1.1fr 1.3fr 1fr 1fr 1fr 1fr;
        gap: 12px;
        padding: 12px 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #64748b;
        border-bottom: 2px solid #cbd5e1;
        margin-bottom: 12px;
        font-weight: 700;
    }
    
    .history-source-tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 30px;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        font-family: 'JetBrains Mono', monospace;
        background: #f1f5f9;
        color: #475569;
        border: 1px solid #cbd5e1;
    }
    
    .detail-banner {
        background: linear-gradient(135deg, #0d9488, #10b981);
        border-radius: 16px;
        padding: 26px 30px;
        color: #ffffff !important;
        margin-bottom: 24px;
        box-shadow: 0 10px 20px rgba(13, 148, 136, 0.2);
    }
    .detail-banner * { color: #ffffff !important; }
    .detail-plate-big {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: 4px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.15);
    }

    /* Streamlit widgets border and input polish */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="slider"] {
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)


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

def ocr_and_predict(crop_bgr):
    """
    OCR plat — identik dengan ocr_plate() pada notebook referensi.
    EasyOCR dijalankan langsung pada crop tanpa preprocessing tambahan
    (tidak ada CLAHE/threshold/sharpening) agar perilaku deteksi sama
    persis dengan hasil training/notebook.
    Return (text_gabungan, confidence_rata_rata_persen).
    """
    reader = load_ocr()

    if crop_bgr is None or crop_bgr.size == 0:
        return "", 0.0

    try:
        result = reader.readtext(crop_bgr, detail=1)
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
        return "TIDAK TERBACA", (255, 193, 7)

    now = datetime.now()

    if (thn > now.year) or (thn == now.year and bln >= now.month):
        return "PAJAK AKTIF", (1, 114, 114)
    else:
        return "PAJAK MATI", (224, 92, 58)


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

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Jalankan inferensi YOLO hanya setiap skip_n frame
                if frame_idx % skip_n == 0:
                    res = model(frame, conf=0.35, verbose=False)
                    last_boxes = res[0].boxes

                    # OCR & annotasi hanya pada frame yang diinfer
                    for box in last_boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        crop = frame[y1:y2, x1:x2]
                        if crop.size == 0:
                            continue

                        conf_yolo = float(box.conf[0]) * 100
                        raw_text, conf_ocr = ocr_and_predict(crop)
                        plat, bln, thn = extract_data(raw_text)
                        status, _ = cek_status_pajak(bln, thn)

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
                for box in last_boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    # Warna default (abu) untuk frame yg di-skip, baru dapat warna asli setelah OCR
                    # Cari di history apakah ada plat yang lokasinya cocok (pakai heuristik area)
                    color = (180, 180, 180)
                    label_txt = "..."
                    # Cek history — ambil entry terakhir sebagai fallback label
                    if detected_history:
                        last_entry = list(detected_history.items())[-1]
                        lbl_plat, lbl_data = last_entry
                        if lbl_data["status"] == "PAJAK AKTIF":
                            color = (1, 114, 114)
                        elif lbl_data["status"] == "PAJAK MATI":
                            color = (224, 92, 58)
                        else:
                            color = (255, 193, 7)
                        label_txt = lbl_plat

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

            cap.release()
            os.unlink(tfile.name)   # Hapus file sementara

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
            
            # Atur resolusi agar ringan saat pemrosesan OCR
            cap_cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap_cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            model = load_yolo()

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

                        for bi, box in enumerate(boxes):
                            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                            crop = frame_to_process[y1:y2, x1:x2]
                            if crop.size == 0:
                                continue

                            conf_yolo = float(box.conf[0]) * 100
                            raw_text, conf_ocr = ocr_and_predict(crop)
                            plat, bln, thn = extract_data(raw_text)
                            status, _ = cek_status_pajak(bln, thn)

                            # Warna berdasarkan status
                            if status == "PAJAK AKTIF":
                                color = (1, 114, 114)
                            elif status == "PAJAK MATI":
                                color = (224, 92, 58)
                            else:
                                color = (255, 193, 7)

                            new_boxes.append((x1, y1, x2, y2))
                            new_labels[bi] = {
                                "plat": plat, "status": status,
                                "color": color,
                                "label_txt": f"{plat} ({status})",
                            }

                            # Simpan ke log jika plat valid dan belum tercatat
                            if plat != "Tidak Terbaca" and plat not in cam_history:
                                if status == "PAJAK AKTIF":
                                    total_aktif_c[0] += 1
                                elif status == "PAJAK MATI":
                                    total_mati_c[0] += 1

                                masa_fmt_c = f"{bln:02d} / {thn}" if bln and thn else "Gagal Parsing"

                                cam_history[plat] = {
                                    "masa": masa_fmt_c,
                                    "status": status,
                                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                                    "conf_yolo": conf_yolo,
                                    "conf_ocr": conf_ocr,
                                }

                                # Catat otomatis ke Histori Deteksi
                                catat_riwayat(
                                    sumber="Kamera",
                                    plat=plat,
                                    masa=masa_fmt_c,
                                    status=status,
                                    conf_yolo=conf_yolo,
                                    conf_ocr=conf_ocr,
                                    raw_ocr=raw_text if raw_text else "Tidak Ada Teks",
                                )

                        # Simpan hasil ke shared state
                        with ai_lock:
                            ai_boxes.clear()
                            ai_boxes.extend(new_boxes)
                            ai_labels.clear()
                            ai_labels.update(new_labels)
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

                # Overlay Info Statis
                status_text = "LIVE" if not ai_busy[0] else "SCANNING..."
                status_color = (0, 255, 0) if not ai_busy[0] else (0, 200, 255)
                cv2.putText(frame_rgb, status_text, (10, 28), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, status_color, 2, cv2.LINE_AA)
                cv2.putText(frame_rgb, f"Plat Unik: {len(cam_history)}", (10, 54), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                # 1. Render Stream ke UI
                frame_holder_cam.image(frame_rgb, use_container_width=True)

                # 2. Render Ringkasan Metric
                metric_holder_cam.markdown(f"""
                <div class='metric-row' style='margin-bottom:14px;'>
                    <div class='metric-box m-total'>
                        <div class='metric-label'>Total Plat</div>
                        <div class='metric-value'>{len(cam_history)}<span class='metric-unit'>unit</span></div>
                    </div>
                    <div class='metric-box m-active'>
                        <div class='metric-label'><span class='tl-dot tl-green'></span>Aktif</div>
                        <div class='metric-value'>{total_aktif_c[0]}<span class='metric-unit'>unit</span></div>
                    </div>
                    <div class='metric-box m-dead'>
                        <div class='metric-label'><span class='tl-dot tl-red'></span>Mati</div>
                        <div class='metric-value'>{total_mati_c[0]}<span class='metric-unit'>unit</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 3. Render Log Kartu Inspeksi Real-time
                log_html = "<div style='max-height:380px; overflow-y:auto;'>"
                if not cam_history:
                    log_html += "<p style='color:#64748b; font-size:0.85rem; padding:12px 0;'>Menghadapkan plat kendaraan ke kamera...</p>"
                else:
                    for plate_no, data in reversed(list(cam_history.items())):
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
                
            # Bersihkan resources
            ai_stop[0] = True
            ai_thread.join(timeout=2)
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