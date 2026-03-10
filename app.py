import streamlit as st
from docx import Document
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# --- 1. 配置区（请把引号里换成你自己的 ID） ---
FOLDER_ID = "zhoujihui@long-loop-489815-v6.iam.gserviceaccount.com"

# --- 2. 网页基础设置 ---
st.set_page_config(page_title="cathy-word", layout="centered")
st.title("📁 upload and analyze")
st.info("提示：上传后点击『提交并保存』，文件会自动同步到我的 Google Drive。")

# --- 3. 连接 Google Drive 服务 ---
def get_drive_service():
    # 从 Streamlit Secrets 读取钥匙
    info = st.secrets["gcp_service_account"]
    creds = service_account.Credentials.from_service_account_info(info)
    return build('drive', 'v3', credentials=creds)

# --- 4. 网页主体逻辑 ---
uploaded_file = st.file_uploader("点击或拖拽上传 Word 文档", type="docx")

if uploaded_file is not None:
    # 先读取文件内容
    file_bytes = uploaded_file.read()
    doc = Document(io.BytesIO(file_bytes))
    
    st.success(f"已加载文件：{uploaded_file.name}")
    
    # 功能 A：识别大纲
    st.subheader("📌 识别到的大纲框架：")
    has_heading = False
    for p in doc.paragraphs:
        if "Heading" in p.style.name:
            level = "".join(filter(str.isdigit, p.style.name))
            indent = "　" * (int(level)-1) if level else ""
            st.write(f"{indent}● **{p.text}**")
            has_heading = True
    
    if not has_heading:
        st.warning("⚠️ 该组员未正确使用 Word 标题样式，无法识别大纲。")

    # 功能 B：点击按钮保存到云端
    if st.button("🚀 确认提交并保存到云端"):
        try:
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
            st.success("✅ 文件已成功同步到你的 Google Drive 文件夹！")
        except Exception as e:
            st.error(f"同步失败，请检查配置或 Secrets 设置。错误信息：{e}")

    # 功能 C：预览正文
    with st.expander("点此预览正文"):
        for p in doc.paragraphs:
            if p.text.strip():
                st.text(p.text)
