from datetime import datetime, timedelta
import bcrypt
import jwt
from db_utils import get_db_session, User

# JWT配置
SECRET_KEY = "your_secret_key"  # 实际应用中应从环境变量获取
TOKEN_EXPIRATION = timedelta(minutes=30)

def create_user(username, password):
    """创建新用户"""
    db = next(get_db_session())
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

def verify_user(username, password):
    """验证用户登录"""
    db = next(get_db_session())
    user = db.query(User).filter(User.username == username).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        # 更新最后登录时间
        user.last_login = datetime.now().date()
        db.commit()
        return user
    return None

def update_password(username, new_password):
    """更新用户密码"""
    db = next(get_db_session())
    user = db.query(User).filter(User.username == username).first()
    if user:
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        user.password = hashed_password.decode('utf-8')
        db.commit()
        return True
    return False

def generate_jwt_token(username):
    """生成JWT token"""
    payload = {
        'username': username,
        'exp': datetime.utcnow() + TOKEN_EXPIRATION
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_jwt_token(token):
    """验证JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['username']
    except jwt.ExpiredSignatureError:
        return None  # Token已过期
    except jwt.InvalidTokenError:
        return None  # 无效Token