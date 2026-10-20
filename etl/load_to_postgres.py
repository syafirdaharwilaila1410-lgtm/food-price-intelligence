
from pathlib import Path
import os
import pandas as pd
import psycopg
from psycopg import sql

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "processed" / "clean_prices.csv"

# Konfigurasi koneksi:
# Nilai default memakai konfigurasi PostgreSQL lokal yang umum.
# Jika berbeda, atur melalui environment variables di terminal.
DB_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", "5432")),
    "dbname": os.getenv("PGDATABASE", "food_price_intelligence"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD"),
}

MONTH_MAP = {
    "januari": 1, "jan": 1,
    "februari": 2, "feb": 2,
    "maret": 3, "mar": 3,
    "april": 4, "apr": 4,
    "mei": 5,
    "juni": 6, "jun": 6,
    "juli": 7, "jul": 7,
    "agustus": 8, "agu": 8, "ags": 8, "aug": 8,
    "september": 9, "sep": 9,
    "oktober": 10, "okt": 10, "oct": 10,
    "november": 11, "nov": 11,
    "desember": 12, "des": 12, "dec": 12,
}


def normalize_month(value):
    text = str(value).strip().lower()

    if text in MONTH_MAP:
        return MONTH_MAP[text]

    # Terima nomor bulan jika sumber memakai angka.
    try:
        number = int(text)
        if 1 <= number <= 12:
            return number
    except ValueError:
        pass

    raise ValueError(f"Format bulan tidak dikenali: {value!r}")


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"File tidak ditemukan: {INPUT_FILE}"
        )

    if not DB_CONFIG["password"]:
        raise ValueError(
            "Password PostgreSQL belum diatur. "
            "Atur environment variable PGPASSWORD di terminal."
        )

    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

    required = ["Komoditas", "Tahun", "Bulan", "Harga"]
    if not set(required).issubset(df.columns):
        raise ValueError(
            f"Kolom CSV harus mencakup: {required}"
        )

    records = []

    for row in df[required].itertuples(index=False, name=None):
        commodity, year, month, price = row

        commodity = str(commodity).strip()
        year = int(year)
        month_number = normalize_month(month)

        if pd.isna(price):
            price = None
        else:
            price = float(price)

        records.append(
            (commodity, year, month_number, price)
        )

    insert_query = """
        INSERT INTO food_prices
            (commodity, year, month, price)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (commodity, year, month)
        DO UPDATE SET price = EXCLUDED.price;
    """

    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.executemany(insert_query, records)

            cur.execute("""
                SELECT COUNT(*)
                FROM food_prices;
            """)
            total_rows = cur.fetchone()[0]

            cur.execute("""
                SELECT COUNT(*)
                FROM food_prices
                WHERE price IS NULL;
            """)
            missing_prices = cur.fetchone()[0]

    print("=" * 45)
    print("LOAD DATA KE POSTGRESQL BERHASIL")
    print(f"Baris diproses dari CSV : {len(records):,}")
    print(f"Total baris di database : {total_rows:,}")
    print(f"Harga kosong di database: {missing_prices:,}")
    print(f"Database                : {DB_CONFIG['dbname']}")
    print("=" * 45)


if __name__ == "__main__":
    main()
