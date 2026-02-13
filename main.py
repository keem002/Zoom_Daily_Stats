import requests
import base64
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import gspread
from google.oauth2.service_account import Credentials

ACCOUNT_ID = "-4alyWSvSeay-Iz89zKrpA"
CLIENT_ID = "ECrXUAlnQTevG5hLyuYk0A"
CLIENT_SECRET = "IPOnFCN5JkkqmSH7PsUjThnMFAA6xf62"
MEETING_ID = "7587549734"

# =====================================
# GET ACCESS TOKEN
# =====================================

def get_access_token():
    url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={ACCOUNT_ID}"
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()

    headers = {"Authorization": f"Basic {encoded}"}
    response = requests.post(url, headers=headers)
    data = response.json()

    if "access_token" not in data:
        print("Error getting token:", data)
        exit()

    return data["access_token"]

# =====================================
# GET MEETING INSTANCES
# =====================================

def get_meeting_instances(meeting_id, token):
    url = f"https://api.zoom.us/v2/past_meetings/{meeting_id}/instances"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    data = response.json()

    if "meetings" not in data:
        print("Error fetching instances:", data)
        exit()

    return data["meetings"]

# =====================================
# GET PARTICIPANTS (FILTER BY JOIN TIME)
# =====================================

def get_all_participants_for_date(meeting_id, token, start_utc, end_utc):
    instances = get_meeting_instances(meeting_id, token)
    all_participants = []

    for meeting in instances:
        uuid = meeting["uuid"]

        url = f"https://api.zoom.us/v2/report/meetings/{uuid}/participants?page_size=300"
        headers = {"Authorization": f"Bearer {token}"}

        next_page_token = ""

        while True:
            full_url = f"{url}&next_page_token={next_page_token}"
            response = requests.get(full_url, headers=headers)
            data = response.json()

            if "participants" not in data:
                break

            for p in data["participants"]:
                join_time = datetime.fromisoformat(
                    p["join_time"].replace("Z", "+00:00")
                )

                if start_utc <= join_time < end_utc:
                    all_participants.append(p)

            next_page_token = data.get("next_page_token")
            if not next_page_token:
                break

    return all_participants

# =====================================
# GENERATE REPORT
# =====================================

def generate_report(participants, loop_start_utc):
    report = []

    sections = [
        ("Move", 0, 10),
        ("Breathe", 10, 10),
        ("Meditate", 20, 10),
        ("Meditate Longer", 30, 20),
        ("Journal", 50, 10)
    ]

    for hour in range(24):
        hour_start = loop_start_utc + timedelta(hours=hour)

        for name, offset, duration in sections:
            section_start = hour_start + timedelta(minutes=offset)
            section_end = section_start + timedelta(minutes=duration)

            joined_names = set()
            total_present = set()
            present_till_end = set()

            for p in participants:
                participant_name = p.get("name", "Unknown")

                if participant_name.strip().lower() == "just10 live":
                    continue

                if p.get("host") is True:
                    continue

                join = datetime.fromisoformat(
                    p["join_time"].replace("Z", "+00:00")
                )

                leave = None
                if p.get("leave_time"):
                    leave = datetime.fromisoformat(
                        p["leave_time"].replace("Z", "+00:00")
                    )

                if section_start <= join < section_end:
                    joined_names.add(participant_name)

                if join < section_end and (leave is None or leave > section_start):
                    total_present.add(participant_name)

                if join <= section_end and (leave is None or leave >= section_end):
                    present_till_end.add(participant_name)

            report.append({
                "section": name,
                "time": (
                    f"{section_start.astimezone(ZoneInfo('Asia/Kolkata')).strftime('%Y-%m-%d %I:%M %p')} - "
                    f"{section_end.astimezone(ZoneInfo('Asia/Kolkata')).strftime('%I:%M %p')}"
                ),
                "joined_count": len(joined_names),
                "total_present_count": len(total_present),
                "present_till_end_count": len(present_till_end),
                "joined_names": ", ".join(sorted(joined_names)),
                "total_present_names": ", ".join(sorted(total_present)),
                "present_till_end_names": ", ".join(sorted(present_till_end))
            })

    return report

# =====================================
# ASK USER FOR DATE
# =====================================

ist = ZoneInfo("Asia/Kolkata")
user_input = input("Enter date (YYYY-MM-DD): ")

selected_date = datetime.strptime(user_input, "%Y-%m-%d").replace(tzinfo=ist)

loop_start_ist = selected_date.replace(hour=10, minute=30, second=0, microsecond=0)
loop_end_ist = loop_start_ist + timedelta(hours=24)

loop_start_utc = loop_start_ist.astimezone(timezone.utc)
loop_end_utc = loop_end_ist.astimezone(timezone.utc)

# =====================================
# MAIN
# =====================================

print("Getting access token...")
token = get_access_token()

print("Fetching participants...")
participants = get_all_participants_for_date(
    MEETING_ID,
    token,
    loop_start_utc,
    loop_end_utc
)

print("Generating report...")
report = generate_report(participants, loop_start_utc)

# =====================================
# UPLOAD TO GOOGLE SHEETS
# =====================================

def upload_to_google_sheets(report, selected_date):

    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_file(
        "service_account.json",
        scopes=scope
    )

    client = gspread.authorize(creds)
    spreadsheet = client.open("zoomAnalytics")

    # 👇 Format sheet name like: Tue 10 Feb 2026
    sheet_name = selected_date.strftime("%a %d %b %Y")

    try:
        sheet = spreadsheet.worksheet(sheet_name)
        sheet.clear()
    except:
        sheet = spreadsheet.add_worksheet(
            title=sheet_name,
            rows="500",
            cols="20"
        )

    header = [
        "Section",
        "Time Range (IST)",
        "Joined Count",
        "Total Present During Session",
        "Present Till End Of Session",
        "Joined Names",
        "Total Present Names",
        "Present Till End Names"
    ]

    sheet.append_row(header)

    all_rows = []
    section_counter = 0

    for row in report:
        all_rows.append([
            row["section"],
            row["time"],
            row["joined_count"],
            row["total_present_count"],
            row["present_till_end_count"],
            row["joined_names"],
            row["total_present_names"],
            row["present_till_end_names"]
        ])

        section_counter += 1
        if section_counter % 5 == 0:
            all_rows.append(["", "", "", "", "", "", "", ""])

    sheet.append_rows(all_rows)

    print(f"Uploaded to sheet: {sheet_name}")

    print("Uploaded to Google Sheets successfully.")

upload_to_google_sheets(report, selected_date)

