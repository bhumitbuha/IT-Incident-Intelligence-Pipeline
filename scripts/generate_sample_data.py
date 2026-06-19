import csv
import json
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import (
    ASSET_COUNT,
    RAW_ASSETS,
    RAW_DEPARTMENTS,
    RAW_KB,
    RAW_TICKETS,
    RAW_USERS,
    SEED,
    SLA_HOURS,
    TICKET_COUNT,
    USER_COUNT,
)

random.seed(SEED)

DEPARTMENTS = [
    ("D-FIN", "Finance", "Toronto"),
    ("D-HR", "Human Resources", "Toronto"),
    ("D-ENG", "Engineering", "Ottawa"),
    ("D-SAL", "Sales", "Vancouver"),
    ("D-MKT", "Marketing", "Toronto"),
    ("D-OPS", "Operations", "Calgary"),
    ("D-LEG", "Legal", "Montreal"),
    ("D-EXE", "Executive", "Toronto"),
    ("D-SUP", "Supply Chain", "Calgary"),
    ("D-CS", "Customer Success", "Vancouver"),
]

DEVICE_MODELS = [
    ("Dell Latitude 5430", "Laptop", 2022),
    ("Dell Latitude 7420", "Laptop", 2021),
    ("Dell Latitude 3520", "Laptop", 2020),
    ("HP EliteBook 840 G9", "Laptop", 2023),
    ("HP ProBook 450 G8", "Laptop", 2020),
    ("Lenovo ThinkPad T14", "Laptop", 2022),
    ("Lenovo ThinkPad X1 Carbon", "Laptop", 2023),
    ("Microsoft Surface Pro 8", "Tablet", 2022),
    ("Apple MacBook Pro 14", "Laptop", 2023),
    ("Dell OptiPlex 7090", "Desktop", 2021),
    ("HP LaserJet Pro M404", "Printer", 2019),
    ("HP LaserJet Enterprise M507", "Printer", 2020),
    ("Brother MFC-L2750DW", "Printer", 2018),
    ("Cisco IP Phone 8841", "Phone", 2019),
    ("Apple iPhone 13", "Phone", 2022),
]

FIRST_NAMES = [
    "Aarav", "Priya", "Mei", "John", "Sarah", "Liam", "Olivia", "Noah",
    "Emma", "Ethan", "Mia", "Wei", "Fatima", "Mohammed", "Diego", "Sofia",
    "Lucas", "Ava", "Hiroshi", "Yuki", "Kofi", "Adaeze", "Jamal", "Aisha",
    "Bhumit", "Carlos", "Elena", "Ivan", "Nadia", "Raj", "Tomas", "Zara",
]

LAST_NAMES = [
    "Smith", "Patel", "Chen", "Khan", "Garcia", "Brown", "Singh", "Wang",
    "Johnson", "Nguyen", "Davis", "Kumar", "Lopez", "Lee", "Anderson",
    "Miller", "Ali", "Tremblay", "Murphy", "Buha", "Reyes", "Okafor",
    "Petrov", "Schmidt", "Yamamoto",
]

TICKET_TEMPLATES = [
    ("VPN disconnects every {n} minutes when working from home", "vpn"),
    ("Cannot connect to corporate VPN since this morning", "vpn"),
    ("VPN client crashes on launch after recent update", "vpn"),
    ("Wifi keeps dropping in the {floor} floor meeting rooms", "wifi"),
    ("Slow internet access on {model} laptop", "internet"),
    ("Outlook freezes when opening calendar invites", "outlook"),
    ("Cannot send external emails from Outlook", "outlook"),
    ("Outlook search index corrupted - cannot find old emails", "outlook"),
    ("Exchange mailbox at quota - cannot receive new email", "exchange"),
    ("Password reset required - account locked after vacation", "password"),
    ("MFA prompts not arriving on registered phone", "mfa"),
    ("Account locked out after travelling abroad", "locked"),
    ("Teams meeting audio cuts out every few seconds", "teams"),
    ("Cannot share screen in Teams call", "teams"),
    ("Teams chat notifications not appearing on desktop", "teams"),
    ("Zoom installer blocked by endpoint security", "zoom"),
    ("SharePoint site permissions need updating for new hire", "sharepoint"),
    ("OneDrive sync stuck at 0 percent for 3 days", "onedrive"),
    ("Printer on {floor} floor showing offline", "printer"),
    ("Printer keeps jamming on duplex prints", "printer"),
    ("Network scanner not scanning to email", "scanner"),
    ("Second monitor not detected after dock change", "monitor"),
    ("Keyboard keys sticking on {model}", "keyboard"),
    ("Mouse cursor freezing intermittently", "mouse"),
    ("Laptop battery drains in under {n} hours", "battery"),
    ("Laptop will not power on - tested with charger", "laptop"),
    ("Device flagged non-compliant in Intune dashboard", "intune"),
    ("SCCM client failing to receive software updates", "sccm"),
    ("Endpoint missing latest security patch", "patch"),
    ("Windows feature update fails at {n} percent", "update"),
    ("BitLocker recovery key needed after motherboard swap", "bitlocker"),
    ("Antivirus quarantined a legitimate work file", "antivirus"),
    ("Suspected phishing email - please review attached header", "phishing"),
    ("Malware alert from endpoint protection on user device", "malware"),
    ("SAP GUI keeps disconnecting from production server", "sap"),
    ("ServiceNow page very slow to load", "servicenow"),
    ("CRM dashboard widgets not rendering", "crm"),
    ("ERP report exports timing out", "erp"),
]

