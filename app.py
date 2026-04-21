import streamlit as st
import numpy as np
import cv2
from PIL import Image
import hashlib, json, os

st.set_page_config(page_title="DeepTrust AI", layout="wide")

# ─── ULTRA ANIMATED UI ───
st.markdown("""
<style>

/* BACKGROUND */
.stApp {
    background: linear-gradient(-45deg, #020617, #0f172a, #1e293b, #020617);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    color: white;
}

/* Gradient animation */
@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* PARTICLES */
.stApp::before {
    content: "";
    position: fixed;
    width: 200%;
    height: 200%;
    top: -50%;
    left: -50%;
    background: radial-gradient(circle, rgba(255,255,255,0.04) 1px, transparent 1px);
    background-size: 50px 50px;
    animation: particlesMove 40s linear infinite;
    z-index: 0;
}

@keyframes particlesMove {
    0% {transform: translate(0,0);}
    100% {transform: translate(200px,200px);}
}

/* CARD */
.card {
    position: relative;
    z-index: 1;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 20px;
    margin: 12px 0;
    backdrop-filter: blur(16px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    transition: 0.3s;
}
.card:hover {
    transform: translateY(-6px);
}

/* RESULT TEXT */
.glow {
    font-size: 2.6rem;
    font-weight: 900;
    text-align: center;
    color: #60a5fa;
    text-shadow: 0 0 15px rgba(96,165,250,0.7);
}

/* BUTTON */
.stButton>button {
    background: linear-gradient(135deg,#3b82f6,#6366f1,#8b5cf6);
    color: white;
    border-radius: 12px;
    font-weight: 600;
    transition: 0.3s;
}
.stButton>button:hover {
    transform: scale(1.05);
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: rgba(2,6,23,0.95);
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

# ─── SIDEBAR ───
with st.sidebar:
    st.write(f"👤 {st.session_state.user}")
    if st.button("Logout"):
        st.session_state.logged=False
        st.rerun()

mode = st.sidebar.radio("Mode", ["Upload","Compare","Video","Dashboard"])

st.title("🛡️ DeepTrust AI")

# ─── DETECTOR ───
class Detector:
    def analyze(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        texture = cv2.Laplacian(gray, cv2.CV_64F).var()
        noise = np.std(gray)
        edges = np.mean(cv2.Canny(gray,100,200))
        blur = cv2.Laplacian(gray, cv2.CV_64F).var()

        t = min(texture / 180, 1)
        n = min(noise / 70, 1)
        e = min(edges / 120, 1)
        b = min(blur / 150, 1)

        irregular = (t*0.35 + n*0.25 + e*0.25 + b*0.15)
        score = int((1 - irregular) * 100)

        face = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        faces = face.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            score = max(score, 70)
        else:
            score += 5

        score = max(45, min(score, 90))

        if score >= 75:
            v = "Likely Real ✅"
        elif score >= 60:
            v = "Uncertain ⚠️"
        else:
            v = "Likely Fake 🚨"

        return score, v

detector = Detector()

# ─── HEATMAP ───
def heatmap(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,100,200)
    heat = cv2.applyColorMap(edges, cv2.COLORMAP_JET)
    return cv2.addWeighted(img,0.6,heat,0.4,0)

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
            st.image(heatmap(img))

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
            std=np.std(scores)

            consistency = int((1 - min(std/50,1)) * 100)
            final = int(avg * 0.7 + consistency * 0.3)

            if final >= 75:
                result="Likely Real ✅"
            elif final >= 60:
                result="Uncertain ⚠️"
            else:
                result="Likely Fake 🚨"

            st.markdown(f"<div class='card'><div class='glow'>{result} ({final})</div></div>", unsafe_allow_html=True)
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
st.caption("🚀 DeepTrust AI | Animated Premium Version")
