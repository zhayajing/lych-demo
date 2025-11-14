# app.py
import streamlit as st
import pandas as pd
import numpy as np
import os
from PIL import Image, ImageFile, ExifTags
import qrcode
import random
import uuid
import io
import time
from datetime import datetime, timedelta

# optional: pillow-heif for HEIC support
try:
    import pillow_heif  # type: ignore
    HEIF_AVAILABLE = True
except Exception:
    HEIF_AVAILABLE = False

# allow loading truncated images sometimes produced by mobile
ImageFile.LOAD_TRUNCATED_IMAGES = True

# ============ 页面设置 ============
st.set_page_config(page_title="荔枝混装实验", layout="wide")
st.title("🍒 荔枝混装实验（70% 妃子笑 + 30% 其他）")
st.markdown(
    """
    上传不同类型的荔枝图片，系统会自动生成一张“混装果堆图”。  
    已做图片格式/大小校验与缓存优化，减少延迟并提高稳定性。
    """
)

# ============ 常量 & 目录 ============
UPLOAD_DIR = "uploads"
THUMB_DIR = os.path.join(UPLOAD_DIR, "thumbs")
LOG_FILE = "upload_log.csv"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(THUMB_DIR, exist_ok=True)

# 最大单文件字节数（例如 8MB）
MAX_FILE_BYTES = 8 * 1024 * 1024

# 支持扩展名
ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic"}

# ============ 帮助函数 ============
def _ext_of(name):
    return os.path.splitext(name)[1].lower()

def generate_safe_filename(orig_name: str) -> str:
    ext = _ext_of(orig_name)
    return f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}{ext}"

def try_open_image(file_bytes: bytes):
    """尝试打开并规范化图像，返回 PIL.Image 或抛异常"""
    # HEIC handling if needed
    ext = None
    if hasattr(file_bytes, "name"):
        ext = _ext_of(file_bytes.name)
    try:
        bio = io.BytesIO(file_bytes)
        if HEIF_AVAILABLE and (ext == ".heic" or b"ftypheic" in file_bytes[:32].lower()):
            # pillow_heif will register HEIF plugin so PIL open works
            img = Image.open(bio).convert("RGB")
        else:
            img = Image.open(bio)
            # If GIF, take first frame
            if getattr(img, "is_animated", False):
                img.seek(0)
                img = img.convert("RGB")
            else:
                img = img.convert("RGB")
        # handle EXIF orientation
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = img._getexif()
            if exif is not None:
                o = exif.get(orientation)
                if o == 3:
                    img = img.rotate(180, expand=True)
                elif o == 6:
                    img = img.rotate(270, expand=True)
                elif o == 8:
                    img = img.rotate(90, expand=True)
        except Exception:
            pass
        return img
    except Exception as e:
        raise

def save_thumbnail(img: Image.Image, thumb_path: str, size=(200,200)):
    img_thumb = img.copy()
    img_thumb.thumbnail(size)
    img_thumb.save(thumb_path, format="JPEG", quality=85)

# 缓存：读取日志（当文件修改时间变更时会重新读取）
@st.cache_data(ttl=30)
def read_log():
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame(columns=["filename","type"])
    try:
        df = pd.read_csv(LOG_FILE, names=["filename","type"])
        return df
    except Exception:
        return pd.DataFrame(columns=["filename","type"])

