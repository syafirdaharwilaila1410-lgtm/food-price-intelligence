from pathlib import Path
import csv
import re
import pandas as pd

# Lokasi project dan file
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "raw_prices.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "clean_prices.csv"

def clean_price(value):
    """Mengubah harga seperti Rp12,319 menjadi angka 12319."""
    if pd.isna(value):
        return None

    value = str(value).strip()

    if value in ("", "-"):
        return None

    # Ambil angka dari format harga, termasuk pemisah ribuan
    digits = re.sub(r"[^\d]", "", value)

    return int(digits) if digits else None


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"File tidak ditemukan: {INPUT_FILE}\n"
            "Pastikan raw_prices.csv berada di folder data."
        )

    # Baca CSV dan deteksi encoding umum
    try:
        df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig", dtype=str)
    except UnicodeDecodeError:
        df = pd.read_csv(INPUT_FILE, encoding="latin-1", dtype=str)

    # Rapikan nama kolom
    df.columns = [str(col).strip() for col in df.columns]

    required_columns = ["Komoditas", "Tahun", "Bulan", "Harga"]
    missing_columns = [
        col for col in required_columns if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Kolom tidak ditemukan: {missing_columns}\n"
            f"Kolom yang tersedia: {list(df.columns)}"
        )

    # Pilih dan rapikan kolom yang dibutuhkan
    df = df[required_columns].copy()

    df["Komoditas"] = (
        df["Komoditas"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    df["Tahun"] = pd.to_numeric(df["Tahun"], errors="coerce")
    df["Harga"] = df["Harga"].apply(clean_price)

    # Baris tanpa identitas komoditas atau periode tidak dapat dianalisis
    df = df[
        df["Komoditas"].ne("")
        & df["Tahun"].notna()
        & df["Bulan"].notna()
    ].copy()

    df["Tahun"] = df["Tahun"].astype(int)
    df["Bulan"] = df["Bulan"].astype(str).str.strip()

    # Catat data kosong, bukan mengubahnya menjadi nol
    missing_prices = int(df["Harga"].isna().sum())

    # Periksa duplikat berdasarkan komoditas dan periode
    duplicate_mask = df.duplicated(
        subset=["Komoditas", "Tahun", "Bulan"],
        keep=False
    )
    duplicate_rows = int(duplicate_mask.sum())

    # Simpan hasil pembersihan
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("=" * 45)
    print("INDONESIA FOOD PRICE INTELLIGENCE")
    print("PEMERIKSAAN DAN PEMBERSIHAN DATA")
    print("=" * 45)
    print(f"Baris hasil: {len(df):,}")
    print(f"Komoditas unik: {df['Komoditas'].nunique():,}")
    print(f"Tahun tersedia: {sorted(df['Tahun'].unique().tolist())}")
    print(f"Harga kosong: {missing_prices:,}")
    print(f"Baris yang terlibat duplikat: {duplicate_rows:,}")
    print(f"File hasil: {OUTPUT_FILE}")
    print("=" * 45)


if __name__ == "__main__":
    main()
