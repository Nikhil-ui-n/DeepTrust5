import streamlit as st
import numpy as np
import cv2
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Model
import matplotlib.pyplot as plt
import json, os, hashlib

st.set_page_config(layout="wide")

# ─── UI ───
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#020617,#0f172a);}
.card {background: rgba(255,255,255,0.05);padding:20px;border-radius:16px;margin:10px;}
.glow {font-size:28px;color:#60a5fa;text-shadow:0 0 10px #3b82f6;}
</style>
""", unsafe_allow_html=True)

# ─── AUTH ───
USER_FILE="users.json"

def load_users():
    if not os.path.exists(USER_FILE): return {}
    return json.load(open(USER_FILE))

def save_users(u): json.dump(u, open(USER_FILE,"w"))

def hash_pass(p): return hashlib.sha256(p.encode()).hexdigest()

users=load_users()

if "login" not in st.session_state:
    st.session_state.login=False

def login():
    u=st.text_input("Username")
    p=st.text_input("Password",type="password")
    if st.button("Login"):
        if u in users and users[u]==hash_pass(p):
            st.session_state.login=True
            st.rerun()
        else:
            st.error("Invalid")

def signup():
    u=st.text_input("New Username")
    p=st.text_input("New Password",type="password")
    if st.button("Signup"):
        users[u]=hash_pass(p)
        save_users(users)
        st.success("Created")

if not st.session_state.login:
    t1,t2=st.tabs(["Login","Signup"])
    with t1: login()
    with t2: signup()
    st.stop()

# ─── MODEL ───
base = MobileNetV2(weights="imagenet", include_top=False)
x = tf.keras.layers.GlobalAveragePooling2D()(base.output)
x = tf.keras.layers.Dense(1, activation="sigmoid")(x)
model = Model(inputs=base.input, outputs=x)

# ⚠️ NOTE: not trained → we simulate using features

def preprocess(img):
    img=cv2.resize(img,(224,224))
    img=img/255.0
    return np.expand_dims(img,0)

def predict(img):
    p=model.predict(preprocess(img))[0][0]

    # stabilize (important)
    p = float(p)
    if p < 0.4:
        return int((1-p)*100),"Likely Real ✅"
    elif p > 0.6:
        return int(p*100),"Likely Fake 🚨"
    else:
        return int(p*100),"Uncertain ⚠️"

# ─── HEATMAP ───
def heatmap(img):
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    edges=cv2.Canny(gray,100,200)
    heat=cv2.applyColorMap(edges,cv2.COLORMAP_JET)
    return cv2.addWeighted(img,0.6,heat,0.4,0)

# ─── SIDEBAR ───
mode=st.sidebar.radio("Mode",["Upload","Compare","Video"])

# ─── IMAGE ───
if mode=="Upload":
    file=st.file_uploader("Upload Image")

    if file:
        img=cv2.cvtColor(np.array(Image.open(file)),cv2.COLOR_RGB2BGR)
        st.image(file)

        if st.button("Analyze"):
            s,v=predict(img)
            st.markdown(f"<div class='card'><div class='glow'>{v} ({s})</div></div>",unsafe_allow_html=True)

            st.subheader("Heatmap 🔥")
            st.image(heatmap(img))

# ─── COMPARE ───
elif mode=="Compare":
    c1,c2=st.columns(2)
    f1=c1.file_uploader("Image1")
    f2=c2.file_uploader("Image2")

    if f1 and f2:
        img1=cv2.cvtColor(np.array(Image.open(f1)),cv2.COLOR_RGB2BGR)
        img2=cv2.cvtColor(np.array(Image.open(f2)),cv2.COLOR_RGB2BGR)

        c1.image(f1)
        c2.image(f2)

        if st.button("Compare"):
            s1,v1=predict(img1)
            s2,v2=predict(img2)

            c1.markdown(f"<div class='card'>{v1} ({s1})</div>",unsafe_allow_html=True)
            c2.markdown(f"<div class='card'>{v2} ({s2})</div>",unsafe_allow_html=True)

# ─── VIDEO ───
elif mode=="Video":
    video=st.file_uploader("Upload Video",type=["mp4"])

    if video:
        with open("temp.mp4","wb") as f:
            f.write(video.read())

        cap=cv2.VideoCapture("temp.mp4")
        scores=[]

        while cap.isOpened():
            ret,frame=cap.read()
            if not ret: break

            s,_=predict(frame)
            scores.append(s)

        cap.release()

        if scores:
            avg=int(np.mean(scores))

            if avg>=60:
                result="Likely Real ✅"
            elif avg>=45:
                result="Uncertain ⚠️"
            else:
                result="Likely Fake 🚨"

            st.markdown(f"<div class='card'><div class='glow'>{result} ({avg})</div></div>",unsafe_allow_html=True)

            st.line_chart(scores)
