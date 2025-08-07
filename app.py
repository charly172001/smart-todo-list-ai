import streamlit as st
import pandas as pd

# Gradient background and custom styling
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(to right, #fceabb, #f8b500);
        }
        .big-title {
            font-size: 3em;
            font-weight: bold;
            color: #ffffff;
            text-align: center;
            margin-bottom: 20px;
        }
        .styled-button button {
            background-color: #ff914d !important;
            color: white !important;
            border-radius: 10px !important;
            padding: 0.5em 1em !important;
            font-weight: bold !important;
            transition: 0.3s;
        }
        .styled-button button:hover {
            background-color: #e06e00 !important;
        }
        .fade-in {
            animation: fadeIn 1.5s ease-in;
        }
        @keyframes fadeIn {
            from {opacity: 0;}
            to {opacity: 1;}
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="big-title fade-in">📋 Smart To-Do List Analyzer</div>', unsafe_allow_html=True)

# Task input
if "task_input" not in st.session_state:
    st.session_state.task_input = ""

st.session_state.task_input = st.text_area(
    "Enter your to-do tasks (one per line):",
    value=st.session_state.task_input,
    key="input_text_area",
    height=150
)

# Buttons
col1, col2 = st.columns([1, 1])
with col1:
    analyze_button = st.button("🧠 Analyze Tasks", type="primary")
with col2:
    if st.button("🗑️ Clear Tasks"):
        st.session_state.task_input = ""
        st.rerun()

# Analysis logic
if analyze_button and st.session_state.task_input.strip():
    tasks = st.session_state.task_input.strip().split("\n")

    task_data = []
    for task in tasks:
        task_info = {
            "task": task,
            "category": "Personal" if "call" in task.lower() else "Errand" if "groceries" in task.lower() else "Work",
            "priority": "High" if "assignment" in task.lower() or "groceries" in task.lower() else "Medium",
        }
        task_data.append(task_info)

    st.success("✅ Analysis Complete!", icon="✅")

    df = pd.DataFrame(task_data)
    df["priority"] = df["priority"].replace({
        "High": "🔥 High",
        "Medium": "⚡ Medium",
        "Low": "💤 Low"
    })

    st.dataframe(df, use_container_width=True)

    # CSV Download
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="todo_tasks.csv", mime="text/csv")
