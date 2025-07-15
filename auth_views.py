import streamlit as st
from auth_utils import *
from datetime import date, timedelta
import db_utils

def show_login_register_page():
    """展示登录/注册/找回密码页面"""
    st.markdown("## 📊 工作记录管理系统 - 登录")
    
    tab_login, tab_register, tab_forgot = st.tabs(["🔐 登录", "📝 注册", "🔑 找回密码"])
    
    with tab_login:
        show_login_form()
    
    with tab_register:
        show_register_form()
    
    with tab_forgot:
        show_forgot_password_form()

def show_login_form():
    """展示登录表单"""
    with st.form("login_form"):
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        remember = st.checkbox("记住我")
        
        if st.form_submit_button("登录"):
            user = verify_user(username, password)
            if user:
                # 生成JWT Token
                token = generate_jwt_token(username)
                st.session_state.jwt_token = token
                st.session_state.username = username
                st.query_params["token"] = token
                
                # 获取所有未完成记录
                db = next(db_utils.get_db_session())
                uncompleted = db_utils.get_uncompleted_records(db)
                if uncompleted:
                    st.session_state.pending_records = uncompleted
                    st.session_state.show_pending_records = True
                    st.toast("⚠️ 检测到未完成工作，请及时处理！", icon='⚠️')
                
                st.success("登录成功！")
                st.rerun()
            else:
                st.error("用户名或密码错误")

def show_register_form():
    """展示注册表单"""
    with st.form("register_form"):
        new_username = st.text_input("用户名")
        new_password = st.text_input("密码", type="password")
        confirm_password = st.text_input("确认密码", type="password")
        
        if st.form_submit_button("注册"):
            if new_password != confirm_password:
                st.error("两次输入的密码不一致")
            else:
                user = create_user(new_username, new_password)
                if user:
                    st.success("注册成功！请登录")
                else:
                    st.error("用户名已存在")

def show_forgot_password_form():
    """展示找回密码表单"""
    with st.form("forgot_form"):
        forgot_username = st.text_input("用户名")
        new_password = st.text_input("新密码", type="password")
        confirm_password = st.text_input("确认新密码", type="password")
        
        if st.form_submit_button("重置密码"):
            if new_password != confirm_password:
                st.error("两次输入的密码不一致")
            else:
                if update_password(forgot_username, new_password):
                    st.success("密码已重置，请使用新密码登录")
                else:
                    st.error("用户名不存在")