st.markdown("""
<style>

/* ===== FULL ANIMATED BACKGROUND ===== */
.stApp {
    background: linear-gradient(-45deg, #020617, #0f172a, #1e293b, #020617);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    color: white;
}

/* Smooth gradient animation */
@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* ===== FLOATING PARTICLE EFFECT ===== */
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

/* ===== CARD (GLASS + ANIMATION) ===== */
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
    transition: all 0.3s ease;
}

.card:hover {
    transform: translateY(-6px) scale(1.01);
    box-shadow: 0 20px 40px rgba(0,0,0,0.5);
}

/* ===== RESULT TEXT GLOW ===== */
.glow {
    font-size: 2.6rem;
    font-weight: 900;
    text-align: center;
    color: #60a5fa;
    text-shadow:
        0 0 10px rgba(96,165,250,0.7),
        0 0 20px rgba(96,165,250,0.5),
        0 0 30px rgba(96,165,250,0.3);
}

/* ===== BUTTON (ANIMATED GRADIENT) ===== */
.stButton>button {
    background: linear-gradient(135deg,#3b82f6,#6366f1,#8b5cf6);
    background-size: 200% 200%;
    animation: buttonGlow 4s ease infinite;
    color: white;
    border-radius: 12px;
    font-weight: 600;
    transition: 0.3s;
}

@keyframes buttonGlow {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 10px 30px rgba(99,102,241,0.5);
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: rgba(2,6,23,0.95);
    backdrop-filter: blur(10px);
}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-thumb {
    background: #475569;
    border-radius: 10px;
}

/* ===== SMOOTH FADE IN ===== */
.stMarkdown, .stImage, .stButton {
    animation: fadeIn 0.8s ease;
}

@keyframes fadeIn {
    from {opacity: 0; transform: translateY(10px);}
    to {opacity: 1; transform: translateY(0);}
}

</style>
""", unsafe_allow_html=True)
