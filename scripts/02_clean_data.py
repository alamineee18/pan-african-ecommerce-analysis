"""
Clean and profile the raw pan-African e-commerce orders dataset.

Demonstrates typical junior data-analyst cleaning tasks:
- duplicate removal
- category text standardization
- invalid value handling (negative/zero quantity & price)
- missing-value treatment
- country name standardization
- type casting / date parsing
- derived columns for analysis (month, is_weekend, order_value_band)

Run: python 02_clean_data.py
Output: ../data/orders_clean.csv + prints a data-quality summary
"""

import pandas as pd
import numpy as np

RAW_PATH = "/home/claude/ecommerce_project/data/orders_raw.csv"
CLEAN_PATH = "/home/claude/ecommerce_project/data/orders_clean.csv"

df = pd.read_csv(RAW_PATH)
n_start = len(df)

report = []

# --- 1. Duplicates --------------------------------------------------------
n_dupes = df.duplicated().sum()
df = df.drop_duplicates()
report.append(f"Removed {n_dupes} exact duplicate rows")

# --- 2. Standardize category text ----------------------------------------
category_map = {
    "phones & tablets": "Phones & Tablets",
    "Phones and Tablets": "Phones & Tablets",
    "PHONES & TABLETS": "Phones & Tablets",
    "beauty & personal care": "Beauty & Personal Care",
    "Beauty and Personal Care": "Beauty & Personal Care",
}
before = df["category"].nunique()
df["category"] = df["category"].replace(category_map)
after = df["category"].nunique()
report.append(f"Standardized category labels: {before} -> {after} unique values")

# --- 3. Standardize country text -----------------------------------------
df["country"] = df["country"].str.strip().str.title()
report.append("Trimmed/title-cased country names (fixed stray whitespace/case)")

# --- 4. Fix invalid quantity / price ---------------------------------------
n_bad_qty = (df["quantity"] <= 0).sum()
n_bad_price = (df["unit_price_usd"] <= 0).sum()
df.loc[df["quantity"] <= 0, "quantity"] = np.nan
df.loc[df["unit_price_usd"] <= 0, "unit_price_usd"] = np.nan
report.append(f"Flagged {n_bad_qty} invalid quantities and {n_bad_price} invalid unit prices as missing")

# recompute amounts for rows where price/qty were invalid but amount wasn't dropped
# (keep net_amount_usd as source of truth where it's valid; drop rows unusable for revenue analysis)
n_unusable = df[df["quantity"].isna() | df["unit_price_usd"].isna()].shape[0]
df = df.dropna(subset=["quantity", "unit_price_usd"])
report.append(f"Dropped {n_unusable} rows with unusable quantity/price for revenue analysis")

# --- 5. Missing value treatment -------------------------------------------
df["discount_pct"] = df["discount_pct"].fillna(0)
df["payment_method"] = df["payment_method"].fillna("Unknown")
df["delivery_days"] = df["delivery_days"].fillna(df["delivery_days"].median())
# customer_rating: legitimately missing (not all customers rate) -> keep NaN, don't impute
report.append("Filled missing discount_pct with 0, payment_method with 'Unknown', "
              "delivery_days with median; left customer_rating as NaN (not everyone rates)")

# --- 6. Types ---------------------------------------------------------------
df["order_date"] = pd.to_datetime(df["order_date"])
df["quantity"] = df["quantity"].astype(int)

# --- 7. Derived columns for analysis ---------------------------------------
df["order_month"] = df["order_date"].dt.to_period("M").astype(str)
df["order_weekday"] = df["order_date"].dt.day_name()
df["is_weekend"] = df["order_date"].dt.weekday >= 5

def value_band(x):
    if x < 10:
        return "Under $10"
    elif x < 50:
        return "$10-$49"
    elif x < 200:
        return "$50-$199"
    else:
        return "$200+"

df["order_value_band"] = df["net_amount_usd"].apply(value_band)

# --- Save --------------------------------------------------------------
df.to_csv(CLEAN_PATH, index=False)

print("=== DATA CLEANING SUMMARY ===")
print(f"Rows before: {n_start:,} | Rows after: {len(df):,}")
for line in report:
    print(f" - {line}")

print("\n=== QUICK PROFILE ===")
print(df[["net_amount_usd", "quantity", "delivery_days"]].describe().round(2))
print("\nOrders by country:")
print(df["country"].value_counts())
print("\nOrders by category:")
print(df["category"].value_counts())
print(f"\nDate range: {df['order_date'].min().date()} to {df['order_date'].max().date()}")
print(f"Unique customers: {df['customer_id'].nunique():,}")
