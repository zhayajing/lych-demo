import streamlit as st
import pandas as pd
import numpy as np
import os
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt
import qrcode

# --- 页面基本设置 ---
st.set_page_config(page_title="诚信与混装实验 - 荔枝案例", layout="wide")

st.title("🍒 诚信教育案例：30% 混装荔枝的视觉化实验")
st.markdown("#### 通过上传不同类型荔枝图片，观察‘混装’对整体品质的影响")

# --- 创建文件保存目录 ---
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- 左右布局 ---
left_col, right_col = st.columns([1, 2])

# =====================
# 左侧：二维码 + 上传区
# =====================
with left_col:
    st.subheader("📱 学生上传区")

    # 上传组件
    uploaded_file = st.file_uploader("请上传荔枝图片（妃子笑 / 其他）", type=["jpg", "png", "jpeg"])

    # 类型选择
    type_choice = st.radio("请选择荔枝类型：", ["妃子笑", "其他类型"])

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        img.save(file_path)
        # 保存图片记录
        with open("upload_log.csv", "a", encoding="utf-8") as f:
            f.write(f"{uploaded_file.name},{type_choice}\n")
        st.success("✅ 上传成功！请等待右侧展示区更新。")

    st.divider()
    st.subheader("📲 扫码参与（可用于课堂展示）")

    # 生成二维码（指向当前本地/公网地址）
    qr_url = "http://localhost:8501"  # 部署后改成公网地址
    qr_img = qrcode.make(qr_url)
    st.image(qr_img, caption="学生扫码上传入口")

# =====================
# 右侧：热力图 + 数据统计
# =====================
with right_col:
    st.subheader("📊 实时混装展示区")

    if os.path.exists("upload_log.csv"):
        df = pd.read_csv("upload_log.csv", names=["filename", "type"])
        total = len(df)
        if total > 0:
            counts = df["type"].value_counts()
            fig, ax = plt.subplots()
            ax.pie(counts, labels=counts.index, autopct=lambda p: f"{p:.1f}%")
            ax.set_title("上传图片类型比例")
            st.pyplot(fig)

            # 展示随机混合热力图
            imgs = []
            for file in os.listdir(UPLOAD_DIR):
                path = os.path.join(UPLOAD_DIR, file)
                try:
                    imgs.append(Image.open(path).resize((100, 100)))
                except:
                    pass

            if imgs:
                n = int(np.ceil(np.sqrt(len(imgs))))
                collage = Image.new("RGB", (n*100, n*100))
                for i, img in enumerate(imgs):
                    collage.paste(img, ((i % n)*100, (i // n)*100))
                st.image(collage, caption="混装荔枝效果（学生上传实时生成）")
        else:
            st.info("等待学生上传图片中……")
    else:
        st.info("等待学生上传图片中……")
