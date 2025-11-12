import streamlit as st
import pandas as pd
import numpy as np
import os
from PIL import Image, ImageOps
import qrcode
import random

# ================== 页面设置 ==================
st.set_page_config(page_title="荔枝智能混装实验", layout="wide")
st.title("🍒 荔枝智能混装实验（70% 妃子笑 + 30% 其他）")
st.markdown(
    "上传不同类型的荔枝图片，系统将智能生成一张真实果堆照片，模拟混装效果。"
)

UPLOAD_DIR = "uploads"
LOG_FILE = "upload_log.csv"
os.makedirs(UPLOAD_DIR, exist_ok=True)

left, right = st.columns([1, 2])

# ---------------- 左侧上传区 ----------------
with left:
    st.subheader("📲 上传入口")
    uploaded_file = st.file_uploader("上传荔枝图片", type=["jpg", "jpeg", "png"])
    type_choice = st.radio("请选择荔枝类型：", ["妃子笑", "其他类型"])

    if uploaded_file:
        img = Image.open(uploaded_file).convert("RGBA")
        img.save(os.path.join(UPLOAD_DIR, uploaded_file.name))
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{uploaded_file.name},{type_choice}\n")
        st.success("✅ 上传成功！右侧效果图将自动更新。")

    st.divider()
    st.subheader("📷 扫码上传")
    qr_url = "https://lychee-demo-yourname.streamlit.app"
    qr_img = qrcode.make(qr_url).convert("RGB")
    st.image(qr_img, caption="学生扫码上传")

    st.divider()
    if st.button("🔄 重置所有数据"):
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
        for f in os.listdir(UPLOAD_DIR):
            os.remove(os.path.join(UPLOAD_DIR, f))
        st.warning("✅ 数据已清空，可重新开始实验。")

# ---------------- 右侧展示区 ----------------
with right:
    st.subheader("🍒 智能混装果堆图")

    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE, names=["filename", "type"])
        if len(df) >= 2:
            group_fx = df[df["type"] == "妃子笑"]["filename"].tolist()
            group_other = df[df["type"] == "其他类型"]["filename"].tolist()

            if group_fx and group_other:
                # 70% 妃子笑 + 30% 其他
                total = 25
                n_fx = int(total * 0.7)
                n_ot = total - n_fx

                fx_samples = random.choices(group_fx, k=n_fx)
                ot_samples = random.choices(group_other, k=n_ot)
                all_samples = fx_samples + ot_samples
                random.shuffle(all_samples)

                # 创建画布
                canvas_size = 800
                canvas = Image.new("RGBA", (canvas_size, canvas_size), (255, 255, 255, 255))

                for i, fname in enumerate(all_samples):
                    try:
                        img = Image.open(os.path.join(UPLOAD_DIR, fname)).convert("RGBA")
                        # 缩放荔枝
                        scale = random.uniform(0.25, 0.4)
                        new_size = (int(img.width * scale), int(img.height * scale))
                        img = img.resize(new_size, Image.LANCZOS)

                        # 随机羽化边缘（让融合更自然）
                        mask = Image.new("L", img.size, 255)
                        feather = 40
                        mask = ImageOps.expand(mask, border=-feather)
                        mask = mask.resize(img.size, Image.LANCZOS)
                        img.putalpha(mask)

                        # 随机位置放置
                        x = random.randint(0, canvas_size - new_size[0])
                        y = random.randint(0, canvas_size - new_size[1])

                        canvas.alpha_composite(img, (x, y))
                    except Exception as e:
                        print("跳过图片:", fname, e)

                result = canvas.convert("RGB")
                st.image(result, caption="智能混装荔枝效果图（自然融合）", use_column_width=True)
            else:
                st.info("请至少上传一张妃子笑和其他类型图片。")
        else:
            st.info("请上传至少两类图片。")
    else:
        st.info("等待学生上传图片中……")
