# Pan-African E-Commerce Performance Analysis

A self-contained data analyst portfolio project: Python data generation/cleaning →
SQL analysis → interactive dashboard. Built to demonstrate the exact stack most
entry-level data-analyst postings in the African market ask for — **SQL, Python
(pandas), and BI/dashboarding** — end to end on one dataset.

**Live dashboard:** https://alamineee18.github.io/pan-african-ecommerce-analysis/

## About the data

This project uses a **simulated** dataset of 18,180 e-commerce orders across
six African markets (Nigeria, Kenya, Egypt, Ghana, Morocco, Uganda) for 2025.
No clean, free, order-level dataset exists publicly for African e-commerce —
real data of this kind is only available through paid scraping services or
company-internal systems — so the dataset was generated with realistic
distributions and relationships, grounded in publicly reported patterns:

- Jumia's multi-country footprint (Nigeria, Kenya, Uganda, Ghana, Egypt,
  Morocco) and Nigeria's ~26% share of African e-commerce revenue.
- Phones/electronics and beauty products as the dominant order categories,
  consistent with Jumia's own reporting on East African order mix.
- Mobile money, cash-on-delivery, card, and bank transfer as the realistic
  payment-method mix for the region.

The messiness (duplicates, inconsistent category labels, invalid values,
missing fields) was injected deliberately so the project includes a real
cleaning step, not just analysis of a pre-cleaned file. **This is clearly
disclosed as simulated data — not a real company's figures — in the dashboard
itself and should be described the same way in interviews and on a CV/GitHub
listing.** The skills demonstrated (data generation logic aside) are the same
ones used on real transactional data.

## Project structure

```
ecommerce_project/
├── data/
│   ├── orders_raw.csv        # generated, intentionally messy
│   ├── orders_clean.csv      # cleaned, analysis-ready
│   └── ecommerce.db          # SQLite database (table: orders)
├── scripts/
│   ├── 01_generate_data.py   # builds the simulated raw dataset
│   ├── 02_clean_data.py      # cleaning + profiling
│   ├── 03_load_sqlite.py     # loads clean data into SQLite
│   └── 04_run_queries.py     # runs every query, saves results as CSV
├── sql/
│   └── analysis_queries.sql  # 12 business-relevant SQL queries
└── output/                   # query results (CSV), used by the dashboard
```

Reproduce end to end:
```bash
cd scripts
python3 01_generate_data.py
python3 02_clean_data.py
python3 03_load_sqlite.py
python3 04_run_queries.py
```

## Business questions answered

1. Which countries and categories drive the most revenue?
2. How does revenue trend across the year, and is there a seasonal spike?
3. What share of revenue comes from repeat customers?
4. How does delivery performance (speed, cancellations, returns) vary by
   country, and does it affect customer satisfaction?
5. Which payment methods dominate, and does discounting actually lift order
   value?

## Key findings

- **Nigeria is the clear leader**, generating $1.26M of the $3.68M total
  revenue (34%) across 5,254 orders — consistent with its real-world position
  as Africa's largest e-commerce market by GMV share.
- **Phones & Tablets dominates the category mix**: 23% of orders but **57% of
  revenue**, since it carries by far the highest average selling price.
  Electronics is a distant second at 23% of revenue. This concentration means
  phone-category stockouts or price changes move the whole business.
- **Revenue has strong seasonality**: monthly revenue grew steadily from
  ~$22K in January to a **November peak of ~$737K** — a Black-Friday/holiday
  effect roughly double October's revenue — before easing slightly in
  December.
- **Repeat customers matter**: 53.7% of customers placed 2+ orders, and
  returning customers contributed 62% of total orders. Retention, not just
  acquisition, is the bigger revenue lever here.
- **Delivery and satisfaction are consistent across countries**: average
  delivery time (~3.5–3.7 days), late-delivery rate (~13–15%), and cancellation
  rate (~13–15%) are all tightly clustered, and customer ratings don't vary
  much by country (3.96–4.01 average) — delivery issues look operational
  rather than country-specific.
- **Discounting doesn't pay for itself here**: discounted orders actually
  have a *lower* average order value ($223 vs. $255) at the same average
  quantity, suggesting discounts are being applied to inherently
  lower-value items rather than lifting basket size.
- **Mobile money is the leading payment method** (41% of orders), ahead of
  cash-on-delivery (33%) and card (18%) — matching the real shift toward
  cashless payment in African e-commerce (e.g. JumiaPay).

## Recommendations (framed as a business reader would expect)

1. Protect and grow the Phones & Tablets category specifically for Nigeria
   and Kenya (the two largest markets for it) — it is the single biggest
   lever on total revenue.
2. Plan inventory and staffing around the November demand spike well ahead
   of time, rather than treating it as a surprise each year.
3. Shift marketing spend from acquisition discounts toward retention
   (loyalty perks, faster reorder flows) given the already-high 53.7% repeat
   rate and the weak link between discounting and basket size.
4. Investigate delivery/cancellation drivers at the *operational* level
   (courier partners, last-mile logistics) rather than by country, since
   country-level performance is already converging.

## Recreating this in Power BI

The CSVs in `output/` (or a live ODBC connection to `ecommerce.db`) map
directly onto standard Power BI visuals:
- Revenue/orders by country → map or bar chart, `country` field
- Monthly trend → line chart, `order_month` on axis
- Category mix → stacked bar or treemap
- Delivery performance table → matrix visual
- A single Power BI dashboard replicating the CSV-backed dashboard above
  takes about 20–30 minutes once the queries are run, since all the
  aggregation already happened in SQL.

## Limitations

- Data is simulated, not sourced from a real company or platform — it should
  always be described as such.
- Currency is a single USD figure per order rather than converted from each
  country's local currency, to keep the analysis simple.
- No customer demographic data (age, gender, income) was modeled, since no
  reliable public source for that exists at this granularity.
