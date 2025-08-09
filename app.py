import streamlit as st
import pandas as pd

# ---------- Styling ----------
st.markdown(
    """
    <style>
        .stApp { background: linear-gradient(to right, #fceabb, #f8b500); }
        .big-title {
            font-size: 3em; font-weight: bold; color: #ffffff;
            text-align: center; margin-bottom: 20px;
        }
        .styled-button button {
            background-color: #ff914d !important; color: white !important;
            border-radius: 10px !important; padding: 0.5em 1em !important;
            font-weight: bold !important; transition: 0.3s;
        }
        .styled-button button:hover { background-color: #e06e00 !important; }
        .fade-in { animation: fadeIn 1.5s ease-in; }
        @keyframes fadeIn { from {opacity: 0;} to {opacity: 1;} }

        /* Summary chips */
        .chip-bar { display: flex; gap: 10px; margin: 10px 0 4px 0; }
        .chip {
            display: inline-flex; align-items: center; gap: 6px;
            padding: 8px 12px; border-radius: 999px; font-weight: 600;
            color: #222; background: #fff; box-shadow: 0 2px 6px rgba(0,0,0,.08);
        }
        .chip-high   { border: 2px solid #ff4d4d; }
        .chip-medium { border: 2px solid #ffcc00; }
        .chip-low    { border: 2px solid #72d572; }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="big-title fade-in">📋 Smart To-Do List Analyzer</div>', unsafe_allow_html=True)

# ---------- Session init ----------
if "df_raw" not in st.session_state:
    st.session_state.df_raw = None
if "priority_filter" not in st.session_state:
    st.session_state.priority_filter = "All"

# ---------- Input (let Streamlit manage the state via key only) ----------
st.text_area(
    "Enter your to-do tasks (one per line):",
    key="task_input",
    height=150
)

col1, col2 = st.columns([1, 1])
with col1:
    analyze_button = st.button("🧠 Analyze Tasks", type="primary")
with col2:
    if st.button("🗑️ Clear Tasks"):
        st.session_state.task_input = ""
        st.session_state.df_raw = None
        st.rerun()

# ---------- Parse on Analyze ----------
if analyze_button and st.session_state.task_input.strip():
    tasks = st.session_state.task_input.strip().split("\n")

    rows = []
    for task in tasks:
        t = task.strip()
        if not t:
            continue
        lower = t.lower()
        category = "Personal" if "call" in lower else "Errand" if "groceries" in lower else "Work"
        priority = "High" if ("assignment" in lower or "groceries" in lower) else "Medium"
        rows.append({"task": t, "category": category, "priority": priority})

    st.session_state.df_raw = pd.DataFrame(rows) if rows else None
    if st.session_state.df_raw is None or st.session_state.df_raw.empty:
        st.info("No valid tasks detected. Please add at least one line.")
    else:
        st.success("✅ Analysis Complete!", icon="✅")

# ---------- Render (independent of the Analyze button) ----------
df_raw = st.session_state.df_raw
if df_raw is not None and not df_raw.empty:

    # Summary counts (no emojis)
    high_n   = int((df_raw["priority"] == "High").sum())
    medium_n = int((df_raw["priority"] == "Medium").sum())
    low_n    = int((df_raw["priority"] == "Low").sum())

    # Summary chips
    st.markdown(
        f"""
        <div class="chip-bar">
            <div class="chip chip-high">🔥 High: {high_n}</div>
            <div class="chip chip-medium">⚡ Medium: {medium_n}</div>
            <div class="chip chip-low">💤 Low: {low_n}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Priority filter (bind directly to session via key; no manual index juggling)
    st.radio(
        "Filter by priority",
        options=["All", "High", "Medium", "Low"],
        key="priority_filter",
        horizontal=True
    )
    filter_choice = st.session_state.priority_filter

    # Apply filtering and sort on RAW data
    if filter_choice == "All":
        df_view = df_raw.copy()
    else:
        df_view = df_raw[df_raw["priority"] == filter_choice].copy()

    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    df_view["__prio"] = df_view["priority"].map(priority_order).fillna(99)
    df_view = df_view.sort_values(["__prio", "task"]).drop(columns="__prio").reset_index(drop=True)

    # Add emoji labels for display only
    df_display = df_view.copy()
    df_display["priority"] = df_display["priority"].replace({
        "High": "🔥 High",
        "Medium": "⚡ Medium",
        "Low": "💤 Low"
    })

    st.dataframe(df_display, use_container_width=True)

    # CSV of the filtered view (no emojis)
    csv = df_view.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="todo_tasks.csv", mime="text/csv")
