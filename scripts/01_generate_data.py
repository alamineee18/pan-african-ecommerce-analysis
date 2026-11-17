"""
Generate a realistic SIMULATED pan-African e-commerce orders dataset.

This is synthetic data, not scraped or real transactional data (no clean
free dataset like this exists publicly for African e-commerce). It is
modeled on publicly reported, real-world patterns so the structure and
relationships are realistic and defensible in an interview:
  - Jumia operates across Nigeria, Kenya, Uganda, Ghana, Egypt (and others);
    Nigeria ~26% of African e-commerce revenue, Kenya/Egypt/Morocco fast-growing
    secondary markets (Market Data Forecast 2026 / Lengow).
  - Phones/electronics and beauty products dominate orders in East Africa,
    especially outside major cities (Nairametrics, 2023, citing Jumia data).
  - Mobile money (JumiaPay-style) is a major payment method alongside
    cash-on-delivery and cards.

Run: python 01_generate_data.py
Output: ../data/orders_raw.csv (with intentional messiness for cleaning practice)
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

rng = np.random.default_rng(42)
random.seed(42)

N_ORDERS = 18000
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 12, 31)
DAYS = (END_DATE - START_DATE).days

# ---- Reference dimensions ----------------------------------------------

countries = {
    # country: (relative order-volume weight, currency, avg FX to USD for context)
    "Nigeria":  (0.34, "NGN"),
    "Kenya":    (0.18, "KES"),
    "Egypt":    (0.16, "EGP"),
    "Uganda":   (0.10, "UGX"),
    "Ghana":    (0.12, "GHS"),
    "Morocco":  (0.10, "MAD"),
}
country_names = list(countries.keys())
country_weights = np.array([v[0] for v in countries.values()])
country_weights = country_weights / country_weights.sum()

categories = {
    # category: (weight, min_price_usd, max_price_usd, return_rate)
    "Phones & Tablets":   (0.22, 40, 900, 0.04),
    "Electronics":        (0.14, 15, 600, 0.05),
    "Fashion":            (0.20, 5, 120, 0.09),
    "Beauty & Personal Care": (0.16, 3, 60, 0.03),
    "Home & Living":      (0.10, 8, 250, 0.05),
    "Groceries & FMCG":   (0.08, 2, 40, 0.01),
    "Sporting Goods":     (0.05, 10, 150, 0.03),
    "Baby Products":      (0.05, 4, 80, 0.02),
}
cat_names = list(categories.keys())
cat_weights = np.array([v[0] for v in categories.values()])
cat_weights = cat_weights / cat_weights.sum()

payment_methods = ["Mobile Money", "Cash on Delivery", "Card", "Bank Transfer"]
payment_weights = [0.42, 0.33, 0.18, 0.07]

device_types = ["Mobile App", "Mobile Web", "Desktop Web"]
device_weights = [0.58, 0.30, 0.12]

delivery_status_options = ["Delivered", "Delivered", "Delivered", "Delivered",
                            "Cancelled", "Returned", "Delivered Late"]

customer_segments = ["New", "Returning"]

# ---- Build customers (so repeat-purchase patterns are realistic) -------

N_CUSTOMERS = int(N_ORDERS * 0.62)  # fewer customers than orders -> repeat buyers
customer_ids = [f"CUST-{i:06d}" for i in range(1, N_CUSTOMERS + 1)]
customer_country = rng.choice(country_names, size=N_CUSTOMERS, p=country_weights)

# give some customers a higher propensity to re-order (power law-ish)
customer_weight = rng.pareto(a=2.0, size=N_CUSTOMERS) + 1

rows = []
order_id_counter = 1

for _ in range(N_ORDERS):
    cust_idx = rng.choice(N_CUSTOMERS, p=customer_weight / customer_weight.sum())
    customer_id = customer_ids[cust_idx]
    country = customer_country[cust_idx]

    # order date with mild seasonality: Black Friday (Nov) + Dec holiday spike
    day_offset = int(rng.triangular(0, DAYS * 0.85, DAYS))
    order_date = START_DATE + timedelta(days=day_offset)
    if order_date.month == 11 and order_date.day >= 20:
        if rng.random() < 0.4:
            order_date = order_date  # keep, already in spike window
    # boost Nov/Dec density by occasionally resampling into that window
    if rng.random() < 0.18:
        order_date = datetime(2025, random.choice([11, 12]), random.randint(1, 28))

    category = rng.choice(cat_names, p=cat_weights)
    cat_meta = categories[category]
    unit_price = round(rng.uniform(cat_meta[1], cat_meta[2]), 2)
    quantity = int(rng.choice([1, 1, 1, 2, 2, 3], p=[0.55, 0.0001, 0.0001, 0.25, 0.0001, 0.0001] if False else None)) if False else int(rng.choice([1, 2, 3], p=[0.72, 0.21, 0.07]))

    discount_pct = round(rng.choice([0, 0, 0, 0.05, 0.10, 0.15, 0.20, 0.30],
                                     p=[0.45, 0.001, 0.049, 0.15, 0.15, 0.10, 0.07, 0.03]), 2)
    gross_amount = round(unit_price * quantity, 2)
    discount_amount = round(gross_amount * discount_pct, 2)
    net_amount = round(gross_amount - discount_amount, 2)

    payment = rng.choice(payment_methods, p=payment_weights)
    device = rng.choice(device_types, p=device_weights)

    status = rng.choice(delivery_status_options)
    if status == "Returned" and rng.random() > cat_meta[3] * 5:
        status = "Delivered"  # keep return rate roughly category-appropriate

    delivery_days = max(1, int(rng.normal(4, 2.2)))

    rating = None
    if status == "Delivered" or status == "Delivered Late":
        if rng.random() < 0.65:  # not everyone rates
            base = 4.2 if status == "Delivered" else 3.3
            rating = int(np.clip(round(rng.normal(base, 0.9)), 1, 5))

    is_new_customer = "New" if rng.random() < 0.38 else "Returning"

    rows.append({
        "order_id": f"ORD-{order_id_counter:07d}",
        "order_date": order_date.strftime("%Y-%m-%d"),
        "customer_id": customer_id,
        "customer_segment": is_new_customer,
        "country": country,
        "category": category,
        "unit_price_usd": unit_price,
        "quantity": quantity,
        "gross_amount_usd": gross_amount,
        "discount_pct": discount_pct,
        "discount_amount_usd": discount_amount,
        "net_amount_usd": net_amount,
        "payment_method": payment,
        "device_type": device,
        "delivery_status": status,
        "delivery_days": delivery_days,
        "customer_rating": rating,
    })
    order_id_counter += 1

df = pd.DataFrame(rows)

# ---- Inject realistic messiness for the cleaning step -------------------

# 1. Some duplicate rows
dupes = df.sample(frac=0.01, random_state=1)
df = pd.concat([df, dupes], ignore_index=True)

# 2. Inconsistent category casing/typos
typo_map = {
    "Phones & Tablets": ["phones & tablets", "Phones and Tablets", "PHONES & TABLETS"],
    "Beauty & Personal Care": ["beauty & personal care", "Beauty and Personal Care"],
}
for correct, variants in typo_map.items():
    mask = df["category"] == correct
    idx = df[mask].sample(frac=0.08, random_state=2).index
    df.loc[idx, "category"] = [random.choice(variants) for _ in idx]

# 3. Missing values scattered
for col, frac in [("customer_rating", 0.0), ("discount_pct", 0.01),
                   ("delivery_days", 0.015), ("payment_method", 0.01)]:
    if frac > 0:
        idx = df.sample(frac=frac, random_state=3).index
        df.loc[idx, col] = np.nan

# 4. A few negative/zero quantity or price glitches (data entry errors)
glitch_idx = df.sample(n=25, random_state=4).index
df.loc[glitch_idx[:12], "quantity"] = -1
df.loc[glitch_idx[12:], "unit_price_usd"] = 0

# 5. Country name inconsistency
df.loc[df.sample(frac=0.005, random_state=5).index, "country"] = "nigeria "

df = df.sample(frac=1, random_state=7).reset_index(drop=True)  # shuffle

out_path = "/home/claude/ecommerce_project/data/orders_raw.csv"
df.to_csv(out_path, index=False)
print(f"Wrote {len(df):,} rows to {out_path}")
print(df.head(3).to_string())
