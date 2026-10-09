"""Motor Claims Leakage & Loss-Ratio Monitor - data generation + dashboard build.
Run: python build_dashboard.py   (needs pandas, numpy)
To use real data (e.g. a Kaggle vehicle-insurance-claims file), replace the
'GENERATE' block with pd.read_csv() and map columns to: quarter, region, cause,
vehicle, amount_paid, days_to_settle, report_delay_days, suspected_fraud."""
import numpy as np, pandas as pd, json, os
OUT = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(42)

# ---------- GENERATE ----------
Q = [f"{y}-Q{q}" for y in (2023, 2024, 2025) for q in (1, 2, 3, 4)]
R = {'Harare': 1.0, 'Bulawayo': .55, 'Mutare': .25, 'Gweru': .2, 'Masvingo': .15, 'Gwanda': .08}
C = ['Collision', 'Theft', 'Weather', 'Windscreen', 'Fire']
V = ['Sedan', 'Pickup', 'SUV', 'Commercial', 'Motorcycle']
MEAN = {'Collision': 2800, 'Theft': 6500, 'Weather': 1500, 'Windscreen': 350, 'Fire': 5200}
N = 6000
qi = rng.choice(12, N, p=np.linspace(.6, 1.4, 12) / np.linspace(.6, 1.4, 12).sum())
ri = rng.choice(len(R), N, p=np.array(list(R.values())) / sum(R.values()))
base = np.array([.5, .14, .12, .18, .06])
ci = np.array([rng.choice(5, p=(base * np.where((np.arange(5) == 1) & (r == 0), 1.5, 1)) /
               (base * np.where((np.arange(5) == 1) & (r == 0), 1.5, 1)).sum()) for r in ri])
cause = np.array(C)[ci]
delay = rng.exponential(3.5, N).round().astype(int)
p_f = .03 + (cause == 'Theft') * .12 + (cause == 'Collision') * .03 + (ri == 0) * .02 + (delay > 6) * .06
fraud = rng.random(N) < p_f
amount = np.array([MEAN[c] for c in cause]) * rng.lognormal(0, .5, N) * np.where(fraud, 1.35, 1)
paid = (amount * rng.uniform(.8, 1, N)).round(0)
days = (rng.gamma(2.5, 6, N) * np.where(cause == 'Theft', 1.6, 1) * np.where(ri >= 3, 1.3, 1)).round().astype(int) + 2
df = pd.DataFrame({'claim_id': [f"CLM{100000+i}" for i in range(N)], 'quarter': np.array(Q)[qi],
                   'region': np.array(list(R))[ri], 'cause': cause, 'vehicle': rng.choice(V, N, p=[.35, .25, .2, .15, .05]),
                   'amount_paid': paid, 'days_to_settle': days, 'report_delay_days': delay,
                   'suspected_fraud': fraud.astype(int)}).sort_values(['quarter', 'claim_id'])
g = df.groupby(['quarter', 'region'])['amount_paid'].sum().reset_index()
lr = rng.uniform(.58, .82, len(g)) + g.region.map({'Harare': .05, 'Gwanda': .08}).fillna(0)
g['earned_premium'] = (g.amount_paid / lr).round(0)
df.to_csv(f"{OUT}/claims_data.csv", index=False)
g[['quarter', 'region', 'earned_premium']].to_csv(f"{OUT}/premiums.csv", index=False)

# ---------- AGGREGATE ----------
rl, qx, cx = list(R), {q: i for i, q in enumerate(Q)}, {c: i for i, c in enumerate(C)}
d2 = df.assign(fp=df.amount_paid * df.suspected_fraud)
A = d2.groupby(['quarter', 'region', 'cause']).agg(n=('claim_id', 'count'), paid=('amount_paid', 'sum'),
        fn=('suspected_fraud', 'sum'), fp=('fp', 'sum'), d=('days_to_settle', 'sum')).reset_index()
A = [[qx[r.quarter], rl.index(r.region), cx[r.cause], int(r.n), int(r.paid), int(r.fn), int(r.fp), int(r.d)] for r in A.itertuples()]
P = [[qx[r.quarter], rl.index(r.region), int(r.earned_premium)] for r in g.itertuples()]

# ---------- INSIGHTS ----------
rlr = (df.groupby('region').amount_paid.sum() / g.groupby('region').earned_premium.sum()).sort_values(ascending=False)
fc = df.groupby('cause').suspected_fraud.mean().sort_values(ascending=False)
late = df.assign(l=df.report_delay_days > 6).groupby('l').suspected_fraud.mean()
leak = (df.amount_paid * df.suspected_fraud).sum()
ins = [f"<b>{rlr.index[0]}</b> runs the highest loss ratio at {rlr.iloc[0]:.0%}; {rlr.index[-1]} the lowest at {rlr.iloc[-1]:.0%}.",
       f"<b>{fc.index[0]}</b> claims carry the highest suspected-fraud rate ({fc.iloc[0]:.1%}), versus {fc.iloc[-1]:.1%} for {fc.index[-1]}.",
       f"Claims reported more than 6 days after the loss are flagged <b>{late[True]/late[False]:.1f}x</b> as often as prompt ones.",
       f"Suspected-fraud claims account for <b>${leak:,.0f}</b> of paid losses ({leak/df.amount_paid.sum():.1%}) - the leakage target for tighter triage."]

html = open(f"{OUT}/template.html").read() if os.path.exists(f"{OUT}/template.html") else None
data = json.dumps({'Q': Q, 'R': rl, 'C': C, 'A': A, 'P': P}, separators=(',', ':'))
if html:
    open(f"{OUT}/index.html", "w").write(html.replace('__DATA__', data).replace('__INSIGHTS__', ''.join(f'<li>{i}</li>' for i in ins)))
print(len(df), "claims;", [i for i in ins])
