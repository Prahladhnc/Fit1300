import os
import csv
from datetime import datetime
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
ACCESS_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")
CLUB_ID = os.getenv("STRAVA_CLUB_ID")

CSV_FILE = "member_count.csv"

def fetch_club_member_count(club_id):
    """Fetch club details from Strava API and return member count."""
    url = f"https://www.strava.com/api/v3/clubs/{club_id}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch club: {response.status_code} - {response.text}")

    data = response.json()
    return data.get("member_count", 0)

def append_to_csv(file_path, timestamp, member_count):
    """Append timestamp and member_count to CSV, creating it if needed."""
    file_exists = os.path.exists(file_path)

    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "member_count"])
        writer.writerow([timestamp, member_count])

def main():
    print("🔁 Fetching club member count from Strava...")
    try:
        member_count = fetch_club_member_count(CLUB_ID)
        timestamp = datetime.utcnow().isoformat(timespec="seconds")

        append_to_csv(CSV_FILE, timestamp, member_count)
        print(f"✅ Added entry: {timestamp} → {member_count} members")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
