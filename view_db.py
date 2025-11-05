# view_db_table.py
from models import Session, Activity
from tabulate import tabulate

def view_database_table():
    session = Session()

    activities = session.query(Activity).order_by(Activity.start_date.desc()).all()
    print(f"Total activities in DB: {len(activities)}\n")

    # Prepare data for tabulate
    table_data = []
    for act in activities:
        table_data.append([
            act.id,
            act.athlete_name,
            act.activity_name,
            act.type,
            act.distance,
            act.moving_time,
            act.elapsed_time,
            act.total_elevation_gain,
            act.start_date
        ])

    headers = ["ID", "Athlete", "Activity", "Type", "Distance (m)", 
               "Moving Time (s)", "Elapsed Time (s)", "Elevation Gain (m)", "Start Date"]

    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    session.close()

if __name__ == "__main__":
    view_database_table()
