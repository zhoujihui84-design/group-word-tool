import streamlit as st
from docx import Document
import io

# 页面基础设置
st.set_page_config(page_title="cathy-word-check", layout="centered")

st.title("📄 三国演义 group-word")
st.info("功能：上传 .docx 文件，自动识别文档里的标题框架（需使用Word标题样式）。")

# 文件上传组件
uploaded_file = st.file_uploader("点击或拖拽上传 Word 文档", type="docx")

if uploaded_file is not None:
    try:
        # 读取文件
        doc = Document(io.BytesIO(uploaded_file.read()))
        st.success(f"✅ 已识别文件：{uploaded_file.name}")
        
        # 提取大纲逻辑
        st.subheader("📌 识别到的大纲框架：")
        has_heading = False
        import streamlit as st
from docx import Document
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# --- 配置区 ---
# 填入你 Google Drive 文件夹的 ID（在浏览器地址栏末尾那一串字符）
FOLDER_ID = "zhoujihui@long-loop-489815-v6.iam.gserviceaccount.com"

# 网页设置
st.set_page_config(page_title="稿件同步工具", layout="centered")
st.title("📁 稿件上传并同步至云端")

# 1. 认证 Google Drive (从 Streamlit 的 Secrets 中读取)
try:
    g_credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
    drive_service = build('drive', 'v3', credentials=g_credentials)
except Exception as e:
    st.error("云端配置未完成，请检查 Secrets 设置。")

uploaded_file = st.file_uploader("上传 Word 文档", type="docx")

if uploaded_file is not None:
    # --- 逻辑 A：显示大纲（保留你之前喜欢的功能） ---
    file_content = uploaded_file.read()
    doc = Document(io.BytesIO(file_content))
    st.success(f"已加载：{uploaded_file.name}")
    
    with st.expander("查看识别到的大纲"):
        for p in doc.paragraphs:
            if "Heading" in p.style.name:
                level = "".join(filter(str.isdigit, p.style.name))
                indent = "　" * (int(level)-1) if level else ""
                st.write(f"{indent}● **{p.text}**")

    # --- 逻辑 B：同步到 Google Drive ---
    if st.button("确认提交并保存到云端"):
        with st.spinner("正在同步到 Google Drive..."):
            file_metadata = {
                'name': uploaded_file.name,
                'parents': [FOLDER_ID]
            }
            media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            
            drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            st.balloons()
            st.success("✅ 同步成功！文件已存入 Google Drive。")
        for para in doc.paragraphs:
            # 检查段落样式是否包含 "Heading"（即：标题 1, 标题 2 等）
            if "Heading" in para.style.name:
                # 提取数字级别（如 Heading 1 提取出 1）
                level_str = "".join(filter(str.isdigit, para.style.name))
                level = int(level_str) if level_str else 1
                
                # 用全角空格做缩进，方便看层级
                indent = "　" * (level - 1)
                st.write(f"{indent}**{para.text}**")
                has_heading = True
        
        if not has_heading:
            st.warning("⚠️ 这位组员没有用 Word 的『标题样式』排版，我没法自动识别框架。")
            
        # 正文预览功能
        with st.expander("点此预览正文内容"):
            for para in doc.paragraphs:
                if para.text.strip():
                    st.text(para.text)
                    
    except Exception as e:
        st.error(f"处理文件时出错：{e}")

else:
    st.write("等待上传中...")
