// POWER QUERY (M) — cleans orders_raw.csv the same way 02_clean_data.py does.
// Use this if you want to show the cleaning step INSIDE Power BI (Power
// Query) rather than importing the already-cleaned CSV. Shows Power Query
// skill alongside DAX.
//
// How to use:
//   Get Data > Text/CSV > select data/orders_raw.csv > Transform Data
//   (opens Power Query Editor) > Home > Advanced Editor > replace
//   everything with this script > Done.

let
    Source = Csv.Document(File.Contents("C:\path\to\orders_raw.csv"),
        [Delimiter=",", Columns=17, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),

    // 1. Remove exact duplicate rows
    RemoveDupes = Table.Distinct(PromoteHeaders),

    // 2. Standardize category text (fix casing/typo variants)
    FixCategory = Table.ReplaceValue(RemoveDupes,
        each [category],
        each
            if Text.Lower(Text.Trim([category])) = "phones & tablets"
                or Text.Lower(Text.Trim([category])) = "phones and tablets"
            then "Phones & Tablets"
            else if Text.Lower(Text.Trim([category])) = "beauty & personal care"
                or Text.Lower(Text.Trim([category])) = "beauty and personal care"
            then "Beauty & Personal Care"
            else [category],
        Replacer.ReplaceValue, {"category"}),

    // 3. Standardize country text (trim + title case)
    FixCountry = Table.TransformColumns(FixCategory,
        {{"country", each Text.Proper(Text.Trim(_)), type text}}),

    // 4. Flag invalid quantity / unit_price as null
    FlagInvalid = Table.ReplaceValue(FixCountry, each [quantity],
            each if [quantity] <= 0 then null else [quantity],
            Replacer.ReplaceValue, {"quantity"}),
    FlagInvalid2 = Table.ReplaceValue(FlagInvalid, each [unit_price_usd],
            each if [unit_price_usd] <= 0 then null else [unit_price_usd],
            Replacer.ReplaceValue, {"unit_price_usd"}),

    // 5. Drop rows that are now unusable for revenue analysis
    DropUnusable = Table.SelectRows(FlagInvalid2,
        each [quantity] <> null and [unit_price_usd] <> null),

    // 6. Fill missing values
    FillDiscount = Table.ReplaceValue(DropUnusable, null, 0, Replacer.ReplaceValue, {"discount_pct"}),
    FillPayment = Table.ReplaceValue(FillDiscount, null, "Unknown", Replacer.ReplaceValue, {"payment_method"}),
    DeliveryMedian = List.Median(List.RemoveNulls(Table.Column(FillPayment, "delivery_days"))),
    FillDelivery = Table.ReplaceValue(FillPayment, null, DeliveryMedian, Replacer.ReplaceValue, {"delivery_days"}),
    // customer_rating is left as null on purpose — not everyone rates.

    // 7. Set types
    SetTypes = Table.TransformColumnTypes(FillDelivery, {
        {"order_date", type date},
        {"quantity", Int64.Type},
        {"unit_price_usd", type number},
        {"gross_amount_usd", type number},
        {"discount_pct", type number},
        {"discount_amount_usd", type number},
        {"net_amount_usd", type number},
        {"delivery_days", type number}
    }),

    // 8. Derived columns for analysis
    AddMonth = Table.AddColumn(SetTypes, "order_month",
        each Date.ToText([order_date], "yyyy-MM"), type text),
    AddWeekday = Table.AddColumn(AddMonth, "order_weekday",
        each Date.DayOfWeekName([order_date]), type text),
    AddWeekend = Table.AddColumn(AddWeekday, "is_weekend",
        each Date.DayOfWeek([order_date], Day.Monday) >= 5, type logical),
    AddBand = Table.AddColumn(AddWeekend, "order_value_band",
        each if [net_amount_usd] < 10 then "Under $10"
             else if [net_amount_usd] < 50 then "$10-$49"
             else if [net_amount_usd] < 200 then "$50-$199"
             else "$200+", type text)

in
    AddBand
