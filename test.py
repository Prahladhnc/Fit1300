from models import Session, Activity
session = Session()
print("Total activities:", session.query(Activity).count())
print(session.query(Activity).limit(5).all())
