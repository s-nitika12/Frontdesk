import streamlit as st
import requests

# Sidebar: API Base URL
API_BASE = st.sidebar.text_input("API Base URL", "http://localhost:8000")

st.title("Supervisor Admin — Human-in-the-Loop")

# Create tabs
tabs = st.tabs(["Pending Requests", "History", "Learned Answers"])

# ---------------- Pending Requests Tab ----------------
with tabs[0]:
    st.header("Pending Requests")
    try:
        resp = requests.get(f"{API_BASE}/api/requests?state=pending")
        pending = resp.json() if resp.status_code == 200 else []
    except Exception as e:
        st.error(f"Failed to fetch pending requests: {e}")
        pending = []

    for r in pending:
        with st.expander(f"Request #{r['id']} — {r['state']}"):
            st.write("Customer ID:", r["customer_id"])
            st.write("Question:", r["question_text"])

            ans = st.text_area("Answer", key=f"ans_{r['id']}")
            sup_id = st.text_input("Supervisor ID (optional)", key=f"sup_{r['id']}")

            if st.button("Submit Answer", key=f"submit_{r['id']}"):
                payload = {"answer": ans, "supervisor_id": sup_id or None}
                try:
                    pr = requests.post(f"{API_BASE}/api/requests/{r['id']}/respond", json=payload)
                    if pr.status_code == 200:
                        st.success("Submitted and customer notified.")
                    else:
                        st.error(f"Error: {pr.text}")
                except Exception as e:
                    st.error(f"Failed to submit answer: {e}")

# ---------------- History Tab ----------------
with tabs[1]:
    st.header("History (resolved/unresolved)")
    try:
        resp = requests.get(f"{API_BASE}/api/requests")
        allreq = resp.json() if resp.status_code == 200 else []
    except Exception as e:
        st.error(f"Failed to fetch history: {e}")
        allreq = []

    for r in allreq:
        st.write(f"#{r['id']} — {r['state']} — {r['created_at']}")
        st.write("Question:", r["question_text"])
        if r.get("response_text"):
            st.info(f"Response: {r['response_text']}")

# ---------------- Learned Answers (KB) Tab ----------------
with tabs[2]:
    st.header("Learned Answers (KB)")
    try:
        resp = requests.get(f"{API_BASE}/api/kb")
        kb = resp.json() if resp.status_code == 200 else []
    except Exception as e:
        st.error(f"Failed to fetch KB entries: {e}")
        kb = []

    q = st.text_input("Search Question (fuzzy)")
    filtered = kb
    if q:
        filtered = [
            e for e in kb
            if q.lower() in e["question_text"].lower() or q.lower() in (e.get("tags") or "").lower()
        ]

    for e in filtered:
        st.write(f"Q: {e['question_text']}")
        st.write(f"A: {e['answer_text']}")
        st.write(f"Added by: {e['created_by']} at {e['created_at']}")
        st.markdown("---")
