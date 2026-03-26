"""
Streamlit Dashboard — Interactive dashboard for the AI Customer Service Platform.
Provides live chat, agent dashboard, sentiment tracking, escalation queue,
ticket analytics, and knowledge base explorer.
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="AI Customer Service Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar Navigation ────────────────────────────────────────────

st.sidebar.title("🤖 Customer Service AI")
page = st.sidebar.radio(
    "Navigate",
    [
        "💬 Live Chat Simulator",
        "👁️ Agent Dashboard",
        "📊 Sentiment Tracking",
        "🚨 Escalation Queue",
        "🎫 Ticket Analytics",
        "📚 Knowledge Base Explorer",
    ],
)


def api_call(method: str, endpoint: str, data: dict | None = None) -> dict | None:
    """Make an API call to the FastAPI backend."""
    url = f"{API_BASE}{endpoint}"
    try:
        if method == "GET":
            resp = requests.get(url, timeout=30)
        else:
            resp = requests.post(url, json=data, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the API server. Make sure it's running on localhost:8000.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"API error: {e}")
        return None


# ── Page: Live Chat Simulator ──────────────────────────────────────

if page == "💬 Live Chat Simulator":
    st.title("💬 Live Chat Simulator")
    st.markdown("Test the AI customer service agent with real conversations.")

    col1, col2 = st.columns([2, 1])

    with col1:
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []
            st.session_state.conversation_id = None

        customer_name = st.text_input("Your name (optional):", key="customer_name")

        for msg in st.session_state.chat_messages:
            role = msg["role"]
            with st.chat_message(role):
                st.write(msg["content"])

        user_input = st.chat_input("Type your message...")

        if user_input:
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    result = api_call("POST", "/chat", {
                        "message": user_input,
                        "conversation_id": st.session_state.conversation_id,
                        "customer_name": customer_name or None,
                    })

                if result:
                    st.session_state.conversation_id = result["conversation_id"]
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": result["response"],
                    })
                    st.write(result["response"])
                else:
                    st.write("Sorry, I'm having trouble connecting. Please try again.")

        if st.button("🔄 New Conversation"):
            st.session_state.chat_messages = []
            st.session_state.conversation_id = None
            st.rerun()

    with col2:
        st.subheader("🔍 Message Analysis")

        if st.session_state.chat_messages:
            last_user_msg = None
            for msg in reversed(st.session_state.chat_messages):
                if msg["role"] == "user":
                    last_user_msg = msg["content"]
                    break

            if last_user_msg:
                st.markdown("**Intent Classification**")
                intent_result = api_call("POST", "/classify", {"message": last_user_msg})
                if intent_result:
                    st.json(intent_result)

                st.markdown("**Sentiment Analysis**")
                sentiment_result = api_call("POST", "/sentiment", {
                    "message": last_user_msg,
                    "conversation_id": st.session_state.conversation_id,
                })
                if sentiment_result:
                    score = sentiment_result.get("sentiment_score", 0)
                    emotion = sentiment_result.get("emotion", "neutral")
                    emoji_map = {
                        "angry": "😡", "frustrated": "😤",
                        "neutral": "😐", "satisfied": "😊", "happy": "😄",
                    }
                    st.metric("Emotion", f"{emoji_map.get(emotion, '😐')} {emotion}")
                    st.metric("Score", f"{score:.2f}")
                    if sentiment_result.get("needs_empathy"):
                        st.warning("⚠️ Empathy response recommended")


# ── Page: Agent Dashboard ──────────────────────────────────────────

elif page == "👁️ Agent Dashboard":
    st.title("👁️ Agent Dashboard")
    st.markdown("Monitor all active conversations and system status.")

    col1, col2, col3 = st.columns(3)
    with col1:
        health = api_call("GET", "/health")
        if health:
            st.metric("API Status", "🟢 Healthy")
        else:
            st.metric("API Status", "🔴 Down")
    with col2:
        st.metric("Active Model", "GPT-4")
    with col3:
        st.metric("Knowledge Base", "ChromaDB")

    st.divider()
    st.subheader("Quick Test Tools")

    test_tab1, test_tab2 = st.tabs(["Intent Classifier", "Sentiment Analyzer"])

    with test_tab1:
        test_msg = st.text_area("Enter a customer message to classify:", key="classify_test")
        if st.button("Classify", key="btn_classify"):
            if test_msg:
                result = api_call("POST", "/classify", {"message": test_msg})
                if result:
                    st.json(result)

    with test_tab2:
        test_msg2 = st.text_area("Enter a message for sentiment analysis:", key="sentiment_test")
        if st.button("Analyze Sentiment", key="btn_sentiment"):
            if test_msg2:
                result = api_call("POST", "/sentiment", {"message": test_msg2})
                if result:
                    st.json(result)


# ── Page: Sentiment Tracking ──────────────────────────────────────

elif page == "📊 Sentiment Tracking":
    st.title("📊 Sentiment Tracking")
    st.markdown("Track customer sentiment over conversations.")

    st.subheader("Analyze a Sequence of Messages")
    st.markdown("Enter multiple messages (one per line) to simulate a conversation sentiment trajectory.")

    messages_input = st.text_area(
        "Messages (one per line):",
        value="Hi, I need help with my billing\n"
              "I've been waiting for 2 hours for a response\n"
              "This is ridiculous, I want to cancel my subscription!\n"
              "Ok fine, let me try the steps you suggested\n"
              "That actually worked, thank you!",
        height=150,
    )

    if st.button("Analyze Trajectory"):
        messages = [m.strip() for m in messages_input.strip().split("\n") if m.strip()]
        if messages:
            results = []
            progress = st.progress(0)
            conv_id = f"trajectory-{int(time.time())}"

            for i, msg in enumerate(messages):
                result = api_call("POST", "/sentiment", {
                    "message": msg,
                    "conversation_id": conv_id,
                })
                if result:
                    result["message"] = msg
                    results.append(result)
                progress.progress((i + 1) / len(messages))

            if results:
                st.subheader("Sentiment Over Time")

                chart_data = {
                    "Message #": list(range(1, len(results) + 1)),
                    "Score": [r.get("sentiment_score", 0) for r in results],
                }
                st.line_chart(chart_data, x="Message #", y="Score")

                st.subheader("Message Details")
                for i, r in enumerate(results):
                    emoji_map = {
                        "angry": "😡", "frustrated": "😤",
                        "neutral": "😐", "satisfied": "😊", "happy": "😄",
                    }
                    emotion = r.get("emotion", "neutral")
                    emoji = emoji_map.get(emotion, "😐")
                    st.markdown(
                        f"**{i + 1}.** {emoji} `{emotion}` (score: {r.get('sentiment_score', 0):.2f}) "
                        f"— *\"{r['message']}\"*"
                    )


# ── Page: Escalation Queue ────────────────────────────────────────

elif page == "🚨 Escalation Queue":
    st.title("🚨 Escalation Queue")
    st.markdown("View and manage escalated conversations.")

    col1, col2 = st.columns(2)
    with col1:
        dept_filter = st.selectbox(
            "Filter by Department",
            ["All", "billing", "technical_l2", "account", "management"],
        )
    with col2:
        priority_filter = st.selectbox(
            "Filter by Priority",
            ["All", "P1", "P2", "P3", "P4"],
        )

    params = {}
    if dept_filter != "All":
        params["department"] = dept_filter
    if priority_filter != "All":
        params["priority"] = priority_filter

    query = "&".join(f"{k}={v}" for k, v in params.items())
    endpoint = f"/escalation-queue?{query}" if query else "/escalation-queue"
    queue = api_call("GET", endpoint)

    if queue:
        if not queue:
            st.info("No escalations in queue. 🎉")
        else:
            for esc in queue:
                priority_colors = {"P1": "🔴", "P2": "🟠", "P3": "🟡", "P4": "🟢"}
                color = priority_colors.get(esc.get("priority", "P4"), "⚪")

                with st.expander(
                    f"{color} {esc.get('id', 'N/A')} | {esc.get('priority', 'N/A')} | "
                    f"{esc.get('department_name', 'N/A')} | {esc.get('status', 'pending')}"
                ):
                    st.markdown(f"**Summary:** {esc.get('summary', 'N/A')}")
                    st.markdown(f"**Recommended Action:** {esc.get('recommended_action', 'N/A')}")
                    st.markdown(f"**Triggers:** {', '.join(esc.get('triggers_matched', []))}")
                    st.markdown(f"**SLA:** {esc.get('sla_hours', 'N/A')} hours")
                    st.markdown(f"**Created:** {esc.get('created_at', 'N/A')}")
    else:
        st.info("Connect to the API to view escalation queue.")

    st.divider()
    st.subheader("Test Escalation Evaluation")
    test_history = st.text_area(
        "Paste conversation history:",
        value="Customer: I've been having sync issues for a week now.\n"
              "Agent: I'm sorry to hear that. Let me help.\n"
              "Customer: I already tried everything you suggested last time. Nothing works!\n"
              "Agent: I understand your frustration.\n"
              "Customer: I want to cancel and switch to Dropbox!",
    )
    if st.button("Evaluate Escalation"):
        result = api_call("POST", "/escalate", {
            "conversation_history": test_history,
            "intent": "technical_support",
            "sentiment": "frustrated",
            "sentiment_score": -0.7,
            "turn_count": 5,
        })
        if result:
            if result.get("should_escalate"):
                st.error(f"🚨 ESCALATE — {result['priority']} → {result.get('department_name', 'N/A')}")
            else:
                st.success("✅ No escalation needed")
            st.json(result)


# ── Page: Ticket Analytics ────────────────────────────────────────

elif page == "🎫 Ticket Analytics":
    st.title("🎫 Ticket Analytics")
    st.markdown("Analyze support tickets for patterns, root causes, and trends.")

    st.subheader("Analyze Tickets")

    sample_tickets = [
        {"subject": "Cannot sync files after update", "body": "Since the latest update v4.2, my files stopped syncing. I've tried restarting."},
        {"subject": "Charged twice this month", "body": "I see two charges of $25 on my credit card for December. Please refund the duplicate."},
        {"subject": "Need to add SSO for our team", "body": "We're on the Professional plan with 50 users. How do we enable SSO integration?"},
        {"subject": "App crashes on Mac M2", "body": "CloudSync Pro crashes immediately on startup on my new MacBook Pro M2. macOS 14.1."},
        {"subject": "Request dark mode", "body": "Would love to see a dark mode option in the desktop app. It's hard on the eyes at night."},
    ]

    st.markdown("**Sample tickets to analyze:**")
    for i, ticket in enumerate(sample_tickets):
        st.markdown(f"{i + 1}. **{ticket['subject']}** — {ticket['body'][:80]}...")

    if st.button("Analyze Sample Tickets"):
        with st.spinner("Analyzing tickets..."):
            result = api_call("POST", "/tickets/analyze", {"tickets": sample_tickets})

        if result:
            analytics = result.get("aggregate_analytics", {})

            st.subheader("Aggregate Analytics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Tickets", analytics.get("total_tickets", len(sample_tickets)))
            with col2:
                avg_hours = analytics.get("avg_estimated_resolution_hours", 0)
                st.metric("Avg Resolution Time", f"{avg_hours:.1f}h")
            with col3:
                st.metric("Top Category", max(
                    analytics.get("category_distribution", {"N/A": 0}),
                    key=analytics.get("category_distribution", {"N/A": 0}).get,
                ))

            cat_dist = analytics.get("category_distribution", {})
            if cat_dist:
                st.subheader("Category Distribution")
                st.bar_chart(cat_dist)

            sev_dist = analytics.get("severity_distribution", {})
            if sev_dist:
                st.subheader("Severity Distribution")
                st.bar_chart(sev_dist)

            trends = analytics.get("trends", [])
            if trends:
                st.subheader("Detected Trends")
                for trend in trends:
                    st.markdown(f"- {trend}")

            recommendations = analytics.get("recommendations", [])
            if recommendations:
                st.subheader("Recommendations")
                for rec in recommendations:
                    st.markdown(f"- {rec}")

            st.subheader("Individual Ticket Analyses")
            individual = result.get("individual_analyses", [])
            for i, analysis in enumerate(individual):
                with st.expander(f"Ticket {i + 1}: {sample_tickets[i]['subject']}"):
                    st.json(analysis)


# ── Page: Knowledge Base Explorer ─────────────────────────────────

elif page == "📚 Knowledge Base Explorer":
    st.title("📚 Knowledge Base Explorer")
    st.markdown("Browse and search the customer service knowledge base.")

    search_query = st.text_input("Search the knowledge base:", placeholder="e.g., How do I reset my password?")

    category_filter = st.selectbox(
        "Filter by category",
        ["All", "Product FAQs", "Billing & Pricing", "Troubleshooting",
         "Returns & Refunds", "Account Management"],
    )

    if search_query:
        st.subheader(f"Results for: \"{search_query}\"")
        st.info(
            "Knowledge base search requires the ChromaDB vector store to be loaded. "
            "Run `make load-kb` to populate the knowledge base, then query via the API."
        )

    st.divider()
    st.subheader("Knowledge Base Files")
    import os
    from pathlib import Path

    kb_dir = Path("data/knowledge_base")
    if kb_dir.exists():
        for f in sorted(kb_dir.glob("*.txt")):
            with st.expander(f"📄 {f.name}"):
                st.text(f.read_text(encoding="utf-8")[:2000])
                if f.stat().st_size > 2000:
                    st.caption(f"... truncated ({f.stat().st_size:,} bytes total)")
    else:
        st.warning(
            "Knowledge base not found. Run `make generate-kb` to create sample documents."
        )
