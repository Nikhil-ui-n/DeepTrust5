import streamlit as st
import numpy as np
import cv2
from PIL import Image
import hashlib, json, os
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="DeepTrust AI", layout="wide")

# ─── UI STYLE ───
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #020617, #0f172a);
    color:white;
}
.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 16px;
    margin: 10px 0;
}
.glow {
    font-size: 2rem;
    font-weight: bold;
    color: #38bdf8;
    text-shadow: 0 0 15px #0ea5e9;
}
</style>
""", unsafe_allow_html=True)

# ─── USER SYSTEM ───
USER_FILE = "users.json"

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    return json.load(open(USER_FILE))

def save_users(u):
    json.dump(u, open(USER_FILE,"w"))

def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

users = load_users()

# ─── SESSION ───
if "logged" not in st.session_state:
    st.session_state.logged = False

if "history" not in st.session_state:
    st.session_state.history = []

# ─── AUTH ───
def login():
    st.subheader("🔐 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u in users and users[u] == hash_pass(p):
            st.session_state.logged = True
            st.session_state.user = u
            st.rerun()
        else:
            st.error("Invalid credentials")

def signup():
    st.subheader("📝 Signup")
    u = st.text_input("New Username")
    p = st.text_input("New Password", type="password")

    if st.button("Create"):
        users[u] = hash_pass(p)
        save_users(users)
        st.success("Account created")

if not st.session_state.logged:
    st.title("🛡️ DeepTrust AI")
    t1,t2 = st.tabs(["Login","Signup"])
    with t1: login()
    with t2: signup()
    st.stop()

# ─── LOGOUT ───
with st.sidebar:
    st.write(f"👤 {st.session_state.user}")
    if st.button("Logout"):
        st.session_state.logged=False
        st.rerun()

st.title("🛡️ DeepTrust AI")

# ─── FEATURE EXTRACTION ───
def extract_features(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    texture = cv2.Laplacian(gray, cv2.CV_64F).var()
    noise = np.std(gray)
    edges = np.mean(cv2.Canny(gray,100,200))
    return [texture, noise, edges]

# ─── TRAIN MODEL INSIDE APP (LIGHTWEIGHT) ───
@st.cache_resource
def train_model():
    # synthetic small dataset (hackathon safe)
    X = [
        [100, 20, 30], [120, 25, 35], [80, 15, 25],   # real
        [300, 60, 80], [250, 55, 70], [280, 65, 90]   # fake
    ]
    y = [0,0,0, 1,1,1]

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)
    return model

model = train_model()

# ─── DETECTOR ───
class Detector:
    def analyze(self, img):
        features = extract_features(img)
        pred = model.predict([features])[0]
        prob = model.predict_proba([features])[0]

        confidence = int(max(prob)*100)

        if confidence < 60:
            return confidence, "Uncertain ⚠️"

        if pred == 0:
            return confidence, "Likely Real ✅"
        else:
            return confidence, "Likely Fake 🚨"

detector = Detector()

# ─── HEATMAP ───
def generate_heatmap(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,100,200)
    heat = cv2.applyColorMap(edges, cv2.COLORMAP_JET)
    return cv2.addWeighted(img,0.6,heat,0.4,0)

# ─── MODE ───
mode = st.sidebar.radio("Mode",
["Upload","Compare","Video","Dashboard"])

# ─── IMAGE ───
if mode=="Upload":
    file = st.file_uploader("Upload Image", type=["jpg","png"])

    if file:
        img = cv2.cvtColor(np.array(Image.open(file)), cv2.COLOR_RGB2BGR)
        st.image(file)

        if st.button("Analyze"):
            s,v = detector.analyze(img)
            st.session_state.history.append(s)

            st.markdown(f"<div class='card'><div class='glow'>{v} ({s})</div></div>", unsafe_allow_html=True)

            st.subheader("🔥 Heatmap")
            st.image(generate_heatmap(img))

# ─── COMPARE ───
elif mode=="Compare":
    c1,c2 = st.columns(2)
    f1 = c1.file_uploader("Image1", key="1")
    f2 = c2.file_uploader("Image2", key="2")

    if f1 and f2:
        img1 = cv2.cvtColor(np.array(Image.open(f1)), cv2.COLOR_RGB2BGR)
        img2 = cv2.cvtColor(np.array(Image.open(f2)), cv2.COLOR_RGB2BGR)

        c1.image(f1)
        c2.image(f2)

        if st.button("Compare"):
            s1,v1 = detector.analyze(img1)
            s2,v2 = detector.analyze(img2)

            c1.markdown(f"<div class='card'>{v1} ({s1})</div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='card'>{v2} ({s2})</div>", unsafe_allow_html=True)

# ─── VIDEO ───
elif mode=="Video":
    video = st.file_uploader("Upload Video", type=["mp4"])

    if video:
        with open("temp.mp4","wb") as f:
            f.write(video.read())

        cap = cv2.VideoCapture("temp.mp4")
        scores=[]
        frames=0

        while cap.isOpened():
            ret,frame=cap.read()
            if not ret: break

            if frames%10==0:
                s,_=detector.analyze(frame)
                scores.append(s)

            frames+=1

        cap.release()

        if scores:
            avg=int(np.mean(scores))

            if avg>=70:
                result="Likely Real ✅"
            elif avg>=55:
                result="Uncertain ⚠️"
            else:
                result="Likely Fake 🚨"

            st.markdown(f"<div class='card'><div class='glow'>{result} ({avg})</div></div>", unsafe_allow_html=True)
            st.line_chart(scores)

# ─── DASHBOARD ───
elif mode=="Dashboard":
    data = st.session_state.history

    if data:
        st.line_chart(data)

        real=sum(1 for x in data if x>70)
        fake=sum(1 for x in data if x<55)

        st.bar_chart({"Real":real,"Fake":fake})
    else:
        st.info("No data")

st.markdown("---")
st.caption("🚀 DeepTrust AI | All-in-One Version")
