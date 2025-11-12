import streamlit as st
import pandas as pd
import numpy as np
import os
from PIL import Image
import qrcode
from sklearn.cluster import KMeans
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt

# ============ 页面设置 ============
st.set_page_config(page_title="诚信教育案例 - 荔枝混装热力图", layout="wide")
st.title("🍒 荔枝混装可视化实验：30% 混装效果展示")
st.markdown(
    """
    **教学目标：**  
    学生上传荔枝图片（妃子笑 / 其他类型），系统自动生成混装热力图，  
    直观展示“30%混装”后整体色彩变化，体会诚信缺失带来的品质差异。
    """
)

# ============ 初始化 ============
UPLOAD_DIR = "uploads"
LOG_FILE = "upload_log.csv"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ============ 页面布局 ============
left, right = st.columns([1, 2])

# ---------------- 左侧上传区 ----------------
with left:
    st.subheader("📲 上传入口")

    uploaded_file = st.file_uploader("请上传荔枝图片（妃子笑 / 其他）", type=["jpg", "jpeg", "png"])
    type_choice = st.radio("请选择荔枝类型：", ["妃子笑", "其他类型"])

    if uploaded_file is not None:
        img = Image.open(uploaded_file).convert("RGB")
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        img.save(file_path)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{uploaded_file.name},{type_choice}\n")
        st.success("✅ 上传成功！右侧效果图将自动更新。")

    st.divider()
    st.subheader("📷 学生扫码参与上传")
    qr_url = "https://lychee-demo-yourname.streamlit.app"  # 部署后改成你的链接
    qr_img = qrcode.make(qr_url).convert("RGB")
    st.image(qr_img, caption="扫码上传入口")

    st.divider()
    if st.button("🔄 重置所有数据"):
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
        for f in os.listdir(UPLOAD_DIR):
            os.remove(os.path.join(UPLOAD_DIR, f))
        st.warning("✅ 数据已清空，可重新开始实验。")

# ---------------- 右侧展示区 ----------------
with right:
    st.subheader("🌈 混装效果图（70% 妃子笑 + 30% 其他类型）")

    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE, names=["filename", "type"])
        if len(df) >= 2:
            group_fx = df[df["type"] == "妃子笑"]["filename"].tolist()
            group_other = df[df["type"] == "其他类型"]["filename"].tolist()

            if group_fx and group_other:
                # 获取主色函数
                def get_main_color(path):
                    img = Image.open(path).resize((100, 100))
                    arr = np.array(img).reshape(-1, 3)
                    kmeans = KMeans(n_clusters=2, n_init=3).fit(arr)
                    return np.mean(kmeans.cluster_centers_, axis=0)

                fx_colors = [get_main_color(os.path.join(UPLOAD_DIR, f)) for f in group_fx]
                ot_colors = [get_main_color(os.path.join(UPLOAD_DIR, f)) for f in group_other]

                fx_mean = np.mean(fx_colors, axis=0)
                ot_mean = np.mean(ot_colors, axis=0)

                # 生成颜色点阵
                size = 400
                n_points = 20000
                fx_points = np.random.multivariate_normal(fx_mean, np.eye(3) * 200, int(n_points * 0.7))
                ot_points = np.random.multivariate_normal(ot_mean, np.eye(3) * 200, int(n_points * 0.3))
                all_points = np.vstack([fx_points, ot_points])
                all_points = np.clip(all_points, 0, 255)

                # 映射到画布
                heat = np.zeros((size, size, 3), dtype=np.float32)
                xs, ys = np.random.randint(0, size, n_points), np.random.randint(0, size, n_points)
                for i in range(n_points):
                    x, y = xs[i], ys[i]
                    heat[x, y] = all_points[i] / 255.0

                # 模糊增强（生成热感）
                blurred = gaussian_filter(heat, sigma=12)
                blurred = blurred / np.max(blurred)

                fig, ax = plt.subplots(figsize=(6, 6))
                ax.imshow(blurred)
                ax.axis("off")
                ax.set_title("🍒 模拟30%混装后的颜色热力分布（越亮表示纯度越高）", fontsize=12)
                st.pyplot(fig)
            else:
                st.info("请至少各上传一张妃子笑与其他类型荔枝图片。")
        else:
            st.info("请上传至少两类荔枝图片。")
    else:
        st.info("等待学生上传图片中……")
