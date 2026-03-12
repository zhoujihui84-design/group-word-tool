import streamlit as st
from docx import Document
import io
import json  # 必须加这一行
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# --- 1. 配置区 ---
# 确保引号里是你那个 Google Drive 文件夹的 ID
FOLDER_ID = "1qkgnZ5LNbyso8MFH76xu6oAIj1ljvNn-" 

# --- 2. 网页基础设置 ---
st.set_page_config(page_title="cathy-words-co", layout="centered")
st.title("📁 analyze")

# --- 3. 连接 Google Drive 服务（修复了报错的关键点） ---
def get_drive_service():
    info = st.secrets["gcp_service_account"]
    
    # 核心修复：如果 info 是字符串（带引号的），就把它转成 Python 字典
    if isinstance(info, str):
        info = json.loads(info)
        
    creds = service_account.Credentials.from_service_account_info(info)
    return build('drive', 'v3', credentials=creds)

# --- 4. 网页主体逻辑 ---
uploaded_file = st.file_uploader("点击或拖拽上传 Word 文档", type="docx")

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    doc = Document(io.BytesIO(file_bytes))
    
    st.success(f"✅ 已加载：{uploaded_file.name}")
    
    # 识别大纲
    st.subheader("📌 识别到的大纲框架：")
    has_heading = False
    for p in doc.paragraphs:
        if "Heading" in p.style.name:
            level = "".join(filter(str.isdigit, p.style.name))
            indent = "　" * (int(level)-1) if level else ""
            st.write(f"{indent}● **{p.text}**")
            has_heading = True
    
    if not has_heading:
        st.warning("⚠️ 该组员未正确使用 Word 标题样式。")

    # 同步按钮
    if st.button("🚀 确认提交并保存到云端"):
        try:
            with st.spinner("正在同步到云端..."):
                service = get_drive_service()
                file_metadata = {
                    'name': uploaded_file.name,
                    'parents': [FOLDER_ID]
                }
                media = MediaIoBaseUpload(
                    io.BytesIO(file_bytes), 
                    mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )
                service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                st.balloons()
                st.success("成功！文件已存入 Google Drive。")
        except Exception as e:
            st.error(f"同步失败，请检查配置。错误：{e}")

    # 预览
    with st.expander("点此预览正文"):
        for p in doc.paragraphs:
            if p.text.strip():
                st.write(p.text)
