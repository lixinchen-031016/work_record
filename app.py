import streamlit as st
from datetime import date, timedelta
import db_utils
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

# 初始化数据库
db_utils.init_db()

# 页面配置
st.set_page_config(page_title="工作记录管理系统", layout="wide")
st.title("工作记录管理系统")

# 获取数据库会话
def get_db():
    return next(db_utils.get_db_session())

# 值班人员管理
with st.expander("值班人员管理"):
    st.subheader("值班人员名单")
    db = get_db()
    duty_personnel = db_utils.get_all_duty_personnel(db)
    
    # 添加新值班人员
    new_person = st.text_input("添加值班人员姓名")
    if st.button("添加") and new_person:
        if db_utils.add_duty_person(db, new_person):
            st.success(f"已添加值班人员: {new_person}")
            st.rerun()
    
    # 显示当前值班人员
    if duty_personnel:
        st.write("当前值班人员名单:")
        st.dataframe(pd.DataFrame(duty_personnel, columns=["姓名"]))
    else:
        st.warning("暂无值班人员，请先添加")

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
    # 添加新记录
    with st.form("add_record_form"):
        db = get_db()
        today_duty = db_utils.get_today_duty_rotation(db)
        if today_duty:
            recorder = st.selectbox("记录人", options=today_duty)
        else:
            st.warning("请先添加值班人员")
            recorder = None
            
        work_type = st.text_input("工作类型")
        start_date = st.date_input("开始日期", value=date.today())
        end_date = st.date_input("结束日期", value=date.today())
        
        if st.form_submit_button("添加记录"):
            if recorder and work_type and start_date <= end_date:
                db = get_db()
                db_utils.create_record(db, recorder, work_type, start_date, end_date)
                st.success("记录添加成功!")
            else:
                st.error("请填写完整信息且结束日期不能早于开始日期")

with tab2:
    # 查看和编辑记录
    db = get_db()
    records = db_utils.get_records(db)
    
    if records:
        # 显示记录表格
        df = pd.DataFrame([{
            "ID": r.id,
            "记录人": r.recorder,
            "工作类型": r.work_type,
            "开始日期": r.start_date,
            "结束日期": r.end_date
        } for r in records])
        
        st.dataframe(df)
        
        # 编辑记录
        st.subheader("编辑记录")
        record_id = st.number_input("输入要编辑的记录ID", min_value=1)
        if record_id:
            record = next((r for r in records if r.id == record_id), None)
            if record:
                with st.form("edit_form"):
                    new_recorder = st.text_input("记录人", value=record.recorder)
                    new_work_type = st.text_input("工作类型", value=record.work_type)
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