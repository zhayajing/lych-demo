import streamlit as st
import pandas as pd
import numpy as np
import os
from PIL import Image, ImageEnhance
import matplotlib.pyplot as plt
import qrcode

# ===================== 页面配置 =====================
st.set_page_config(page_title="诚信教育案例 - 荔枝混装实验", layout="wide")
st.title("🍒 诚信教育案例：30% 混装荔枝可视化实验")
st.markdown(
    """
    **教学目标：**  
    通过上传不同类型荔枝图片，观察“30%混装”带来的视觉变化，理解诚信在国际贸易中的重要性。
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

        # 保存上传记录
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

            st.markdown(f"**当前已上传总数：{total} 张图片**")

            # 分类图片
            group_fx = df[df["type"] == "妃子笑"]["filename"].tolist()
            group_other = df[df["type"] == "其他类型"]["filename"].tolist()

            if len(group_fx) > 0 and len(group_other) > 0:
                # 按比例混合图像
                img_fx = [Image.open(os.path.join(UPLOAD_DIR, f)).resize((400, 400)).convert("RGB") for f in group_fx]
                img_ot = [Image.open(os.path.join(UPLOAD_DIR, f)).resize((400, 400)).convert("RGB") for f in group_other]

                # 计算平均图像
                def average_image(imgs):
                    arrs = [np.array(i, dtype=np.float32) for i in imgs]
                    return np.mean(arrs, axis=0)

                avg_fx = average_image(img_fx)
                avg_ot = average_image(img_ot)

                # 混合比例：70% 妃子笑 + 30% 其他类型
                mixed_arr = avg_fx * 0.7 + avg_ot * 0.3
                mixed_arr = np.clip(mixed_arr, 0, 255).astype(np.uint8)
                mixed_img = Image.fromarray(mixed_arr)

                st.image(mixed_img, caption="🍒 模拟混装荔枝效果（70% 妃子笑 + 30% 其他）")

            elif len(group_fx) == 0:
                st.warning("请先上传一些【妃子笑】图片")
            elif len(group_other) == 0:
                st.warning("请先上传一些【其他类型】图片")

        else:
            st.info("等待学生上传图片中……")
    else:
        st.info("等待学生上传图片中……")
