import streamlit as st
from datetime import date, timedelta
import db_utils
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import jwt
import time

# 初始化数据库
db_utils.init_db()
plt.rcParams['font.sans-serif'] = ['PingFang HK']  # 或其他你喜欢的中文字体
plt.rcParams['axes.unicode_minus'] = False
# 页面配置
st.set_page_config(page_title="工作记录管理系统", layout="wide")

# 获取数据库会话
def get_db():
    return next(db_utils.get_db_session())

# 检查JWT并自动续期
def check_auth():
    if 'jwt_token' not in st.session_state:
        return False
    
    # 验证当前Token
    username = db_utils.verify_jwt_token(st.session_state.jwt_token)
    
    # Token无效或过期
    if not username:
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
            st.session_state.jwt_token = db_utils.generate_jwt_token(username)
            st.experimental_set_query_params(token=st.session_state.jwt_token)
    except:
        pass
    
    return True

# 登录/注册页面
if not check_auth():
    st.title("工作记录管理系统 - 登录")
    
    tab_login, tab_register, tab_forgot = st.tabs(["登录", "注册", "找回密码"])
    
    with tab_login:
        with st.form("login_form"):
            username = st.text_input("用户名")
            password = st.text_input("密码", type="password")
            remember = st.checkbox("记住我")
            
            if st.form_submit_button("登录"):
                db = get_db()
                user = db_utils.verify_user(db, username, password)
                if user:
                    # 生成JWT Token
                    token = db_utils.generate_jwt_token(username)
                    st.session_state.jwt_token = token
                    st.session_state.username = username
                    st.experimental_set_query_params(token=token)
                    st.success("登录成功！")
                    st.rerun()
                else:
                    st.error("用户名或密码错误")
    
    with tab_register:
        with st.form("register_form"):
            new_username = st.text_input("用户名")
            new_password = st.text_input("密码", type="password")
            confirm_password = st.text_input("确认密码", type="password")
            
            if st.form_submit_button("注册"):
                if new_password != confirm_password:
                    st.error("两次输入的密码不一致")
                else:
                    db = get_db()
                    user = db_utils.create_user(db, new_username, new_password)
                    if user:
                        st.success("注册成功！请登录")
                    else:
                        st.error("用户名已存在")
    
    with tab_forgot:
        with st.form("forgot_form"):
            forgot_username = st.text_input("用户名")
            new_password = st.text_input("新密码", type="password")
            confirm_password = st.text_input("确认新密码", type="password")
            
            if st.form_submit_button("重置密码"):
                if new_password != confirm_password:
                    st.error("两次输入的密码不一致")
                else:
                    db = get_db()
                    if db_utils.update_password(db, forgot_username, new_password):
                        st.success("密码已重置，请使用新密码登录")
                    else:
                        st.error("用户名不存在")
    
    st.stop()

# 主界面重构
st.title(f"工作记录管理系统 - 欢迎 {st.session_state.username}")

# 退出登录按钮
if st.button("退出登录"):
    st.session_state.pop('jwt_token', None)
    st.session_state.pop('username', None)
    st.experimental_set_query_params()
    st.rerun()

# 新增系统管理页面
tab_main, tab_admin = st.tabs(["工作记录", "系统管理"])

with tab_admin:
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

    # 值班人员管理 - 增强功能
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

