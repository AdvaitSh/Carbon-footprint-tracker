import os
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Get the PostgreSQL connection string from environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")

# Create SQLAlchemy engine
engine = sa.create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Define the CarbonFootprint table
class CarbonFootprint(Base):
    __tablename__ = "carbon_footprints"
    
    id = sa.Column(sa.Integer, primary_key=True)
    user_name = sa.Column(sa.String(100))
    email = sa.Column(sa.String(100))
    weekly_total = sa.Column(sa.Float)
    annual_total = sa.Column(sa.Float)
    transport_emissions = sa.Column(sa.Float)
    short_flights_emissions = sa.Column(sa.Float)
    long_flights_emissions = sa.Column(sa.Float)
    household_emissions = sa.Column(sa.Float)
    diet_emissions = sa.Column(sa.Float)
    country = sa.Column(sa.String(50))
    timestamp = sa.Column(sa.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_name": self.user_name,
            "email": self.email,
            "weekly_total": self.weekly_total,
            "annual_total": self.annual_total,
            "transport_emissions": self.transport_emissions,
            "short_flights_emissions": self.short_flights_emissions,
            "long_flights_emissions": self.long_flights_emissions,
            "household_emissions": self.household_emissions,
            "diet_emissions": self.diet_emissions,
            "country": self.country,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

# Function to create the database tables
def create_tables():
    Base.metadata.create_all(engine)

# Function to save a carbon footprint calculation to the database
def save_footprint(user_name, email, results):
    session = Session()
    try:
        footprint = CarbonFootprint(
            user_name=user_name,
            email=email,
            weekly_total=results["weekly_total"],
            annual_total=results["annual_total"],
            transport_emissions=results["weekly_breakdown"]["Transportation"],
            short_flights_emissions=results["weekly_breakdown"]["Short Flights"],
            long_flights_emissions=results["weekly_breakdown"]["Long Flights"],
            household_emissions=results["weekly_breakdown"]["Household Energy"],
            diet_emissions=results["weekly_breakdown"]["Diet"],
            country=results["comparison"]["country"]
        )
        session.add(footprint)
        session.commit()
        return footprint.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# Function to get all footprints
def get_all_footprints():
    session = Session()
    try:
        footprints = session.query(CarbonFootprint).all()
        return [footprint.to_dict() for footprint in footprints]
    finally:
        session.close()

# Function to get a footprint by ID
def get_footprint_by_id(footprint_id):
    session = Session()
    try:
        footprint = session.query(CarbonFootprint).filter_by(id=footprint_id).first()
        if footprint:
            return footprint.to_dict()
        return None
    finally:
        session.close()

# Function to get footprints by email
def get_footprints_by_email(email):
    session = Session()
    try:
        footprints = session.query(CarbonFootprint).filter_by(email=email).all()
        return [footprint.to_dict() for footprint in footprints]
    finally:
        session.close()

# Function to delete a footprint by ID
def delete_footprint(footprint_id):
    session = Session()
    try:
        footprint = session.query(CarbonFootprint).filter_by(id=footprint_id).first()
        if footprint:
            session.delete(footprint)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# Initialize the database tables
create_tables()

[server]
headless = true
address = "0.0.0.0"
port = 5000