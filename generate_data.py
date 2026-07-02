import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import date, timedelta
from sqlalchemy import create_engine

fake = Faker()
random.seed(42)
np.random.seed(42)

# ── CONFIG ──────────────────────────────────────────────────────────────────
# Update SERVER to your SQL Server instance name (check SSMS connection dialog)
SERVER   = "localhost"
DATABASE = "BechtelAWP"
ENGINE = create_engine(
    f"mssql+pyodbc://DESKTOP-FKU7PGG/{DATABASE}"
    "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes"
)

DISCIPLINES = ["Civil", "Structural Steel", "Mechanical", "Electrical", "Piping"]
AREAS       = ["Area A", "Area B", "Area C", "Area D", "Turbine Island", "Reactor Building"]
STATUSES    = ["Not Started", "In Progress", "Complete"]
COMPLIANCE  = ["Compliant", "Non-Compliant", "Partial"]

PROJECT_START = date(2024, 1, 1)
PROJECT_END   = date(2025, 6, 30)

# ── 1. CONTRACTORS (20 rows) ─────────────────────────────────────────────────
contractors = []
for i in range(1, 21):
    contractors.append({
        "contractor_id":    i,
        "name":             fake.company(),
        "discipline":       random.choice(DISCIPLINES),
        "compliance_status": random.choice(COMPLIANCE),
    })
df_contractors = pd.DataFrame(contractors)


# ── 2. WORK PACKAGES (600 rows) ──────────────────────────────────────────────
def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

work_packages = []
for i in range(1, 601):
    discipline  = random.choice(DISCIPLINES)
    planned_qty = round(random.uniform(10, 500), 1)
    status      = random.choice(STATUSES)

    planned_start  = random_date(PROJECT_START, date(2025, 1, 1))
    planned_finish = planned_start + timedelta(days=random.randint(7, 120))

    # Actual dates only make sense if work has started
    if status in ["In Progress", "Complete"]:
        actual_start  = planned_start + timedelta(days=random.randint(-5, 15))
        actual_finish = planned_finish + timedelta(days=random.randint(-10, 30)) \
                        if status == "Complete" else None
    else:
        actual_start  = None
        actual_finish = None

    # Actual qty depends on status
    if status == "Complete":
        actual_qty = round(planned_qty * random.uniform(0.9, 1.05), 1)
    elif status == "In Progress":
        actual_qty = round(planned_qty * random.uniform(0.1, 0.85), 1)
    else:
        actual_qty = 0.0

    work_packages.append({
        "IWP_ID":        f"IWP-{i:04d}",
        "discipline":    discipline,
        "area":          random.choice(AREAS),
        "planned_qty":   planned_qty,
        "actual_qty":    actual_qty,
        "status":        status,
        "planned_start": planned_start,
        "actual_start":  actual_start,
        "planned_finish": planned_finish,
        "actual_finish": actual_finish,
        "contractor_id": random.randint(1, 20),
    })

df_wp = pd.DataFrame(work_packages)


# ── 3. INJECT BAD DATA (intentional errors for the QA validation queries) ────
# Pick 60 random rows to corrupt
bad_idx = random.sample(range(len(df_wp)), 60)

for idx in bad_idx[:20]:   # actual_qty > planned_qty (over-reporting)
    df_wp.at[idx, "actual_qty"] = round(df_wp.at[idx, "planned_qty"] * random.uniform(1.2, 2.0), 1)

for idx in bad_idx[20:35]: # actual_finish before actual_start (impossible date)
    df_wp.at[idx, "actual_start"]  = date(2024, 6, 1)
    df_wp.at[idx, "actual_finish"] = date(2024, 3, 1)

for idx in bad_idx[35:50]: # planned_finish in the future but status = "Complete" (mismatch)
    df_wp.at[idx, "planned_finish"] = date(2026, 12, 31)
    df_wp.at[idx, "status"]         = "Complete"

for idx in bad_idx[50:60]: # null planned_start (missing critical field)
    df_wp.at[idx, "planned_start"] = None


# ── 4. DAILY PROGRESS (800 rows) ─────────────────────────────────────────────
daily_progress = []
started_iwps = df_wp[df_wp["status"].isin(["In Progress", "Complete"])]["IWP_ID"].tolist()

for i in range(1, 801):
    iwp_id = random.choice(started_iwps)
    row = df_wp[df_wp["IWP_ID"] == iwp_id].iloc[0]

    progress_date = random_date(
        row["actual_start"] if pd.notna(row["actual_start"]) else PROJECT_START,
        date(2025, 3, 1)
    )
    qty_installed = round(random.uniform(1, 50), 1)

    # Inject bad data into ~10% of daily records
    flag = None
    if random.random() < 0.07:
        qty_installed = None          # missing quantity
        flag = "Missing qty_installed"
    elif random.random() < 0.05:
        progress_date = date(2027, 1, 1)   # future date
        flag = "Future date"
    elif random.random() < 0.04:
        qty_installed = -abs(qty_installed) # negative quantity
        flag = "Negative qty"

    daily_progress.append({
        "record_id":         i,
        "IWP_ID":            iwp_id,
        "progress_date":     progress_date,
        "qty_installed":     qty_installed,
        "reported_by":       fake.name(),
        "data_quality_flag": flag,
    })

df_dp = pd.DataFrame(daily_progress)


# ── 5. LOAD INTO SQL SERVER ───────────────────────────────────────────────────
print("Loading contractors...")
df_contractors.to_sql("contractors", ENGINE, if_exists="append", index=False)

print("Loading work_packages...")
df_wp.to_sql("work_packages", ENGINE, if_exists="append", index=False)

print("Loading daily_progress...")
df_dp.to_sql("daily_progress", ENGINE, if_exists="append", index=False)

print("Done. Rows loaded:")
print(f"  contractors:    {len(df_contractors)}")
print(f"  work_packages:  {len(df_wp)}")
print(f"  daily_progress: {len(df_dp)}")