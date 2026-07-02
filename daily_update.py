import pandas as pd
import random
from datetime import date, timedelta
from sqlalchemy import create_engine, text
from faker import Faker

fake = Faker()
random.seed()

ENGINE = create_engine(
    "mssql+pyodbc://DESKTOP-FKU7PGG/BechtelAWP"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes&TrustServerCertificate=yes"
)

def get_active_iwps():
    with ENGINE.connect() as conn:
        result = conn.execute(text(
            "SELECT IWP_ID FROM work_packages WHERE status = 'In Progress'"
        ))
        return [row[0] for row in result]

def get_max_record_id():
    with ENGINE.connect() as conn:
        result = conn.execute(text(
            "SELECT ISNULL(MAX(record_id), 0) FROM daily_progress"
        ))
        return result.scalar()

def generate_daily_records(iwp_ids, start_id):
    records = []
    today = date.today()

    for i, iwp_id in enumerate(random.sample(iwp_ids, min(20, len(iwp_ids)))):
        qty = round(random.uniform(5, 50), 1)
        flag = None

        # Inject ~15% bad data
        r = random.random()
        if r < 0.07:
            qty = None
            flag = "Missing qty_installed"
        elif r < 0.12:
            qty = -abs(qty)
            flag = "Negative qty"

        records.append({
            "record_id":         start_id + i + 1,
            "IWP_ID":            iwp_id,
            "progress_date":     today,
            "qty_installed":     qty,
            "reported_by":       fake.name(),
            "data_quality_flag": flag,
        })
    return records

def run_quality_report(df):
    print("\n===== DAILY DATA QUALITY REPORT =====")
    print(f"Date: {date.today()}")
    print(f"Total records generated: {len(df)}")

    flagged = df[df["data_quality_flag"].notna()]
    clean = df[df["data_quality_flag"].isna()]

    print(f"Clean records:   {len(clean)}")
    print(f"Flagged records: {len(flagged)}")

    if len(flagged) > 0:
        print("\nFlagged records breakdown:")
        print(flagged.groupby("data_quality_flag")["record_id"].count().to_string())
        print("\nFlagged record details:")
        print(flagged[["record_id","IWP_ID","qty_installed","data_quality_flag"]].to_string(index=False))

    # Save flagged records to CSV
    if len(flagged) > 0:
        filename = f"flagged_records_{date.today()}.csv"
        flagged.to_csv(filename, index=False)
        print(f"\nFlagged records saved to: {filename}")

    print("=====================================\n")

def main():
    print("Starting daily progress update...")

    iwp_ids = get_active_iwps()
    if not iwp_ids:
        print("No active work packages found.")
        return
    start_id = get_max_record_id()
    records = generate_daily_records(iwp_ids, start_id)
    df = pd.DataFrame(records)

    # Load into SQL Server
    df.to_sql("daily_progress", ENGINE, if_exists="append", index=False)
    print(f"Inserted {len(records)} new daily progress records.")

    # Run quality report
    run_quality_report(df)
    print("Done. Refresh Power BI to see updated data.")

if __name__ == "__main__":
    main()