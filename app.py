import streamlit as st
import os
import datetime
import sqlite3
from utils.parse_pdf import extract_text_from_file
from utils.extract_llm import extract_fields
from utils.db_ops import insert_or_update_drug, init_db

UPLOAD_DIR = "data/uploads"
DB_PATH = "data/drugs.db"

st.set_page_config(page_title="Drug Trial Extractor", layout="wide")
st.title("🧬 药物临床试验信息提取工具")

# 初始化数据库
init_db(DB_PATH)

uploaded_file = st.file_uploader("上传 PDF 或 TXT 文件", type=["pdf", "txt"])

if uploaded_file:
    # 保存文件
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success(f"✅ 文件已保存：{uploaded_file.name}")

    # 解析文本
    text = extract_text_from_file(file_path)

    # 调用 LLM 提取信息（mock 模拟）
    trial_data = extract_fields(text)

    # 增加文件路径与更新时间字段
    trial_data["source_file"] = uploaded_file.name
    trial_data["update_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 显示结果
    st.subheader("🔎 提取结果")
    st.json(trial_data)

    # 存入数据库
    insert_or_update_drug(trial_data, DB_PATH)
    st.success("✅ 数据已保存（自动创建或更新）")


st.markdown("---")
st.subheader("📤 导出数据")

if st.button("导出为 CSV"):
    conn = sqlite3.connect("data/drugs.db")
    df = pd.read_sql_query("SELECT * FROM trial_data", conn)
    conn.close()

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 点击下载 CSV",
        data=csv,
        file_name='trial_data_export.csv',
        mime='text/csv'
)