RESOLUTION_TEMPLATES = {
    "vpn": [
        "Reinstalled VPN client and pushed updated profile via Intune.",
        "Cleared cached VPN credentials and forced re-auth - issue resolved.",
        "Identified ISP routing issue at user location - advised to use mobile hotspot until ISP fix.",
        "Updated split tunnel config and confirmed connectivity restored.",
    ],
    "wifi": [
        "Replaced access point on affected floor and confirmed signal strength.",
        "Migrated user to 5GHz SSID and dropouts stopped.",
        "Removed conflicting wireless profile from laptop and reconnected.",
    ],
    "internet": [
        "Replaced ethernet cable at desk, throughput back to baseline.",
        "Coordinated with network team to bump VLAN priority for user segment.",
        "Identified DNS misconfiguration - applied corporate DNS profile.",
    ],
    "outlook": [
        "Recreated Outlook profile and rebuilt OST cache.",
        "Cleared autocomplete cache and resolved freeze.",
        "Bumped mailbox quota and verified send/receive.",
        "Reset search index via Windows control panel.",
    ],
    "email": [
        "Re-enabled SMTP send permission in Exchange admin center.",
        "Released held messages from quarantine.",
    ],
    "exchange": [
        "Increased mailbox quota and archived older items via retention policy.",
        "Repaired corrupt mailbox folder via Exchange shell.",
    ],
    "password": [
        "Reset password via Active Directory and unlocked account.",
        "Walked user through self-service password reset portal.",
    ],
    "mfa": [
        "Re-registered MFA device in Azure AD and tested sign-in.",
        "Generated temporary access pass while user re-registers token.",
    ],
    "account": [
        "Unlocked account in Active Directory and verified sign-in.",
        "Cleared stale Kerberos tickets and user signed in successfully.",
    ],
    "locked": [
        "Unlocked account in Active Directory and verified sign-in.",
        "Reviewed sign-in logs - no compromise indicators - account unlocked.",
    ],
    "teams": [
        "Cleared Teams cache folder and reinstalled client.",
        "Switched user to new Teams client and notifications work.",
        "Updated audio driver and reset Teams device settings.",
    ],
    "zoom": [
        "Approved Zoom installer via endpoint security exception.",
        "Pushed Zoom MSI via Intune and confirmed launch.",
    ],
    "sharepoint": [
        "Granted contribute permission on requested SharePoint library.",
        "Removed legacy group membership causing access conflict.",
    ],
    "onedrive": [
        "Unlinked and relinked OneDrive client - sync completed overnight.",
        "Cleared stuck file lock and resumed sync.",
    ],
    "printer": [
        "Replaced fuser unit and ran calibration - printer back in service.",
        "Reinstalled print driver and shared queue from print server.",
        "Cleared jam path and serviced rollers - duplex working.",
    ],
    "scanner": [
        "Updated scan-to-email SMTP settings on device.",
        "Replaced ADF roller and recalibrated scanner.",
    ],
    "monitor": [
        "Replaced dock and confirmed dual monitor detection.",
        "Updated graphics driver and adjusted display profile.",
    ],
    "keyboard": [
        "Replaced keyboard under warranty - shipped to user.",
        "Cleaned debris from affected keys, restored function.",
    ],
    "mouse": [
        "Replaced mouse with spare from stock.",
        "Updated mouse driver and disabled enhanced pointer precision.",
    ],
    "battery": [
        "Replaced battery under warranty and tested runtime.",
        "Ran battery diagnostic - flagged for replacement.",
    ],
    "laptop": [
        "Sent device for depot repair - motherboard replaced.",
        "Reseated RAM and battery - laptop boots normally.",
    ],
    "intune": [
        "Forced compliance check-in and remediated missing baseline.",
        "Reassigned device to correct compliance policy group.",
    ],
    "sccm": [
        "Repaired SCCM client and triggered machine policy refresh.",
        "Reinstalled CCM client - updates now receiving.",
    ],
    "compliance": [
        "Applied missing security baseline and verified compliance.",
    ],
    "patch": [
        "Forced patch deployment via SCCM and verified KB installed.",
    ],
    "update": [
        "Cleared software distribution cache and rerun update.",
        "Used media creation tool to repair feature update.",
    ],
    "bitlocker": [
        "Retrieved BitLocker recovery key from Azure AD and unlocked drive.",
    ],
    "antivirus": [
        "Restored file from quarantine and added allowlist exception.",
    ],
    "phishing": [
        "Confirmed phishing - removed from all mailboxes via Defender.",
        "Reported to security team - user re-trained.",
    ],
    "malware": [
        "Isolated device, ran full scan, no persistence found - returned to user.",
    ],
    "sap": [
        "Updated SAP GUI to latest patch level and reconnected.",
    ],
    "servicenow": [
        "Cleared browser cache and tested in incognito - page loads.",
    ],
    "crm": [
        "Disabled conflicting browser extension and widgets render.",
    ],
    "erp": [
        "Optimized report query with DBA team and exports complete.",
    ],
}

