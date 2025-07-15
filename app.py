

import jwt
import streamlit as st
from datetime import date, timedelta, datetime
import db_utils
import pandas as pd
import plotly.express as px
from io import BytesIO
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from auth_views import show_login_register_page
from auth_utils import verify_jwt_token, generate_jwt_token
import time

from work_record_views import show_work_record_page, show_export_section

# 初始化数据库
db_utils.init_db()

# 页面配置
st.set_page_config(page_title="工作记录管理系统", layout="wide")

# 获取数据库会话
def get_db():
    return next(db_utils.get_db_session())

# 检查JWT并自动续期
def check_auth():
    # 先检查URL参数中的token
    if 'token' in st.query_params and 'jwt_token' not in st.session_state:
        st.session_state.jwt_token = st.query_params["token"]
    
    if 'jwt_token' not in st.session_state:
        return False
    
    # 验证当前Token
    username = verify_jwt_token(st.session_state.jwt_token)
    
    # Token无效或过期
    if not username:
        # 尝试使用URL参数中的token
        if 'token' in st.query_params:
            username = verify_jwt_token(st.query_params["token"])
            if username:
                st.session_state.jwt_token = st.query_params["token"]
                st.session_state.username = username
                return True
        return False
    
    # 检查Token是否需要续期（剩余时间小于5分钟）
    try:
        payload = jwt.decode(
            st.session_state.jwt_token,
            db_utils.SECRET_KEY,
            algorithms=['HS256'],
            options={"verify_exp": False}  # 不验证过期时间
        )
        exp_time = payload['exp']
        if exp_time - time.time() < 300:  # 剩余时间小于5分钟
            # 生成新Token
            st.session_state.jwt_token = generate_jwt_token(username)
            st.query_params["token"] = st.session_state.jwt_token
    except:
        pass
    
    # 确保username也在session state中
    if 'username' not in st.session_state:
        st.session_state.username = username
        
    # 检查前一天未完成的工作
    if username:
        yesterday = date.today() - timedelta(days=1)
        db = next(db_utils.get_db_session())
        uncompleted = db_utils.get_uncompleted_records(db, yesterday)
        if uncompleted:
            st.session_state.pending_records = uncompleted
            st.session_state.show_pending_records = True
    
    return True

# 登录/注册页面
if not check_auth():
    show_login_register_page()
    st.stop()

# 主界面重构
st.title(f"工作记录管理系统 - 欢迎 {st.session_state.username}")

