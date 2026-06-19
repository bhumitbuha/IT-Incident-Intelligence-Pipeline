# IT Incident Intelligence Pipeline

A data pipeline and dashboard that turns IT support tickets, endpoint inventory and asset records into insights for reducing repeat incidents.

This is a portfolio project that mirrors the kind of work an IT operations or service desk analyst would do. It takes raw ticket and asset exports, cleans them, blends them with knowledge base content, loads everything into a relational database and surfaces insights through SQL reports and a Streamlit dashboard.

## Why I built this

In most IT environments the same problems show up week after week. VPN drops, password resets, Outlook crashes, printer queues, Intune compliance failures. The data is usually there to spot them, but it sits in three different places. Tickets are in ServiceNow. Assets are in an inventory tool. Knowledge base articles are in SharePoint or Confluence.

The goal of this project is to pull those sources together and answer a small set of questions that actually drive action:

1. Which devices generate the most tickets
2. Which departments need the most support
3. Which issues keep coming back every week
4. Which common issues have no knowledge base article
5. Which assets are old or non-compliant and should be replaced

## What it does

The pipeline runs in four stages.

**Generate** a realistic sample dataset of 1200 tickets, 220 users, 260 assets, 10 departments and a small set of knowledge base articles. The generator deliberately injects duplicate rows, blank fields, mixed-case categories and orphan references so the cleaning logic is doing real work.

**Extract** the raw CSV and JSON files into pandas DataFrames.

**Transform** the data. This step strips whitespace, lower-cases emails, drops duplicates, validates foreign keys, parses dates, extracts keywords from ticket descriptions and resolution notes using a curated keyword dictionary, normalises categories, derives resolution time and flags SLA breaches based on priority.

**Load** the cleaned data into a SQLite database with a proper relational schema, indexes and a reporting view.

On top of the database there are two ways to consume the insights. A command line report that prints every analysis to the terminal, and a Streamlit dashboard with KPIs and charts.

## Tech stack

- Python 3.10 or later
- pandas and numpy for the ETL
- SQLite for the analytical store
- Streamlit and Plotly for the dashboard
- Standard library logging for pipeline traces

There are no external services and no API keys required. Everything runs locally.

## Architecture

```
                +-------------------------+
                |   scripts/generate_*    |
                |   (raw CSV and JSON)    |
                +-----------+-------------+
                            |
                            v
+---------+        +--------+--------+        +----------+
| extract |  --->  |    transform    |  --->  |   load   |
+---------+        +--------+--------+        +----+-----+
                            |                      |
                            v                      v
                  keyword and category       SQLite database
                  enrichment                 (db/incident_intel.db)
                                                  |
                          +----------+------------+
                          |                       |
                          v                       v
                  analysis/insights        dashboard/app.py
                  (CLI reports)            (Streamlit UI)
```

## Project layout

```
.
├── config.py                       Paths, seeds, SLA targets, keyword map
├── requirements.txt
├── run_all.ps1                     One shot helper for Windows PowerShell
├── README.md
├── .gitignore
│
├── scripts/
│   └── generate_sample_data.py     Builds the raw CSV and JSON inputs
│
├── data/
│   ├── raw/                        tickets.csv, assets.csv, users.csv ...
│   └── processed/
│
├── db/
│   ├── schema.sql                  Tables, indexes, v_ticket_full view
│   └── incident_intel.db           Created by the pipeline at runtime
│
├── etl/
│   ├── extract.py
│   ├── transform.py                Cleaning, keyword extraction, SLA flag
│   ├── keywords.py                 Keyword dictionary and matching
│   ├── load.py
│   ├── run_pipeline.py             Orchestrator
│   └── logger.py
│
├── analysis/
│   ├── queries.py                  Raw SQL for each insight
│   └── insights.py                 Callable report functions and CLI dump
│
├── dashboard/
│   └── app.py                      Streamlit UI
│
└── logs/
    └── pipeline.log                Created at runtime
```

## Data model

