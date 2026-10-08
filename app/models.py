from sqlalchemy import Column, Float, Integer, String, DateTime, ForeignKey

from .database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    department = Column(String, nullable=False)


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    check_in = Column(DateTime, nullable=True)
    check_out = Column(DateTime, nullable=True)
    status = Column(String, nullable=False)
    from datetime import datetime, date, time
from fastapi import HTTPException

LATE_AFTER = time(9, 30)

start = datetime.combine(date.today(), time.min)
end = datetime.combine(date.today(), time.max)

existing = db.query(models.Attendance).filter(
    models.Attendance.employee_id == employee_id,
    models.Attendance.check_in >= start,
    models.Attendance.check_in <= end,
).first()
if existing:
    raise HTTPException(status_code=400, detail="Already checked in today")

now = datetime.now()
status = "Late" if now.time() > LATE_AFTER else "Present"