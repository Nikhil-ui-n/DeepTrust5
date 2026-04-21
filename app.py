import streamlit as st
import numpy as np
import cv2
from PIL import Image
import matplotlib.pyplot as plt

st.set_page_config(page_title="DeepTrust AI", layout="wide")

# ---------- UI ----------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #1f1c2c, #928dab);
}
.big-title {
    text-align: center;
    font-size: 40px;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='big-title'>🔍 DeepTrust AI</h1>", unsafe_allow_html=True)

# ---------- Sidebar ----------
mode = st.sidebar.selectbox("Mode", ["Image Detection", "Compare Images"])

# ---------- FUNCTION ----------
def analyze_image(image):
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Feature extraction
    edges = cv2.Canny(gray, 100, 200)
    edge_score = np.mean(edges)

    noise = cv2.Laplacian(gray, cv2.CV_64F).var()

    # Heuristic logic (tuned)
    score = (edge_score * 0.6 + noise * 0.4)

    if score > 50:
        label = "FAKE"
    else:
        label = "REAL"

    confidence = min(99, int(score))

    return label, confidence, edges

# ---------- IMAGE DETECTION ----------
if mode == "Image Detection":
    uploaded = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

    if uploaded:
        image = Image.open(uploaded)

        col1, col2 = st.columns(2)

        with col1:
            st.image(image, caption="Uploaded Image", use_column_width=True)

        label, conf, heatmap = analyze_image(image)

        with col2:
            st.subheader("Result")
            if label == "FAKE":
                st.error(f"FAKE ❌ ({conf}%)")
            else:
                st.success(f"REAL ✅ ({conf}%)")

            st.subheader("Heatmap")
            fig, ax = plt.subplots()
            ax.imshow(heatmap, cmap="hot")
            ax.axis("off")
            st.pyplot(fig)

# ---------- COMPARE ----------
if mode == "Compare Images":
    img1 = st.file_uploader("Upload Image 1", key="1")
    img2 = st.file_uploader("Upload Image 2", key="2")

    if img1 and img2:
        image1 = Image.open(img1)
        image2 = Image.open(img2)

        col1, col2 = st.columns(2)

        with col1:
            st.image(image1, caption="Image 1")

        with col2:
            st.image(image2, caption="Image 2")

        label1, conf1, _ = analyze_image(image1)
        label2, conf2, _ = analyze_image(image2)

        st.write("### Comparison Result")
        st.write(f"Image 1: {label1} ({conf1}%)")
        st.write(f"Image 2: {label2} ({conf2}%)")

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("🚀 Built for Hackathon | DeepTrust AI")
