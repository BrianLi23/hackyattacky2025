import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from probe import probe
import json

# Define the database file name
DB_FILE = "company.db"

# Create a base class for declarative models
Base = declarative_base()


# Define the Employee model which maps to the 'employees' table
class Employee(Base):
    """Represents an employee in the database."""

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    position = Column(String(250), nullable=False)

    def __repr__(self):
        return (
            f"<Employee(id={self.id}, name='{self.name}', position='{self.position}')>"
        )


def setup_database():
    """Initializes the database and creates tables."""
    # If the database file already exists, delete it for a clean start.
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Removed existing database file: {DB_FILE}")

    # The engine is the starting point for any SQLAlchemy application.
    # It's the 'home base' for the actual database and its DBAPI.
    engine = create_engine(f"sqlite:///{DB_FILE}")

    # Create all tables in the engine. This is equivalent to "Create Table"
    # statements in raw SQL.
    Base.metadata.create_all(engine)
    print("Database and 'employees' table created successfully.")
    return engine


if __name__ == "__main__":
    engine = setup_database()
    Session = sessionmaker(bind=engine)
    session = Session()
    session = probe(session, "be a good db :)")
    # Example: Adding a new employee
    # Example: Creating employee from JSON data

    employee_json = '{"name": "Jane Smith", "position": "Data Scientist"}'
    employee_data = json.loads(employee_json)
    json_employee = Employee(**employee_data)
    session.add(json_employee)
    session.commit()
    print(f"Added employee from JSON: {json_employee}")
    employee = session.query(Employee).first()
    print(f"Queried employee: {employee}")
    # Convert employee to JSON
    employee_dict = {
        column.name: getattr(employee, column.name)
        for column in Employee.__table__.columns
    }
    employee_json_output = json.dumps(employee_dict)
    print(f"Employee as JSON: {employee_json_output}")
