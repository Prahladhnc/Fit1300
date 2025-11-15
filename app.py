# app.py
from flask import Flask, render_template
from sqlalchemy import func
from models import Session, Activity
import csv

app = Flask(__name__)
def get_member_count_from_csv(csv_path="status.csv"):
    try:
        with open(csv_path, "r") as file:
            reader = list(csv.DictReader(file))
            if not reader:
                return 0
            last_row = reader[-1]
            return int(last_row.get("member_count", 0))
    except Exception as e:
        print("Error reading CSV:", e)
        return 0


@app.route("/")
def home():
    session = Session()
    total_athletes = get_member_count_from_csv()

    # Calculate total distance for each sport type
    total_run = session.query(func.sum(Activity.distance)).filter(Activity.type == "Run").scalar() or 0
    total_ride = session.query(func.sum(Activity.distance)).filter(Activity.type == "Ride").scalar() or 0

    # Convert to kilometers
    total_run_km = total_run / 1000
    total_ride_km = total_ride / 1000

    session.close()

    return render_template(
        "index.html",
        total_run_km=total_run_km,
        total_ride_km=total_ride_km,
        total_athletes=total_athletes
    )

@app.route("/activities")
def show_activities():
    session = Session()
    activities = session.query(Activity).order_by(Activity.start_date.desc()).all()
    session.close()
    return render_template("activities.html", activities=activities)

@app.route("/stats")
def show_stats():
    session = Session()

    # Get all unique sport types
    sport_types = [r[0] for r in session.query(Activity.type).distinct()]

    stats = []
    for sport in sport_types:
        q = session.query(Activity).filter(Activity.type == sport)

        unique_athletes = len(set([a.athlete_name for a in q]))
        total_activities = q.count()
        total_distance_m = sum([a.distance or 0 for a in q])
        total_elapsed_s = sum([a.elapsed_time or 0 for a in q])

        # Convert units
        total_distance_km = total_distance_m / 1000
        total_hours = int(total_elapsed_s // 3600)
        total_minutes = int((total_elapsed_s % 3600) // 60)

        stats.append({
            "sport": sport,
            "unique_athletes": unique_athletes,
            "total_activities": total_activities,
            "total_distance": total_distance_km,
            "total_time": f"{total_hours}h {total_minutes:02d}m"
        })

    session.close()
    return render_template("stats.html", stats=stats)
    
@app.route("/cycle-rally")
def cycle_rally():
    return render_template("cycle_rally.html", title="Cycle Rally | FIT@1100")

if __name__ == "__main__":
    app.run(debug=True)
