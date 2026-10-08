from datetime import datetime, date, time
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import Base, engine, SessionLocal
from . import models, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Employee Attendance API")
LATE_AFTER = time(9, 30)

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
@app.post("/attendance/check-in/{employee_id}", status_code=201)
def check_in(employee_id: int, db: Session = Depends(get_db)):
    # 1. Does the employee exist?
    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # 2. Already checked in today?
    today_start = datetime.combine(date.today(), time.min)
    today_end = datetime.combine(date.today(), time.max)
    existing = db.query(models.Attendance).filter(
        models.Attendance.employee_id == employee_id,
        models.Attendance.check_in.between(today_start, today_end),
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already checked in today")

    # 3. Record the check-in
    now = datetime.now()
    status = "Late" if now.time() > LATE_AFTER else "Present"

    attendance = models.Attendance(
        employee_id=employee_id,
        check_in=now,
        status=status,
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)

    return {
        "message": "Check-in successful",
        "employee_id": employee_id,
        "check_in": attendance.check_in,
        "status": attendance.status,
    }
@app.post("/attendance/check-out/{employee_id}", status_code=200)
def check_out(employee_id: int, db: Session = Depends(get_db)):
    # 1. Does the employee exist?
    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # 2. Find today's open check-in (checked in, not checked out yet)
    today_start = datetime.combine(date.today(), time.min)
    today_end = datetime.combine(date.today(), time.max)
    attendance = db.query(models.Attendance).filter(
        models.Attendance.employee_id == employee_id,
        models.Attendance.check_in.between(today_start, today_end),
        models.Attendance.check_out.is_(None),
    ).first()

    if not attendance:
        raise HTTPException(
            status_code=400,
            detail="No open check-in found for today",
        )

    # 3. Record check-out
    attendance.check_out = datetime.now()
    db.commit()
    db.refresh(attendance)

    hours = (attendance.check_out - attendance.check_in).total_seconds() / 3600

    return {
        "message": "Check-out successful",
        "employee_id": employee_id,
        "check_in": attendance.check_in,
        "check_out": attendance.check_out,
        "hours_worked": round(hours, 2),
        "status": attendance.status,
    }
@app.get("/attendance/{employee_id}")
def get_attendance(
    employee_id: int,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    query = db.query(models.Attendance).filter(
        models.Attendance.employee_id == employee_id
    )

    if from_date:
        query = query.filter(
            models.Attendance.check_in >= datetime.combine(from_date, time.min)
        )
    if to_date:
        query = query.filter(
            models.Attendance.check_in <= datetime.combine(to_date, time.max)
        )

    return query.order_by(models.Attendance.check_in.desc()).all()