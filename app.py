import streamlit as st

from inference import generate_response


def safe_rerun():
    rerun_func = getattr(st, "rerun", None)
    if callable(rerun_func):
        rerun_func()
        return

    experimental_rerun = getattr(st, "experimental_rerun", None)
    if callable(experimental_rerun):
        experimental_rerun()
        return

    st.warning("Refresh the page to see the updated chat.")


st.set_page_config(page_title="AI E-Commerce Bot", page_icon="🛍️", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0b1220 0%, #111827 100%);
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1 {
        font-size: 3rem !important;
        font-weight: 800;
        color: #f3f4f6;
        letter-spacing: -0.04em;
    }
    .subtitle {
        font-size: 1.25rem;
        color: #dbeafe;
        margin-top: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .sidebar .block-container {
        background: rgba(17, 24, 39, 0.85);
        border-radius: 18px;
        padding: 1rem;
    }
    .chat-row {
        display: flex;
        justify-content: flex-start;
        margin: 10px 0;
    }
    .chat-row.user {
        justify-content: flex-end;
    }
    .message-box {
        max-width: 80%;
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 18px;
        padding: 0.8rem 1rem;
        color: white;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    .chat-row.user .message-box {
        background: rgba(91, 90, 255, 0.30);
        border-color: rgba(132, 122, 255, 0.7);
    }
    .stTextInput > div > div > input {
        border-radius: 14px;
        border: 1px solid rgba(148, 163, 184, 0.5);
        background: rgba(15, 23, 42, 0.9);
        color: white;
        min-height: 52px;
    }
    .stButton > button {
        border-radius: 12px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        color: white;
        border: none;
        font-weight: 600;
        min-height: 48px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("AI E-Commerce Assistant")
st.markdown('<div class="subtitle">Product recommendations, order tracking, and FAQ support</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("What I can help with")
    st.markdown(
        "- Recommend products\n"
        "- Track orders\n"
        "- Answer common shopping questions"
    )
    st.write("Example queries:")
    st.markdown(
        "- Recommend a laptop under 60000 for programming\n"
        "- Where is my order ORD1001?\n"
        "- What is your return policy?"
    )
    if st.button("Clear chat"):
        st.session_state["chat_history"] = []

try:
    chat_history = st.session_state["chat_history"]
except Exception:
    chat_history = []
    st.session_state["chat_history"] = chat_history

for role, message in chat_history:
    align = "user" if role == "user" else "assistant"
    label = "You" if role == "user" else "Assistant"
    st.markdown(
        f'<div class="chat-row {align}"><div class="message-box"><strong>{label}:</strong> {message}</div></div>',
        unsafe_allow_html=True,
    )

with st.form(key="chat_form"):
    user_input = st.text_input("Ask about products, orders, or delivery...", key="user_query")
    submitted = st.form_submit_button("Send")

if submitted and user_input.strip():
    user_text = user_input.strip()
    if not st.session_state["chat_history"] or st.session_state["chat_history"][-1] != ("user", user_text):
        st.session_state["chat_history"].append(("user", user_text))

    response = generate_response(user_text, st.session_state["chat_history"])
    if not st.session_state["chat_history"] or st.session_state["chat_history"][-1] != ("assistant", response):
        st.session_state["chat_history"].append(("assistant", response))

    safe_rerun()