| Table                | Purpose                                                       |
| -------------------- | ------------------------------------------------------------- |
| `departments`        | Department id, name and location                              |
| `users`              | User id, name, email and department                           |
| `assets`             | Endpoint inventory with model, type, age, warranty and owner  |
| `ticket_categories`  | Normalised category lookup                                    |
| `tickets`            | Cleaned tickets with category, resolution hours and SLA flag  |
| `ticket_keywords`    | Many to many keywords extracted from ticket text              |
| `kb_articles`        | Knowledge base content with category and keyword tags         |
| `kb_keywords`        | Normalised keyword tags per article                           |
| `resolution_metrics` | Pre aggregated metrics by date, category and priority         |

The view `v_ticket_full` joins tickets to their reporter, department, asset and category so you can run ad hoc queries without writing the joins each time.

## Setup

Python 3.10 or later is required. On Windows, install it from python.org and tick the *Add Python to PATH* checkbox during install. The Microsoft Store version is not recommended because it ships as a stub that opens the store instead of running.

Clone the repository and create a virtual environment:

```powershell
git clone https://github.com/bhumitbuha2016/it-incident-intelligence-pipeline.git
cd it-incident-intelligence-pipeline
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On macOS or Linux:

```bash
git clone https://github.com/bhumitbuha2016/it-incident-intelligence-pipeline.git
cd it-incident-intelligence-pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the pipeline

The easiest way on Windows is the helper script:

```powershell
.\run_all.ps1
```

Add `-Dashboard` to also launch the Streamlit UI at the end:

```powershell
.\run_all.ps1 -Dashboard
```

To run each step manually:

```powershell
python scripts/generate_sample_data.py
python -m etl.run_pipeline
python -m analysis.insights
streamlit run dashboard/app.py
```

After the pipeline finishes you should see:

- A new SQLite file at `db/incident_intel.db`
- A log file at `logs/pipeline.log`
- All eight insight reports printed to the terminal
- A Streamlit dashboard at http://localhost:8501

## Insights produced

The dashboard and CLI both expose the same reports.

**Top problem devices.** Ranks asset models by ticket volume, average resolution time and SLA breach count. Useful for spotting a bad batch of hardware or a model that needs a driver fix pushed out.

**Top departments by ticket demand.** Which teams are filing the most tickets and where their resolution time sits compared to SLA. A high count from one team usually signals a tooling gap or training need rather than individual issues.

**Repeating weekly issues.** Keywords like vpn, outlook, printer or intune that show up in multiple ISO weeks of the year. If a keyword appears every week with steady volume, it is a recurring problem worth a permanent fix.

**Knowledge base coverage gaps.** Cross references the most common ticket keywords with the keywords tagged on knowledge base articles. Anything with high ticket volume and no matching article is a documentation gap.

**Assets near end of life.** Lists devices over three years old or flagged as non compliant, ordered by how many tickets they have generated. Used as input to a hardware refresh plan.

**Priority and SLA breakdown.** Average resolution time and breach counts by Critical, High, Medium and Low priority.

**Top reporters.** Users with abnormally high ticket counts. Sometimes this points at a power user with a broken setup. Sometimes it points at a training opportunity.

## Using your own data

The pipeline expects four CSV files and one JSON file in `data/raw/`. The exact column names are documented in `scripts/generate_sample_data.py`. To run the pipeline on real exports:

1. Drop your files into `data/raw/` with the same column names as the generator produces
2. Run `python -m etl.run_pipeline`
3. Refresh the dashboard

The cleaning logic is intentionally tolerant of duplicates, missing values and orphan references so a typical ITSM export should land cleanly.

## Sample insights

The keyword dictionary in `config.py` covers the common ServiceNow ticket categories. A few examples of the kind of finding the pipeline surfaces:

- Repeating VPN tickets concentrated in one location point to an access point or ISP issue
- A spike in Outlook tickets after a Windows update is visible in the daily volume chart
- A printer model with disproportionate ticket counts becomes a candidate for a fleet replacement
- High volume keywords like *bitlocker* or *intune* with no matching KB article highlight documentation work for the service desk team

## What I would add next

- Wire the extract step to a live ServiceNow API instead of CSV exports
- Add a small forecasting model on top of `resolution_metrics` to predict next week's volume per category
- Send a weekly Markdown summary of the insights to a Teams or Slack channel
- Add unit tests for the cleaning rules in `etl/transform.py`

## License

Released under the MIT License. See [LICENSE](LICENSE) for the full text.
