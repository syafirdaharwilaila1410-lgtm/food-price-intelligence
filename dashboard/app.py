import os

import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st


# ==========================================================
# INDONESIA FOOD PRICE INTELLIGENCE
# ==========================================================

st.set_page_config(
    page_title="Indonesia Food Price Intelligence",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------- THEME -------------------------

NAVY = "#203A36"
NAVY_DARK = "#172C29"
CREAM = "#F7F4EC"
SAGE = "#A9B9A1"
SAGE_LIGHT = "#E5EBE1"
INK = "#26332F"
MUTED = "#68756E"
BORDER = "#DDE3D8"
WHITE = "#FFFFFF"

# ====================================================================
st.markdown(
    f"""
    <!-- Mengambil Font Manrope secara resmi dari Google Fonts -->
    <link rel="stylesheet" href="https://googleapis.com">
    
    <style>
        /* Mengubah Font dasar seluruh dashboard menjadi Manrope */
        .main .block-container {{
            font-family: 'Manrope', sans-serif !important;
        }}
        
        /* 1. Menerapkan Gaya Kualitas Judul Section Baru Anda */
        .section-title {{
            font-family: 'Manrope', sans-serif !important;
            font-size: 1.65rem !important;        
            font-weight: 800 !important;
            letter-spacing: -0.025em !important;  
            margin: 1.2rem 0 0.4rem !important;
            
            /* Trik Gradasi Mewah */
            background: linear-gradient(135deg, {NAVY} 40%, {SAGE} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        /* 2. Menerapkan Gaya Penjelasan Deskripsi Baru Anda */
        .section-desc {{
            font-family: 'Manrope', sans-serif !important;
            color: {MUTED} !important;
            font-size: 0.92rem !important;        
            line-height: 1.65 !important;
            margin-bottom: 1.6rem !important;
            max-width: 1050px !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------ LANGUAGE -------------------------

if "language" not in st.session_state:
    st.session_state.language = "Indonesia"

LANG = {
    "Indonesia": {
        "language": "Bahasa",
        "filter": "Filter Dashboard",
        "filter_help": "Pilih tahun dan komoditas yang ingin dianalisis.",
        "year": "Tahun",
        "commodity": "Komoditas",
        "search_commodity": "Cari komoditas...",
        "reload": "Muat ulang data",
        "data_source": "Data bersumber dari Badan Pangan Nasional. Harga kosong tidak dianggap nol.",
        "hero_kicker": "PASAR PANGAN NASIONAL · 2021–2025",
        "hero_title": "Indonesia Food Price Intelligence",
        "hero_subtitle": "Memantau tren harga, membaca perubahan bulanan, dan mengevaluasi kualitas data harga pangan konsumen nasional.",
        "hero_foot": "PEMANTAUAN HARGA PANGAN & ANALISIS RISIKO BERBASIS DATA",
        "hero_image": "Memahami harga pangan<br>melalui data",
        "overview": "Ringkasan",
        "overview_desc": "Ringkasan data berdasarkan filter yang sedang aktif.",
        "total_obs": "Total observasi",
        "selected_rows": "Baris data terpilih",
        "commodities": "Komoditas",
        "unique_commodities": "Komoditas unik",
        "available": "Harga tersedia",
        "non_null": "Harga non-NULL",
        "completeness": "Kelengkapan harga",
        "missing": "harga kosong",
        "intelligence": "Analisis Harga & Insight",
        "intelligence_desc": "Ringkasan perubahan harga pada komoditas dan tahun yang dipilih. Perubahan harga tidak dengan sendirinya menjelaskan penyebabnya.",
        "highest_avg": "Rata-rata tertinggi",
        "lowest_avg": "Rata-rata terendah",
        "avg_on_filter": "Rata-rata harga {}.",
        "latest_change": "Perubahan terbaru tersedia",
        "no_data": "Belum tersedia",
        "need_two_months": "Diperlukan harga pada dua bulan kalender berurutan.",
        "largest_increase": "Kenaikan bulanan terbesar",
        "largest_decrease": "Penurunan bulanan terbesar",
        "rupiah_change": "Perubahan harga (Rp)",
        "change_amount": "Selisih harga",
        "previous_price": "Harga bulan sebelumnya",
        "current_price": "Harga bulan ini",
        "section_trend": "01 · Tren harga bulanan",
        "trend_desc": "Perhatikan arah perubahan harga komoditas pada periode yang dipilih.",
        "trend_title": "Pergerakan harga pangan per bulan",
        "period": "Periode",
        "price": "Harga (Rp)",
        "month": "Bulan",
        "no_prices": "Tidak ada harga tersedia untuk grafik tren.",
        "section_comparison": "02 · Perbandingan harga dua periode",
        "comparison_desc": "Bandingkan harga rata-rata komoditas pada dua bulan yang berbeda.",
        "section_ranking": "03 · Peringkat rata-rata harga",
        "ranking_desc": "Perbandingan deskriptif. Pertimbangkan satuan masing-masing komoditas sebelum menyimpulkan mana yang lebih mahal.",
        "ranking_title": "Rata-rata harga per komoditas",
        "stats": "Ringkasan statistik harga",
        "average": "Rata-rata",
        "minimum": "Minimum",
        "maximum": "Maksimum",
        "observations": "Observasi",
        "section_volatility": "04 · Volatilitas harga",
        "volatility_desc": "Rata-rata perubahan persentase absolut antarbulan kalender yang berurutan. Nilai yang lebih besar menunjukkan perubahan relatif yang lebih besar.",
        "volatility_title": "Komoditas dengan perubahan relatif terbesar",
        "abs_change": "Rata-rata perubahan absolut (%)",
        "no_volatility": "Belum cukup data harga pada dua bulan berurutan untuk menghitung volatilitas.",
        "section_annual": "05 · Perbandingan rata-rata tahunan",
        "annual_desc": "Membandingkan rata-rata harga setiap komoditas per tahun. Tahun dengan data sebagian harus ditafsirkan secara hati-hati.",
        "annual_title": "Rata-rata harga tahunan",
        "view_annual": "Lihat tabel perbandingan tahunan",
        "year_label": "Tahun",
        "avg_price": "Rata-rata harga",
        "price_observations": "Observasi harga",
        "no_annual": "Belum ada data yang dapat dibandingkan per tahun.",
        "section_quality": "06 · Kualitas dan kelengkapan data",
        "quality_desc": "Periksa harga yang belum tersedia sebelum menarik kesimpulan.",
        "total_rows": "Total baris",
        "filtered_data": "Data terfilter",
        "empty_not_zero": "Tidak diubah menjadi nol",
        "view_data": "Lihat data yang digunakan",
        "period_col": "Periode",
        "year_col": "Tahun",
        "month_number": "Bulan (angka)",
        "price_col": "Harga",
        "unavailable": "Belum tersedia",
        "view_missing": "Lihat data dengan harga kosong",
        "no_missing": "Tidak ada harga kosong pada filter ini.",
        "section_export": "07 · Ekspor data",
        "export_desc": "Unduh data sesuai filter aktif untuk analisis lanjutan.",
        "download": "⬇ Unduh data terfilter (CSV)",
        "source": "Sumber data",
        "open_source": "Buka sumber dataset",
        "methodology": "Catatan metodologi",
        "methodology_text": "Harga kosong dipertahankan sebagai nilai tidak tersedia. Perubahan bulanan hanya dihitung ketika harga pada dua bulan kalender berurutan tersedia dan harga bulan sebelumnya tidak nol. Rata-rata antar-komoditas merupakan ringkasan deskriptif, bukan indeks harga pangan nasional. Data harga saja tidak cukup untuk memastikan penyebab perubahan.",
        "choose_year": "Pilih setidaknya satu tahun pada sidebar.",
        "choose_commodity": "Pilih setidaknya satu komoditas pada sidebar.",
        "empty_filter": "Tidak ada data untuk filter yang dipilih.",
        "db_error": "Dashboard belum bisa terhubung ke PostgreSQL.",
        "db_help": "Pastikan PostgreSQL aktif, database food_price_intelligence tersedia, dan PGPASSWORD sudah diatur di terminal.",
        "db_detail": "Detail error",
        "empty_table": "Tabel food_prices belum memiliki data.",
        "latest_prefix": "{} pada {} dibandingkan bulan sebelumnya.",
        "change_prefix": "{} pada {}.",
        "commodity_axis": "Komoditas",
        "no_change": "Belum tersedia perubahan harga yang dapat dihitung.",
        "national_prices": "Harga konsumen nasional",
        "streak_title": "Tren bulanan berturut-turut",
        "streak_desc": "Rangkaian kenaikan atau penurunan harga berdasarkan bulan kalender yang berurutan.",
        "streak_up": "Rangkaian kenaikan terpanjang",
        "streak_down": "Rangkaian penurunan terpanjang",
        "streak_none": "Belum ada rangkaian perubahan yang cukup untuk dianalisis.",
        "streak_copy": "{} bulan berturut-turut hingga {}.",
        "streak_start": "Dimulai {}.",
        "streak_unit": "perubahan bulanan",
        "no_streak": "Tidak ditemukan rangkaian perubahan dengan arah yang sama.",
        "interpretation": "Interpretasi",
        "interpretation_text": "Kenaikan atau penurunan merupakan pola yang teramati, bukan bukti penyebab. Faktor seperti pasokan, cuaca, distribusi, permintaan, dan kebijakan dapat diteliti lebih lanjut, tetapi tidak dapat dipastikan dari data harga saja.",
        "volatility_insight_title": "Insight volatilitas tertinggi",
        "volatility_insight_text": (
        "Rata-rata perubahan harga absolut bulanan mencapai "
        "{}%. Artinya, perubahan harga bulan ke bulan "
        "relatif lebih besar dibandingkan komoditas lain "
        "pada periode yang dipilih."
        ),
        "volatility_stable_title": "Insight volatilitas terendah",
        "volatility_stable_text": (
        "Rata-rata perubahan harga absolut bulanan hanya "
        "{}%. Artinya, perubahan harga bulan ke bulan "
        "relatif lebih kecil dibandingkan komoditas lain "
        "pada periode yang dipilih."
        ),
        "annual_increase_title": "Kenaikan rata-rata tahunan terbesar",
        "annual_decrease_title": "Penurunan rata-rata tahunan terbesar",
        "quality_complete": (
        "Data harga lengkap: {}% dari data pada filter ini memiliki harga."
        ),
        "quality_partial": (
        "Kelengkapan data harga: {}%. Masih terdapat {} catatan "
        "dengan harga kosong pada filter ini."
        ),
    },
    "English": {
        "language": "Language",
        "filter": "Dashboard Filters",
        "filter_help": "Select the years and commodities you want to analyze.",
        "year": "Year",
        "commodity": "Commodity",
        "search_commodity": "Search commodities...",
        "reload": "Refresh data",
        "data_source": "Data source: National Food Agency. Missing prices are not treated as zero.",
        "hero_kicker": "NATIONAL FOOD MARKET · 2021–2025",
        "hero_title": "Indonesia Food Price Intelligence",
        "hero_subtitle": "Monitor price trends, explore monthly changes, and evaluate the quality of national consumer food price data.",
        "hero_foot": "DATA-DRIVEN FOOD PRICE MONITORING & RISK ANALYTICS",
        "hero_image": "Understanding food prices<br>through data",
        "overview": "Overview",
        "overview_desc": "Summary of data based on the active filters.",
        "total_obs": "Total observations",
        "selected_rows": "Selected data rows",
        "commodities": "Commodities",
        "unique_commodities": "Unique commodities",
        "available": "Available prices",
        "non_null": "Non-NULL prices",
        "completeness": "Price completeness",
        "missing": "missing prices",
        "intelligence": "Price Intelligence & Insights",
        "intelligence_desc": "Summary of measured price changes for the selected commodities and years. Price changes alone do not explain their causes.",
        "highest_avg": "Highest average",
        "lowest_avg": "Lowest average",
        "avg_on_filter": "Average price: {}.",
        "latest_change": "Latest available change",
        "no_data": "Not available",
        "need_two_months": "Prices for two consecutive calendar months are required.",
        "largest_increase": "Largest monthly increase",
        "largest_decrease": "Largest monthly decrease",
        "rupiah_change": "Price change (IDR)",
        "change_amount": "Price difference",
        "previous_price": "Previous month's price",
        "current_price": "Current month's price",
        "section_trend": "01 · Monthly price trends",
        "trend_desc": "Explore commodity price movements during the selected period.",
        "trend_title": "Monthly food price movements",
        "period": "Period",
        "price": "Price (IDR)",
        "month": "Month",
        "no_prices": "No prices are available for the trend chart.",
        "section_comparison": "02 · Two-period price comparison",
        "comparison_desc": "Compare average commodity prices across two different months.",
        "section_ranking": "03 · Average price ranking",
        "ranking_desc": "A descriptive comparison. Consider each commodity's unit before concluding which is more expensive.",
        "ranking_title": "Average price by commodity",
        "stats": "Price statistics summary",
        "average": "Average",
        "minimum": "Minimum",
        "maximum": "Maximum",
        "observations": "Observations",
        "section_volatility": "04 · Price volatility",
        "volatility_desc": "Mean absolute percentage change between consecutive calendar months. Higher values indicate larger relative changes.",
        "volatility_title": "Commodities with the largest relative changes",
        "abs_change": "Mean absolute change (%)",
        "no_volatility": "There is insufficient price data for two consecutive months to calculate volatility.",
        "section_annual": "05 · Annual average comparison",
        "annual_desc": "Compare each commodity's average price by year. Interpret years with partial data carefully.",
        "annual_title": "Annual average prices",
        "view_annual": "View annual comparison table",
        "year_label": "Year",
        "avg_price": "Average price",
        "price_observations": "Price observations",
        "no_annual": "No data is available for annual comparison.",
        "section_quality": "06 · Data quality and completeness",
        "quality_desc": "Check for missing prices before drawing conclusions.",
        "total_rows": "Total rows",
        "filtered_data": "Filtered data",
        "empty_not_zero": "Not converted to zero",
        "view_data": "View underlying data",
        "period_col": "Period",
        "year_col": "Year",
        "month_number": "Month (number)",
        "price_col": "Price",
        "unavailable": "Unavailable",
        "view_missing": "View records with missing prices",
        "no_missing": "There are no missing prices under these filters.",
        "section_export": "07 · Data export",
        "export_desc": "Download the filtered data for further analysis.",
        "download": "⬇ Download filtered data (CSV)",
        "source": "Data source",
        "open_source": "Open dataset source",
        "methodology": "Methodology notes",
        "methodology_text": "Missing prices remain unavailable. Monthly changes are calculated only when prices exist for two consecutive calendar months and the previous price is nonzero. Cross-commodity averages are descriptive summaries, not a national food price index. Price data alone cannot establish the causes of changes.",
        "choose_year": "Select at least one year in the sidebar.",
        "choose_commodity": "Select at least one commodity in the sidebar.",
        "empty_filter": "No data matches the selected filters.",
        "db_error": "The dashboard could not connect to PostgreSQL.",
        "db_help": "Ensure PostgreSQL is running, the food_price_intelligence database exists, and PGPASSWORD is set in the terminal.",
        "db_detail": "Error details",
        "empty_table": "The food_prices table contains no data.",
        "latest_prefix": "{} in {}, compared with the previous month.",
        "change_prefix": "{} in {}.",
        "commodity_axis": "Commodity",
        "no_change": "No price changes are available to calculate.",
        "national_prices": "National consumer prices",
        "streak_title": "Consecutive monthly trends",
        "streak_desc": "Sequences of price increases or decreases across consecutive calendar months.",
        "streak_up": "Longest consecutive increase",
        "streak_down": "Longest consecutive decrease",
        "streak_none": "There is insufficient data to analyze a consecutive trend.",
        "streak_copy": "{} consecutive monthly changes through {}.",
        "streak_start": "Started {}.",
        "streak_unit": "monthly changes",
        "no_streak": "No sequence of changes in the same direction was found.",
        "interpretation": "Interpretation",
        "interpretation_text": "An increase or decrease is an observed pattern, not proof of its cause. Supply, weather, distribution, demand, and policy may warrant further investigation, but cannot be confirmed from price data alone.",
        "volatility_insight_title": "Highest volatility insight",
        "volatility_insight_text": (
        "The average absolute monthly price change reached "
        "{}%. This indicates relatively larger month-to-month "
        "price movements than other commodities in the selected period."
        ),  
        "volatility_stable_title": "Lowest volatility insight",
        "volatility_stable_text": (
        "The average absolute monthly price change was only "
        "{}%. This indicates relatively smaller month-to-month "
        "price movements than other commodities in the selected period."
        ),
        "annual_increase_title": "Largest annual average price increase",
        "annual_decrease_title": "Largest annual average price decrease",
        "quality_complete": (
        "Price data is complete: {}% of records in this filter have prices."
        ),
        "quality_partial": (
        "Price data completeness: {}%. There are still {} records "
        "with missing prices in this filter."
        ),
    },
}


# ---------------------------- CSS ---------------------------


st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {{
        --forest: {NAVY};
        --forest-dark: {NAVY_DARK};
        --cream: {CREAM};
        --sage: {SAGE};
        --sage-light: {SAGE_LIGHT};
        --ink: {INK};
        --muted: {MUTED};
        --border: {BORDER};
        --white: {WHITE};
    }}

    .stApp {{
        background: var(--cream);
        color: var(--ink);
        font-family: 'DM Sans', sans-serif;
    }}

    [data-testid="stHeader"] {{
        background: rgba(247,244,236,0.96);
    }}

    [data-testid="stSidebar"] {{
        background: #EEF0E8;
        border-right: 1px solid var(--border);
    }}

    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 1.4rem;
    }}

    .block-container {{
        max-width: 1500px;
        padding: 2rem 2.5rem 3.5rem;
    }}

    h1, h2, h3 {{
        color: var(--forest) !important;
        font-family: 'Manrope', sans-serif !important;
        letter-spacing: -0.035em;
    }}

    h1 {{
        font-weight: 800 !important;
    }}

    h2, h3 {{
        font-weight: 700 !important;
    }}

    p, li, label {{
        line-height: 1.65;
    }}

    .sidebar-brand {{
        padding: 0.4rem 0 1.3rem;
    }}

    .sidebar-logo {{
        display: flex;
        align-items: center;
        justify-content: center;
        width: 80px;
        height: 80px;
        background: var(--sage-light);
        border: 1px solid var(--border);
        border-radius: 22px;
        font-size: 2.8rem;
        margin-left: auto;
        margin-right: auto;
        margin-bottom: 0.9rem;
    }}

    .sidebar-title {{
        color: var(--forest);
        font-family: 'Manrope', sans-serif;
        font-size: 1.05rem;
        font-weight: 800;
        line-height: 1.4;
        letter-spacing: -0.03em;
    }}

    .sidebar-subtitle {{
        color: var(--muted);
        font-size: 0.78rem;
        margin-top: 0.35rem;
    }}

    /* HERO */

    .hero {{
        position: relative;
        overflow: hidden;
        background: linear-gradient(
            125deg,
            var(--forest-dark) 0%,
            var(--forest) 60%,
            #607D68 100%
        );
        color: white;
        padding: clamp(1.6rem, 3vw, 2.5rem);
        border-radius: 22px;
        margin-bottom: 0.8rem;
        min-height: 250px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 12px 28px rgba(32,58,54,0.10);
    }}

    .hero::after {{
        content: "";
        position: absolute;
        width: 220px;
        height: 220px;
        border-radius: 50%;
        right: -90px;
        top: -110px;
        border: 1px solid rgba(255,255,255,0.13);
        box-shadow:
            0 0 0 24px rgba(255,255,255,0.025),
            0 0 0 48px rgba(255,255,255,0.025);
        pointer-events: none;
    }}

    .hero-kicker {{
        color: #DCE7D9;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.13em;
        margin-bottom: 0.9rem;
    }}

    .hero h1 {{
        color: white !important;
        font-size: clamp(2.4rem, 4vw, 3.6rem);
        font-weight: 800;
        letter-spacing: -0.03em;
        color: var(--navy-dark);
        line-height: 1.15;
        margin: 0;
        line-height: 1.15;
        margin-bottom: 0.5rem;
        max-width: 800px;
    }}

    .hero-subtitle {{
        color: #E4EAE0;
        font-size: clamp(0.95rem, 1.5vw, 1.1rem);
        line-height: 1.6;
        color: var(--muted);
        font-weight: 400;    
        margin-top: 1rem;
        max-width: 700px;
    }}

    .hero-foot {{
        color: #DCE7D9;
        font-size: 0.7rem;
        font-weight: 600;
        margin-top: 1.3rem;
        letter-spacing: 0.07em;
    }}
    
    /* FLOATING HAMBURGER NAVIGATION */

    html {{
        scroll-behavior: smooth;
    }}

    .floating-nav {{
        position: fixed;
        top: 3rem;
        left: 1rem;
        right: auto;
        z-index: 999999;
    }}

    .floating-nav details {{
        position: relative;
    }}

    .floating-nav summary {{
        list-style: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 44px;
        height: 44px;
        background: var(--forest);
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 12px;
        box-shadow: 0 6px 18px rgba(32,58,54,0.2);
        font-size: 1.4rem;
        font-weight: 700;
        user-select: none;
        transition: transform 0.2s ease, background 0.2s ease;
    }}

    .floating-nav summary::-webkit-details-marker {{
        display: none;
    }}

    .floating-nav summary:hover {{
        background: var(--forest-dark);
        transform: translateY(-2px);
    }}

    .floating-nav .floating-nav-panel {{
        position: absolute;
        top: 0;
        left: 54px;
        width: 250px;
        max-width: calc(100vw - 2rem);
        padding: 0.75rem;
        background: var(--white);
        border: 1px solid var(--border);
        border-radius: 16px;
        box-shadow: 0 12px 30px rgba(32,58,54,0.16);
        display: flex;
        flex-direction: column;
        gap: 0.2rem;
    }}

    .floating-nav-title {{
        color: var(--muted);
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 0.6rem 0.75rem;
    }}

    .floating-nav a {{
        display: block;
        padding: 0.55rem 0.7rem;
        color: var(--forest);
        text-decoration: none;
        border-radius: 9px;
        font-size: 0.88rem;
        font-weight: 600;
        line-height: 1.5;
        transition: background 0.2s ease;
    }}

    .floating-nav a:hover {{
        background: var(--sage-light);
    }}

    @media (max-width: 768px) {{
        .floating-nav {{
            top: 4.2rem;
            left: 0.6rem;
        }}

        .floating-nav .floating-nav-panel {{
            width: 245px;
        }}
    }}

    /* SECTION HEADINGS */

    .section-title {{
        font-family: 'Manrope', sans-serif;
        color: var(--forest);
        font-size: 1.38rem;
        font-weight: 800;
        letter-spacing: -0.035em;
        margin: 1.5rem 0 0.3rem;
        background: linear-gradient(135deg, var(--forest) 30%, var(--sage) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .section-desc {{
        font-family: 'Manrope', sans-serif;
        color: var(--ink);
        opacity: 0.85; 
        font-size: 0.95rem;
        letter-spacing: 0.01em;
        line-height: 1.7;
        margin-bottom: 1.15rem;
        max-width: 1050px;
    }}

    /* KPI AND INSIGHT CARDS */

    .kpi-card,
    .insight-card {{
        background: var(--white);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 1.3rem;
        box-shadow: 0 4px 14px rgba(32,58,54,0.035);
        height: 100%;
        box-sizing: border-box;
        transition: box-shadow 0.2s ease, transform 0.2s ease;
    }}

    .kpi-card {{
        min-height: 142px;
        border-top: 3px solid var(--sage);
    }}

    .insight-card {{
        min-height: 155px;
        padding: 1.4rem;
        box-sizing: border-box;
    }}

    .kpi-label {{
        color: var(--muted);
        font-size: 0.83rem;
        font-weight: 600;
        line-height: 1.5;
        margin-bottom: 0.75rem;
    }}

    .kpi-value {{
        color: var(--forest);
        font-family: 'Manrope', sans-serif;
        font-size: clamp(1.65rem, 2.1vw, 2.2rem);
        font-weight: 800;
        line-height: 1.2;
        overflow-wrap: anywhere;
        font-variant-numeric: tabular-nums;
    }}

    .kpi-foot {{
        color: var(--muted);
        font-size: 0.76rem;
        line-height: 1.5;
        margin-top: 0.55rem;
    }}

    .insight-label {{
        color: var(--muted);
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.065em;
        line-height: 1.6;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }}

    .insight-value {{
        color: var(--forest);
        font-family: 'Manrope', sans-serif;
        font-size: 1.2rem;
        font-weight: 800;
        line-height: 1.45;
        margin-top: 0.25rem;
        overflow-wrap: anywhere;
    }}

    .insight-copy {{
        color: var(--muted);
        font-size: 0.9rem;
        line-height: 1.8;
        margin-top: 0.65rem;
        overflow-wrap: anywhere;
    }}

    /* CHARTS AND TABLES */

    div[data-testid="stPlotlyChart"] {{
        background: var(--white);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 0;
        margin: 0;
        box-shadow: 0 4px 14px rgba(32,58,54,0.025);
        box-sizing: border-box;
        width: 100%;
        overflow: hidden;
    }}

    div[data-testid="stPlotlyChart"] > div {{
        width: 100%;
        box-sizing: border-box;
    }}


    div[data-testid="stDataFrame"] {{
        border: 1px solid var(--border);
        border-radius: 14px;
        overflow: hidden;
    }}

    /* FILTERS AND BUTTONS */

    div[data-testid="stMultiSelect"] > div,
    div[data-testid="stSelectbox"] > div {{
        border-radius: 11px;
    }}

    div[data-testid="stButton"] button,
    div[data-testid="stDownloadButton"] button {{
        border-radius: 11px;
        font-weight: 600;
        min-height: 42px;
        transition: all 0.2s ease;
    }}

    div[data-testid="stButton"] button[kind="primary"],
    div[data-testid="stDownloadButton"] button[kind="primary"] {{
        background: var(--forest);
        border-color: var(--forest);
    }}

    div[data-testid="stExpander"] {{
        background: rgba(255,255,255,0.65);
        border: 1px solid var(--border);
        border-radius: 14px;
    }}

    /* SOURCE AND METHODOLOGY */

    .source-note {{
        color: var(--muted);
        font-size: 0.84rem;
        line-height: 1.85;
        border-top: 1px solid var(--border);
        padding-top: 1.4rem;
        margin-top: 2.5rem;
    }}

    /* RESPONSIVE LAYOUT */

    @media (max-width: 1100px) {{
        .block-container {{
            padding-left: 1.5rem;
            padding-right: 1.5rem;
        }}

        .hero {{
            min-height: 220px;
        }}
    }}

    @media (max-width: 768px) {{
        .block-container {{
            padding: 1.2rem 1rem 2.5rem;
        }}

        .hero {{
            padding: 1.5rem;
            min-height: auto;
            border-radius: 18px;
        }}

        .hero h1 {{
            font-size: 1.85rem;
        }}

        .section-title {{
            font-size: 1.2rem;
        }}

        .kpi-card,
        .insight-card {{
            padding: 1rem;
            min-height: 120px;
        }}

        .kpi-value {{
            font-size: 1.55rem;
        }}
    }}

    @media (prefers-reduced-motion: reduce) {{
        *,
        *::before,
        *::after {{
            transition: none !important;
        }}
    }}
    
    
    /* ===== FONT & TEXT ALIGNMENT ===== */

    /* Font utama */
    .stApp,
    [data-testid="stMarkdownContainer"] {{
        font-family: 'DM Sans', sans-serif;
    }}

    /* Judul */
    h1, h2, h3, h4, h5, h6,
    [data-testid="stHeading"] {{
        font-family: 'Manrope', sans-serif;
        line-height: 1.4;
    }}

    /* Paragraf rata kiri-kanan */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stCaptionContainer"] p,
    .section-desc,
    .hero-subtitle,
    .insight-copy,
    .source-note {{
        text-align: justify;
        line-height: 1.8;
    }}

    /* Jarak daftar */
    [data-testid="stMarkdownContainer"] li {{
        margin-bottom: 0.45rem;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        font-family: 'DM Sans', sans-serif;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------- HELPERS -------------------------

def tr(key):
    return LANG[st.session_state.language][key]


def fmt_int(value):
    if pd.isna(value):
        return "—"
    return f"{value:,.0f}".replace(",", ".")


def fmt_rp(value):
    if pd.isna(value):
        return "—"

    value = float(value)

    if value < 0:
        return f"-Rp {abs(value):,.0f}".replace(",", ".")

    return f"Rp {value:,.0f}".replace(",", ".")


def fmt_pct(value, digits=2):
    if pd.isna(value):
        return "—"

    result = f"{value:+.{digits}f}%"

    if st.session_state.language == "Indonesia":
        result = result.replace(".", ",")

    return result


def section_title(title, description=""):
    st.markdown(
        f'<div class="section-title">{title}</div>',
        unsafe_allow_html=True,
    )

    if description:
        st.markdown(
            f'<div class="section-desc">{description}</div>',
            unsafe_allow_html=True,
        )


def kpi_card(label, value, foot=""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-foot">{foot}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_card(label, value, copy):
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-label">{label}</div>
            <div class="insight-value">{value}</div>
            <div class="insight-copy">{copy}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_chart(fig, height=400):
    fig.update_layout(
        height=height,
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(family="DM Sans, sans-serif", color=INK, size=12),
        margin=dict(l=12, r=16, t=55, b=15),
        title=dict(
            font=dict(family="Manrope, sans-serif", size=16, color=NAVY),
            x=0.02,
            xanchor="left",
        ),
        legend_title_text=tr("commodity"),
        hoverlabel=dict(bgcolor=WHITE, font_color=INK),
    )

    fig.update_xaxes(showgrid=True, gridcolor="#EDF0E9", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#EDF0E9", zeroline=False)

    return fig


def calculate_monthly_changes(data):
    """
    Menghitung perubahan persentase hanya jika:
    - Bulan sebelumnya benar-benar bulan kalender sebelumnya.
    - Harga bulan ini dan sebelumnya tersedia.
    - Harga bulan sebelumnya tidak nol.

    Data tetap diurutkan berdasarkan komoditas dan periode.
    """
    monthly = (
        data.dropna(subset=["period"])
        .sort_values(["commodity", "period"])
        .copy()
    )

    monthly["previous_price"] = (
        monthly.groupby("commodity")["price"].shift(1)
    )

    monthly["previous_period"] = (
        monthly.groupby("commodity")["period"].shift(1)
    )

    current_index = (
        monthly["period"].dt.year * 12
        + monthly["period"].dt.month
    )

    previous_index = (
        monthly["previous_period"].dt.year * 12
        + monthly["previous_period"].dt.month
    )

    valid_previous_price = monthly["previous_price"].notna() & (
        monthly["previous_price"] != 0
    )

    consecutive_months = current_index.eq(previous_index + 1)

    valid_current_price = monthly["price"].notna()

    valid_change = (
        consecutive_months
        & valid_previous_price
        & valid_current_price
    )
    monthly["change_amount"] = pd.NA
    monthly["change_pct"] = pd.NA

    monthly.loc[valid_change, "change_amount"] = (
        monthly.loc[valid_change, "price"]
        - monthly.loc[valid_change, "previous_price"]
    )

    monthly.loc[valid_change, "change_pct"] = (
        (
            monthly.loc[valid_change, "price"]
            - monthly.loc[valid_change, "previous_price"]
        )
        / monthly.loc[valid_change, "previous_price"]
        * 100
    )

    return monthly


def longest_directional_streak(data, direction):
    """
    Mencari rangkaian perubahan naik atau turun terpanjang
    untuk setiap komoditas.

    Satu rangkaian hanya berlanjut apabila:
    - Periode berurutan satu bulan.
    - Perubahan memiliki arah yang sama.
    - Perubahan harga tersedia.
    """
    if data.empty:
        return None

    candidates = []

    for commodity, group in data.groupby("commodity"):
        group = group.sort_values("period").copy()

        streak = []
        previous_row = None

        for _, row in group.iterrows():
            change = row["change_pct"]

            if pd.isna(change):
                if streak:
                    candidates.append((commodity, streak.copy()))
                    streak = []

                previous_row = None
                continue

            if direction == "up":
                matches_direction = change > 0
            else:
                matches_direction = change < 0

            if not matches_direction:
                if streak:
                    candidates.append((commodity, streak.copy()))

                streak = []
                previous_row = row
                continue

            if previous_row is None:
                streak = [row]
            else:
                expected_period = (
                    previous_row["period"] + pd.DateOffset(months=1)
                )

                same_sequence = (
                    row["period"].year == expected_period.year
                    and row["period"].month == expected_period.month
                )

                if same_sequence:
                    streak.append(row)
                else:
                    if streak:
                        candidates.append((commodity, streak.copy()))

                    streak = [row]

            previous_row = row

        if streak:
            candidates.append((commodity, streak.copy()))

    if not candidates:
        return None

    # Prioritaskan jumlah perubahan terbanyak.
    # Jika sama, pilih rangkaian yang berakhir paling baru.
    candidates.sort(
        key=lambda item: (
            len(item[1]),
            item[1][-1]["period"],
        ),
        reverse=True,
    )

    commodity, streak = candidates[0]

    return {
        "commodity": commodity,
        "start": streak[0]["period"],
        "end": streak[-1]["period"],
        "count": len(streak),
        "first_change": streak[0]["change_pct"],
        "last_change": streak[-1]["change_pct"],
    }


def format_period(period):
    if pd.isna(period):
        return "—"

    if st.session_state.language == "Indonesia":
        months = [
            "Jan", "Feb", "Mar", "Apr",
            "Mei", "Jun", "Jul", "Agu",
            "Sep", "Okt", "Nov", "Des",
        ]

        return f"{months[period.month - 1]} {period.year}"

    return period.strftime("%b %Y")


# ------------------------- DATABASE -------------------------

@st.cache_data(ttl=300)
def load_data():
    password = os.getenv("PGPASSWORD")

    if not password:
        raise ValueError(
            "PGPASSWORD is not set in the terminal running Streamlit."
        )

    connection = psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", "5432")),
        dbname=os.getenv("PGDATABASE", "food_price_intelligence"),
        user=os.getenv("PGUSER", "postgres"),
        password=password,
        connect_timeout=8,
    )

    try:
        query = """
            SELECT
                commodity,
                year,
                month::INTEGER AS month_num,
                price
            FROM food_prices
            ORDER BY commodity, year, month::INTEGER;
        """

        data = pd.read_sql_query(query, connection)

    finally:
        connection.close()

    data["year"] = pd.to_numeric(data["year"], errors="coerce")
    data["month_num"] = pd.to_numeric(data["month_num"], errors="coerce")
    data["price"] = pd.to_numeric(data["price"], errors="coerce")

    data["period"] = pd.to_datetime(
        {
            "year": data["year"],
            "month": data["month_num"],
            "day": 1,
        },
        errors="coerce",
    )

    return data


# -------------------------- LOAD DATA -----------------------

try:
    df = load_data()

except Exception as error:
    st.error(tr("db_error"))
    st.info(tr("db_help"))

    with st.expander(tr("db_detail")):
        st.code(str(error))

    st.stop()

if df.empty:
    st.warning(tr("empty_table"))
    st.stop()


# --------------------------- SIDEBAR ------------------------

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-logo">🌾</div>
            <div class="sidebar-title">Food Price Intelligence</div>
            <div class="sidebar-subtitle">National consumer prices</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.selectbox(
        "🌐 " + tr("language"),
        options=["Indonesia", "English"],
        key="language",
    )

    st.divider()

    st.markdown(f"### {tr('filter')}")
    st.caption(tr("filter_help"))

    years = sorted(
        df["year"].dropna().astype(int).unique().tolist()
    )

    default_years = years[-3:] if len(years) > 3 else years

    selected_years = st.multiselect(
        tr("year"),
        options=years,
        default=default_years,
    )

    commodities = sorted(
        df["commodity"].dropna().unique().tolist()
    )

    preferred = [
        "Beras Premium",
        "Beras Medium",
        "Cabai Rawit Merah",
        "Bawang Merah",
        "Daging Ayam Ras",
        "Minyak Goreng Kemasan",
    ]

    default_commodities = [
        commodity
        for commodity in preferred
        if commodity in commodities
    ]

    if not default_commodities:
        default_commodities = commodities[:5]

    selected_commodities = st.multiselect(
        tr("commodity"),
        options=commodities,
        default=default_commodities,
        placeholder=tr("search_commodity"),
        help=tr("filter_help"),
    )

    st.divider()

    if st.button(tr("reload"), width="stretch"):
        st.cache_data.clear()
        st.rerun()

    st.caption(tr("data_source"))


# ----------------------- FLOATING NAVIGATION -----------------------

nav_menu = {
    "id": {
        "title": "Navigasi Dashboard",
        "overview": "Ringkasan",
        "insights": "Analisis Harga & Insight",
        "trend": "Tren Harga Bulanan",
        "comparison": "Perbandingan Dua Periode",
        "ranking": "Peringkat Harga",
        "volatility": "Volatilitas Harga",
        "annual": "Perbandingan Tahunan",
        "quality": "Kualitas Data",
        "export": "Ekspor Data",
    },
    "en": {
        "title": "Dashboard Navigation",
        "overview": "Overview",
        "insights": "Price Intelligence & Insights",
        "trend": "Monthly Price Trends",
        "comparison": "Two-Period Comparison",
        "ranking": "Price Ranking",
        "volatility": "Price Volatility",
        "annual": "Annual Comparison",
        "quality": "Data Quality",
        "export": "Export Data",
    },
}

nav = nav_menu.get(st.session_state.get("language", "id"), nav_menu["id"])

st.markdown(
    f"""
    <div class="floating-nav">
        <details>
            <summary title="{nav['title']}">☰</summary>
            <div class="floating-nav-panel">
                <div class="floating-nav-title">{nav['title']}</div>
                <a href="#section-overview">{nav['overview']}</a>
                <a href="#section-insights">{nav['insights']}</a>
                <a href="#section-trend">{nav['trend']}</a>
                <a href="#section-comparison">{nav['comparison']}</a>
                <a href="#section-ranking">{nav['ranking']}</a>
                <a href="#section-volatility">{nav['volatility']}</a>
                <a href="#section-annual">{nav['annual']}</a>
                <a href="#section-quality">{nav['quality']}</a>
                <a href="#section-export">{nav['export']}</a>
            </div>
        </details>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------- HEADER ------------------------

left, right = st.columns([1.7, 1], gap="medium")

with left:
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-kicker">{tr('hero_kicker')}</div>
            <h1>{tr('hero_title')}</h1>
            <div class="hero-subtitle">{tr('hero_subtitle')}</div>
            <div class="hero-foot">{tr('hero_foot')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        f"""
        <div style="
            min-height:240px;
            height:100%;
            border-radius:20px;
            overflow:hidden;
            background:
                linear-gradient(0deg,rgba(23,44,41,.48),rgba(23,44,41,.02)),
                url('https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=1000&q=85')
                center/cover no-repeat;
            display:flex;
            align-items:flex-end;
            padding:1.2rem;
        ">
            <div style="color:white;font-family:Manrope,sans-serif;
                        font-size:1.12rem;font-weight:800;line-height:1.4;">
                {tr('hero_image')}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------ FILTERED DATA ---------------------

if not selected_years:
    st.warning(tr("choose_year"))
    st.stop()

if not selected_commodities:
    st.warning(tr("choose_commodity"))
    st.stop()

filtered = df[
    df["year"].isin(selected_years)
    & df["commodity"].isin(selected_commodities)
].copy()

if filtered.empty:
    st.warning(tr("empty_filter"))
    st.stop()

filtered = filtered.sort_values(["commodity", "period"])
priced = filtered.dropna(subset=["price"]).copy()

total_rows = len(filtered)
available_prices = int(filtered["price"].notna().sum())
missing_prices = int(filtered["price"].isna().sum())
total_commodities = int(filtered["commodity"].nunique())

completeness = (
    available_prices / total_rows * 100
    if total_rows
    else 0
)


# ----------------------------- KPI --------------------------
st.markdown(
    '<div id="section-overview"></div>',
    unsafe_allow_html=True,
)

section_title(tr("overview"), tr("overview_desc"))

cols = st.columns(4, gap="medium")

with cols[0]:
    kpi_card(
        tr("total_obs"),
        fmt_int(total_rows),
        tr("selected_rows"),
    )

with cols[1]:
    kpi_card(
        tr("commodities"),
        fmt_int(total_commodities),
        tr("unique_commodities"),
    )

with cols[2]:
    kpi_card(
        tr("available"),
        fmt_int(available_prices),
        tr("non_null"),
    )

with cols[3]:
    percentage = f"{completeness:.2f}%"

    if st.session_state.language == "Indonesia":
        percentage = percentage.replace(".", ",")

    kpi_card(
        tr("completeness"),
        percentage,
        f"{fmt_int(missing_prices)} {tr('missing')}",
    )


# ---------------------- MONTHLY CHANGES ---------------------

# Perhitungan menggunakan seluruh data sebelum filter tahun.
# Dengan begitu, Januari pada tahun terpilih tetap dapat
# dibandingkan dengan Desember tahun sebelumnya jika tersedia.
all_monthly = calculate_monthly_changes(df)

# Data untuk perhitungan perubahan harga yang valid
changes = all_monthly[
    all_monthly["commodity"].isin(selected_commodities)
    & all_monthly["year"].isin(selected_years)
].dropna(subset=["change_pct"]).copy()

# Data khusus streak: pertahankan baris dengan perubahan harga kosong
# agar rangkaian kenaikan atau penurunan terputus dengan benar
streak_data = all_monthly[
    all_monthly["commodity"].isin(selected_commodities)
    & all_monthly["year"].isin(selected_years)
].copy()

streak_data = streak_data.sort_values(
    ["commodity", "year", "month_num"]
).reset_index(drop=True)

changes = changes.sort_values(["commodity", "period"])


# --------------------- PRICE INTELLIGENCE -------------------

st.divider()

section_title(
    tr("intelligence"),
    tr("intelligence_desc"),
)

i1, i2, i3 = st.columns(3, gap="medium")

if not priced.empty:
    average_by_commodity = (
        priced.groupby("commodity", as_index=False)
        .agg(avg_price=("price", "mean"))
        .sort_values("avg_price", ascending=False)
    )

    highest_avg = average_by_commodity.iloc[0]
    lowest_avg = average_by_commodity.iloc[-1]

    with i1:
        insight_card(
            tr("highest_avg"),
            highest_avg["commodity"],
            tr("avg_on_filter").format(
                fmt_rp(highest_avg["avg_price"])
            ),
        )

    with i2:
        insight_card(
            tr("lowest_avg"),
            lowest_avg["commodity"],
            tr("avg_on_filter").format(
                fmt_rp(lowest_avg["avg_price"])
            ),
        )

else:
    with i1:
        insight_card(
            tr("highest_avg"),
            tr("no_data"),
            tr("no_prices"),
        )

    with i2:
        insight_card(
            tr("lowest_avg"),
            tr("no_data"),
            tr("no_prices"),
        )

if not changes.empty:
    latest_by_commodity = (
        changes.sort_values("period")
        .groupby("commodity", as_index=False)
        .tail(1)
        .sort_values("period")
    )

    latest_change = latest_by_commodity.iloc[-1]

    with i3:
        insight_card(
            tr("latest_change"),
            latest_change["commodity"],
            tr("latest_prefix").format(
                fmt_pct(latest_change["change_pct"]),
                format_period(latest_change["period"]),
            ),
        )

else:
    with i3:
        insight_card(
            tr("latest_change"),
            tr("no_data"),
            tr("need_two_months"),
        )


# ---------------- LARGEST INCREASE AND DECREASE -------------

if not changes.empty:
    st.markdown(
        "<div style='height:0.7rem;'></div>",
        unsafe_allow_html=True,
    )

    increase, decrease = st.columns(2, gap="medium")

    biggest_increase = changes.loc[
        changes["change_pct"].idxmax()
    ]

    biggest_decrease = changes.loc[
        changes["change_pct"].idxmin()
    ]

    with increase:
        insight_card(
            tr("largest_increase"),
            biggest_increase["commodity"],
            (
                f"{tr('change_amount')}: "
                f"{'-Rp ' + f'{abs(biggest_increase['change_amount']):,.0f}'.replace(',', '.') if biggest_increase['change_amount'] < 0 else fmt_rp(biggest_increase['change_amount'])}"
                f"<br>"
                f"{tr('change_prefix').format(
                    fmt_pct(biggest_increase['change_pct']),
                    format_period(biggest_increase['period']),
                )}"
            ),
        )

    with decrease:
        insight_card(
            tr("largest_decrease"),
            biggest_decrease["commodity"],
            (
                f"{tr('change_amount')}: "
                f"{fmt_rp(biggest_decrease['change_amount'])}"
                f"<br>"
                f"{tr('change_prefix').format(
                    fmt_pct(biggest_decrease['change_pct']),
                    format_period(biggest_decrease['period']),
                )}"
            ),
        )

else:
    st.info(tr("no_change"))


# ------------------ CONSECUTIVE MONTHLY TRENDS --------------

st.markdown(
    "<div style='height:0.7rem;'></div>",
    unsafe_allow_html=True,
)

section_title(
    tr("streak_title"),
    tr("streak_desc"),
)

if not streak_data.empty:
    longest_increase = longest_directional_streak(
        streak_data,
        "up",
    )

    longest_decrease = longest_directional_streak(
        streak_data,
        "down",
    )

    s1, s2 = st.columns(2, gap="medium")

    if longest_increase:
        with s1:
            insight_card(
                tr("streak_up"),
                longest_increase["commodity"],
                (
                    tr("streak_copy").format(
                        longest_increase["count"],
                        format_period(longest_increase["end"]),
                    )
                    + " "
                    + tr("streak_start").format(
                        format_period(longest_increase["start"])
                    )
                ),
            )
    else:
        with s1:
            insight_card(
                tr("streak_up"),
                tr("no_data"),
                tr("no_streak"),
            )

    if longest_decrease:
        with s2:
            insight_card(
                tr("streak_down"),
                longest_decrease["commodity"],
                (
                    tr("streak_copy").format(
                        longest_decrease["count"],
                        format_period(longest_decrease["end"]),
                    )
                    + " "
                    + tr("streak_start").format(
                        format_period(longest_decrease["start"])
                    )
                ),
            )
    else:
        with s2:
            insight_card(
                tr("streak_down"),
                tr("no_data"),
                tr("no_streak"),
            )

else:
    st.info(tr("streak_none"))

st.caption(
    f"**{tr('interpretation')}:** {tr('interpretation_text')}"
)


# ------------------------ MONTHLY TREND ---------------------

st.divider()
st.markdown(
    '<div id="section-trend"></div>',
    unsafe_allow_html=True,
)

section_title(
    tr("section_trend"),
    tr("trend_desc"),
)

if not priced.empty:
    # Pilihan komoditas khusus untuk grafik tren
    available_commodities = sorted(
        priced["commodity"].dropna().unique().tolist()
    )

    if available_commodities:
        selected_trend_commodity = st.selectbox(
            "Pilih komoditas untuk melihat tren harga",
            options=available_commodities,
            key="trend_commodity_selector",
        )

        # Ambil data komoditas yang dipilih
        trend = (
            priced[
                priced["commodity"] == selected_trend_commodity
            ]
            .groupby("period", as_index=False)
            .agg(avg_price=("price", "mean"))
            .sort_values("period")
        )

        if not trend.empty:
            # Ringkasan perubahan harga selama periode terpilih
            first_price = trend["avg_price"].iloc[0]
            last_price = trend["avg_price"].iloc[-1]

            if first_price != 0:
                change_pct = (
                    (last_price - first_price) / first_price
                ) * 100
            else:
                change_pct = None

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Harga awal",
                    fmt_rp(first_price),
                    help=f"Periode: {format_period(trend['period'].iloc[0])}",
                )

            with col2:
                st.metric(
                    "Harga terakhir",
                    fmt_rp(last_price),
                    help=f"Periode: {format_period(trend['period'].iloc[-1])}",
                )

            with col3:
                st.metric(
                    "Perubahan harga",
                    (
                        fmt_pct(change_pct)
                        if change_pct is not None
                        else "Tidak tersedia"
                    ),
                    delta=(
                        f"{change_pct:+.2f}%"
                        if change_pct is not None
                        else None
                    ),
                    help="Perbandingan harga terakhir dengan harga awal pada periode yang dipilih.",
                )

            # Grafik tren harga bulanan
            fig = px.line(
                trend,
                x="period",
                y="avg_price",
                markers=True,
                labels={
                    "period": tr("period"),
                    "avg_price": tr("price"),
                },
                title=(
                    f"{tr('trend_title')} — "
                    f"{selected_trend_commodity}"
                ),
                color_discrete_sequence=[NAVY],
            )

            fig.update_traces(
                line=dict(width=3),
                marker=dict(size=6),
                hovertemplate=(
                    "%{x|%b %Y}<br>"
                    "Harga: Rp %{y:,.0f}"
                    "<extra></extra>"
                ),
            )

            fig.update_layout(hovermode="x unified")
            fig.update_xaxes(
                title=tr("month"),
                tickformat="%b %Y",
            )
            fig.update_yaxes(
                title=tr("price"),
                tickformat=",.0f",
            )

            style_chart(fig, 430)
            st.plotly_chart(fig, width="stretch")

        else:
            st.info(tr("no_prices"))

    else:
        st.info(tr("no_prices"))

else:
    st.info(tr("no_prices"))
 
# ------------------------ PERIOD COMPARISON ---------------------

st.divider()
st.markdown(
    '<div id="section-comparison"></div>',
    unsafe_allow_html=True,
)

section_title(
    tr("section_comparison"),
    tr("comparison_desc"),
)


if not priced.empty:
    comparison_data = (
        priced.groupby(
            ["period", "commodity"],
            as_index=False,
        )
        .agg(avg_price=("price", "mean"))
        .sort_values("period")
    )

    available_periods = sorted(
        comparison_data["period"].dropna().unique().tolist()
    )

    if len(available_periods) >= 2:
        period_options = {
            format_period(period): period
            for period in available_periods
        }

        period_labels = list(period_options.keys())

        col1, col2 = st.columns(2)

        with col1:
            period_1_label = st.selectbox(
                "Periode pertama",
                options=period_labels,
                index=0,
                key="comparison_period_1",
            )

        with col2:
            period_2_label = st.selectbox(
                "Periode kedua",
                options=period_labels,
                index=len(period_labels) - 1,
                key="comparison_period_2",
            )

        period_1 = period_options[period_1_label]
        period_2 = period_options[period_2_label]

        if period_1 == period_2:
            st.warning(
                "Pilih dua periode yang berbeda untuk membandingkan harga."
            )

        else:
            data_1 = comparison_data[
                comparison_data["period"] == period_1
            ][["commodity", "avg_price"]].rename(
                columns={"avg_price": "price_1"}
            )

            data_2 = comparison_data[
                comparison_data["period"] == period_2
            ][["commodity", "avg_price"]].rename(
                columns={"avg_price": "price_2"}
            )

            comparison = data_1.merge(
                data_2,
                on="commodity",
                how="inner",
            )

            if not comparison.empty:
                comparison["difference"] = (
                    comparison["price_2"] - comparison["price_1"]
                )

                comparison["change_pct"] = (
                    comparison["difference"]
                    / comparison["price_1"].replace(0, float("nan"))
                ) * 100

                comparison["status"] = comparison["difference"].apply(
                    lambda value: (
                        "Naik" if value > 0
                        else "Turun" if value < 0
                        else "Tetap"
                    )
                )

                comparison = comparison.sort_values(
                    "difference",
                    ascending=False,
                )

                total_compared = len(comparison)
                increased = int((comparison["difference"] > 0).sum())
                decreased = int((comparison["difference"] < 0).sum())
                unchanged = int((comparison["difference"] == 0).sum())

                col1, col2, col3 = st.columns(3)

                
                col1.metric("Komoditas dibandingkan", total_compared)
                col2.metric("Komoditas naik", increased)
                col3.metric("Komoditas turun", decreased)


                st.caption(
                    f"Harga tetap: {unchanged} komoditas. "
                    "Hanya komoditas yang memiliki data pada kedua periode "
                    "yang disertakan."
                )

                display_comparison = comparison.copy()

                display_comparison["price_1"] = (
                    display_comparison["price_1"].apply(fmt_rp)
                )
                display_comparison["price_2"] = (
                    display_comparison["price_2"].apply(fmt_rp)
                )
                display_comparison["difference"] = (
                    display_comparison["difference"].apply(fmt_rp)
                )
                display_comparison["change_pct"] = (
                    display_comparison["change_pct"].apply(
                        lambda value: (
                            fmt_pct(value)
                            if pd.notna(value)
                            else "Tidak tersedia"
                        )
                    )
                )

                display_comparison = display_comparison.rename(
                    columns={
                        "commodity": "Komoditas",
                        "price_1": f"Harga {period_1_label}",
                        "price_2": f"Harga {period_2_label}",
                        "difference": "Selisih harga",
                        "change_pct": "Perubahan (%)",
                        "status": "Status",
                    }
                )

                st.dataframe(
                    display_comparison,
                    width="stretch",
                    hide_index=True,
                )

                chart_data = comparison.sort_values(
                    "difference",
                    ascending=True,
                )

                fig_comparison = px.bar(
                    chart_data,
                    x="difference",
                    y="commodity",
                    orientation="h",
                    labels={
                        "difference": "Selisih harga (Rp)",
                        "commodity": "Komoditas",
                    },
                    title=(
                        f"Perubahan harga: {period_1_label} "
                        f"ke {period_2_label}"
                    ),
                    color="status",
                    color_discrete_map={
                        "Naik": "#78917A",
                        "Turun": "#B66D61",
                        "Tetap": "#8B8B8B",
                    },
                )

                fig_comparison.update_layout(
                    showlegend=True,
                    yaxis={"categoryorder": "total ascending"},
                )
                fig_comparison.update_xaxes(tickformat=",.0f")

                style_chart(fig_comparison, 450)
                st.plotly_chart(
                    fig_comparison,
                    width="stretch",
                )
                
                
                # Automated comparison insights
                highest_increase = (
                    comparison.loc[
                        comparison["change_pct"].idxmax()
                    ]
                    if (
                        (comparison["difference"] > 0)
                        & comparison["change_pct"].notna()
                    ).any()
                    else None
                )

                highest_decrease = (
                    comparison.loc[
                        comparison["change_pct"].idxmin()
                    ]
                    if (
                        (comparison["difference"] < 0)
                        & comparison["change_pct"].notna()
                    ).any()
                    else None
                )

                st.markdown("#### Insight perbandingan periode")

                insight_col1, insight_col2 = st.columns(2)

                with insight_col1:
                    if highest_increase is not None:
                        st.success(
                            f"**Kenaikan persentase terbesar**\n\n"
                            f"{highest_increase['commodity']} mengalami "
                            f"kenaikan sebesar "
                            f"{fmt_pct(highest_increase['change_pct'])}, "
                            f"dari {fmt_rp(highest_increase['price_1'])} "
                            f"menjadi {fmt_rp(highest_increase['price_2'])}."
                        )
                    else:
                        st.info(
                            "Tidak ada komoditas yang mengalami kenaikan "
                            "pada kedua periode terpilih."
                        )

                with insight_col2:
                    if highest_decrease is not None:
                        st.warning(
                            f"**Penurunan persentase terbesar**\n\n"
                            f"{highest_decrease['commodity']} mengalami "
                            f"penurunan sebesar "
                            f"{fmt_pct(highest_decrease['change_pct'])}, "
                            f"dari {fmt_rp(highest_decrease['price_1'])} "
                            f"menjadi {fmt_rp(highest_decrease['price_2'])}."
                        )
                    else:
                        st.info(
                            "Tidak ada komoditas yang mengalami penurunan "
                            "pada kedua periode terpilih."
                        )

                
                # Automated interpretation
                if total_compared > 0:
                    if increased == total_compared:
                        interpretation = (
                            f"Seluruh {total_compared} komoditas yang "
                            "dibandingkan mengalami kenaikan harga "
                            "pada periode terpilih."
                        )
                    elif decreased == total_compared:
                        interpretation = (
                            f"Seluruh {total_compared} komoditas yang "
                            "dibandingkan mengalami penurunan harga "
                            "pada periode terpilih."
                        )
                    elif unchanged == total_compared:
                        interpretation = (
                            "Seluruh komoditas yang dibandingkan "
                            "memiliki harga yang sama pada kedua periode."
                        )
                    else:
                        interpretation = (
                            f"Perubahan harga bervariasi: {increased} "
                            f"komoditas naik, {decreased} turun, dan "
                            f"{unchanged} tetap."
                        )

                    if highest_increase is not None:
                        interpretation += (
                            f" {highest_increase['commodity']} mencatat "
                            f"kenaikan persentase tertinggi sebesar "
                            f"{fmt_pct(highest_increase['change_pct'])}."
                        )

                    interpretation += (
                        " Pola ini menggambarkan perubahan harga pada "
                        "periode terpilih, bukan penyebab perubahan."
                    )

                    st.caption(interpretation)



            else:
                st.info(
                    "Tidak ada komoditas yang memiliki data pada "
                    "kedua periode tersebut."
                )

    else:
        st.info(
            "Dibutuhkan minimal dua periode data untuk melakukan perbandingan."
        )

else:
    st.info(tr("no_prices"))


# ------------------------ AUTOMATED REPORT ------------------------

st.divider()

st.markdown(
    '<div id="section-report"></div>',
    unsafe_allow_html=True,
)

section_title(
    "Ringkasan Laporan",
    "Ikhtisar otomatis berdasarkan data dan filter yang dipilih.",
)

if not priced.empty:
    report_data = priced.copy()

    # Ringkasan harga berdasarkan komoditas
    commodity_summary = (
        report_data.groupby("commodity")["price"]
        .agg(["mean", "min", "max", "count"])
        .reset_index()
    )

    # Ringkasan harga keseluruhan
    overall_avg = report_data["price"].mean()
    overall_min = report_data["price"].min()
    overall_max = report_data["price"].max()
    total_records = len(report_data)
    total_commodities = report_data["commodity"].nunique()
    total_periods = report_data["period"].nunique()

    # Komoditas dengan rata-rata harga tertinggi dan terendah
    highest_avg = commodity_summary.loc[
        commodity_summary["mean"].idxmax()
    ]
    lowest_avg = commodity_summary.loc[
        commodity_summary["mean"].idxmin()
    ]

    # KPI laporan
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Rata-rata harga",
        fmt_rp(overall_avg),
    )

    col2.metric(
        "Komoditas dianalisis",
        total_commodities,
    )

    col3.metric(
        "Jumlah observasi",
        f"{total_records:,}".replace(",", "."),
    )

    # Narasi laporan otomatis
    st.markdown("#### Ikhtisar kondisi harga")

    st.write(
        f"Berdasarkan data yang ditampilkan, terdapat "
        f"**{total_commodities} komoditas** dengan "
        f"**{total_records:,} observasi harga** "
        f"yang mencakup **{total_periods} periode**. "
        f"Rata-rata harga seluruh observasi adalah "
        f"**{fmt_rp(overall_avg)}**, dengan harga terendah "
        f"**{fmt_rp(overall_min)}** dan harga tertinggi "
        f"**{fmt_rp(overall_max)}**."
        .replace(",", ".")
    )

    st.write(
        f"Jika dilihat berdasarkan rata-rata harga per komoditas, "
        f"**{highest_avg['commodity']}** memiliki rata-rata tertinggi "
        f"sebesar **{fmt_rp(highest_avg['mean'])}**, sedangkan "
        f"**{lowest_avg['commodity']}** memiliki rata-rata terendah "
        f"sebesar **{fmt_rp(lowest_avg['mean'])}**."
    )

    st.caption(
        "Ringkasan ini bersifat deskriptif dan mengikuti data yang "
        "tersedia pada filter aktif. Nilai rata-rata antarobservasi "
        "tidak dengan sendirinya menjelaskan penyebab perubahan harga."
    )

else:
    st.info("Tidak ada data yang tersedia untuk menyusun laporan.")


# ------------------------ CONCLUSION & RECOMMENDATIONS ------------------------

st.divider()

section_title(
    "Kesimpulan dan Rekomendasi",
    "Interpretasi pola harga berdasarkan data yang tersedia.",
)

if not priced.empty:
    # Hitung rata-rata harga per komoditas pada setiap periode
    monthly_summary = (
        priced.groupby(["period", "commodity"], as_index=False)
        .agg(avg_price=("price", "mean"))
        .sort_values("period")
    )

    commodity_changes = []

    for commodity, group in monthly_summary.groupby("commodity"):
        group = group.sort_values("period")

        if len(group) >= 2:
            first_price = group.iloc[0]["avg_price"]
            last_price = group.iloc[-1]["avg_price"]

            if first_price != 0:
                change_pct = (
                    (last_price - first_price) / first_price
                ) * 100

                commodity_changes.append({
                    "commodity": commodity,
                    "first_price": first_price,
                    "last_price": last_price,
                    "change_pct": change_pct,
                })

    if commodity_changes:
        changes_df = pd.DataFrame(commodity_changes)

        increased_count = int(
            (changes_df["change_pct"] > 0).sum()
        )
        decreased_count = int(
            (changes_df["change_pct"] < 0).sum()
        )
        unchanged_count = int(
            (changes_df["change_pct"] == 0).sum()
        )

        highest_increase = changes_df.loc[
            changes_df["change_pct"].idxmax()
        ]

        highest_decrease = changes_df.loc[
            changes_df["change_pct"].idxmin()
        ]

        # Kesimpulan otomatis
        st.markdown("#### Kesimpulan")

        if increased_count == len(changes_df):
            st.write(
                f"Seluruh {len(changes_df)} komoditas yang dianalisis "
                "menunjukkan kenaikan harga antara periode pertama "
                "dan terakhir yang tersedia pada filter aktif."
            )
        elif decreased_count == len(changes_df):
            st.write(
                f"Seluruh {len(changes_df)} komoditas yang dianalisis "
                "menunjukkan penurunan harga antara periode pertama "
                "dan terakhir yang tersedia pada filter aktif."
            )
        else:
            st.write(
                f"Perubahan harga bervariasi: {increased_count} "
                f"komoditas naik, {decreased_count} turun, dan "
                f"{unchanged_count} tetap antara periode pertama "
                "dan terakhir yang tersedia."
            )

        st.write(
            f"Perubahan persentase terbesar tercatat pada "
            f"**{highest_increase['commodity']}** "
            f"({fmt_pct(highest_increase['change_pct'])}), "
            "sedangkan perubahan persentase terendah tercatat pada "
            f"**{highest_decrease['commodity']}** "
            f"({fmt_pct(highest_decrease['change_pct'])})."
        )

        # Rekomendasi berbasis hasil analisis
        st.markdown(
            """
            1. **Prioritaskan pemantauan komoditas dengan perubahan harga terbesar.**  
               Periksa pergerakan harga bulanan untuk mengetahui apakah perubahan berlangsung konsisten atau hanya terjadi pada periode tertentu.

            2. **Evaluasi volatilitas harga.**  
               Gunakan bagian analisis volatilitas untuk mengidentifikasi komoditas dengan pergerakan harga yang relatif tidak stabil.

            3. **Perbarui data secara berkala.**  
               Pastikan kelengkapan periode dan konsistensi pencatatan sebelum menarik kesimpulan untuk pengambilan keputusan.
            """
        )


        st.caption(
            "Kesimpulan membandingkan observasi pertama dan terakhir "
            "yang tersedia untuk setiap komoditas, bukan seluruh "
            "perubahan yang terjadi di antara keduanya. Rekomendasi "
            "merupakan arahan analitis, bukan bukti penyebab perubahan "
            "harga."
        )
    else:
        st.info(
            "Belum cukup data untuk menyusun kesimpulan perubahan harga."
        )
else:
    st.info(
        "Tidak ada data yang tersedia untuk menyusun kesimpulan."
    )

# ------------------------ PRICE RANKING ---------------------

st.divider()

st.markdown(
    '<div id="section-ranking"></div>',
    unsafe_allow_html=True,
)

section_title(
    tr("section_ranking"),
    tr("ranking_desc"),
)

if not priced.empty:
    ranking = (
        priced.groupby("commodity", as_index=False)
        .agg(
            avg_price=("price", "mean"),
            min_price=("price", "min"),
            max_price=("price", "max"),
            observations=("price", "count"),
        )
        .sort_values("avg_price", ascending=False)
    )

    left, right = st.columns([1.1, 1], gap="medium")

    with left:
        rank_fig = px.bar(
            ranking.sort_values(
                "avg_price",
                ascending=True,
            ),
            x="avg_price",
            y="commodity",
            orientation="h",
            color="avg_price",
            color_continuous_scale=[
                "#DDE7D8",
                NAVY,
            ],
            labels={
                "avg_price": tr("price"),
                "commodity": tr("commodity"),
            },
            title=tr("ranking_title"),
        )

        rank_fig.update_coloraxes(showscale=False)
        rank_fig.update_xaxes(tickformat=",.0f")

        style_chart(
            rank_fig,
            max(380, 26 * len(ranking) + 110),
        )

        st.plotly_chart(rank_fig, width="stretch")

    with right:
        st.markdown(f"**{tr('stats')}**")

        table = ranking.copy()

        for column in [
            "avg_price",
            "min_price",
            "max_price",
        ]:
            table[column] = table[column].map(fmt_rp)

        table = table.rename(
            columns={
                "commodity": tr("commodity"),
                "avg_price": tr("average"),
                "min_price": tr("minimum"),
                "max_price": tr("maximum"),
                "observations": tr("observations"),
            }
        )

        st.dataframe(
            table,
            width="stretch",
            hide_index=True,
            height=420,
        )


# ------------------------- VOLATILITY -----------------------

st.divider()

st.markdown(
    '<div id="section-volatility"></div>',
    unsafe_allow_html=True,
)

section_title(
    tr("section_volatility"),
    tr("volatility_desc"),
)

if not changes.empty:
    volatility_ranking = (
        changes.groupby("commodity", as_index=False)
        .agg(
            avg_abs_change_pct=(
                "change_pct",
                lambda values: values.abs().mean(),
            ),
            valid_month_changes=("change_pct", "count"),
        )
        .sort_values(
            "avg_abs_change_pct",
            ascending=False,
        )
    )

    vol_fig = px.bar(
        volatility_ranking.sort_values(
            "avg_abs_change_pct",
            ascending=True,
        ),
        x="avg_abs_change_pct",
        y="commodity",
        orientation="h",
        color="avg_abs_change_pct",
        color_continuous_scale=[
            "#DDE7D8",
            "#78917A",
            NAVY,
        ],
        labels={
            "avg_abs_change_pct": tr("abs_change"),
            "commodity": tr("commodity"),
        },
        title=tr("volatility_title"),
        hover_data={
            "valid_month_changes": True,
        },
    )

    vol_fig.update_coloraxes(showscale=False)
    vol_fig.update_xaxes(ticksuffix="%")

    style_chart(
        vol_fig,
        max(350, 28 * len(volatility_ranking) + 110),
    )

    st.plotly_chart(vol_fig, width="stretch")
        # Automated volatility insight
    if not volatility_ranking.empty:
        highest_volatility = volatility_ranking.iloc[0]

        volatility_value = (
            f"{highest_volatility['avg_abs_change_pct']:.2f}"
            .replace(".", ",")
        )

        st.markdown(
            f"""
            <div style="
                padding: 1rem 1.2rem;
                border-left: 4px solid #78917A;
                border-radius: 8px;
                background: rgba(120, 145, 122, 0.10);
                margin-top: 0.5rem;
                margin-bottom: 1rem;
            ">
                <div style="font-size: 0.85rem; opacity: 0.75;">
                    {tr("volatility_insight_title")}
                </div>
                <div style="
                    font-size: 1.1rem;
                    font-weight: 650;
                    margin: 0.25rem 0;
                ">
                    {highest_volatility["commodity"]}
                </div>
                <div>
                    {tr("volatility_insight_text").format(volatility_value)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
                # Most stable commodity insight
        lowest_volatility = volatility_ranking.iloc[-1]

        stable_value = (
            f"{lowest_volatility['avg_abs_change_pct']:.2f}"
            .replace(".", ",")
        )

        st.markdown(
            f"""
            <div style="
                padding: 1rem 1.2rem;
                border-left: 4px solid #78917A;
                border-radius: 8px;
                background: rgba(120, 145, 122, 0.10);
                margin-top: 0.5rem;
                margin-bottom: 1rem;
            ">
                <div style="font-size: 0.85rem; opacity: 0.75;">
                    {tr("volatility_stable_title")}
                </div>
                <div style="
                    font-size: 1.1rem;
                    font-weight: 650;
                    margin: 0.25rem 0;
                ">
                    {lowest_volatility["commodity"]}
                </div>
                <div>
                    {tr("volatility_stable_text").format(stable_value)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.info(tr("no_volatility"))



# ---------------------- ANNUAL COMPARISON -------------------

st.divider()

st.markdown(
    '<div id="section-annual"></div>',
    unsafe_allow_html=True,
)

annual = (
    priced.groupby(["commodity", "year"], as_index=False)
    .agg(
        avg_price=("price", "mean"),
        observations=("price", "count"),
    )
    .sort_values(["commodity", "year"])
)

if not annual.empty:

    # Calculate year-to-year price changes
    annual_comparison = annual.sort_values(
        ["commodity", "year"]
    ).copy()

    annual_comparison["previous_year"] = (
        annual_comparison.groupby("commodity")["year"].shift(1)
    )

    annual_comparison["previous_avg_price"] = (
        annual_comparison.groupby("commodity")["avg_price"].shift(1)
    )

    annual_comparison["change_amount"] = (
        annual_comparison["avg_price"]
        - annual_comparison["previous_avg_price"]
    )

    annual_comparison["change_pct"] = (
        annual_comparison["change_amount"]
        / annual_comparison["previous_avg_price"]
        * 100
    )

    # Compare only consecutive calendar years
    consecutive_years = (
        annual_comparison["year"]
        == annual_comparison["previous_year"] + 1
    )

    annual_comparison.loc[
        ~consecutive_years,
        ["change_amount", "change_pct"],
    ] = pd.NA

    valid_annual_changes = annual_comparison.dropna(
        subset=["change_pct"]
    )
    
    # Annual price insight cards
    if not valid_annual_changes.empty:

        annual_increase = valid_annual_changes.loc[
            valid_annual_changes["change_pct"].idxmax()
        ]

        annual_decrease = valid_annual_changes.loc[
            valid_annual_changes["change_pct"].idxmin()
        ]

        col_increase, col_decrease = st.columns(
            [1, 1],
            gap="medium",
        )

        with col_increase:
            insight_card(
                tr("annual_increase_title"),
                annual_increase["commodity"],
                (
                    f"{fmt_rp(annual_increase['change_amount'])}"
                    f"<br>"
                    f"{annual_increase['change_pct']:+.2f}".replace(".", ",")
                    + "% "
                    f"({int(annual_increase['previous_year'])}"
                    f" → {int(annual_increase['year'])})"
                ),
            )

        with col_decrease:
            insight_card(
                tr("annual_decrease_title"),
                annual_decrease["commodity"],
                (
                    f"{fmt_rp(annual_decrease['change_amount'])}"
                    f"<br>"
                    f"{annual_decrease['change_pct']:+.2f}".replace(".", ",")
                    + "% "
                    f"({int(annual_decrease['previous_year'])}"
                    f" → {int(annual_decrease['year'])})"
                ),
            )

    else:
        st.info(tr("no_annual"))

    st.markdown(
        "<div style='height: 1.25rem;'></div>",
        unsafe_allow_html=True,
    )

    
    
    # Annual average price chart
    annual_fig = px.line(
        annual,
        x="year",
        y="avg_price",
        color="commodity",
        markers=True,
        labels={
            "year": tr("year_label"),
            "avg_price": tr("price"),
            "commodity": tr("commodity"),
        },
        title=tr("annual_title"),
        color_discrete_sequence=[
            NAVY,
            "#78917A",
            "#C58B55",
            "#7E8DB2",
            "#B66D61",
            "#6C9B9A",
            "#8B789F",
            "#B3A05E",
        ],
    )

    annual_fig.update_xaxes(dtick=1)
    annual_fig.update_yaxes(tickformat=",.0f")

    style_chart(annual_fig, 420)

    st.plotly_chart(annual_fig, width="stretch")

    # Annual comparison table
    annual_table = annual.copy()
    annual_table["avg_price"] = annual_table["avg_price"].map(fmt_rp)

    annual_table = annual_table.rename(
        columns={
            "commodity": tr("commodity"),
            "year": tr("year_label"),
            "avg_price": tr("avg_price"),
            "observations": tr("price_observations"),
        }
    )

    with st.expander(tr("view_annual")):
        st.dataframe(
            annual_table,
            width="stretch",
            hide_index=True,
        )

else:
    st.info(tr("no_annual"))



# ------------------------- DATA QUALITY ---------------------

st.divider()
st.markdown(
    '<div id="section-quality"></div>',
    unsafe_allow_html=True,
)

section_title(
    tr("section_quality"),
    tr("quality_desc"),
)

q1, q2, q3 = st.columns(3, gap="medium")

with q1:
    kpi_card(
        tr("total_rows"),
        fmt_int(total_rows),
        tr("filtered_data"),
    )

with q2:
    kpi_card(
        tr("available"),
        fmt_int(available_prices),
        tr("non_null"),
    )

with q3:
    kpi_card(
        tr("missing"),
        fmt_int(missing_prices),
        tr("empty_not_zero"),
    )

# Beri jarak antara kartu dan notifikasi kelengkapan data
st.markdown(
    "<div style='height: 1rem;'></div>",
    unsafe_allow_html=True,
)

# Data completeness insight
if total_rows > 0:
    completeness_pct = available_prices / total_rows * 100

    if missing_prices == 0:
        st.success(
            tr("quality_complete").format(
                f"{completeness_pct:.2f}".replace(".", ",")
            )
        )
    else:
        st.info(
            tr("quality_partial").format(
                f"{completeness_pct:.2f}".replace(".", ","),
                fmt_int(missing_prices),
            )
        )


with st.expander(tr("view_data")):
    display_df = filtered.copy()

    display_df[tr("period_col")] = (
        display_df["period"].dt.strftime("%b %Y")
    )

    display_df["price"] = display_df["price"].map(
        lambda value: (
            fmt_rp(value)
            if pd.notna(value)
            else tr("unavailable")
        )
    )

    display_df = display_df.rename(
        columns={
            "commodity": tr("commodity"),
            "year": tr("year_col"),
            "month_num": tr("month_number"),
            "price": tr("price_col"),
        }
    )

    st.dataframe(
        display_df[
            [
                tr("period_col"),
                tr("commodity"),
                tr("year_col"),
                tr("month_number"),
                tr("price_col"),
            ]
        ],
        width="stretch",
        hide_index=True,
    )

with st.expander(tr("view_missing")):
    missing_df = filtered[
        filtered["price"].isna()
    ][
        ["commodity", "year", "month_num"]
    ].rename(
        columns={
            "commodity": tr("commodity"),
            "year": tr("year_col"),
            "month_num": tr("month_number"),
        }
    )

    if missing_df.empty:
        st.success(tr("no_missing"))

    else:
        st.dataframe(
            missing_df.sort_values(
                [
                    tr("commodity"),
                    tr("year_col"),
                    tr("month_number"),
                ]
            ),
            width="stretch",
            hide_index=True,
        )


# -------------------------- CSV EXPORT ----------------------

st.divider()

st.markdown(
    '<div id="section-export"></div>',
    unsafe_allow_html=True,
)

section_title(
    tr("section_export"),
    tr("export_desc"),
)

export_df = filtered[
    [
        "commodity",
        "year",
        "month_num",
        "period",
        "price",
    ]
].copy()

export_df["period"] = export_df["period"].dt.strftime("%Y-%m")

export_df = export_df.rename(
    columns={
        "commodity": "commodity",
        "year": "year",
        "month_num": "month",
        "period": "period",
        "price": "price",
    }
)

st.download_button(
    label=tr("download"),
    data=export_df.to_csv(index=False).encode("utf-8-sig"),
    file_name="food_price_filtered.csv",
    mime="text/csv",
)


# ----------------------------- FOOTER -----------------------

st.markdown(
    f"""
    <div class="source-note">
        <b style="color:{NAVY};">{tr('source')}</b><br>
        Badan Pangan Nasional — Rata-rata Harga Pangan Bulanan Konsumen Nasional.<br>
        <a href="https://data.badanpangan.go.id/datasetpublications/cx8/rata-rata-harga-pangan-bulanan-konsumen-nasional"
           target="_blank" style="color:{NAVY};">
            {tr('open_source')}
        </a>
        <br><br>
        <b style="color:{NAVY};">{tr('methodology')}</b><br>
        {tr('methodology_text')}
    </div>
    """,
    unsafe_allow_html=True,
)