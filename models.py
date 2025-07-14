from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class WorkRecord(Base):
    __tablename__ = 'work_records'
    
    id = Column(Integer, primary_key=True)
    recorder = Column(String(50), nullable=False)  # 记录人
    work_type = Column(String(50), nullable=False)  # 工作类型
    start_date = Column(Date, nullable=False)      # 开始日期
    end_date = Column(Date, nullable=False)        # 结束日期

class DutyPersonnel(Base):
    __tablename__ = 'duty_personnel'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)  # 值班人员姓名