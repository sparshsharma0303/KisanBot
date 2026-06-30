import streamlit as st
import requests
import uuid
from datetime import datetime

API_URL = "http://localhost:8000/ask"

# ---------------------------------------------------------
# Page config — must be the first Streamlit command
# ---------------------------------------------------------
st.set_page_config(
    page_title="KisanBot",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Light theme styling
# ---------------------------------------------------------
st.markdown("""
    <style>
        /* Force light backgrounds everywhere, regardless of OS/browser dark mode */
        html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #FAFAF7 !important;
            color: #2B2B22 !important;
        }
        [data-testid="stHeader"] {
            background-color: #FAFAF7 !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #F2F1EA !important;
            border-right: 1px solid #E0DFD5;
        }
        section[data-testid="stSidebar"] * {
            color: #2B2B22 !important;
        }
        [data-testid="stBottomBlockContainer"] {
            background-color: #FAFAF7 !important;
        }
        h1, h2, h3, h4, p, span, label, div {
            color: #2B2B22;
        }
        h1 {
            color: #2F4F2F !important;
        }
        /* Buttons */
        .stButton button {
            background-color: #FFFFFF;
            color: #2B2B22;
            border: 1px solid #D8D6C8;
        }
        .stButton button:hover {
            background-color: #E8E6DA;
            border-color: #C5C3B0;
            color: #2B2B22;
        }
        /* Chat input box */
        div[data-testid="stChatInput"] {
            background-color: #FAFAF7 !important;
        }
        div[data-testid="stChatInput"] textarea {
            background-color: #FFFFFF !important;
            color: #2B2B22 !important;
        }
        /* Chat message bubbles */
        [data-testid="stChatMessage"] {
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 4px;
        }
        /* Info box */
        div[data-testid="stAlertContainer"] {
            background-color: #E8F0E3 !important;
            color: #2B2B22 !important;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------
if "chats" not in st.session_state:
    # chats is a dict: { chat_id: {"title": str, "thread_id": str, "messages": [...]} }
    first_chat_id = str(uuid.uuid4())
    st.session_state.chats = {
        first_chat_id: {
            "title": "New chat",
            "thread_id": "",
            "messages": []
        }
    }
    st.session_state.active_chat_id = first_chat_id

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = list(st.session_state.chats.keys())[0]


def create_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.chats[new_id] = {
        "title": "New chat",
        "thread_id": "",
        "messages": []
    }
    st.session_state.active_chat_id = new_id


def switch_chat(chat_id):
    st.session_state.active_chat_id = chat_id


def delete_chat(chat_id):
    if len(st.session_state.chats) == 1:
        return  # always keep at least one chat
    del st.session_state.chats[chat_id]
    if st.session_state.active_chat_id == chat_id:
        st.session_state.active_chat_id = list(st.session_state.chats.keys())[0]


# ---------------------------------------------------------
# Sidebar — navigation pane
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🌾 KisanBot")
    st.caption("Agricultural Assistant")
    st.divider()

    if st.button("➕ New chat", use_container_width=True):
        create_new_chat()
        st.rerun()

    st.markdown("#### Recent chats")

    # Show chats newest first
    chat_ids = list(st.session_state.chats.keys())[::-1]

    for chat_id in chat_ids:
        chat = st.session_state.chats[chat_id]
        is_active = chat_id == st.session_state.active_chat_id

        col1, col2 = st.columns([5, 1])
        with col1:
            label = ("📍 " if is_active else "💬 ") + chat["title"]
            if st.button(label, key=f"chat_{chat_id}", use_container_width=True):
                switch_chat(chat_id)
                st.rerun()
        with col2:
            if st.button("✕", key=f"del_{chat_id}"):
                delete_chat(chat_id)
                st.rerun()

    st.divider()
    st.caption(f"{len(st.session_state.chats)} conversation(s)")

# ---------------------------------------------------------
# Main chat area
# ---------------------------------------------------------
active_chat = st.session_state.chats[st.session_state.active_chat_id]

st.title("🌾 KisanBot")
st.caption("Your Multilingual Agricultural Assistant — ask anything about crops, soil, pests, or farming practices.")
st.divider()

# Render existing messages
if not active_chat["messages"]:
    st.info("Ask a farming question to get started — e.g. *\"how to protect wheat crop from pests?\"*")

for message in active_chat["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("sources"):
            with st.expander("View sources"):
                for i, src in enumerate(message["sources"], 1):
                    st.markdown(f"**Source {i}:** {src}")

# Chat input
if prompt := st.chat_input("Ask your farming question..."):
    active_chat["messages"].append({"role": "user", "content": prompt})

    # Auto-title the chat from the first message
    if active_chat["title"] == "New chat":
        active_chat["title"] = prompt[:30] + ("..." if len(prompt) > 30 else "")

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    API_URL,
                    json={
                        "question": prompt,
                        "top_k": 3,
                        "thread_id": active_chat["thread_id"]
                    },
                    timeout=60
                )
                data = response.json()
                active_chat["thread_id"] = data["thread_id"]
                answer = data["answer"]
                sources = [s["content"] for s in data.get("sources", [])]

                st.markdown(answer)
                if sources:
                    with st.expander("View sources"):
                        for i, src in enumerate(sources, 1):
                            st.markdown(f"**Source {i}:** {src}")

                active_chat["messages"].append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to KisanBot API. Make sure FastAPI is running on port 8000.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

    st.rerun()