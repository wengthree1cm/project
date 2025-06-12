import sys
import locale
sys.getdefaultencoding = lambda: "utf-8"
locale.getpreferredencoding = lambda: "utf-8"

import streamlit as st
import os
import datetime
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from utils.parse_pdf import extract_text_from_file
from utils.extract_llm import extract_fields
from utils.db_ops import insert_or_update_drug, init_db
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# 初始化
UPLOAD_DIR = "data/uploads"
DB_PATH = "data/drugs.db"
GOOGLE_SHEET_CSV = "https://docs.google.com/spreadsheets/d/1EXKqsz1nYaubjNJpUPy73nyvT9uaNRhutMXMDEjvsk4/export?format=csv"

st.set_page_config(page_title="Drug Trial Extractor", layout="wide")
st.title("🧬 药物临床试验信息提取工具")

# 初始化数据库
init_db(DB_PATH)

# 文件上传
uploaded_file = st.file_uploader("上传 PDF 或 TXT 文件", type=["pdf", "txt"])

if uploaded_file:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success(f"✅ 文件已保存：{uploaded_file.name}")
    text = extract_text_from_file(file_path)
    trial_data = extract_fields(text)
    trial_data["source_file"] = uploaded_file.name
    trial_data["update_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    st.subheader("🔎 提取结果")
    st.json(trial_data)
    insert_or_update_drug(trial_data, DB_PATH)
    st.success("✅ 数据已保存（自动创建或更新）")

# 数据导出
st.markdown("---")
st.subheader("📤 导出数据")
if st.button("导出为 CSV"):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM trial_data", conn)
    conn.close()
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 点击下载 CSV", csv, "trial_data_export.csv", "text/csv")

# Google Sheet 药物匹配功能
st.markdown("---")
st.subheader("🔍 查找最相似药物信息（来自 Google Sheet）")

query = st.text_input("请输入药物名（用于查找最相似的 Modality & Indication）")

if query:
    try:
        df_sheet = pd.read_csv(GOOGLE_SHEET_CSV)
        df_sheet = df_sheet.dropna(subset=["Modality (ADC / CAR-T / TCE)", "Indication"])
        df_sheet["combined"] = df_sheet["Modality (ADC / CAR-T / TCE)"].astype(str) + " " + df_sheet["Indication"].astype(str)
        
        # 相似度匹配
        corpus = df_sheet["combined"].tolist()
        corpus.append(query)
        vectorizer = TfidfVectorizer().fit_transform(corpus)
        similarity = cosine_similarity(vectorizer[-1], vectorizer[:-1])
        most_similar_index = similarity.argmax()
        best_match_row = df_sheet.iloc[[most_similar_index]]
        
        st.markdown("### 📌 最相似的药物信息如下：")
        st.dataframe(best_match_row)

        # 提取时间列绘图
        timeline_cols = [
            "FIH → Pivotal Start",
            "Accelerated Approval Trial Enrollment Duration",
            "Full Approval Trial Enrollment Duration",
            "Accelerated Approval Trial Topline Lag",
            "Full Approval Trial Topline Lag"
        ]
        timeline_values = []
        for col in timeline_cols:
            val = best_match_row[col].values[0]
            try:
                val = float(val)
                timeline_values.append(val)
            except:
                timeline_values.append(0.0)

        fig, ax = plt.subplots(figsize=(10, 4))
        bars = ax.barh(timeline_cols, timeline_values, color="orange")
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.5, bar.get_y() + bar.get_height() / 2, f"{width:.2f}", va='center')
        ax.set_xlabel("时间（月）")
        ax.set_title("药物临床试验主要阶段时间线可视化")
        st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ 无法处理 Google Sheet 或数据格式异常：{e}")
