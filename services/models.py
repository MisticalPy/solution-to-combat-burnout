from sqlalchemy import Column, Integer, String, Boolean, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Employee(Base):
    """Модель сотрудника"""
    
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fio = Column(String(255), nullable=False)
    legal_entity = Column(String(255))
    gender = Column(String(10))
    city = Column(String(100))
    position = Column(String(255))
    experience = Column(String(100))
    age = Column(Integer)
    subordinates = Column(String(100))
    
    june_performance = Column(String(10))
    july_performance = Column(String(10))
    august_performance = Column(String(10))
    september_performance = Column(String(10))
    october_performance = Column(String(10))
    
    certification = Column(String(50))
    training = Column(String(100))
    last_vacation = Column(String(50))
    sick_leave_2025 = Column(Boolean, default=False)
    reprimand = Column(Boolean, default=False)
    corporate_activities = Column(Boolean, default=False)
    
    notes = Column(Text)
    
    created_at = Column(Date, default=datetime.now)
    updated_at = Column(Date, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Employee(id={self.id}, fio='{self.fio}')>"


if __name__ == "__main__":
    print('Запуск программы должен быть из функции main')