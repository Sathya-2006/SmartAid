import os
import streamlit as st
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from dotenv import load_dotenv
import google.generativeai as genai
from auth import check_login, get_role, logout

check_login()
logout()

role = get_role()

if role not in ["Admin", "Volunteer"]:
    st.error("Access denied.")
    st.stop()

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Government Scheme Knowledge Base",
    page_icon="📚",
    layout="wide"
)

# --------------------------------------------------
# THEME
# --------------------------------------------------
st.markdown("""
<style>

.stApp{
background: linear-gradient(135deg,#020617,#0f172a,#1e293b);
}

section[data-testid="stSidebar"]{
background:#020617;
}

section[data-testid="stSidebar"] *{
color:white !important;
}

h1,h2,h3,h4,label,p{
color:white !important;
}

.main-title{
font-size:42px;
font-weight:900;
color:white;
}

.subtitle{
font-size:16px;
color:#cbd5e1;
margin-bottom:20px;
}

.metric-card{
padding:20px;
border-radius:18px;
color:white;
text-align:center;
box-shadow:0px 8px 25px rgba(0,0,0,0.30);
}

.blue{
background:linear-gradient(135deg,#2563eb,#06b6d4);
}

.green{
background:linear-gradient(135deg,#16a34a,#22c55e);
}

.orange{
background:linear-gradient(135deg,#ea580c,#facc15);
}

.glass{
background:rgba(255,255,255,0.08);
padding:20px;
border-radius:18px;
border:1px solid rgba(255,255,255,0.1);
margin-bottom:15px;
}

.chunk-card{
background:rgba(14,165,233,0.12);
padding:15px;
border-left:5px solid #0ea5e9;
border-radius:12px;
margin-bottom:10px;
color:white;
}

.answer-card{
background:rgba(34,197,94,0.14);
padding:20px;
border-left:6px solid #22c55e;
border-radius:15px;
color:#dcfce7;
font-size:16px;
line-height:1.8;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown(
    '<div class="main-title">📚 Government Scheme Knowledge Base</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">PDF-based RAG Search Engine powered by FAISS + Gemini</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# SETTINGS
# --------------------------------------------------
PDF_FOLDER = "scheme_pdfs"

if not os.path.exists(PDF_FOLDER):
    os.makedirs(PDF_FOLDER)

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# --------------------------------------------------
# EMBEDDING MODEL
# --------------------------------------------------
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

# --------------------------------------------------
# PDF EXTRACTION
# --------------------------------------------------
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text

# --------------------------------------------------
# CHUNKING
# --------------------------------------------------
def chunk_text(text, chunk_size=800, overlap=150):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunks.append(text[start:end])

        start = end - overlap

    return chunks

# --------------------------------------------------
# LOAD PDF CHUNKS
# --------------------------------------------------
@st.cache_data
def load_all_pdf_chunks():

    chunks = []
    sources = []

    for file_name in os.listdir(PDF_FOLDER):

        if file_name.endswith(".pdf"):

            path = os.path.join(
                PDF_FOLDER,
                file_name
            )

            text = extract_text_from_pdf(path)

            pdf_chunks = chunk_text(text)

            for chunk in pdf_chunks:
                chunks.append(chunk)
                sources.append(file_name)

    return chunks, sources

# --------------------------------------------------
# FAISS
# --------------------------------------------------
@st.cache_resource
def create_index(chunks_tuple):

    model = load_embedding_model()

    chunks = list(chunks_tuple)

    embeddings = model.encode(chunks)

    embeddings = np.array(
        embeddings
    ).astype("float32")

    index = faiss.IndexFlatL2(
        embeddings.shape[1]
    )

    index.add(embeddings)

    return index

# --------------------------------------------------
# SEARCH
# --------------------------------------------------
def search_chunks(
        query,
        chunks,
        sources,
        model,
        index,
        top_k=3
):

    query_embedding = model.encode([query])

    query_embedding = np.array(
        query_embedding
    ).astype("float32")

    distances, indices = index.search(
        query_embedding,
        min(top_k, len(chunks))
    )

    results = []

    for idx in indices[0]:

        results.append({
            "source": sources[idx],
            "content": chunks[idx]
        })

    return results

# --------------------------------------------------
# GEMINI
# --------------------------------------------------
def generate_answer(query, results):

    context = ""

    for r in results:

        context += (
            f"\nSource:{r['source']}\n"
        )

        context += r["content"]
        context += "\n"

    prompt = f"""
You are SmartAid Scheme Advisor.

Use ONLY the context.

Question:
{query}

Context:
{context}

Provide:

Recommended Scheme
Eligibility
Benefits
Reason
Next Action
"""

    try:

        model = genai.GenerativeModel(
            "gemini-2.5-flash"
        )

        response = model.generate_content(
            prompt
        )

        return response.text

    except Exception as e:
        return str(e)

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------
pdf_files = [
    f for f in os.listdir(PDF_FOLDER)
    if f.endswith(".pdf")
]

c1,c2,c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="metric-card blue">
    <h2>{len(pdf_files)}</h2>
    PDF Files
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="metric-card green">
    <h2>FAISS</h2>
    Vector Search
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card orange">
    <h2>Gemini</h2>
    AI Advisor
    </div>
    """, unsafe_allow_html=True)

st.write("")

# --------------------------------------------------
# PDF UPLOAD
# --------------------------------------------------


st.subheader("📤 Upload Government Scheme PDFs")

uploaded_files = st.file_uploader(
    "Upload PDF Files",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:

    for uploaded_file in uploaded_files:

        file_path = os.path.join(
            PDF_FOLDER,
            uploaded_file.name
        )

        with open(file_path, "wb") as f:
            f.write(
                uploaded_file.getbuffer()
            )

    st.success(
        "PDF files uploaded successfully."
    )

st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# VIEW PDF LIST
# --------------------------------------------------
with st.expander("📂 Uploaded PDF Library"):

    if len(pdf_files) == 0:
        st.info("No PDFs uploaded.")
    else:
        for pdf in pdf_files:
            st.write("📄", pdf)

# --------------------------------------------------
# QUERY
# --------------------------------------------------
st.subheader("🔍 Ask Scheme Question")

query = st.text_area(
    "Enter person profile or question",
    placeholder="Age 65, unemployed, widow, needs pension support"
)

if st.button(
    "Generate RAG Recommendation",
    use_container_width=True
):

    chunks, sources = load_all_pdf_chunks()

    if len(chunks) == 0:
        st.error(
            "Upload PDF files first."
        )

    elif not GOOGLE_API_KEY:
        st.error(
            "Google API Key missing."
        )

    else:

        model = load_embedding_model()

        index = create_index(
            tuple(chunks)
        )

        results = search_chunks(
            query,
            chunks,
            sources,
            model,
            index
        )

        st.subheader(
            "📄 Retrieved PDF Chunks"
        )

        for r in results:

            st.markdown(f"""
            <div class="chunk-card">
            <b>Source:</b> {r['source']}<br><br>
            {r['content'][:1000]}
            </div>
            """, unsafe_allow_html=True)

        st.subheader(
            "🤖 Gemini Recommendation"
        )

        answer = generate_answer(
            query,
            results
        )

        st.markdown(f"""
        <div class="answer-card">
        {answer}
        </div>
        """, unsafe_allow_html=True)