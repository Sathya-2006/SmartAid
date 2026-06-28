import os
import streamlit as st
from firebase_config import db
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from dotenv import load_dotenv
from groq import Groq
from auth import check_login, get_role, logout

check_login()
logout()

role = get_role()

if role not in ["Admin", "Volunteer"]:
    st.error("Access denied. Admin/Volunteer only.")
    st.stop()

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #020617, #0f172a, #1e293b); }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #020617, #0f172a); }
section[data-testid="stSidebar"] * { color: white !important; }
h1, h2, h3, h4, label, p { color: white !important; }
.page-title { font-size: 44px; font-weight: 900; color: white; margin-bottom: 5px; }
.page-subtitle { color: #cbd5e1; font-size: 17px; margin-bottom: 25px; }
.kpi-card { padding: 20px; border-radius: 18px; color: white; box-shadow: 0px 10px 25px rgba(0,0,0,0.30); text-align: center; min-height: 120px; }
.kpi-number { font-size: 34px; font-weight: 900; }
.kpi-label { font-size: 15px; font-weight: 700; }
.card-blue { background: linear-gradient(135deg, #2563eb, #06b6d4); }
.card-purple { background: linear-gradient(135deg, #7c3aed, #a855f7); }
.card-green { background: linear-gradient(135deg, #059669, #22c55e); }
.glass-card { background: rgba(255,255,255,0.08); padding: 24px; border-radius: 22px; border: 1px solid rgba(255,255,255,0.12); box-shadow: 0px 10px 30px rgba(0,0,0,0.25); margin-bottom: 20px; }
.profile-card { background: rgba(14,165,233,0.15); padding: 18px; border-radius: 15px; border-left: 5px solid #0ea5e9; color: white; line-height: 1.8; }
.scheme-card { background: rgba(250,204,21,0.12); padding: 18px; border-radius: 15px; border-left: 5px solid #facc15; color: #fef3c7; margin-bottom: 12px; line-height: 1.7; }
.gemini-card { background: rgba(34,197,94,0.14); padding: 22px; border-radius: 18px; border-left: 6px solid #22c55e; color: #dcfce7; font-size: 16px; line-height: 1.8; }
.warning-card { background: rgba(220,38,38,0.16); padding: 18px; border-radius: 16px; border-left: 6px solid #dc2626; color: #fecaca; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">🧠 RAG Scheme Advisor</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Retrieve scheme documents using embeddings and generate personalized AI-based welfare recommendations.</div>',
    unsafe_allow_html=True
)

SCHEME_FOLDER = "scheme_docs"

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = None
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)


@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


@st.cache_data
def load_scheme_documents():
    documents = []
    filenames = []
    if not os.path.exists(SCHEME_FOLDER):
        return documents, filenames
    for file_name in os.listdir(SCHEME_FOLDER):
        if file_name.endswith(".txt"):
            file_path = os.path.join(SCHEME_FOLDER, file_name)
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
            documents.append(text)
            filenames.append(file_name)
    return documents, filenames


@st.cache_resource
def create_faiss_index_cached(_model, documents_tuple):
    documents = list(documents_tuple)
    embeddings = _model.encode(documents)
    embeddings = np.array(embeddings).astype("float32")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index


def search_relevant_schemes(query, documents, filenames, model, index, top_k=3):
    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")
    top_k = min(top_k, len(documents))
    distances, indices = index.search(query_embedding, top_k)
    results = []
    for idx in indices[0]:
        results.append({
            "file": filenames[idx],
            "content": documents[idx]
        })
    return results


def generate_ai_recommendation(person_profile, retrieved_schemes):
    if not groq_client:
        return "⚠️ GROQ_API_KEY not found. Please add it in .env file."

    context = ""
    for scheme in retrieved_schemes:
        context += f"\nScheme File: {scheme['file']}\n"
        context += scheme["content"]
        context += "\n"

    prompt = f"""You are SmartAid AI Advisor.

Your job is to recommend suitable government schemes, training programs,
or welfare support based on the person's profile.

Use ONLY the scheme information provided in the context.
Do not invent schemes outside the context.

Person Profile:
{person_profile}

Available Scheme Context:
{context}

Give output in this format:

Recommended Schemes:
1.
2.
3.

Reason:
Explain why these schemes are suitable.

Next Action:
Tell what NGO/Admin should do next."""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are SmartAid AI Advisor helping NGOs recommend government schemes to vulnerable people in India."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI error: {e}"


embedding_model = load_embedding_model()
documents, filenames = load_scheme_documents()
people_docs = list(db.collection("people").stream())

k1, k2, k3 = st.columns(3)

with k1:
    st.markdown(f"""
    <div class="kpi-card card-blue">
        <div class="kpi-number">{len(documents)}</div>
        <div class="kpi-label">📚 Scheme Documents</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card card-purple">
        <div class="kpi-number">{len(people_docs)}</div>
        <div class="kpi-label">👥 Registered People</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card card-green">
        <div class="kpi-number">FAISS</div>
        <div class="kpi-label">🔍 Vector Search</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

if len(documents) == 0:
    st.markdown("""
    <div class="warning-card">
    No scheme documents found in scheme_docs folder. Add .txt scheme files first.
    </div>
    """, unsafe_allow_html=True)

elif len(people_docs) == 0:
    st.warning("No registered people found.")

else:
    index = create_faiss_index_cached(embedding_model, tuple(documents))

    people_options = {}
    for doc in people_docs:
        data = doc.to_dict()
        label = (
            f"{data.get('name', 'Unknown')} | "
            f"Age {data.get('age', 'N/A')} | "
            f"{data.get('location', 'No Location')}"
        )
        people_options[label] = {"id": doc.id, "data": data}

    selected_label = st.selectbox("Select Beneficiary", list(people_options.keys()))
    selected_person = people_options[selected_label]
    person_id = selected_person["id"]
    data = selected_person["data"]

    col1, col2 = st.columns([1, 1.4])

    with col1:
        st.subheader("👤 Person Profile")
        person_profile = f"""
Name: {data.get("name")}
Age: {data.get("age")}
Gender: {data.get("gender")}
Skill: {data.get("skill")}
Disability: {data.get("disability")}
Work Willingness: {data.get("work_willingness")}
Physical Fitness: {data.get("physical_fitness")}
Family Status: {data.get("family_status")}
Education Status: {data.get("education_status")}
Location: {data.get("location")}
"""
        st.markdown(f"""
        <div class="profile-card">
        <b>Name:</b> {data.get("name")}<br>
        <b>Age:</b> {data.get("age")}<br>
        <b>Gender:</b> {data.get("gender")}<br>
        <b>Skill:</b> {data.get("skill")}<br>
        <b>Disability:</b> {data.get("disability")}<br>
        <b>Work Willingness:</b> {data.get("work_willingness")}<br>
        <b>Physical Fitness:</b> {data.get("physical_fitness")}<br>
        <b>Family Status:</b> {data.get("family_status")}<br>
        <b>Education:</b> {data.get("education_status")}<br>
        <b>Location:</b> {data.get("location")}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.subheader("🔍 RAG Search & AI Recommendation")

        if st.button("Generate RAG Recommendation", use_container_width=True):
            retrieved_schemes = search_relevant_schemes(
                person_profile, documents, filenames, embedding_model, index, top_k=3
            )

            st.subheader("📄 Retrieved Scheme Documents")
            for scheme in retrieved_schemes:
                st.markdown(f"""
                <div class="scheme-card">
                <b>Scheme File:</b> {scheme["file"]}<br><br>
                {scheme["content"]}
                </div>
                """, unsafe_allow_html=True)

            st.subheader("🤖 AI Final Recommendation")

            with st.spinner("Generating recommendation..."):
                final_recommendation = generate_ai_recommendation(person_profile, retrieved_schemes)

            st.markdown(f"""
            <div class="gemini-card">
            {final_recommendation}
            </div>
            """, unsafe_allow_html=True)

            db.collection("people").document(person_id).update({
                "rag_recommendation": final_recommendation
            })

            st.success("RAG recommendation saved to Firebase.")

        else:
            st.info("Click the button to retrieve scheme documents and generate recommendation.")