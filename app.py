import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Smart Answer Evaluator", layout="wide")

# ---------------- GLOBAL CSS ----------------
st.markdown("""
<style>

/* -------- FILE UPLOADER CLEANUP -------- */

/* Remove drag-drop text */
[data-testid="stFileUploader"] div {
    font-size: 0px;
}

/* Remove "limit 200MB..." text */
[data-testid="stFileUploader"] small {
    display: none;
}

/* Make uploader compact */
[data-testid="stFileUploader"] {
    margin-top: -10px;
}

/* Hide document icon */
[data-testid="stFileUploader"] svg {
    display: none !important;
}

/* -------- FIX: HIDE ONLY ❌ BUTTON -------- */

/* Hide only icon-only buttons (this is the blue ❌) */
[data-testid="stFileUploader"] button:has(svg):not(:has(span)) {
    display: none !important;
}

/* Extra safety */
[data-testid="stFileUploader"] button[aria-label="Clear file"] {
    display: none !important;
}

/* -------- KEEP & STYLE BROWSE BUTTON -------- */

[data-testid="stFileUploader"] button {
    width: 100%;
    border-radius: 10px;
    background: linear-gradient(90deg, #007bff, #00c6ff);
    color: white;
    font-weight: 500;
    border: none;
    padding: 10px;
    display: flex !important;
    justify-content: center;
    align-items: center;
}

/* Hover */
[data-testid="stFileUploader"] button:hover {
    transform: scale(1.03);
    background: linear-gradient(90deg, #0066d6, #00aaff);
}

/* Ensure text inside button is visible */
[data-testid="stFileUploader"] button span {
    display: inline !important;
    font-size: 14px !important;
}

/* -------- MAIN BUTTONS -------- */

div.stButton > button {
    background: linear-gradient(90deg, #007bff, #00c6ff);
    color: white;
    font-size: 18px;
    padding: 12px;
    border-radius: 10px;
    border: none;
    transition: 0.3s;
}

/* Hover */
div.stButton > button:hover {
    transform: scale(1.04);
    background: linear-gradient(90deg, #0066d6, #00aaff);
}

/* -------- GENERAL POLISH -------- */

button:focus {
    outline: none !important;
    box-shadow: none !important;
}

* {
    transition: all 0.2s ease-in-out;
}

</style>
""", unsafe_allow_html=True)
# ---------------- HEADER ----------------
st.markdown("""
<div style="text-align:center; margin-top:20px;">
<h1 style="font-size:42px;
background: linear-gradient(90deg, #007bff, #00c6ff);
-webkit-background-clip: text;
color: transparent;">
🧠 Smart Answer Evaluator
</h1>
<p style="font-size:18px;color:gray;">
AI-powered Answer Evaluation using NLP
</p>
</div>
""", unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------
def preprocess(text):
    return text.lower()

def calculate_similarity(t1, t2):
    vec = TfidfVectorizer()
    vectors = vec.fit_transform([t1, t2])
    return cosine_similarity(vectors[0], vectors[1])[0][0]

def extract_keywords(text):
    return list(set(text.split()))[:6]

def read_file(file):
    return file.read().decode("utf-8")

# ---------------- SESSION ----------------
for key in ["matched","keywords","similarity","score"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ["matched","keywords"] else 0

# ---------------- UPLOAD UI ----------------
st.markdown("""
<div style="background: linear-gradient(135deg, #f8f9fa, #ffffff);
padding:25px;border-radius:15px;
box-shadow:0 4px 12px rgba(0,0,0,0.08);
margin-bottom:20px;text-align:center;">
<h3>📁 Upload Required Files</h3>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

def upload_card(title, key):
    st.markdown(f"""
    <div style="
    background:white;
    padding:20px;
    border-radius:15px;
    text-align:center;
    box-shadow:0 4px 12px rgba(0,0,0,0.08);
    border:2px dashed #bdbdbd;
    ">
    <h4>{title}</h4>
    </div>
    """, unsafe_allow_html=True)

    file = st.file_uploader(
        " ",
        type=["txt"],
        key=key,
        label_visibility="collapsed"
    )

    # Show uploaded file name inside uploader
    if file:
        st.markdown(f"""
        <div style="
        background:#f0f0f0;
        padding:8px 12px;
        margin-top:5px;
        border-radius:5px;
        text-align:center;
        font-size:14px;
        color:#333;
        ">
        {file.name}
        </div>
        """, unsafe_allow_html=True)

    return file

with col1:
    question_file = upload_card("📄 Question Paper", "q")
with col2:
    model_file = upload_card("🧠 Model Answer", "m")
with col3:
    student_file = upload_card("👨‍🎓 Student Answer", "s")

# ---------------- EVALUATE BUTTON ----------------
st.markdown("<br>", unsafe_allow_html=True)
col_center = st.columns([1,2,1])
with col_center[1]:
    evaluate = st.button("🚀 Evaluate Answer", use_container_width=True)

# ---------------- PROCESS ----------------
if evaluate:
    if question_file and model_file and student_file:
        with st.spinner("🔍 Analyzing Answer..."):
            student = preprocess(read_file(student_file))
            model = preprocess(read_file(model_file))

            similarity = calculate_similarity(student, model)
            keywords = extract_keywords(model)
            matched = [w for w in keywords if w in student]

            score = round((similarity*0.7 + (len(matched)/len(keywords))*0.3)*10, 2)

            st.session_state.matched = matched
            st.session_state.keywords = keywords
            st.session_state.similarity = similarity
            st.session_state.score = score
    else:
        st.error("⚠️ Please upload all files")

# ---------------- FETCH RESULTS ----------------
matched = st.session_state.matched
keywords = st.session_state.keywords
similarity = st.session_state.similarity
score = st.session_state.score

if len(keywords) > 0:
    matched_count = len(matched)
    total_keywords = len(keywords)

    # ---------------- DASHBOARD ----------------
    st.markdown("## 📊 Evaluation Dashboard")
    c1,c2,c3 = st.columns(3)

    def card(title,value,desc,color):
        return f"""
        <div style="background:white;padding:20px;border-radius:15px;
        box-shadow:0 4px 12px rgba(0,0,0,0.08);text-align:center;">
        <h4>{title}</h4>
        <h2>{value}</h2>
        <p style="color:{color};">{desc}</p>
        </div>
        """

    c1.markdown(card("📊 Similarity",f"{round(similarity*100,2)}%",
        "High" if similarity>0.7 else "Medium" if similarity>0.4 else "Low",
        "green" if similarity>0.7 else "orange" if similarity>0.4 else "red"),True)
    c2.markdown(card("🧠 Keywords",f"{matched_count}/{total_keywords}",
        "Strong" if matched_count/total_keywords>0.7 else "Average" if matched_count/total_keywords>0.4 else "Weak",
        "green" if matched_count/total_keywords>0.7 else "orange" if matched_count/total_keywords>0.4 else "red"),True)
    c3.markdown(card("⭐ Score",f"{score}/10",
        "Excellent" if score>7 else "Moderate" if score>4 else "Poor",
        "green" if score>7 else "orange" if score>4 else "red"),True)

    st.markdown("---")

    # ---------------- KEYWORDS ----------------
    st.markdown("### 🔑 Keyword Analysis")
    st.progress(matched_count/total_keywords)
    cols = st.columns(len(keywords))
    for i,w in enumerate(keywords):
        if w in matched:
            cols[i].success(f"{w} ✔")
        else:
            cols[i].error(f"{w} ✖")

    st.markdown("---")

    # ---------------- FEEDBACK ----------------
    st.markdown("### 💬 AI Feedback")
    if score > 7:
        st.success("🌟 Excellent Answer! Well structured.")
    elif score > 4:
        st.warning("👍 Good Answer. Improve coverage.")
    else:
        st.error("⚠️ Needs Improvement.")

    # ---------------- SUGGESTIONS ----------------
    st.markdown("### 🧠 Suggestions")
    if similarity < 0.7:
        st.info("Improve answer relevance")
    if matched_count < total_keywords:
        missing = [k for k in keywords if k not in matched]
        st.info(f"Add keywords: {', '.join(missing[:3])}")
    if score <= 7:
        st.info("Add more explanation")

    # ---------------- SUBMIT BUTTON ----------------
    st.markdown("<br>", unsafe_allow_html=True)
    col_center = st.columns([1,2,1])
    with col_center[1]:
        submit = st.button("✅ Submit Evaluation", use_container_width=True)
        if submit:
            st.success("✔ Your evaluation has been submitted!")