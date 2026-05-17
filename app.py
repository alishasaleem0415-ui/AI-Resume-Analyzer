import streamlit as st
import pandas as pd
import os
from utils.pdf_reader import extract_text_from_pdf
from utils.scorer import calculate_ats_score
from analyzer import analyze_resume, get_resume_tips
from dataset_loader import (
    load_csv, get_csv_categories, get_csv_sample_resumes,
    get_top_keywords_from_csv, get_csv_stats,
    get_pdf_categories, get_pdf_files, count_pdfs_per_category,
    get_top_keywords_from_pdfs, get_sample_pdf_texts,
    get_smart_keywords
)

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main { padding: 1.5rem; }
    .stButton>button {
        background-color: #4F46E5; color: white;
        border-radius: 8px; padding: 0.5rem 2rem;
        font-size: 1rem; font-weight: 600;
        border: none; width: 100%;
    }
    .stButton>button:hover { background-color: #4338CA; }
    .score-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px; padding: 2rem;
        text-align: center; color: white; margin: 1rem 0;
    }
    .score-number { font-size: 3.5rem; font-weight: 800; line-height: 1; }
    .score-label  { font-size: 1.1rem; font-weight: 600; margin-top: 0.5rem; }
    .chip { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.82rem; margin:3px; }
    .chip-green { background:#D1FAE5; color:#065F46; }
    .chip-red   { background:#FEE2E2; color:#991B1B; }
    .chip-blue  { background:#DBEAFE; color:#1E40AF; }
    .chip-purple{ background:#EDE9FE; color:#5B21B6; }
    .sample-box {
        background:#F8FAFC; border-left:4px solid #4F46E5;
        border-radius:4px; padding:1rem; font-size:0.82rem;
        color:#374151; white-space:pre-wrap;
        max-height:220px; overflow-y:auto;
    }
    .stat-card {
        background:#F1F5F9; border-radius:10px;
        padding:1rem; text-align:center;
    }
    .footer {
        text-align:center; color:#9CA3AF;
        font-size:0.8rem; margin-top:3rem;
        padding-top:1rem; border-top:1px solid #E5E7EB;
    }
    .badge {
        background:#EEF2FF; border:1px solid #C7D2FE;
        border-radius:8px; padding:0.4rem 0.8rem;
        color:#4338CA; font-size:0.82rem; font-weight:600;
        display:inline-block; margin:2px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  LOAD DATA (cached)
# ─────────────────────────────────────────────
@st.cache_data
def load_all_data():
    df, err = load_csv()
    csv_cats  = get_csv_categories(df)
    pdf_cats  = get_pdf_categories()
    pdf_counts = count_pdfs_per_category()
    return df, err, csv_cats, pdf_cats, pdf_counts

df, csv_error, csv_cats, pdf_cats, pdf_counts = load_all_data()

csv_loaded = df is not None
pdf_loaded = len(pdf_cats) > 0
total_pdfs = sum(pdf_counts.values()) if pdf_counts else 0

# All unique categories (union of CSV + PDF)
all_categories = sorted(set(csv_cats + pdf_cats))

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📄 AI Resume Analyzer")
    st.markdown("**Alisha Saleem · BS-AI · UMT Lahore**")
    st.markdown("---")

    # Dataset status
    st.markdown("### 📦 Dataset Status")
    if csv_loaded:
        st.markdown(f'<div class="badge">✅ CSV: {len(df):,} resumes</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="badge" style="background:#FEE2E2;border-color:#FCA5A5;color:#991B1B;">❌ CSV not found</div>', unsafe_allow_html=True)

    if pdf_loaded:
        st.markdown(f'<div class="badge">✅ PDFs: {total_pdfs:,} files · {len(pdf_cats)} categories</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="badge" style="background:#FEE2E2;border-color:#FCA5A5;color:#991B1B;">❌ PDF folders not found</div>', unsafe_allow_html=True)

    if not csv_loaded or not pdf_loaded:
        st.markdown("---")
        st.markdown("**📁 Expected folder structure:**")
        st.code("""AI-Resume-Analyzer/
└── data/
    ├── resume/
    │   └── Resume.csv
    └── data/
        ├── ENGINEERING/
        │   ├── resume1.pdf
        │   └── ...
        ├── MEDICAL/
        └── ...""")

    st.markdown("---")
    st.markdown("### ℹ️ How to Use")
    st.markdown("""
1. Select a **job category**
2. Review **smart keywords** (from real PDFs!)
3. Upload your **resume PDF**
4. Click **Analyze**
5. Review score & tips
    """)

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("# 📄 AI Resume Analyzer")
st.markdown("**ATS Score · Smart Keywords from Real Resumes · Skills Gap · Dataset Explorer**")
st.markdown("---")

# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Analyze Resume",
    "📊 Dataset Overview",
    "📚 Browse PDF Resumes",
    "📝 CSV Explorer"
])

# ══════════════════════════════════════════════
#  TAB 1 — ANALYZE
# ══════════════════════════════════════════════
with tab1:
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown("### 🎯 Step 1 — Select Job Category")

        selected_cat = st.selectbox(
            "Choose a job category",
            ["-- Select --"] + all_categories,
            key="analyze_cat"
        )

        st.markdown("### 🔑 Step 2 — Keywords")

        if selected_cat != "-- Select --":
            with st.spinner(f"Extracting smart keywords from real {selected_cat} resumes..."):
                smart_kws = get_smart_keywords(df, selected_cat, top_n=15)

            if smart_kws:
                st.markdown("**💡 Smart keywords (extracted from real PDF + CSV resumes):**")
                chips = "".join(f'<span class="chip chip-purple">{k}</span>' for k in smart_kws)
                st.markdown(chips, unsafe_allow_html=True)
                default_kws = ", ".join(smart_kws[:12])
            else:
                default_kws = ""
        else:
            default_kws = ""
            st.info("Select a category above to get smart keyword suggestions.")

        job_input = st.text_area(
            "Edit or add your own keywords (comma separated)",
            value=default_kws,
            height=130,
            placeholder="e.g. Python, Machine Learning, NLP, TensorFlow, SQL"
        )
        st.caption("These keywords are compared against your resume for ATS scoring")

    with right:
        st.markdown("### 📁 Step 3 — Upload Your Resume")
        uploaded_file = st.file_uploader("PDF only", type=["pdf"], label_visibility="collapsed")

        if uploaded_file:
            st.success(f"✅ **{uploaded_file.name}** uploaded")
        else:
            st.info("📂 Upload your resume as a PDF file")

        st.markdown("")
        st.markdown("### 🚀 Step 4 — Analyze")
        analyze_btn = st.button("🔍 Analyze My Resume", use_container_width=True)

    # ── RUN ANALYSIS ──────────────────────────────────
    if analyze_btn:
        if not uploaded_file:
            st.warning("⚠️ Please upload your resume PDF.")
            st.stop()
        if not job_input.strip():
            st.warning("⚠️ Please enter at least a few keywords.")
            st.stop()

        with st.spinner("🤖 Analyzing your resume..."):
            resume_text = extract_text_from_pdf(uploaded_file)

            if resume_text.startswith("Error"):
                st.error(f"❌ {resume_text}")
                st.stop()
            if len(resume_text.strip()) < 50:
                st.error("❌ Not enough text extracted. Make sure your PDF is not a scanned image.")
                st.stop()

            job_keywords = [k.strip() for k in job_input.split(",") if k.strip()]
            score, matched, missing = calculate_ats_score(resume_text, job_keywords)
            found_skills, missing_skills = analyze_resume(resume_text)
            tips = get_resume_tips(score, missing)

        # ── RESULTS ───────────────────────────────────
        st.markdown("---")
        st.markdown("## 📊 Your Results")

        score_label = (
            "Excellent Match 🎉" if score >= 70 else
            "Needs Improvement ⚠️" if score >= 40 else
            "Low Match — Revamp Needed ❌"
        )

        # Top metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f"""
        <div class="score-box">
            <div style="opacity:.85;font-size:.85rem;">ATS Score</div>
            <div class="score-number">{score}%</div>
            <div class="score-label">{score_label}</div>
        </div>""", unsafe_allow_html=True)
        m2.metric("✅ Keywords Matched", f"{len(matched)} / {len(job_keywords)}")
        m3.metric("❌ Keywords Missing", len(missing))
        word_count = len(resume_text.split())
        m4.metric("📝 Word Count", word_count)

        st.progress(score / 100)
        st.markdown("")

        # Keywords
        kc1, kc2 = st.columns(2)
        with kc1:
            st.markdown(f"### ✅ Matched ({len(matched)})")
            if matched:
                st.markdown("".join(f'<span class="chip chip-green">✅ {k}</span>' for k in matched), unsafe_allow_html=True)
            else:
                st.info("No keywords matched yet.")

        with kc2:
            st.markdown(f"### ❌ Missing ({len(missing)})")
            if missing:
                st.markdown("".join(f'<span class="chip chip-red">❌ {k}</span>' for k in missing), unsafe_allow_html=True)
            else:
                st.success("All keywords found! 🎉")

        st.markdown("---")

        # Skills
        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown("### 💡 Skills Found")
            if found_skills:
                for cat, skills in found_skills.items():
                    with st.expander(f"✅ {cat} ({len(skills)})"):
                        st.write(", ".join(f"**{s}**" for s in skills))
            else:
                st.warning("No standard skills detected in your resume.")

        with sc2:
            st.markdown("### 🚀 Skills to Add")
            if missing_skills:
                for cat, skills in missing_skills.items():
                    with st.expander(f"➕ {cat} ({len(skills)})"):
                        st.write(", ".join(skills))

        st.markdown("---")

        # Tips
        st.markdown("### 📝 Personalized Tips")
        for tip in tips:
            st.markdown(tip)

        # Compare with dataset
        if selected_cat != "-- Select --" and pdf_loaded:
            st.markdown("---")
            st.markdown(f"### 📊 How You Compare — {selected_cat} Resumes")
            cat_pdfs = get_pdf_files(selected_cat)
            st.info(f"There are **{len(cat_pdfs)} real {selected_cat} resumes** in the dataset. "
                    f"Browse them in the **Browse PDF Resumes** tab to see what top resumes look like!")


# ══════════════════════════════════════════════
#  TAB 2 — DATASET OVERVIEW
# ══════════════════════════════════════════════
with tab2:
    st.markdown("### 📊 Full Dataset Overview")

    if not pdf_loaded and not csv_loaded:
        st.warning("⚠️ No dataset found. Please add the Kaggle dataset files as shown in the sidebar.")
    else:
        # Summary stats
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("📄 CSV Resumes", f"{len(df):,}" if csv_loaded else "N/A")
        s2.metric("📁 PDF Categories", len(pdf_cats) if pdf_loaded else "N/A")
        s3.metric("📑 Total PDF Files", f"{total_pdfs:,}" if pdf_loaded else "N/A")
        s4.metric("🗂️ Total Categories", len(all_categories))

        st.markdown("---")

        if pdf_loaded:
            st.markdown("#### 📁 PDF Resumes by Category")
            pdf_df = pd.DataFrame(
                list(pdf_counts.items()),
                columns=["Category", "PDF Count"]
            ).sort_values("PDF Count", ascending=False)
            st.bar_chart(pdf_df.set_index("Category"))
            st.dataframe(pdf_df, use_container_width=True)

        if csv_loaded and "Category" in df.columns:
            st.markdown("---")
            st.markdown("#### 📝 CSV Resumes by Category")
            csv_counts = df["Category"].value_counts().reset_index()
            csv_counts.columns = ["Category", "Count"]
            st.bar_chart(csv_counts.set_index("Category"))


# ══════════════════════════════════════════════
#  TAB 3 — BROWSE PDF RESUMES
# ══════════════════════════════════════════════
with tab3:
    st.markdown("### 📚 Browse Real PDF Resumes from Dataset")
    st.markdown("Read actual resume content extracted from the Kaggle PDF dataset.")

    if not pdf_loaded:
        st.warning("⚠️ PDF folders not found. Place the category folders in `data/data/`.")
    else:
        pdf_cat_select = st.selectbox("Select a job category", pdf_cats, key="pdf_browse_cat")

        pdf_files_list = get_pdf_files(pdf_cat_select)
        st.markdown(f"**{len(pdf_files_list)} PDF resumes** found in **{pdf_cat_select}**")

        n_show = st.slider("How many sample resumes to display?", 1, min(10, len(pdf_files_list)), 3)

        if st.button("📖 Load Sample Resumes", key="load_pdfs"):
            with st.spinner(f"Extracting text from {n_show} {pdf_cat_select} resumes..."):
                samples = get_sample_pdf_texts(pdf_cat_select, n=n_show)

            if samples:
                for i, (filename, text) in enumerate(samples, 1):
                    with st.expander(f"📄 Resume #{i} — {filename}"):
                        word_c = len(text.split())
                        st.caption(f"Word count: {word_c}")
                        st.markdown(f'<div class="sample-box">{text[:2000]}{"..." if len(text) > 2000 else ""}</div>',
                                    unsafe_allow_html=True)
            else:
                st.warning("Could not extract text from these PDFs. They may be scanned images.")

        st.markdown("---")
        st.markdown("#### 🔑 Top Keywords in This Category's PDFs")
        if st.button("Extract Keywords from PDFs", key="pdf_kws"):
            with st.spinner("Analyzing PDF resumes for top keywords..."):
                kws = get_top_keywords_from_pdfs(pdf_cat_select, max_pdfs=15, top_n=25)
            if kws:
                st.markdown("**Most frequent meaningful words in real resumes:**")
                st.markdown("".join(f'<span class="chip chip-purple">{k}</span>' for k in kws),
                            unsafe_allow_html=True)
            else:
                st.info("No keywords extracted. PDFs may be image-based.")


# ══════════════════════════════════════════════
#  TAB 4 — CSV EXPLORER
# ══════════════════════════════════════════════
with tab4:
    st.markdown("### 📝 CSV Dataset Explorer")
    st.markdown("Explore the Resume.csv text dataset from Kaggle.")

    if not csv_loaded:
        st.warning(f"⚠️ Resume.csv not found. Place it in `data/resume/Resume.csv`")
    else:
        st.markdown(f"**{len(df):,} resumes** across **{len(csv_cats)} categories**")

        # Filter
        csv_cat_filter = st.selectbox("Filter by category", ["-- All --"] + csv_cats, key="csv_cat")
        show_df = df if csv_cat_filter == "-- All --" else df[df["Category"] == csv_cat_filter]

        st.dataframe(
            show_df[["Category", "Resume_str"]].head(20) if "Resume_str" in df.columns else show_df.head(20),
            use_container_width=True
        )

        if csv_cat_filter != "-- All --":
            st.markdown("---")
            st.markdown(f"#### 💡 Top Keywords — {csv_cat_filter}")
            kws = get_top_keywords_from_csv(df, csv_cat_filter, top_n=20)
            if kws:
                st.markdown("".join(f'<span class="chip chip-blue">{k}</span>' for k in kws),
                            unsafe_allow_html=True)

            st.markdown("---")
            st.markdown(f"#### 📄 Sample Resumes — {csv_cat_filter}")
            samples = get_csv_sample_resumes(df, csv_cat_filter, n=2)
            for i, sample in enumerate(samples, 1):
                with st.expander(f"Sample Resume #{i}"):
                    st.markdown(f'<div class="sample-box">{sample[:1500]}...</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Built with ❤️ by <strong>Alisha Saleem</strong> &nbsp;|&nbsp;
    BS Artificial Intelligence · UMT Lahore &nbsp;|&nbsp;
    🤖 Python · Streamlit · Kaggle Dataset
</div>
""", unsafe_allow_html=True)
