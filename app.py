import streamlit as st
from docx import Document
import io

# 页面基础设置
st.set_page_config(page_title="稿件收集大纲识别器", layout="centered")

st.title("📄 组员稿件大纲识别器")
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