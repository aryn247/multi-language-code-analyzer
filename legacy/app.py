import streamlit as st
import tempfile
import os
from multi_language_analyzer import analyze_code, visualize_dependencies

st.set_page_config(
    page_title="Multi-Language Code Analyzer & Optimizer",
    layout="wide",
    page_icon="🧠"
)

st.title("🧠 Multi-Language Code Analyzer & Optimizer")
st.markdown("Analyze and visualize your code’s structure, maintainability, and dependencies across multiple languages.")

# --- File Upload Section ---
uploaded_file = st.file_uploader("📂 Upload your code file", type=["py", "java", "js", "c", "cpp"])

if uploaded_file:
    # Save temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_path = temp_file.name

    st.success(f"✅ File uploaded successfully: `{uploaded_file.name}`")

    # Detect language based on extension
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    lang_map = {
        ".py": "python",
        ".java": "java",
        ".js": "js",
        ".c": "c",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp"
    }
    lang = lang_map.get(ext, "unknown")

    st.info(f"🔍 Detected Language: **{lang.upper()}**")

    # --- Run Analysis ---
    with st.spinner("Analyzing code..."):
        report = analyze_code(temp_path, lang)
    
    st.subheader("📊 Analysis Result")
    if isinstance(report, dict):
        # Display key metrics in columns
        cols = st.columns(3)
        if "Maintainability Index" in report:
            cols[0].metric("Maintainability Index", round(report["Maintainability Index"], 2))
        if "Average Complexity" in report:
            cols[1].metric("Average Complexity", round(report["Average Complexity"], 2))
        if "Efficiency Grade" in report:
            cols[2].metric("Efficiency Grade", report["Efficiency Grade"])

        # Show full JSON summary
        with st.expander("View Full Report"):
            st.json(report)
    else:
        st.error("⚠️ Analyzer returned an unexpected response. Check your analyzer module.")

    # --- Dependency Graph ---
    st.subheader("🔗 Dependency Graph")
    try:
        graph_path = visualize_dependencies(temp_path)
        if graph_path and os.path.exists(graph_path):
            st.image(graph_path, caption="Dependency Graph", use_container_width=True)
        else:
            st.info("No dependency graph generated for this file.")
    except Exception as e:
        st.warning(f"Could not visualize dependencies: {e}")

else:
    st.info("👆 Upload a source code file to begin analysis.")

st.markdown("---")
st.caption("Developed as part of Final Year Project — Multi-Language Code Analyzer & Optimizer")
