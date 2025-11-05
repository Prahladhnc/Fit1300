import os
import csv
import requests
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import func
from models import Session, Activity

load_dotenv()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")
ACCESS_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")
CLUB_ID = os.getenv("STRAVA_CLUB_ID")

CSV_FILE = "status.csv"
ENV_FILE = ".env"


# ---------- TOKEN REFRESH ----------
def refresh_access_token():
    """Refresh Strava access token and update .env"""
    url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token",
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    data = response.json()

    new_access_token = data["access_token"]
    new_refresh_token = data.get("refresh_token", REFRESH_TOKEN)

    # Update .env
    with open(ENV_FILE, "r") as f:
        lines = f.readlines()
    updated = []
    for line in lines:
        if line.startswith("STRAVA_ACCESS_TOKEN="):
            updated.append(f"STRAVA_ACCESS_TOKEN={new_access_token}\n")
        elif line.startswith("STRAVA_REFRESH_TOKEN="):
            updated.append(f"STRAVA_REFRESH_TOKEN={new_refresh_token}\n")
        else:
            updated.append(line)
    if not any(l.startswith("STRAVA_ACCESS_TOKEN=") for l in updated):
        updated.append(f"STRAVA_ACCESS_TOKEN={new_access_token}\n")
    with open(ENV_FILE, "w") as f:
        f.writelines(updated)

    print("🔁 Refreshed access token and updated .env")
    return new_access_token


# ---------- FETCH CLUB INFO ----------
def fetch_member_count(club_id, access_token):
    """Fetch club details to get current member count"""
    url = f"https://www.strava.com/api/v3/clubs/{club_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 401:
        raise PermissionError("Access token invalid or expired")
    response.raise_for_status()
    data = response.json()
    return data.get("member_count", 0)


# ---------- FETCH DB STATS ----------
def fetch_activity_stats():
    """Compute total distances for Runs and Rides from database"""
    session = Session()

    # Get total Run distance
    total_run_m = session.query(func.sum(Activity.distance)).filter(Activity.type == "Run").scalar() or 0
    total_ride_m = session.query(func.sum(Activity.distance)).filter(Activity.type == "Ride").scalar() or 0

    session.close()

    total_run_km = round(total_run_m / 1000, 2)
    total_ride_km = round(total_ride_m / 1000, 2)
    return total_run_km, total_ride_km


# ---------- APPEND TO CSV ----------
def append_to_csv(file_path, timestamp, member_count, total_run_km, total_ride_km):
    file_exists = os.path.exists(file_path)
    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "member_count", "total_run_km", "total_ride_km"])
        writer.writerow([timestamp, member_count, total_run_km, total_ride_km])


# ---------- MAIN ----------
def main():
    global ACCESS_TOKEN
    try:
        member_count = fetch_member_count(CLUB_ID, ACCESS_TOKEN)
    except PermissionError:
        ACCESS_TOKEN = refresh_access_token()
        member_count = fetch_member_count(CLUB_ID, ACCESS_TOKEN)

    total_run_km, total_ride_km = fetch_activity_stats()
    timestamp = datetime.utcnow().isoformat(timespec="seconds")

    append_to_csv(CSV_FILE, timestamp, member_count, total_run_km, total_ride_km)
    print(f"✅ Added entry: {timestamp}")
    print(f"👥 Members: {member_count}")
    print(f"🏃‍♂️ Run distance: {total_run_km} km")
    print(f"🚴‍♀️ Ride distance: {total_ride_km} km")


if __name__ == "__main__":
    main()