# 主工作记录页面
with tab_main:
    # 显示今日值班人员
    st.subheader("今日值班人员")
    db = get_db()
    today_duty = db_utils.get_today_duty_rotation(db)
    if today_duty:
        cols = st.columns(4)
        for i, person in enumerate(today_duty):
            cols[i].success(f"值班人员 {i+1}: {person}")
    else:
        st.warning("请先添加值班人员")

    # 工作记录管理
    st.subheader("工作记录管理")
    tab1, tab2, tab3 = st.tabs(["添加记录", "查看/编辑记录", "数据统计"])

    with tab1:
        # 添加新记录 - 增加工作内容字段
        with st.form("add_record_form"):
            db = get_db()
            today_duty = db_utils.get_today_duty_rotation(db)
            if today_duty:
                recorder = st.selectbox("记录人", options=today_duty)
            else:
                st.warning("请先添加值班人员")
                recorder = None
                
            work_type = st.text_input("工作类型")
            work_content = st.text_area("工作内容")  # 新增字段
            start_date = st.date_input("开始日期", value=date.today())
            end_date = st.date_input("结束日期", value=date.today())
            
            if st.form_submit_button("添加记录"):
                if recorder and work_type and work_content and start_date <= end_date:  # 新增验证
                    db = get_db()
                    db_utils.create_record(db, recorder, work_type, work_content, start_date, end_date)  # 新增参数
                    st.success("记录添加成功!")
                else:
                    st.error("请填写完整信息且结束日期不能早于开始日期")

    with tab2:
        # 查看和编辑记录 - 增加工作内容字段
        db = get_db()
        records = db_utils.get_records(db)
        
        if records:
            # 显示记录表格 - 增加工作内容列
            df = pd.DataFrame([{
                "ID": r.id,
                "记录人": r.recorder,
                "工作类型": r.work_type,
                "工作内容": r.work_content,  # 新增列
                "开始日期": r.start_date,
                "结束日期": r.end_date
            } for r in records])
            
            st.dataframe(df)
            
            # 编辑记录 - 增加工作内容字段
            st.subheader("编辑记录")
            record_id = st.number_input("输入要编辑的记录ID", min_value=1)
            if record_id:
                record = next((r for r in records if r.id == record_id), None)
                if record:
                    with st.form("edit_form"):
                        new_recorder = st.text_input("记录人", value=record.recorder)
                        new_work_type = st.text_input("工作类型", value=record.work_type)
                        new_work_content = st.text_area("工作内容", value=record.work_content)  # 新增字段
                        new_start = st.date_input("开始日期", value=record.start_date)
                        new_end = st.date_input("结束日期", value=record.end_date)
                        
                        if st.form_submit_button("更新记录"):
                            if new_start <= new_end:
                                db = get_db()
                                db_utils.update_record(
                                    db, 
                                    record_id,
                                    recorder=new_recorder,
                                    work_type=new_work_type,
                                    work_content=new_work_content,  # 新增参数
                                    start_date=new_start,
                                    end_date=new_end
                                )
                                st.success("记录更新成功!")
                                st.rerun()
                            else:
                                st.error("结束日期不能早于开始日期")
                else:
                    st.warning("找不到该ID的记录")
            
            # 删除记录
            st.subheader("删除记录")
            del_id = st.number_input("输入要删除的记录ID", min_value=1)
            if st.button("删除记录") and del_id:
                db = get_db()
                if db_utils.delete_record(db, del_id):
                    st.success("记录已删除!")
                    st.rerun()
                else:
                    st.error("删除失败，请检查ID")
        else:
            st.info("暂无工作记录")

    with tab3:
        # 数据统计和可视化
        db = get_db()
        records = db_utils.get_records(db)
        
        if records:
            # 按工作类型统计
            st.subheader("工作类型分布")
            work_types = [r.work_type for r in records]
            type_counts = pd.Series(work_types).value_counts()
            
            fig1, ax1 = plt.subplots()
            ax1.pie(type_counts, labels=type_counts.index, autopct='%1.1f%%')
            st.pyplot(fig1)
            
            # 按记录人统计
            st.subheader("记录人工作统计")
            recorders = [r.recorder for r in records]
            recorder_counts = pd.Series(recorders).value_counts()
            
            fig2, ax2 = plt.subplots(figsize=(10, 4))
            ax2.bar(recorder_counts.index, recorder_counts.values)
            plt.xticks(rotation=45)
            st.pyplot(fig2)
            
            # 时间趋势分析
            st.subheader("工作记录时间分布")
            df = pd.DataFrame([{
                "date": r.start_date,
                "count": 1
            } for r in records])
            
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date').resample('W').count()
                
                fig3, ax3 = plt.subplots(figsize=(10, 4))
                ax3.plot(df.index, df['count'], marker='o')
                ax3.set_xlabel("日期")
                ax3.set_ylabel("记录数量")
                st.pyplot(fig3)
        else:
            st.info("暂无数据可供统计")

# Excel导出功能
st.subheader("导出工作记录")
export_start = st.date_input("起始日期", value=date.today() - timedelta(days=30))
export_end = st.date_input("结束日期", value=date.today())

if st.button("导出为Excel"):
    db = get_db()
    df = db_utils.export_to_excel(db, export_start, export_end)
    
    if not df.empty:
        # 创建Excel文件
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='工作记录')
        output.seek(0)
        
        # 提供下载
        st.download_button(
            label="下载Excel文件",
            data=output,
            file_name=f"work_records_{export_start}_{export_end}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("所选时间段内没有记录")

