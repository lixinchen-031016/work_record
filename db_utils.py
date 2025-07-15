from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, WorkRecord, DutyPersonnel, User, DailyDuty
import pandas as pd
import bcrypt
import jwt
from datetime import datetime, timedelta

# JWT配置
SECRET_KEY = "your_secret_key"  # 实际应用中应从环境变量获取
TOKEN_EXPIRATION = timedelta(minutes=30)

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
def create_record(db, recorder, work_type, work_content, start_date, end_date):
    new_record = WorkRecord(
        recorder=recorder,
        work_type=work_type,
        work_content=work_content,
        start_date=start_date,
        end_date=end_date,
        is_completed=0  # 新增：默认未完成
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

# 新增：获取未完成的工作记录
def get_uncompleted_records(db, date=None):
    """获取未完成的工作记录，优化查询逻辑"""
    query = db.query(WorkRecord).filter(WorkRecord.is_completed == 0)
    
    return query.order_by(WorkRecord.end_date.asc()).all()

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
    """每天只有一名值班人员，如果已存在今日值班人员则返回保存的值"""
    today = datetime.now().date()
    
    # 检查是否有保存的今日值班人员
    saved_duty = db.query(DailyDuty).filter(DailyDuty.date == today).first()
    if saved_duty and saved_duty.personnel:
        return [saved_duty.personnel]
    
    # 无保存则自动轮换
    all_personnel = get_all_duty_personnel(db)
    if not all_personnel:
        return []
    
    day_of_year = today.timetuple().tm_yday
    selected_index = day_of_year % len(all_personnel)
    
    return [all_personnel[selected_index]]

def save_today_duty(db, personnel_list):
    """保存今日值班人员(只保存第一个)"""
    today = datetime.now().date()
    if not personnel_list:
        return False
    
    # 检查是否已有今日记录
    existing = db.query(DailyDuty).filter(DailyDuty.date == today).first()
    if existing:
        existing.personnel = personnel_list[0]
    else:
        new_duty = DailyDuty(date=today, personnel=personnel_list[0])
        db.add(new_duty)
    
    db.commit()
    return True

# 值班人员管理 - 新增编辑功能
def update_duty_person(db, old_name, new_name):
    person = db.query(DutyPersonnel).filter(DutyPersonnel.name == old_name).first()
    if person:
        person.name = new_name
        db.commit()
        return True
    return False

# 值班人员管理 - 新增删除功能
def delete_duty_person(db, name):
    person = db.query(DutyPersonnel).filter(DutyPersonnel.name == name).first()
    if person:
        db.delete(person)
        db.commit()
        return True
    return False

# 导出Excel
def export_to_excel(db, start_date, end_date):
    records = get_records_by_date_range(db, start_date, end_date)
    data = [{
        "ID": r.id,
        "记录人": r.recorder,
        "工作类型": r.work_type,
        "工作内容": r.work_content,
        "开始日期": r.start_date,
        "结束日期": r.end_date,
        "是否完成": "是" if r.is_completed else "否"  # 新增是否完成列
    } for r in records]
    
    df = pd.DataFrame(data)
    return df

# 用户管理功能
def create_user(db, username, password):
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == username).first():
        return None
    
    # 使用bcrypt加密密码
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # 存储为字符串
    hashed_password_str = hashed_password.decode('utf-8')
    
    new_user = User(
        username=username,
        password=hashed_password_str,
        last_login=datetime.now().date()
    )
    db.add(new_user)
    db.commit()
    return new_user

def verify_user(db, username, password):
    user = db.query(User).filter(User.username == username).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        # 更新最后登录时间
        user.last_login = datetime.now().date()
        db.commit()
        return user
    return None

def get_user_by_username(db, username):
    return db.query(User).filter(User.username == username).first()

def update_password(db, username, new_password):
    user = db.query(User).filter(User.username == username).first()
    if user:
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        user.password = hashed_password.decode('utf-8')
        db.commit()
        return True
    return False

# 新增：获取所有用户
def get_all_users(db):
    return db.query(User).all()

# 新增：删除用户
def delete_user(db, username):
    user = db.query(User).filter(User.username == username).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False

def generate_jwt_token(username):
    payload = {
        'username': username,
        'exp': datetime.utcnow() + TOKEN_EXPIRATION
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['username']
    except jwt.ExpiredSignatureError:
        return None  # Token已过期
    except jwt.InvalidTokenError:
        return None  # 无效Token

# 新增：数据库备份功能
import os
import zipfile
from io import BytesIO
from datetime import datetime
from sqlalchemy import text

def backup_database(db):
    """备份数据库到内存中的zip文件"""
    # 获取所有表名
    tables = db.execute(text("SHOW TABLES")).fetchall()
    tables = [table[0] for table in tables]
    
    # 创建内存中的zip文件
    zip_buffer = BytesIO()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for table in tables:
            # 获取表结构
            create_table = db.execute(text(f"SHOW CREATE TABLE {table}")).fetchone()[1]
            
            # 获取表数据
            data = db.execute(text(f"SELECT * FROM {table}")).fetchall()
            
            # 生成SQL内容
            sql_content = f"{create_table};\n\n"
            for row in data:
                values = ", ".join([f"'{str(v)}'" if v is not None else "NULL" for v in row])
                sql_content += f"INSERT INTO {table} VALUES ({values});\n"
            
            # 将SQL添加到zip
            zip_file.writestr(f"backup_{timestamp}/{table}.sql", sql_content)
    
    zip_buffer.seek(0)
    return zip_buffer
