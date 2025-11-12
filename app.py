import streamlit as st
import pandas as pd
import numpy as np
import os
from PIL import Image
import matplotlib.pyplot as plt
import qrcode

# ===================== 页面配置 =====================
st.set_page_config(page_title="诚信教育案例 - 荔枝混装实验", layout="wide")
st.title("🍒 诚信教育案例：30% 混装荔枝可视化实验")
st.markdown(
    """
    **教学目标：**  
    通过上传不同类型荔枝图片，观察“混装”带来的视觉变化，理解诚信在商业中的价值。  
    """
)

# ===================== 初始化目录 =====================
UPLOAD_DIR = "uploads"
LOG_FILE = "upload_log.csv"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ===================== 页面布局 =====================
left_col, right_col = st.columns([1, 2])

# ===================== 左侧上传区 =====================
with left_col:
    st.subheader("📱 学生上传区")

    uploaded_file = st.file_uploader("请上传荔枝图片（妃子笑 / 其他）", type=["jpg", "jpeg", "png"])
    type_choice = st.radio("请选择荔枝类型：", ["妃子笑", "其他类型"])

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        img.save(file_path)

        # 记录上传日志
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{uploaded_file.name},{type_choice}\n")

        st.success("✅ 上传成功！右侧展示区将自动更新。")

    st.divider()
    st.subheader("📲 扫码参与上传（课堂展示用）")

    qr_url = "https://lychee-demo-yourname.streamlit.app"  # 部署后改成你自己的 Streamlit 链接
    qr_img = qrcode.make(qr_url).convert("RGB")
    qr_pil = Image.new("RGB", qr_img.size, "white")
    qr_pil.paste(qr_img)
    st.image(qr_pil, caption="学生扫码上传入口")

    st.divider()
    st.subheader("🧹 教师工具区")
    if st.button("🔄 重置所有上传数据"):
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
        for f in os.listdir(UPLOAD_DIR):
            os.remove(os.path.join(UPLOAD_DIR, f))
        st.warning("已清空所有上传记录与图片！课堂实验可重新开始。")

# ===================== 右侧展示区 =====================
with right_col:
    st.subheader("📊 实时混装展示区")

    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE, names=["filename", "type"])
        total = len(df)

        if total > 0:
            counts = df["type"].value_counts()

            # ----- 上传统计 -----
            st.markdown(f"**当前已上传总数：{total} 张图片**")

            # ----- 拼贴展示 -----
            imgs = []
            for file in os.listdir(UPLOAD_DIR):
                path = os.path.join(UPLOAD_DIR, file)
                try:
                    imgs.append(Image.open(path).resize((100, 100)))
                except:
                    pass

            if imgs:
                n = int(np.ceil(np.sqrt(len(imgs))))
                collage = Image.new("RGB", (n * 100, n * 100))
                for i, img in enumerate(imgs):
                    collage.paste(img, ((i % n) * 100, (i // n) * 100))
                st.image(collage, caption="混装荔枝效果图（学生上传实时生成）")

        else:
            st.info("等待学生上传图片中……")
    else:
        st.info("等待学生上传图片中……")

