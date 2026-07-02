# AWP Construction Progress Dashboard

A simulated EPC project automation system built to demonstrate construction 
digital delivery skills relevant to Bechtel's Construction Automation team.

## System Architecture

![AWP Construction Automation Architecture](architecture/awp_architecture_diagram.png)

## Tech Stack
- **SQL Server 2022** — database and data validation queries
- **Python** — data generation and daily automation script
- **Power BI** — 3-page field reporting dashboard

## Project Structure
bechtel-awp-dashboard/
├── generate_data.py        # Generates 1,420 rows of EPC project data
├── daily_update.py         # Daily automation: inserts records + flags bad data
├── sql/
│   ├── 01_data_quality_check.sql
│   ├── 02_progress_by_discipline.sql
│   ├── 03_scurve_data.sql
│   └── 04_contractor_compliance.sql
└── AWP_Dashboard.pbix      # Power BI dashboard (3 pages)

## Dashboard Pages
1. **Discipline KPIs** — actual vs planned quantities with 80% target line
2. **Contractor Compliance** — completion rates and compliance breakdown
3. **Data Quality Log** — flagged work packages and daily progress records

## Key Features
- Simulates AWP field data across 5 disciplines and 20 contractors
- Intentional bad data injection for QA validation demonstration
- Daily automation script generates new records and exports flagged CSV report