KB_ARTICLES = [
    {
        "kb_id": "KB0001",
        "title": "Resetting your corporate password",
        "category": "Access",
        "keywords": ["password", "reset", "locked"],
        "body": "Use the self-service password portal at sspr.company.local. If MFA is unavailable, contact the service desk.",
    },
    {
        "kb_id": "KB0002",
        "title": "Reconnecting the corporate VPN",
        "category": "Network",
        "keywords": ["vpn", "internet"],
        "body": "Disconnect the VPN client, clear cached credentials, and reconnect using your network password.",
    },
    {
        "kb_id": "KB0003",
        "title": "Rebuilding Outlook OST cache",
        "category": "Email",
        "keywords": ["outlook", "email", "exchange"],
        "body": "Close Outlook, delete the OST file at the listed path, then relaunch Outlook to rebuild cache.",
    },
    {
        "kb_id": "KB0004",
        "title": "Reinstalling Microsoft Teams",
        "category": "Collaboration",
        "keywords": ["teams"],
        "body": "Uninstall Teams classic, clear AppData cache, then install the new Teams via Company Portal.",
    },
    {
        "kb_id": "KB0005",
        "title": "Removing a stuck print job",
        "category": "Hardware",
        "keywords": ["printer"],
        "body": "Stop the print spooler service, clear the spool folder, then restart the spooler service.",
    },
    {
        "kb_id": "KB0006",
        "title": "Recovering BitLocker keys from Azure AD",
        "category": "Security",
        "keywords": ["bitlocker"],
        "body": "Sign in to the device portal in Azure AD and copy the recovery key for the affected device.",
    },
    {
        "kb_id": "KB0007",
        "title": "Forcing an Intune compliance check-in",
        "category": "Endpoint",
        "keywords": ["intune", "compliance"],
        "body": "Open Company Portal, select the device, then trigger Check status to force a compliance refresh.",
    },
    {
        "kb_id": "KB0008",
        "title": "Reporting a suspected phishing email",
        "category": "Security",
        "keywords": ["phishing"],
        "body": "Use the Report Phish button in Outlook. Do not click any links in the suspect message.",
    },
]


def write_departments():
    RAW_DEPARTMENTS.parent.mkdir(parents=True, exist_ok=True)
    with RAW_DEPARTMENTS.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["dept_id", "dept_name", "location"])
        for row in DEPARTMENTS:
            writer.writerow(row)


def make_users():
    users = []
    for i in range(1, USER_COUNT + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        dept = random.choice(DEPARTMENTS)
        email = f"{first.lower()}.{last.lower()}{i}@company.local"
        users.append(
            {
                "user_id": f"U{i:04d}",
                "full_name": f"{first} {last}",
                "email": email,
                "dept_id": dept[0],
            }
        )
    if random.random() < 1.0:
        dup = dict(users[0])
        dup["email"] = dup["email"].upper()
        users.append(dup)
    users.append({"user_id": "U9999", "full_name": "", "email": "", "dept_id": ""})
    return users


def write_users(users):
    with RAW_USERS.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["user_id", "full_name", "email", "dept_id"])
        writer.writeheader()
        writer.writerows(users)


