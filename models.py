from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class WorkRecord(Base):
    __tablename__ = 'work_records'
    
    id = Column(Integer, primary_key=True)
    recorder = Column(String(50), nullable=False)  # 记录人
    work_type = Column(String(50), nullable=False)  # 工作类型
    work_content = Column(String(255), nullable=False)  # 新增：工作内容
    start_date = Column(Date, nullable=False)      # 开始日期
    end_date = Column(Date, nullable=False)        # 结束日期

class DutyPersonnel(Base):
    __tablename__ = 'duty_personnel'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)  # 值班人员姓名

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)  # 用户名
    password = Column(String(255), nullable=False)            # 密码（加密存储）
    last_login = Column(Date)                                 # 上次登录时间
