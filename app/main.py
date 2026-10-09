from fastapi.security import OAuth2PasswordRequestForm
from . import auth
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


# ---------- Health check ----------
@app.get("/")
def home():
    return {"message": "Employee Attendance API is running"}


# ---------- Employee routes ----------
@app.post("/employees", status_code=201)
def create_employee(
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(auth.require_admin),
):
    new_employee = models.Employee(
        name=employee.name,
        email=employee.email,
        department=employee.department,
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee


@app.get("/employees", response_model=list[schemas.EmployeeResponse])
def get_employees(
    db: Session = Depends(get_db),
    _user: models.User = Depends(auth.get_current_user),
):
    return db.query(models.Employee).all()


@app.get("/employees/{employee_id}", response_model=schemas.EmployeeResponse)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    _user: models.User = Depends(auth.get_current_user),
):
    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@app.put("/employees/{employee_id}", response_model=schemas.EmployeeResponse)
def update_employee(
    employee_id: int,
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(auth.require_admin),
):
    existing = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()
    if existing is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    existing.name = employee.name
    existing.email = employee.email
    existing.department = employee.department

    db.commit()
    db.refresh(existing)
    return existing


@app.delete("/employees/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(auth.require_admin),
):
    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(employee)
    db.commit()
    return {"message": "Employee deleted successfully"}


# ---------- Attendance routes ----------
@app.post("/attendance/check-in/{employee_id}", status_code=201)
def check_in(
    employee_id: int,
    db: Session = Depends(get_db),
    _user: models.User = Depends(auth.get_current_user),
):
    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    today_start = datetime.combine(date.today(), time.min)
    today_end = datetime.combine(date.today(), time.max)
    existing = db.query(models.Attendance).filter(
        models.Attendance.employee_id == employee_id,
        models.Attendance.check_in.between(today_start, today_end),
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already checked in today")

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
def check_out(
    employee_id: int,
    db: Session = Depends(get_db),
    _user: models.User = Depends(auth.get_current_user),
):
    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

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
    _user: models.User = Depends(auth.get_current_user),
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


# ---------- Auth routes ----------
@app.post("/auth/register", response_model=schemas.UserResponse, status_code=201)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = models.User(
        email=user.email,
        hashed_password=auth.hash_password(user.password),
        role="employee",
        employee_id=user.employee_id,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
@app.post("/auth/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(
        models.User.email == form_data.username
    ).first()

    if not user or not auth.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = auth.create_access_token(
        data={"sub": user.email, "role": user.role}
    )

    return {"access_token": token, "token_type": "bearer"}