# 缓存：生成拼图（key 由日志内容/hash 控制）
@st.cache_data(ttl=60*5)  # 5 minutes cache
def build_collage(filenames, tile_size=100, grid=10):
    total = tile_size * grid
    collage = Image.new("RGB", (total, total), (255,255,255))
    for idx, fname in enumerate(filenames):
        try:
            p = os.path.join(UPLOAD_DIR, fname)
            img = Image.open(p).convert("RGB")
            img = img.resize((tile_size, tile_size))
            x = (idx % grid) * tile_size
            y = (idx // grid) * tile_size
            collage.paste(img, (x, y))
        except Exception as e:
            print("跳过", fname, e)
    return collage

# ============ 页面布局 ============
left, right = st.columns([1, 2])

# ---------------- 左侧上传区 ----------------
with left:
    st.subheader("📲 上传入口")
    st.info("支持 jpg/jpeg/png/webp/gif（heic 可选，需安装 pillow-heif）。最大单文件：8MB（可修改）")

    uploaded_file = st.file_uploader("请上传荔枝图片（妃子笑 / 其他类型）", type=["jpg", "jpeg", "png", "webp", "gif", "heic"])
    type_choice = st.radio("请选择荔枝类型：", ["妃子笑", "其他类型"])

    if uploaded_file is not None:
        # size check
        uploaded_bytes = uploaded_file.getbuffer().nbytes
        if uploaded_bytes > MAX_FILE_BYTES:
            st.error(f"文件过大（{uploaded_bytes/1024/1024:.1f} MB），最大允许 {MAX_FILE_BYTES/1024/1024:.1f} MB。请压缩后重试。")
        else:
            # try open and validate
            with st.spinner("正在验证图片..."):
                try:
                    file_bytes = uploaded_file.getvalue()
                    img = try_open_image(file_bytes)
                    # safe filename
                    safe_name = generate_safe_filename(uploaded_file.name)
                    save_path = os.path.join(UPLOAD_DIR, safe_name)
                    # save resized original (限制最大边长以节省存储，避免大图)
                    max_edge = 1600
                    w,h = img.size
                    if max(w,h) > max_edge:
                        scale = max_edge / max(w,h)
                        new_size = (int(w*scale), int(h*scale))
                        img = img.resize(new_size, Image.LANCZOS)
                    img.save(save_path, format="JPEG", quality=90)
                    # save thumbnail
                    thumb_path = os.path.join(THUMB_DIR, safe_name + ".jpg")
                    save_thumbnail(img, thumb_path, size=(200,200))
                    # append log
                    with open(LOG_FILE, "a", encoding="utf-8") as f:
                        f.write(f"{safe_name},{type_choice}\n")
                    st.success("✅ 上传并保存成功！右侧混装图将自动更新。")
                except Exception as e:
                    st.error(f"无法处理图片：{e}")
                    st.exception(e)

    st.divider()
    st.subheader("📷 学生扫码上传")
    qr_url = "https://lych-demo-5gk9t8rb34wwy8ofu6euph.streamlit.app"
    qr_img = qrcode.make(qr_url).convert("RGB")
    st.image(qr_img, caption="扫码上传入口")

    st.divider()
    if st.button("🔄 重置所有数据（清除上传 & 日志）"):
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
        for f in os.listdir(UPLOAD_DIR):
            p = os.path.join(UPLOAD_DIR, f)
            if os.path.isfile(p):
                os.remove(p)
        for f in os.listdir(THUMB_DIR):
            p = os.path.join(THUMB_DIR, f)
            if os.path.isfile(p):
                os.remove(p)
        st.warning("✅ 已清空所有上传记录与图片。")

    # 清理多久之前的文件（避免空间耗尽）
    st.markdown("**🔧 清理旧文件**")
    days = st.number_input("保留最近多少天的文件（自动删除更旧文件）", min_value=1, max_value=365, value=30)
    if st.button("🧹 执行清理"):
        cutoff = datetime.utcnow() - timedelta(days=int(days))
        removed = 0
        for fname in os.listdir(UPLOAD_DIR):
            p = os.path.join(UPLOAD_DIR, fname)
            if os.path.isfile(p):
                mtime = datetime.utcfromtimestamp(os.path.getmtime(p))
                if mtime < cutoff:
                    os.remove(p); removed += 1
        for fname in os.listdir(THUMB_DIR):
            p = os.path.join(THUMB_DIR, fname)
            if os.path.isfile(p):
                mtime = datetime.utcfromtimestamp(os.path.getmtime(p))
                if mtime < cutoff:
                    os.remove(p)
        st.success(f"已删除 {removed} 个旧文件。")

# ---------------- 右侧展示区 ----------------
with right:
    st.subheader("🍒 混装荔枝果堆效果图")
    df = read_log()

    st.markdown(f"当前上传记录：**{len(df)}** 张（需要至少一类妃子笑和一类其他）")
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

            # build collage with cache
            with st.spinner("生成混装图（缓存可降低重复生成）..."):
                collage = build_collage(tuple(all_samples), tile_size=100, grid=10)
                st.image(collage, caption="混装荔枝果堆图（70% 妃子笑 + 30% 其他类型）", use_column_width=True)

            # 显示示例缩略图（防止全部加载大图）
            st.markdown("**示例上传缩略图（随机 8 张）**")
            sample_thumb = random.sample(all_samples, min(8, len(all_samples)))
            cols = st.columns(8)
            for c, name in zip(cols, sample_thumb):
                p = os.path.join(THUMB_DIR, name + ".jpg")
                if os.path.exists(p):
                    c.image(p, width=80)
                else:
                    # fallback show original small
                    p2 = os.path.join(UPLOAD_DIR, name)
                    if os.path.exists(p2):
                        c.image(p2, width=80)
        else:
            st.info("请至少上传一种【妃子笑】和【其他类型】图片。")
    else:
        st.info("等待学生上传图片中……")

    st.divider()
    st.markdown("**上传日志预览（最近 20 条）**")
    st.dataframe(df.tail(20))

    st.markdown("**调试/帮助**")
    st.write(f"HEIC 支持：{HEIF_AVAILABLE}（如需支持 HEIC，请 `pip install pillow-heif` 并重启）")
