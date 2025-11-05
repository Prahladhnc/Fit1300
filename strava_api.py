# strava_api.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")

def get_access_token():
    """Exchange refresh token for a new short-lived access token."""
    url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': REFRESH_TOKEN
    }
    res = requests.post(url, data=payload)
    res.raise_for_status()
    return res.json()['access_token']

def fetch_club_activities(club_id, per_page=100, page=1):
    """Fetch recent club activities."""
    access_token = get_access_token()
    url = f"https://www.strava.com/api/v3/clubs/{club_id}/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"per_page": per_page, "page": page}
    res = requests.get(url, headers=headers, params=params)
    res.raise_for_status()
    return res.json()