# 添加全局样式优化
st.markdown("""
<style>
    /* 卡片式容器样式 */
    .card {
        padding: 2rem;
        border-radius: 1.5rem;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        background-color: #ffffff;
        margin: 1.5rem 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .card:hover {
        transform: translateY(-8px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
    }
    
    /* 增强型按钮样式 */
    .stButton button {
        border-radius: 1rem;
        padding: 0.8rem 1.5rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        background: linear-gradient(45deg, #3b82f6, #6366f1, #8b5cf6);
        color: white;
        border: none;
        transition: all 0.4s ease;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4);
    }
    .stButton button:hover {
        transform: scale(1.03);
        box-shadow: 0 6px 18px rgba(59, 130, 246, 0.6);
    }
    
    /* 数据表格样式优化 */
    .stDataFrame {
        border-radius: 1rem;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
    }
    .stDataFrame thead th {
        background-color: #bfdbfe !important;
        color: #1e40af !important;
        font-weight: 600;
    }
    .stDataFrame tbody tr:nth-child(even) {
        background-color: #efefef !important;
    }
    
    /* 日期选择器样式优化 */
    .stDateInput input {
        border-radius: 1rem;
        padding: 0.6rem 1.2rem;
        border: 2px solid #bfdbfe;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    .stDateInput input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }
    
    /* 分页控件样式 */
    .stNumberInput input {
        border-radius: 0.75rem;
        padding: 0.4rem 0.8rem;
        border: 1px solid #d1d5db;
        font-weight: 500;
    }
    
    /* 提醒卡片样式优化 */
    .reminder-card {
        padding: 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        background: linear-gradient(to right, #fef3c7, #fee3a1);
        border-left: 5px solid #f59e0b;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    }
    .reminder-card:hover {
        transform: translateX(5px);
    }
    
    /* 图标动画效果 */
    .icon-animation {
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

# 退出登录按钮（添加图标和样式优化）
st.markdown("""
<style>
    .logout-button {
        background: linear-gradient(45deg, #ff6b6b, #ff8e53);
        color: white;
        border-radius: 10px;
        padding: 8px 15px;
        font-weight: bold;
    }
    .logout-button:hover {
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

if st.button("🚪 退出登录", key="logout_button", help="点击退出系统", use_container_width=True):
    st.session_state.pop('jwt_token', None)
    st.session_state.pop('username', None)
    st.query_params.clear()  # 修改为使用query_params.clear()
    st.rerun()

# 新增系统管理页面
tab_main, tab_admin = st.tabs(["📊 工作记录", "⚙️ 系统管理"])

with tab_admin:
    # 系统管理功能卡片导航
    cols = st.columns(3)  # 修改为3列，增加备份按钮
    with cols[0]:
        if st.button("👥 用户管理", use_container_width=True, key="user_mgmt_btn"):
            st.session_state.current_admin_view = "users"
    with cols[1]:
        if st.button("👤 值班管理", use_container_width=True, key="duty_mgmt_btn"):
            st.session_state.current_admin_view = "duty"
    with cols[2]:
        if st.button("💾 数据库备份", use_container_width=True, key="backup_btn"):
            st.session_state.current_admin_view = "backup"
    

    # 根据选择显示对应功能
    if 'current_admin_view' not in st.session_state:
        st.session_state.current_admin_view = "users"
    
    if st.session_state.current_admin_view == "users":
        # 用户管理
        with st.expander("用户管理"):
            st.subheader("用户列表")
            db = get_db()
            users = db_utils.get_all_users(db)
            
            if users:
                # 显示用户表格
                user_df = pd.DataFrame([{
                    "ID": u.id,
                    "用户名": u.username,
                    "上次登录": u.last_login
                } for u in users])
                st.dataframe(user_df)
            else:
                st.warning("暂无用户")
            
            # 添加新用户
            st.subheader("添加用户")
            with st.form("add_user_form"):
                new_username = st.text_input("用户名")
                new_password = st.text_input("密码", type="password")
                confirm_password = st.text_input("确认密码", type="password")
                
                if st.form_submit_button("添加"):
                    if new_password != confirm_password:
                        st.error("两次输入的密码不一致")
                    else:
                        db = get_db()
                        user = db_utils.create_user(db, new_username, new_password)
                        if user:
                            st.success(f"用户 {new_username} 添加成功")
                            st.rerun()
                        else:
                            st.error("用户名已存在")
            
            # 修改密码
            st.subheader("修改密码")
            if users:
                usernames = [u.username for u in users]
                selected_user = st.selectbox("选择用户", usernames)
                with st.form("change_password_form"):
                    new_password = st.text_input("新密码", type="password")
                    confirm_password = st.text_input("确认新密码", type="password")
                    
                    if st.form_submit_button("修改"):
                        if new_password != confirm_password:
                            st.error("两次输入的密码不一致")
                        else:
                            db = get_db()
                            if db_utils.update_password(db, selected_user, new_password):
                                st.success("密码已更新")
                                st.rerun()
                            else:
                                st.error("更新失败")
            else:
                st.info("没有用户可修改")
            
            # 删除用户
            st.subheader("删除用户")
            if users:
                del_username = st.selectbox("选择要删除的用户", usernames, key="del_user_select")
                if st.button("删除用户"):
                    db = get_db()
                    if db_utils.delete_user(db, del_username):
                        st.success(f"用户 {del_username} 已删除")
                        st.rerun()
                    else:
                        st.error("删除失败")
            else:
                st.info("没有用户可删除")

    elif st.session_state.current_admin_view == "duty":
        # 值班人员管理
        with st.expander("值班人员管理"):
            st.subheader("值班人员名单")
            db = get_db()
            duty_personnel = db_utils.get_all_duty_personnel(db)
            
            # 添加新值班人员
            new_person = st.text_input("添加值班人员姓名", key="new_person")
            if st.button("添加") and new_person:
                if db_utils.add_duty_person(db, new_person):
                    st.success(f"已添加值班人员: {new_person}")
                    st.rerun()
            
            # 显示当前值班人员并支持编辑/删除
            if duty_personnel:
                st.write("当前值班人员名单:")
                for person in duty_personnel:
                    cols = st.columns([3, 1, 1])
                    cols[0].write(person)
                    
                    # 编辑功能
                    with cols[1].form(f"edit_{person}"):
                        new_name = st.text_input("新姓名", value=person, key=f"edit_name_{person}")
                        if st.form_submit_button("更新"):
                            if db_utils.update_duty_person(db, person, new_name):
                                st.success(f"已更新: {person} → {new_name}")
                                st.rerun()
                    
                    # 删除功能
                    if cols[2].button("删除", key=f"del_{person}"):
                        if db_utils.delete_duty_person(db, person):
                            st.success(f"已删除: {person}")
                            st.rerun()
            else:
                st.warning("暂无值班人员，请先添加")

    elif st.session_state.current_admin_view == "backup":
        # 数据库备份功能
        with st.expander("数据库备份"):
            st.subheader("数据库备份")
            st.write("点击下方按钮备份当前数据库，系统将生成包含所有表结构和数据的SQL文件，并打包为ZIP下载。")
            
            if st.button("🔽 立即备份", use_container_width=True):
                db = get_db()
                backup_zip = db_utils.backup_database(db)
                
                st.download_button(
                    label="📥 下载备份文件",
                    data=backup_zip,
                    file_name=f"work_record_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip",
                    use_container_width=True
                )

# 主工作记录页面优化布局
with tab_main:
    # 值班人员显示优化为卡片式布局
    st.markdown("### 📅 今日值班人员")
    db = get_db()
    today_duty = db_utils.get_today_duty_rotation(db)
    
    if today_duty:
        st.markdown(f"""
        <div class="card">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="font-size: 2rem;">👤</div>
                <div>
                    <h3 style="margin: 0; font-size: 1.2rem; color: #4b5563;">当前值班人员</h3>
                    <p style="margin: 0.25rem 0 0 0; font-size: 1.5rem; font-weight: 600; color: #1f2937;">{today_duty[0]}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 修改表单优化
        with st.expander("🔧 修改值班人员"):
            with st.form("edit_duty_form"):
                new_duty = st.selectbox(
                    "选择值班人员",
                    options=db_utils.get_all_duty_personnel(db),
                    index=db_utils.get_all_duty_personnel(db).index(today_duty[0]) if today_duty[0] in db_utils.get_all_duty_personnel(db) else 0,
                    key="duty_select"
                )
                
                if st.form_submit_button("保存修改"):
                    db_utils.save_today_duty(db, [new_duty])
                    st.success("今日值班人员已更新!")
                    st.rerun()
    else:
        st.warning("请先添加值班人员")

    # 替换原有的工作记录管理代码为模块化调用
    show_work_record_page()
    
    # 替换原有的导出功能代码为模块化调用
    show_export_section()

# 侧边栏提醒部分 - 移动到主界面之外
with st.sidebar:
    # 添加: 强化提醒条件判断
    if 'show_pending_records' in st.session_state and st.session_state.show_pending_records:
        st.markdown("### ⚠️ 待处理工作提醒")
        
        # 获取最新未完成记录（防止数据陈旧）
        db = get_db()
        current_pending = db_utils.get_uncompleted_records(db)
        
        if current_pending:
            for record in current_pending:
                st.markdown(f"""
                <div class="reminder-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong class="icon-animation">📌 {record.work_type}</strong><br>
                            <small>记录人: {record.recorder}\n</small>
                            <small>工作类型: {record.work_type}\n</small>
                            <small>工作内容: {record.work_content}\n</small>
                            <small>截止时间: {record.end_date}</small>
                        </div>
                        <div style="font-size: 1.5rem; color: #ea580c;">❗</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                    
                if st.button(f"✅ 标记为已完成", key=f"sidebar_complete_{record.id}", use_container_width=True):
                        db = get_db()
                        db_utils.update_record(db, record.id, is_completed=1)
                        st.session_state.pending_records = [
                            r for r in st.session_state.pending_records if r.id != record.id
                        ]
                        st.toast(f"记录 {record.id} 已标记为完成", icon='✅')
                        st.rerun()
        else:
            st.info("暂无待处理工作")







