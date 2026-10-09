# Motor Claims Leakage & Loss-Ratio Monitor

An interactive dashboard showing where motor insurance claims money goes and where it leaks.

**[View the live dashboard](https://YOUR-USERNAME.github.io/motor-claims-dashboard/)**

## What it answers
- Which regions run the highest loss ratio?
- Which claim causes carry the most suspected fraud?
- How much paid loss is tied to suspected-fraud claims (leakage)?
- Does late reporting predict fraud flags?

## Key findings
- Theft claims have the highest suspected-fraud rate (16.1%)
- Claims reported more than 6 days late are flagged 1.8x as often as prompt ones
- Suspected-fraud claims make up 13.1% of paid losses (about $2.5M)

## Dashboard features
- Filters by region and cause of loss
- KPI cards: claims, paid, loss ratio, days to settle, fraud rate, fraud leakage
- Four charts: quarterly paid vs loss ratio, loss ratio by region, paid by cause, fraud rate by cause

## Data
6,000 claims, 6 regions, 12 quarters (2023-2025). **The dataset is synthetic**, modelled on a standard vehicle-insurance claims schema, created for demonstration. Loss ratio = claims paid / earned premium.

| File | Purpose |
|---|---|
| `index.html` | The dashboard (open in a browser) |
| `claims_data.csv` | Claim-level data |
| `premiums.csv` | Earned premium by region and quarter |
| `build_dashboard.py` | Generates the data and rebuilds the dashboard |
| `template.html` | Dashboard template used by the script |

## Run it yourself
```
pip install -r requirements.txt
python build_dashboard.py
```
To use real data, replace the GENERATE block in `build_dashboard.py` with `pd.read_csv(...)` and map your columns.

## Tools
Python (pandas, numpy), JavaScript, Chart.js, HTML/CSS
