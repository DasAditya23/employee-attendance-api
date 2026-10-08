from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .database import Base, engine, SessionLocal
from . import models, schemas
from datetime import datetime

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Employee Attendance API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {
        "message": "Employee Attendance API is running"
    }


@app.post("/employees")
def create_employee(
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db)
):
    new_employee = models.Employee(
        name=employee.name,
        email=employee.email,
        department=employee.department
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return new_employee


@app.get("/employees", response_model=list[schemas.EmployeeResponse])
def get_employees(db: Session = Depends(get_db)):
    employees = db.query(models.Employee).all()
    return employees


@app.get("/employees/{employee_id}")
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()

    if employee is None:
        return {"message": "Employee not found"}

    return employee


@app.put("/employees/{employee_id}")
def update_employee(
    employee_id: int,
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db)
):
    existing_employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()

    if existing_employee is None:
        return {"message": "Employee not found"}

    existing_employee.name = employee.name
    existing_employee.email = employee.email
    existing_employee.department = employee.department

    db.commit()
    db.refresh(existing_employee)

    return existing_employee


@app.delete("/employees/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()

    if employee is None:
        return {"message": "Employee not found"}

    db.delete(employee)
    db.commit()

    return {
        "message": "Employee deleted successfully"
    }
@app.post("/attendance/check-in/{employee_id}")
def check_in(
    employee_id: int,
    db: Session = Depends(get_db)
):
    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()

    if employee is None:
        return {"message": "Employee not found"}

    attendance = models.Attendance(
        employee_id=employee_id,
        check_in=datetime.now(),
        status="Present"
    )

    db.add(attendance)
    db.commit()
    db.refresh(attendance)

    return {
        "message": "Check-in successful",
        "employee_id": employee_id,
        "check_in": attendance.check_in,
        "status": attendance.status
    }