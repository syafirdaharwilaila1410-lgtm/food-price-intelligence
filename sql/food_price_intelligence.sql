
-- =====================================================
-- PROJECT: INDONESIA FOOD PRICE INTELLIGENCE
-- FILE: food_price_intelligence.sql
-- DBMS: PostgreSQL
-- =====================================================


-- =====================================================
-- BAGIAN 01: STRUKTUR DATABASE
-- =====================================================

CREATE TABLE IF NOT EXISTS food_prices (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    commodity VARCHAR(150) NOT NULL,
    year INTEGER NOT NULL,
    month VARCHAR(20) NOT NULL,
    price NUMERIC(14, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_food_prices_period
        UNIQUE (commodity, year, month),

    CONSTRAINT chk_food_prices_year
        CHECK (year BETWEEN 2000 AND 2100),

    CONSTRAINT chk_food_prices_price
        CHECK (price IS NULL OR price >= 0)
);

CREATE INDEX IF NOT EXISTS idx_food_prices_period
    ON food_prices (year, month);

CREATE INDEX IF NOT EXISTS idx_food_prices_commodity
    ON food_prices (commodity);


-- =====================================================
-- BAGIAN 02: VERIFIKASI TABEL DAN DATABASE
-- =====================================================

-- 2. Verifikasi tabel

SELECT *
FROM food_prices
LIMIT 5;

-- 3. Cara mengetahui nama username database

SELECT
    current_database() AS nama_database,
    current_user AS username;


-- =====================================================
-- BAGIAN 03: ANALISIS DATA DAN KUALITAS DATA
-- =====================================================

-- ANALISIS 01: VALIDASI DATA DAN KUALITAS DATA
-- TUJUAN: Memeriksa jumlah data, komoditas, tahun,
--         dan harga yang tidak tersedia.
-- =====================================================

SELECT
    COUNT(*) AS total_baris,
    COUNT(DISTINCT commodity) AS total_komoditas,
    COUNT(DISTINCT year) AS total_tahun,
    COUNT(*) FILTER (WHERE price IS NULL) AS harga_kosong
FROM food_prices;


-- ANALISIS 02: PERINGKAT HARGA RATA-RATA KOMODITAS
-- TUJUAN: Menampilkan 10 komoditas dengan rata-rata
--         harga tertinggi selama periode yang tersedia.
-- =====================================================

SELECT
    commodity,
    ROUND(AVG(price), 2) AS avg_price,
    MIN(price) AS min_price,
    MAX(price) AS max_price,
    COUNT(price) AS jumlah_observasi
FROM food_prices
GROUP BY commodity
HAVING COUNT(price) > 0
ORDER BY avg_price DESC
LIMIT 10;


-- =====================================================
-- BAGIAN 04: TREN DAN VOLATILITAS HARGA
-- =====================================================

-- ANALISIS 03: TREN DAN PERUBAHAN HARGA BULANAN
-- TUJUAN: Menghitung perubahan harga berdasarkan urutan
--         bulan yang benar untuk setiap komoditas.
-- =====================================================

WITH monthly_trend AS (
    SELECT
        commodity,
        year,
        month::INTEGER AS month_num,
        price,
        LAG(price) OVER (
            PARTITION BY commodity
            ORDER BY year, month::INTEGER
        ) AS previous_price
    FROM food_prices
)
SELECT
    commodity,
    year,
    month_num AS month,
    price,
    previous_price,
    ROUND(price - previous_price, 2) AS price_change,
    ROUND(
        100.0 * (price - previous_price)
        / NULLIF(previous_price, 0),
        2
    ) AS change_pct
FROM monthly_trend
WHERE previous_price IS NOT NULL
ORDER BY ABS(
    100.0 * (price - previous_price)
    / NULLIF(previous_price, 0)
) DESC NULLS LAST
LIMIT 20;


-- ANALISIS 04: RANKING VOLATILITAS HARGA
-- TUJUAN: Mengidentifikasi komoditas dengan perubahan
--         harga relatif paling tidak stabil.
-- =====================================================

WITH monthly_data AS (
    SELECT
        commodity,
        year,
        month::INTEGER AS month_num,
        price,
        LAG(price) OVER (
            PARTITION BY commodity
            ORDER BY year, month::INTEGER
        ) AS previous_price
    FROM food_prices
),
volatility AS (
    SELECT
        commodity,
        COUNT(price) AS observations,
        ROUND(AVG(price), 2) AS avg_price,
        ROUND(STDDEV_SAMP(price), 2) AS price_stddev,
        ROUND(
            AVG(
                ABS(
                    100.0 * (price - previous_price)
                    / NULLIF(previous_price, 0)
                )
            ) FILTER (
                WHERE previous_price IS NOT NULL
            ),
            2
        ) AS avg_abs_change_pct
    FROM monthly_data
    GROUP BY commodity
)
SELECT
    commodity,
    observations,
    avg_price,
    price_stddev,
    avg_abs_change_pct
FROM volatility
WHERE observations >= 12
ORDER BY avg_abs_change_pct DESC NULLS LAST;


-- ANALISIS 05: VALIDASI PERUBAHAN ANTARBULAN
-- TUJUAN: Membandingkan harga hanya dengan bulan
--         kalender sebelumnya yang benar-benar tersedia.
-- =====================================================

WITH monthly_data AS (
    SELECT
        commodity,
        year,
        month::INTEGER AS month_num,
        price,
        (year * 12 + month::INTEGER) AS month_index
    FROM food_prices
),
matched_months AS (
    SELECT
        current_month.commodity,
        current_month.year,
        current_month.month_num,
        current_month.price,
        previous_month.price AS previous_price
    FROM monthly_data AS current_month
    LEFT JOIN monthly_data AS previous_month
        ON current_month.commodity = previous_month.commodity
        AND current_month.month_index = previous_month.month_index + 1
)
SELECT
    commodity,
    year,
    month_num AS month,
    price,
    previous_price,
    ROUND(price - previous_price, 2) AS price_change,
    ROUND(
        100.0 * (price - previous_price)
        / NULLIF(previous_price, 0),
        2
    ) AS change_pct
FROM matched_months
WHERE previous_price IS NOT NULL
  AND price IS NOT NULL
ORDER BY ABS(
    100.0 * (price - previous_price)
    / NULLIF(previous_price, 0)
) DESC NULLS LAST
LIMIT 20;


-- =====================================================
-- BAGIAN 05: ANALISIS HARGA TAHUNAN
-- =====================================================

-- ANALISIS 06: TREN HARGA TAHUNAN
-- TUJUAN: Membandingkan rata-rata harga per komoditas
--         pada setiap tahun yang tersedia.
-- =====================================================

SELECT
    commodity,
    year,
    COUNT(price) AS jumlah_observasi,
    ROUND(AVG(price), 2) AS rata_rata_harga,
    MIN(price) AS harga_terendah,
    MAX(price) AS harga_tertinggi
FROM food_prices
GROUP BY commodity, year
HAVING COUNT(price) > 0
ORDER BY commodity, year;


-- ANALISIS 07: PERTUMBUHAN HARGA TAHUNAN
-- TUJUAN: Menghitung perubahan harga tahunan (%).
-- CATATAN: Perbandingan hanya untuk tahun berurutan.
-- =====================================================

WITH annual_prices AS (
    SELECT
        commodity,
        year,
        COUNT(price) AS observations,
        AVG(price) AS avg_price
    FROM food_prices
    GROUP BY commodity, year
    HAVING COUNT(price) > 0
),
annual_comparison AS (
    SELECT
        commodity,
        year,
        observations,
        avg_price,
        LAG(year) OVER (
            PARTITION BY commodity
            ORDER BY year
        ) AS previous_year,
        LAG(avg_price) OVER (
            PARTITION BY commodity
            ORDER BY year
        ) AS previous_avg_price
    FROM annual_prices
)
SELECT
    commodity,
    year,
    observations,
    ROUND(avg_price, 2) AS avg_price,
    ROUND(previous_avg_price, 2) AS previous_avg_price,
    ROUND(
        100.0 * (avg_price - previous_avg_price)
        / NULLIF(previous_avg_price, 0),
        2
    ) AS growth_pct
FROM annual_comparison
WHERE year = previous_year + 1
ORDER BY growth_pct DESC;


-- =====================================================
-- BAGIAN 06: KELENGKAPAN DAN KUALITAS DATA
-- =====================================================

-- ANALISIS 08: KELENGKAPAN DATA BULANAN
-- TUJUAN: Memeriksa jumlah bulan tersedia per komoditas
--         dan tahun untuk membantu validasi analisis.
-- =====================================================

SELECT
    commodity,
    year,
    COUNT(*) AS total_baris,
    COUNT(price) AS bulan_dengan_harga,
    COUNT(DISTINCT month::INTEGER) AS bulan_unik,
    STRING_AGG(
        DISTINCT month::INTEGER::TEXT,
        ', ' ORDER BY month::INTEGER::TEXT
    ) AS daftar_bulan
FROM food_prices
GROUP BY commodity, year
ORDER BY commodity, year;


-- ANALISIS 09: IDENTIFIKASI HARGA KOSONG
-- TUJUAN: Menemukan periode yang memiliki baris data
--         tetapi nilai harganya belum tersedia.
-- =====================================================

SELECT
    commodity,
    year,
    month::INTEGER AS month_num,
    price
FROM food_prices
WHERE price IS NULL
ORDER BY commodity, year, month::INTEGER;


-- =====================================================
-- BAGIAN 07: KPI DAN VISUALISASI DASHBOARD
-- =====================================================

-- ANALISIS 10: KPI UTAMA DASHBOARD
-- TUJUAN: Menghasilkan ringkasan kualitas dan cakupan
--         data untuk dashboard pemantauan harga pangan.
-- =====================================================

SELECT
    COUNT(*) AS total_baris,
    COUNT(DISTINCT commodity) AS total_komoditas,
    MIN(year) AS tahun_awal,
    MAX(year) AS tahun_akhir,
    COUNT(price) AS observasi_harga_tersedia,
    COUNT(*) FILTER (
        WHERE price IS NULL
    ) AS harga_kosong,
    ROUND(
        100.0 * COUNT(price) / NULLIF(COUNT(*), 0),
        2
    ) AS persentase_harga_tersedia,
    ROUND(AVG(price), 2) AS rata_rata_harga_seluruh_observasi
FROM food_prices;


-- ANALISIS 11: TREN HARGA BULANAN
-- TUJUAN: Menyiapkan data untuk visualisasi tren harga.
-- =====================================================

SELECT
    commodity,
    year,
    month::INTEGER AS month_num,
    ROUND(AVG(price), 2) AS avg_price,
    COUNT(price) AS jumlah_observasi
FROM food_prices
GROUP BY
    commodity,
    year,
    month::INTEGER
ORDER BY
    commodity,
    year,
    month::INTEGER;


-- =====================================================
-- BAGIAN 08: PEMERIKSAAN TAMBAHAN
-- =====================================================

-- Memeriksa nama kolom dan tipe data
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'food_prices'
ORDER BY ordinal_position;


-- Memeriksa nilai bulan yang tersimpan
SELECT DISTINCT month
FROM food_prices
ORDER BY month
LIMIT 20;


-- Analisis periode Minyak Goreng Kemasan
SELECT
    year,
    month::INTEGER AS month_num,
    price
FROM food_prices
WHERE commodity = 'Minyak Goreng Kemasan'
  AND (
      (year = 2024 AND month::INTEGER >= 9)
      OR year = 2025
      OR (year = 2023 AND month::INTEGER >= 5)
      OR (year = 2024 AND month::INTEGER <= 1)
  )
ORDER BY year, month::INTEGER;


-- =====================================================
-- AKHIR FILE

