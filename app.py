import streamlit as st
import pandas as pd
import numpy as np
import os
from PIL import Image
import qrcode
import random

# ============ 页面设置 ============
st.set_page_config(page_title="荔枝混装实验", layout="wide")
st.title("🍒 荔枝混装实验（70% 妃子笑 + 30% 其他）")
st.markdown(
    """
    上传不同类型的荔枝图片，系统会自动生成一张“混装果堆图”，  
    展示两种荔枝混放后的实际视觉效果。
    """
)

UPLOAD_DIR = "uploads"
LOG_FILE = "upload_log.csv"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ============ 页面布局 ============
left, right = st.columns([1, 2])

# ---------------- 左侧上传区 ----------------
with left:
    st.subheader("📲 上传入口")

    uploaded_file = st.file_uploader("请上传荔枝图片（妃子笑 / 其他类型）", type=["jpg", "jpeg", "png"])
    type_choice = st.radio("请选择荔枝类型：", ["妃子笑", "其他类型"])

    if uploaded_file is not None:
        img = Image.open(uploaded_file).convert("RGB")
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        img.save(file_path)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{uploaded_file.name},{type_choice}\n")
        st.success("✅ 上传成功！右侧混装图将自动更新。")

    st.divider()
    st.subheader("📷 学生扫码上传")
    qr_url = "https://lych-demo-5gk9t8rb34wwy8ofu6euph.streamlit.app"
    qr_img = qrcode.make(qr_url).convert("RGB")
    st.image(qr_img, caption="扫码上传入口")

    st.divider()
    if st.button("🔄 重置所有数据"):
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
        for f in os.listdir(UPLOAD_DIR):
            os.remove(os.path.join(UPLOAD_DIR, f))
        st.warning("✅ 已清空所有上传记录与图片。")

# ---------------- 右侧展示区 ----------------
with right:
    st.subheader("🍒 混装荔枝果堆效果图")

    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE, names=["filename", "type"])
        if len(df) >= 2:
            group_fx = df[df["type"] == "妃子笑"]["filename"].tolist()
            group_other = df[df["type"] == "其他类型"]["filename"].tolist()

            if group_fx and group_other:
                # 取 70% 妃子笑 + 30% 其他
                total_tiles = 100
                n_fx = int(total_tiles * 0.7)
                n_other = total_tiles - n_fx

                fx_samples = random.choices(group_fx, k=n_fx)
                ot_samples = random.choices(group_other, k=n_other)
                all_samples = fx_samples + ot_samples
                random.shuffle(all_samples)

                # 拼接成“果堆图”
                tile_size = 100
                grid = 10
                collage = Image.new("RGB", (tile_size * grid, tile_size * grid))

                for idx, fname in enumerate(all_samples):
                    try:
                        img = Image.open(os.path.join(UPLOAD_DIR, fname)).convert("RGB")
                        img = img.resize((tile_size, tile_size))
                        x = (idx % grid) * tile_size
                        y = (idx // grid) * tile_size
                        collage.paste(img, (x, y))
                    except Exception as e:
                        print("跳过", fname, e)

                st.image(collage, caption="混装荔枝果堆图（70% 妃子笑 + 30% 其他类型）")
            else:
                st.info("请至少上传一种【妃子笑】和【其他类型】图片。")
        else:
            st.info("请上传至少两类荔枝图片。")
    else:
        st.info("等待学生上传图片中……")



