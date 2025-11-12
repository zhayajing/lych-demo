import streamlit as st
import pandas as pd
import numpy as np
import os
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import qrcode
from sklearn.cluster import KMeans

# ===================== 页面配置 =====================
st.set_page_config(page_title="诚信教育案例 - 荔枝混装实验", layout="wide")
st.title("🍒 诚信教育案例：30% 混装荔枝热力图实验")
st.markdown(
    """
    **教学目标：**  
    学生通过上传不同品种的荔枝图片，观察“30%混装”后整体颜色的变化，  
    直观理解诚信缺失对产品品质的影响。
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

        st.success("✅ 上传成功！右侧热力图将自动更新。")

    st.divider()
    st.subheader("📲 扫码参与上传（课堂展示用）")

    qr_url = "https://lychee-demo-yourname.streamlit.app"  # 部署后换成你的链接
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
        st.warning("已清空所有上传记录与图片，实验可重新开始。")

# ===================== 右侧展示区 =====================
with right_col:
    st.subheader("📊 实时混装热力图展示")

    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE, names=["filename", "type"])
        total = len(df)

        if total > 0:
            counts = df["type"].value_counts()

            st.markdown(f"**当前已上传总数：{total} 张图片**")

            # 饼图展示比例
            fig, ax = plt.subplots()
            ax.pie(counts, labels=counts.index, autopct=lambda p: f"{p:.1f}%", startangle=90)
            ax.set_title("荔枝类型比例（实时更新）")
            st.pyplot(fig)

            # 获取图片路径
            group_fx = df[df["type"] == "妃子笑"]["filename"].tolist()
            group_other = df[df["type"] == "其他类型"]["filename"].tolist()

            if len(group_fx) > 0 and len(group_other) > 0:
                # 读取图片主色（KMeans提取 dominant color）
                def dominant_color(img_path):
                    img = Image.open(img_path).resize((100, 100)).convert("RGB")
                    pixels = np.array(img).reshape(-1, 3)
                    kmeans = KMeans(n_clusters=1, n_init=3)
                    kmeans.fit(pixels)
                    return kmeans.cluster_centers_[0]

                fx_colors = np.array([dominant_color(os.path.join(UPLOAD_DIR, f)) for f in group_fx])
                ot_colors = np.array([dominant_color(os.path.join(UPLOAD_DIR, f)) for f in group_other])

                # 按比例混合颜色
                n_points = 500
                fx_ratio, ot_ratio = 0.7, 0.3
                fx_points = fx_colors[np.random.choice(len(fx_colors), int(n_points * fx_ratio))]
                ot_points = ot_colors[np.random.choice(len(ot_colors), int(n_points * ot_ratio))]
                all_points = np.vstack((fx_points, ot_points))

                # 生成热力图（颜色分布）
                heat_size = 300
                heat_map = np.zeros((heat_size, heat_size, 3), dtype=np.float32)
                for color in all_points:
                    x, y = np.random.randint(0, heat_size, 2)
                    heat_map[x, y] = color / 255.0

                # 模糊生成热力视觉
                from scipy.ndimage import gaussian_filter
                heat_map_blur = gaussian_filter(heat_map, sigma=8)

                # 归一化显示
                heat_map_blur = np.clip(heat_map_blur / np.max(heat_map_blur), 0, 1)

                fig2, ax2 = plt.subplots()
                ax2.imshow(heat_map_blur)
                ax2.axis("off")
                ax2.set_title("🍒 模拟混装荔枝颜色热力图（70% 妃子笑 + 30% 其他）")
                st.pyplot(fig2)

            else:
                st.warning("请至少上传一种【妃子笑】和【其他类型】图片。")

        else:
            st.info("等待学生上传图片中……")
    else:
        st.info("等待学生上传图片中……")
