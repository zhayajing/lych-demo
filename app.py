import streamlit as st
import pandas as pd
import numpy as np
import os
from PIL import Image
import matplotlib.pyplot as plt
import qrcode

# ============ 页面配置 ============
st.set_page_config(page_title="诚信教育案例 - 荔枝混装实验", layout="wide")
st.title("🍒 诚信教育案例：30% 混装荔枝可视化实验")
st.markdown("通过上传不同类型荔枝图片，直观观察“混装”对整体品质的影响。")

# ============ 初始化目录 ============
UPLOAD_DIR = "uploads"
LOG_FILE = "upload_log.csv"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ============ 页面布局 ============
left_col, right_col = st.columns([1, 2])

# =======================
# 左侧：上传入口 + 二维码
# =======================
with left_col:
    st.subheader("📱 学生上传区")

    uploaded_file = st.file_uploader("请上传荔枝图片（妃子笑 / 其他）", type=["jpg", "jpeg", "png"])
    type_choice = st.radio("请选择荔枝类型：", ["妃子笑", "其他类型"])

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        img.save(file_path)

        # 保存记录
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{uploaded_file.name},{type_choice}\n")

        st.success("✅ 上传成功！右侧展示区将自动更新。")

    st.divider()
    st.subheader("📲 扫码参与上传（课堂展示用）")

    # ✅ 生成二维码（修复版本）
    qr_url = "https://lychee-demo-yourname.streamlit.app"  # 部署后改成你的链接
    qr_img = qrcode.make(qr_url)
    qr_pil = Image.new("RGB", qr_img.size, "white")
    qr_pil.paste(qr_img)

    st.image(qr_pil, caption="学生扫码上传入口")

# =======================
# 右侧：数据展示 + 可视化
# =======================
with right_col:
    st.subheader("📊 实时混装展示区")

    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE, names=["filename", "type"])
        total = len(df)

        if total > 0:
            counts = df["type"].value_counts()
            fig, ax = plt.subplots()
            ax.pie(counts, labels=counts.index, autopct=lambda p: f"{p:.1f}%", startangle=90)
            ax.set_title("上传荔枝类型比例")
            st.pyplot(fig)

            # 展示混装效果图（拼贴）
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
                st.image(collage, caption="混装荔枝效果图（学生上传实时生成）")

        else:
            st.info("等待学生上传图片中……")
    else:
        st.info("等待学生上传图片中……")
