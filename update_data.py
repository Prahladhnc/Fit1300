# update_data.py
import os
import hashlib
from datetime import datetime
from sqlalchemy import exists
from sqlalchemy.orm import sessionmaker
from models import engine, Activity, Session
from strava_api import fetch_club_activities
from dotenv import load_dotenv

# Load env variables
load_dotenv()
CLUB_ID = os.getenv("STRAVA_CLUB_ID")

# Generate a unique pseudo-ID for summary activities
def generate_activity_id(a):
    s = f"{a['athlete']['firstname']} {a['athlete']['lastname']} {a.get('start_date_local','')} {a.get('distance',0)} {a.get('name','')}"
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)

def update_data():
    session = Session()
    page = 1
    added = 0

    print("Fetching activities from Strava...")

    while True:
        activities = fetch_club_activities(CLUB_ID, per_page=100, page=page)
        if not activities:
            break

        for a in activities:
            act_id = generate_activity_id(a)

            # Skip if already exists
            if session.query(exists().where(Activity.id == act_id)).scalar():
                continue

            athlete_name = a['athlete']['firstname'] + " " + a['athlete']['lastname']

            # Parse start date
            start_date_str = a.get('start_date_local')
            try:
                start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00")) if start_date_str else None
            except Exception:
                start_date = None

            activity = Activity(
                id=act_id,
                athlete_name=athlete_name.strip(),
                distance=a.get('distance', 0),
                moving_time=a.get('moving_time', 0),
                elapsed_time=a.get('elapsed_time', 0),
                total_elevation_gain=a.get('total_elevation_gain', 0),
                type=a.get('sport_type', 'Unknown'),
                start_date=start_date,
                activity_name=a.get('name', '')
            )

            session.add(activity)
            added += 1

        print(f"Processed page {page} with {len(activities)} activities.")
        page += 1

    session.commit()
    session.close()
    print(f"Done! Added {added} new activities to the database.")

if __name__ == "__main__":
    update_data()
