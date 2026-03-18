import streamlit as st
import os
import json
import pandas as pd
import plotly.express as px
import vertexai
from vertexai.generative_models import GenerativeModel, Part
# ================= 1. 物理挂载核弹钥匙 =================
KEY_PATH = "vertex-key.json"

# 【极客新增：云端自动锻造钥匙】
# 如果是在云服务器上，物理文件不存在，我们就从保险箱里把文本拿出来，当场写一个文件！
if not os.path.exists(KEY_PATH):
    with open(KEY_PATH, "w") as f:
        f.write(st.secrets["GOOGLE_JSON"])

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_PATH

# 自动提取 Project ID
try:
    with open(KEY_PATH, "r") as f:
        key_data = json.load(f)
        PROJECT_ID = key_data["project_id"]
except Exception as e:
    st.error(f"🚨 致命错误：读取密钥失败！请检查 Secrets 配置。错误信息: {e}")
    st.stop()

# 点火：初始化谷歌云 Vertex AI 引擎
vertexai.init(project=PROJECT_ID, location="us-central1")
# 召唤最强性价比/速度的 Gemini 3。1 大模型
model = GenerativeModel("gemini-2.5-pro")

# ================= 2. 赛博朋克前端装潢 (CSS 注入) =================
st.set_page_config(page_title="Geek AI 核心控制台", page_icon="🌌", layout="wide")

# 强制注入暗黑极客风 CSS
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #00FF41; }
    h1, h2, h3 { color: #00FF41 !important; font-family: 'Courier New', Courier, monospace; }
    .stChatMessage { border-radius: 10px; border: 1px solid #333; margin-bottom: 10px; }
    .stButton>button { border: 1px solid #00FF41; color: #00FF41; background-color: transparent; border-radius: 8px; transition: 0.3s; }
    .stButton>button:hover { background-color: #00FF41; color: #000; box-shadow: 0 0 10px #00FF41; }
</style>
""", unsafe_allow_html=True)

st.title("🌌 Geek AI 云端控制台 (Vertex 引擎)")
st.caption("⚡ 算力核心: Gemini 3.1 Pro | 状态: 300刀 API 全功率输出 | 密级: 最高")

# ================= 3. 炫技控制台 (数据可视化) =================
with st.sidebar:
    st.markdown("---")
    st.subheader("📂 多模态解析舱")
    # 允许小白朋友上传图片和 PDF
    uploaded_file = st.file_uploader("上传需分析的图片/文档", type=["png", "jpg", "jpeg", "pdf"])
    if uploaded_file:
        st.success(f"已锁定目标: {uploaded_file.name}，准备解析！")
    st.header("🛠️ 降维打击控制台")
    st.markdown("给小白朋友展示一下什么叫真正的全栈开发：")
    
    if st.button("📊 开启全息数据大屏 (炫技专用)"):
        st.session_state.show_chart = True
    
    if st.button("🧹 清空当前对话"):
        st.session_state.messages = []
        st.session_state.show_chart = False
        st.rerun()

# 处理可视化炫技逻辑
if st.session_state.get("show_chart", False):
    st.subheader("📈 模拟实时全球算力监控 (动态生成)")
    # 随便捏造一点炫酷的假数据用来画图
    df = pd.DataFrame({
        "节点": ["东京", "硅谷", "新加坡", "伦敦", "法兰克福"],
        "算力负荷 (%)": [85, 92, 78, 65, 88],
        "延迟 (ms)": [24, 12, 35, 80, 45]
    })
    # 用 Plotly 画一个高级的可交互气泡图
    fig = px.scatter(df, x="节点", y="算力负荷 (%)", size="延迟 (ms)", color="节点", 
                     hover_name="节点", size_max=40, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

# ================= 4. 核心对话中枢 =================
if "messages" not in st.session_state:
    st.session_state.messages = []

# 渲染历史记忆
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 接收用户指令
if prompt := st.chat_input("输入你的指令，呼叫 Gemini 核弹..."):
    # 显示用户消息
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 带着历史记录去请求 Vertex AI
    with st.chat_message("assistant"):
        with st.spinner("信号正在穿越太平洋，呼叫谷歌云..."):
            try:
                # 组装上下文，由于 Vertex SDK 接收文本流比较特殊，咱们简单点，把历史拼接起来
                context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
                
               # 判断用户有没有上传文件
                if uploaded_file is not None:
                    # 识别是图片还是 PDF
                    mime_type = "application/pdf" if uploaded_file.name.lower().endswith("pdf") else "image/jpeg"
                    # 把文件转成 Vertex AI 能吃的数据块 (Part)
                    file_part = Part.from_data(data=uploaded_file.getvalue(), mime_type=mime_type)
                    
                    # 将文件和聊天的上下文打包在一起发射
                    response = model.generate_content([file_part, context])
                else:
                    # 没传文件，就纯聊天
                    response = model.generate_content(context)
                bot_reply = response.text
                
                st.markdown(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                st.error(f"🚨 连接中断！错误信息: {e}")
