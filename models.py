# models.py
import os
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Ensure data folder exists
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

# SQLite DB path
db_path = os.path.join(BASE_DIR, "data", "club.db")
engine = create_engine(f"sqlite:///{db_path}")

# Base class for models
Base = declarative_base()

# Activity table
class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True)  # pseudo ID we generate
    athlete_name = Column(String)
    distance = Column(Float)
    moving_time = Column(Float)
    elapsed_time = Column(Float)
    total_elevation_gain = Column(Float)
    type = Column(String)
    start_date = Column(DateTime)
    activity_name = Column(String)

# Create table if not exists
Base.metadata.create_all(engine)

# Session factory
Session = sessionmaker(bind=engine)
