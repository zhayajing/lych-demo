import streamlit as st
import pandas as pd
import numpy as np
import os
from PIL import Image, ImageEnhance
import matplotlib.pyplot as plt
import qrcode
from random import randint, uniform, choice

# ===================== 页面配置 =====================
st.set_page_config(page_title="诚信教育案例 - 荔枝混装实验", layout="wide")
st.title("🍒 诚信教育案例：30% 混装荔枝可视化实验")
st.markdown(
    """
    **教学目标：**  
    学生通过上传不同类型荔枝图片，观察“30%混装”带来的视觉影响，  
    从中体会诚信在国际贸易中的重要性。
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

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{uploaded_file.name},{type_choice}\n")

        st.success("✅ 上传成功！右侧展示区将自动更新。")

    st.divider()
    st.subheader("📲 扫码参与上传（课堂展示用）")

    qr_url = "https://lychee-demo-yourname.streamlit.app"  # 部署后改成你自己的链接
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

            # --- 生成混装叠加效果 ---
            canvas_size = 800
            mixed = Image.new("RGBA", (canvas_size, canvas_size), (255, 255, 255, 255))

            # 按比例确定混合数量（30% 其他类型）
            ratio = 0.3
            num_other = max(1, int(total * ratio))
            num_feizixiao = max(1, total - num_other)

            # 分组路径
            group_fx = df[df["type"] == "妃子笑"]["filename"].tolist()
            group_other = df[df["type"] == "其他类型"]["filename"].tolist()

            selected_fx = [choice(group_fx)] * num_feizixiao if group_fx else []
            selected_ot = [choice(group_other)] * num_other if group_other else []

            selected_files = selected_fx + selected_ot
            np.random.shuffle(selected_files)

            for img_path in selected_files:
                try:
                    img = Image.open(os.path.join(UPLOAD_DIR, img_path)).convert("RGBA")

                    # 随机缩放、旋转
                    scale = uniform(0.4, 1.0)
                    new_size = (int(img.width * scale), int(img.height * scale))
                    img = img.resize(new_size)
                    img = img.rotate(uniform(-20, 20), expand=True)

                    # 类别颜色区分
                    if img_path in selected_ot:
                        enhancer = ImageEnhance.Color(img)
                        img = enhancer.enhance(0.6)  # 让“其他类型”偏灰红，区分明显

                    # 随机透明度
                    alpha = img.split()[3]
                    alpha = alpha.point(lambda p: p * uniform(0.5, 0.9))
                    img.putalpha(alpha)

                    # 随机位置
                    x = randint(0, canvas_size - new_size[0])
                    y = randint(0, canvas_size - new_size[1])

                    mixed.alpha_composite(img, (x, y))

                except Exception as e:
                    print("跳过图片:", img_path, e)

            st.image(mixed.convert("RGB"), caption="🍒 模拟混装荔枝效果（30% 其他类型）")

        else:
            st.info("等待学生上传图片中……")
    else:
        st.info("等待学生上传图片中……")

