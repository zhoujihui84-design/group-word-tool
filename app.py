import streamlit as st
from docx import Document
import io
import requests
import base64

# --- 1. 配置区 ---
# 这里的名字要和你在 Streamlit Secrets 里的名字一模一样
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["GITHUB_REPO"]

st.set_page_config(page_title="Cathy-word", layout="centered")
st.title("📁 upload and analyze")
st.markdown("### 提示：上传后**务必点击**下方的同步按钮")

# --- 2. 网页主体逻辑 ---
uploaded_file = st.file_uploader("点击或拖拽上传 Word 文档", type="docx")

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    doc = Document(io.BytesIO(file_bytes))
    
    st.success(f"✅ 已加载文件：{uploaded_file.name}")
    
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
        st.warning("⚠️ 没检测到标题样式，请提醒组员使用 Word 的『标题』样式。")

    # --- 关键：同步按钮 ---
    if st.button("🚀 确认提交并同步到 GitHub"):
        try:
            with st.spinner("正在全力同步中..."):
                # 将文件转为 Base64 格式发送给 GitHub
                content = base64.b64encode(file_bytes).decode("utf-8")
                path = f"uploads/{uploaded_file.name}"
                url = f"https://api.github.com/repos/{REPO}/contents/{path}"
                
                headers = {
                    "Authorization": f"token {TOKEN}",
                    "Accept": "application/vnd.github.v3+json"
                }
                data = {
                    "message": f"Upload {uploaded_file.name} via Streamlit",
                    "content": content
                }
                
                # 发送请求
                res = requests.put(url, headers=headers, json=data)
                
                if res.status_code in [200, 201]:
                    st.balloons()
                    st.success("🎉 太棒了！文件已经成功存入你的 GitHub 仓库。")
                else:
                    st.error(f"同步失败，GitHub 报错：{res.json().get('message')}")
        except Exception as e:
            st.error(f"发生错误：{e}")

    # 预览
    with st.expander("点此预览正文"):
        for p in doc.paragraphs:
            if p.text.strip():
                st.write(p.text)
