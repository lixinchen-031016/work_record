from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, WorkRecord, DutyPersonnel
import pandas as pd
from datetime import datetime

# 数据库配置
DATABASE_URI = "mysql+pymysql://root:lxc20031016@localhost/work_record_db"

# 初始化数据库连接
engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 工作记录CRUD操作
def create_record(db, recorder, work_type, start_date, end_date):
    new_record = WorkRecord(
        recorder=recorder,
        work_type=work_type,
        start_date=start_date,
        end_date=end_date
    )
    db.add(new_record)
    db.commit()
    return new_record

def get_records(db, skip=0, limit=100):
    return db.query(WorkRecord).offset(skip).limit(limit).all()

def update_record(db, record_id, **kwargs):
    record = db.query(WorkRecord).filter(WorkRecord.id == record_id).first()
    if record:
        for key, value in kwargs.items():
            setattr(record, key, value)
        db.commit()
        return record
    return None

def delete_record(db, record_id):
    record = db.query(WorkRecord).filter(WorkRecord.id == record_id).first()
    if record:
        db.delete(record)
        db.commit()
        return True
    return False

def get_records_by_date_range(db, start_date, end_date):
    return db.query(WorkRecord).filter(
        WorkRecord.start_date >= start_date,
        WorkRecord.end_date <= end_date
    ).all()

# 值班人员管理
def add_duty_person(db, name):
    if not db.query(DutyPersonnel).filter(DutyPersonnel.name == name).first():
        new_person = DutyPersonnel(name=name)
        db.add(new_person)
        db.commit()
        return new_person
    return None

def get_all_duty_personnel(db):
    return [person.name for person in db.query(DutyPersonnel).all()]

def get_today_duty_rotation(db):
    """每天轮换4名值班人员"""
    all_personnel = get_all_duty_personnel(db)
    if not all_personnel:
        return []
    
    # 基于当前日期计算轮换索引
    today = datetime.now().date()
    day_of_year = today.timetuple().tm_yday
    start_index = (day_of_year * 4) % len(all_personnel)
    
    # 循环获取4名值班人员
    return [all_personnel[(start_index + i) % len(all_personnel)] for i in range(4)]

# 导出Excel
def export_to_excel(db, start_date, end_date):
    records = get_records_by_date_range(db, start_date, end_date)
    data = [{
        "ID": r.id,
        "记录人": r.recorder,
        "工作类型": r.work_type,
        "开始日期": r.start_date,
        "结束日期": r.end_date
    } for r in records]
    
    df = pd.DataFrame(data)
    return df