def make_assets(users):
    assets = []
    active_users = [u for u in users if u["user_id"] != "U9999" and u["full_name"]]
    for i in range(1, ASSET_COUNT + 1):
        model, kind, model_year = random.choice(DEVICE_MODELS)
        purchase = datetime(model_year, random.randint(1, 12), random.randint(1, 28))
        warranty_end = purchase + timedelta(days=365 * random.choice([3, 3, 4, 5]))
        owner = random.choice(active_users) if random.random() > 0.05 else {"user_id": ""}
        compliance = random.choices(
            ["Compliant", "Non-compliant", "Unknown"], weights=[80, 15, 5]
        )[0]
        assets.append(
            {
                "asset_id": f"A{i:04d}",
                "asset_tag": f"AST-{1000 + i}",
                "model": model,
                "asset_type": kind,
                "purchase_date": purchase.strftime("%Y-%m-%d"),
                "warranty_end": warranty_end.strftime("%Y-%m-%d"),
                "assigned_user_id": owner["user_id"],
                "compliance_status": compliance,
            }
        )
    assets.append(dict(assets[0]))
    return assets


def write_assets(assets):
    with RAW_ASSETS.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "asset_id",
                "asset_tag",
                "model",
                "asset_type",
                "purchase_date",
                "warranty_end",
                "assigned_user_id",
                "compliance_status",
            ],
        )
        writer.writeheader()
        writer.writerows(assets)


def pick_priority():
    return random.choices(
        ["Critical", "High", "Medium", "Low"], weights=[5, 20, 55, 20]
    )[0]


def resolution_hours(priority):
    base = SLA_HOURS[priority]
    breach_chance = {"Critical": 0.25, "High": 0.18, "Medium": 0.12, "Low": 0.08}[priority]
    if random.random() < breach_chance:
        return round(base * random.uniform(1.2, 3.0), 2)
    return round(base * random.uniform(0.1, 0.95), 2)


def make_tickets(users, assets):
    tickets = []
    active_users = [u for u in users if u["user_id"] != "U9999" and u["full_name"]]
    laptop_assets = [a for a in assets if a["asset_type"] in ("Laptop", "Desktop", "Tablet")]
    start = datetime(2025, 10, 1)
    for i in range(1, TICKET_COUNT + 1):
        template, kw = random.choice(TICKET_TEMPLATES)
        user = random.choice(active_users)
        priority = pick_priority()
        opened = start + timedelta(
            days=random.randint(0, 240),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        rhours = resolution_hours(priority)
        closed = opened + timedelta(hours=rhours)
        status = random.choices(["Closed", "Resolved", "Open"], weights=[80, 15, 5])[0]
        if status == "Open":
            closed_str = ""
            rhours_val = ""
            resolution = ""
        else:
            closed_str = closed.strftime("%Y-%m-%d %H:%M:%S")
            rhours_val = rhours
            resolution = random.choice(RESOLUTION_TEMPLATES.get(kw, ["Issue resolved."]))
        description = template.format(
            n=random.choice([2, 5, 10, 15, 30, 45, 60, 80]),
            floor=random.choice(["3rd", "4th", "5th", "ground"]),
            model=random.choice(["Latitude 5430", "EliteBook 840", "ThinkPad T14"]),
        )
        if random.random() < 0.04:
            description = ""
        asset = random.choice(laptop_assets) if random.random() < 0.6 else None
        tickets.append(
            {
                "ticket_id": f"INC{100000 + i}",
                "opened_at": opened.strftime("%Y-%m-%d %H:%M:%S"),
                "closed_at": closed_str,
                "status": status,
                "priority": priority,
                "raw_category": random.choice([kw, kw.upper(), kw.title(), ""]),
                "short_description": description,
                "resolution_notes": resolution,
                "reporter_user_id": user["user_id"],
                "asset_tag": asset["asset_tag"] if asset else "",
                "resolution_hours": rhours_val,
            }
        )
    tickets.append(dict(tickets[0]))
    tickets.append(dict(tickets[5]))
    return tickets


def write_tickets(tickets):
    fields = [
        "ticket_id",
        "opened_at",
        "closed_at",
        "status",
        "priority",
        "raw_category",
        "short_description",
        "resolution_notes",
        "reporter_user_id",
        "asset_tag",
        "resolution_hours",
    ]
    with RAW_TICKETS.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(tickets)


def write_kb():
    with RAW_KB.open("w", encoding="utf-8") as fh:
        json.dump(KB_ARTICLES, fh, indent=2)


def main():
    write_departments()
    users = make_users()
    write_users(users)
    assets = make_assets(users)
    write_assets(assets)
    tickets = make_tickets(users, assets)
    write_tickets(tickets)
    write_kb()
    print(f"Wrote {len(DEPARTMENTS)} departments")
    print(f"Wrote {len(users)} user rows (includes duplicates and blanks)")
    print(f"Wrote {len(assets)} asset rows")
    print(f"Wrote {len(tickets)} ticket rows (includes duplicates and blanks)")
    print(f"Wrote {len(KB_ARTICLES)} KB articles")


if __name__ == "__main__":
    main()
