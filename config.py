from pathlib import Path

ROOT = Path(__file__).resolve().parent

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DB_DIR = ROOT / "db"
LOG_DIR = ROOT / "logs"

DB_PATH = DB_DIR / "incident_intel.db"
SCHEMA_PATH = DB_DIR / "schema.sql"

RAW_TICKETS = RAW_DIR / "tickets.csv"
RAW_ASSETS = RAW_DIR / "assets.csv"
RAW_USERS = RAW_DIR / "users.csv"
RAW_DEPARTMENTS = RAW_DIR / "departments.csv"
RAW_KB = RAW_DIR / "kb_articles.json"

SEED = 42

TICKET_COUNT = 1200
USER_COUNT = 220
ASSET_COUNT = 260

SLA_HOURS = {
    "Critical": 4,
    "High": 8,
    "Medium": 24,
    "Low": 72,
}

CATEGORY_MAP = {
    "vpn": "Network",
    "wifi": "Network",
    "internet": "Network",
    "outlook": "Email",
    "email": "Email",
    "exchange": "Email",
    "password": "Access",
    "mfa": "Access",
    "account": "Access",
    "locked": "Access",
    "teams": "Collaboration",
    "zoom": "Collaboration",
    "sharepoint": "Collaboration",
    "onedrive": "Collaboration",
    "printer": "Hardware",
    "scanner": "Hardware",
    "monitor": "Hardware",
    "keyboard": "Hardware",
    "mouse": "Hardware",
    "battery": "Hardware",
    "laptop": "Hardware",
    "intune": "Endpoint",
    "sccm": "Endpoint",
    "compliance": "Endpoint",
    "patch": "Endpoint",
    "update": "Endpoint",
    "bitlocker": "Security",
    "antivirus": "Security",
    "phishing": "Security",
    "malware": "Security",
    "sap": "Application",
    "servicenow": "Application",
    "crm": "Application",
    "erp": "Application",
}
