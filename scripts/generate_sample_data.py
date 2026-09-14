"""
Generate synthetic sample datasets in the four input layouts GFLS supports.

Usage:
    python scripts/generate_sample_data.py [output_dir]   (default: sample_data/)

The data is random but seeded, so the files are reproducible. A few values for
2023 are removed on purpose so that year correction, clustering (partial vs.
complete countries) and KNN classification all have something to work on.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "sample_data"
out.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(7)

countries = [
    "Argentina", "Australia", "Brazil", "Canada", "China", "Egypt", "France",
    "Germany", "India", "Indonesia", "Japan", "Kenya", "Mexico", "Nigeria",
    "South Africa", "Spain", "United Kingdom", "United States",
]
# metric -> (low, high, yearly growth)
metrics = {
    "GDP per capita": (2_000, 65_000, 0.03),
    "Population": (5, 1_400, 0.01),
    "Life expectancy": (58, 84, 0.002),
    "CO2 per capita": (0.3, 16, -0.01),
}
years = list(range(2015, 2024))

rows = []
for c in countries:
    for m, (lo, hi, growth) in metrics.items():
        base = rng.uniform(lo, hi)
        for i, y in enumerate(years):
            val = base * (1 + growth) ** i * rng.normal(1, 0.015)
            rows.append({"country": c, "year": y, "metric": m, "value": round(val, 3)})
long_df = pd.DataFrame(rows)

# One missing metric -> KNN candidate, two missing -> insufficient data
drop = [
    ("Kenya", 2023, "CO2 per capita"),
    ("Nigeria", 2023, "Life expectancy"),
    ("Egypt", 2023, "GDP per capita"),
    ("Indonesia", 2023, "Population"),
    ("Argentina", 2023, "CO2 per capita"),
    ("Argentina", 2023, "Life expectancy"),
    ("Spain", 2019, "Population"),
]
for c, y, m in drop:
    long_df = long_df[~((long_df.country == c) & (long_df.year == y) & (long_df.metric == m))]
long_df["source"] = "World Bank (synthetic)"
long_df["assumption"] = None


def save(df, name):
    df.to_csv(out / f"{name}.csv", index=False)
    df.to_excel(out / f"{name}.xlsx", index=False, sheet_name="Sheet1")


# Format 1: long layout, but with non-standard column labels
save(long_df.rename(columns={
    "country": "Nation", "year": "Yr", "metric": "Indicator",
    "value": "Amount", "source": "Data Source", "assumption": "Notes",
}), "format1_long")

# Format 2: one row per country + parameter, years as columns
f2 = long_df.pivot_table(index=["country", "metric"], columns="year", values="value").reset_index()
f2.columns = ["Country", "Parameter"] + [f"Y{i + 1} {y}" for i, y in enumerate(years)]
save(f2, "format2_years_as_columns")

# Format 3: one row per country + year, metrics as columns
f3 = long_df.pivot_table(index=["country", "year"], columns="metric", values="value").reset_index()
f3 = f3.rename(columns={"country": "Country", "year": "Year"})
f3.columns.name = None
save(f3, "format3_metrics_as_columns")

# Format 4: one row per country, "<metric> (<year>)" columns
f4 = long_df[long_df.year >= 2021].copy()
f4["col"] = f4.metric + " (" + f4.year.astype(str) + ")"
f4 = f4.pivot_table(index="country", columns="col", values="value").reset_index()
f4 = f4.rename(columns={"country": "Country"})
f4.columns.name = None
save(f4, "format4_labelled_years")

for p in sorted(out.iterdir()):
    print(f"{p.name:40} {p.stat().st_size:>8} bytes")
