import json
import os
import time
import uuid
from typing import Any, Callable, Dict, List

import streamlit as st
from dotenv import find_dotenv, load_dotenv

# Nạp file .env từ thư mục gốc hoặc thư mục hiện tại
load_dotenv(find_dotenv())

# ===========================================================================
# Cấu hình & Bảng giá từ template.py
# ===========================================================================
PRICING_PER_1K_TOKENS = {
    "gpt-4o": {"input": 0.0025, "output": 0.010},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gemini-2.5-flash": {"input": 0.0003, "output": 0.0025},
    "gemini-2.5-flash-lite": {"input": 0.0001, "output": 0.0004},
    "gemini-2.0-flash": {"input": 0.0001, "output": 0.0004},
    "gemini-2.0-flash-lite": {"input": 0.000075, "output": 0.0003},
    "gemini-3.6-flash": {"input": 0.0003, "output": 0.0025},
    "gemini-flash-latest": {"input": 0.0003, "output": 0.0025},
    "gemini-flash-lite-latest": {"input": 0.0001, "output": 0.0004},
}

DEFAULT_MODEL = os.getenv("LAB_MODEL", "gemini-3.6-flash")

MOVIE_PERSONA = (
    "Bạn là CineBrain - Trợ lý & Chuyên gia điện ảnh AI hàng đầu. "
    "Nhiệm vụ của bạn là tư vấn phim hay, giải thích cốt truyện, so sánh phim, phân tích nhân vật và đạo diễn. "
    "Trả lời bằng tiếng Việt thân thiện, cuốn hút, giàu cảm xúc điện ảnh. "
    "Sử dụng định dạng Markdown đẹp mắt (bôi đậm tên phim, liệt kê danh sách rõ ràng, trích dẫn câu thoại nổi tiếng)."
)

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "history_data.json")


# ===========================================================================
# Tiện ích từ template.py
# ===========================================================================
def count_tokens(text: str, model: str = DEFAULT_MODEL) -> int:
    try:
        import tiktoken

        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))
    except Exception:
        return max(1, len(text) // 4)


def estimate_cost(prompt: str, response: str, model: str = DEFAULT_MODEL) -> dict:
    prompt_tokens = count_tokens(prompt, model=model)
    completion_tokens = count_tokens(response, model=model)
    pricing = PRICING_PER_1K_TOKENS.get(model, PRICING_PER_1K_TOKENS["gpt-4o"])
    prompt_cost = (prompt_tokens / 1000) * pricing["input"]
    completion_cost = (completion_tokens / 1000) * pricing["output"]
    total_cost = prompt_cost + completion_cost
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "prompt_cost": prompt_cost,
        "completion_cost": completion_cost,
        "total_cost": total_cost,
    }


def retry_with_backoff(
    fn: Callable, max_retries: int = 3, base_delay: float = 0.1
) -> Any:
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception:
            if attempt == max_retries:
                raise
            time.sleep(base_delay * (2**attempt))


def get_openai_client():
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    if not api_key:
        st.error("⚠️ Thiếu OPENAI_API_KEY trong môi trường hoặc file .env")
        st.stop()

    return OpenAI(api_key=api_key, base_url=base_url if base_url else None)


# ===========================================================================
# Quản lý Lịch sử Chat (Persistent Session Storage)
# ===========================================================================
def load_sessions() -> Dict[str, dict]:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_sessions(sessions: Dict[str, dict]):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Lỗi khi lưu lịch sử: {e}")


# ===========================================================================
# Streamlit Page Config & Custom CSS
# ===========================================================================
st.set_page_config(
    page_title="CineBrain AI - Movie Chatbot",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Dark Cinematic Theme Customizations */
    .stApp {
        background-color: #0b0d14;
        color: #f1f5f9;
    }
    .stSidebar {
        background-color: #101320 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    h1, h2, h3 {
        color: #e5a00d !important;
        font-family: 'Outfit', sans-serif;
    }
    .stButton button {
        background: linear-gradient(135deg, #e5a00d 0%, #d97706 100%) !important;
        color: #000000 !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 10px !important;
        transition: all 0.2s ease !important;
    }
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(229, 160, 13, 0.4) !important;
    }
    .metric-card {
        background: #141724;
        padding: 12px 16px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 10px;
    }
    .badge-info {
        background: rgba(229, 160, 13, 0.15);
        color: #e5a00d;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.78rem;
        display: inline-block;
        margin-top: 4px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Initialize Session State
if "sessions" not in st.session_state:
    st.session_state.sessions = load_sessions()

if "current_session_id" not in st.session_state:
    # Nếu chưa có session nào, khởi tạo session đầu tiên
    if st.session_state.sessions:
        first_id = list(st.session_state.sessions.keys())[0]
        st.session_state.current_session_id = first_id
    else:
        new_id = str(uuid.uuid4())
        st.session_state.sessions[new_id] = {
            "id": new_id,
            "title": "Cuộc trò chuyện mới",
            "created_at": time.time(),
            "messages": [],
            "total_cost": 0.0,
            "total_tokens": 0,
        }
        st.session_state.current_session_id = new_id
        save_sessions(st.session_state.sessions)


def create_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = {
        "id": new_id,
        "title": f"Chat Phim {len(st.session_state.sessions) + 1}",
        "created_at": time.time(),
        "messages": [],
        "total_cost": 0.0,
        "total_tokens": 0,
    }
    st.session_state.current_session_id = new_id
    save_sessions(st.session_state.sessions)


# ===========================================================================
# SIDEBAR
# ===========================================================================
with st.sidebar:
    st.title("🎬 CineBrain AI")
    st.caption("Trợ lý & Chuyên gia Điện ảnh Thông minh")

    # Nút Chat mới
    if st.button("➕ Cuộc trò chuyện mới", use_container_width=True):
        create_new_chat()
        st.rerun()

    st.markdown("---")
    st.subheader("📜 Lịch sử hội thoại")

    # Danh sách các phiên chat
    session_options = {
        sid: sdata.get("title", f"Chat {sid[:6]}")
        for sid, sdata in st.session_state.sessions.items()
    }

    if session_options:
        selected_sid = st.selectbox(
            "Chọn phiên chat:",
            options=list(session_options.keys()),
            format_func=lambda x: session_options[x],
            index=list(session_options.keys()).index(
                st.session_state.current_session_id
            )
            if st.session_state.current_session_id in session_options
            else 0,
        )
        if selected_sid != st.session_state.current_session_id:
            st.session_state.current_session_id = selected_sid
            st.rerun()

    # Nút xóa session hiện tại & Xóa tất cả
    col_del1, col_del2 = st.columns(2)
    with col_del1:
        if st.button("🗑️ Xóa chat này", use_container_width=True):
            if st.session_state.current_session_id in st.session_state.sessions:
                del st.session_state.sessions[st.session_state.current_session_id]
                save_sessions(st.session_state.sessions)
                if st.session_state.sessions:
                    st.session_state.current_session_id = list(
                        st.session_state.sessions.keys()
                    )[0]
                else:
                    create_new_chat()
                st.rerun()

    with col_del2:
        if st.button("⚠️ Xóa tất cả", use_container_width=True):
            st.session_state.sessions = {}
            save_sessions({})
            create_new_chat()
            st.rerun()

    st.markdown("---")

    # Model Parameters Settings
    with st.expander("⚙️ Cài đặt Tham số Model", expanded=True):
        model_choice = st.selectbox(
            "Mô hình AI:",
            options=[
                "gemini-3.6-flash",
                "gemini-flash-lite-latest",
                "gpt-4o",
                "gpt-4o-mini",
            ],
            index=0,
        )
        temperature = st.slider("Độ sáng tạo (Temperature):", 0.0, 1.0, 0.7, 0.1)
        max_tokens = st.select_slider(
            "Số token tối đa:", options=[256, 512, 1024, 2048, 4096], value=1024
        )

    # Thống kê chi phí của phiên hiện tại
    current_session = st.session_state.sessions.get(
        st.session_state.current_session_id, {}
    )
    st.markdown("---")
    st.markdown("### 📊 Thống kê Phiên")
    st.markdown(
        f"""
    <div class="metric-card">
        <div>🔢 <b>Tổng Tokens:</b> {current_session.get('total_tokens', 0):,}</div>
        <div>💰 <b>Ước tính Chi phí:</b> ${current_session.get('total_cost', 0.0):.5f}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# ===========================================================================
# MAIN CHAT VIEW
# ===========================================================================
current_session = st.session_state.sessions[st.session_state.current_session_id]

# Main Header
col_hdr1, col_hdr2 = st.columns([3, 1])
with col_hdr1:
    st.title(f"🍿 {current_session.get('title', 'CineBrain - Trợ lý Điện ảnh')}")
with col_hdr2:
    st.markdown(
        f"""
        <div style="text-align: right; margin-top: 15px;">
            <span class="badge-info">🤖 {model_choice}</span>
            <span class="badge-info">⚡ Streaming Active</span>
        </div>
    """,
        unsafe_allow_html=True,
    )

# Quick Prompts if no messages yet
messages = current_session.get("messages", [])
if not messages:
    st.info(
        "👋 **Chào mừng bạn đến với CineBrain AI!** Bạn có thể chọn nhanh gợi ý bên dưới hoặc gõ câu hỏi ở khung chat:"
    )
    col_qp1, col_qp2, col_qp3, col_qp4 = st.columns(4)

    prompt_selected = None
    with col_qp1:
        if st.button("🚀 Top Phim Sci-Fi", use_container_width=True):
            prompt_selected = "Gợi ý cho tôi 5 bộ phim khoa học viễn tưởng hay nhất 10 năm qua có điểm IMDb cao."
    with col_qp2:
        if st.button("☕ Phim Chữa Lành", use_container_width=True):
            prompt_selected = (
                "Tôi đang cảm thấy mệt mỏi, hãy đề xuất 3 bộ phim chữa lành (healing) nhẹ nhàng."
            )
    with col_qp3:
        if st.button("🧠 Phân Tích Kịch Bản", use_container_width=True):
            prompt_selected = "Hãy phân tích cốt truyện và ý nghĩa biểu tượng trong đoạn kết phim Interstellar."
    with col_qp4:
        if st.button("⚔️ So Sánh Đạo Diễn", use_container_width=True):
            prompt_selected = "So sánh phong cách làm phim giữa Christopher Nolan và Quentin Tarantino."

    if prompt_selected:
        user_input_prompt = prompt_selected
    else:
        user_input_prompt = None
else:
    user_input_prompt = None

# Render Existing Messages
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and "cost_info" in msg:
            c_info = msg["cost_info"]
            total_toks = (
                c_info.get("prompt_tokens", 0) + c_info.get("completion_tokens", 0)
            )
            st.caption(
                f"⚡ {msg.get('latency', 0.0)}s | 🔢 {total_toks} tokens | 🏷️ ${c_info.get('total_cost', 0.0):.5f}"
            )

# Chat Input & Processing
prompt_from_chat = st.chat_input("Hỏi CineBrain về phim, diễn viên, gợi ý phim hay...")
user_message = user_input_prompt or prompt_from_chat

if user_message:
    # Update Session Title if first message
    if not messages:
        current_session["title"] = (
            user_message[:30] + "..." if len(user_message) > 30 else user_message
        )

    # Add User message to session
    current_session["messages"].append(
        {"role": "user", "content": user_message, "timestamp": time.time()}
    )
    with st.chat_message("user"):
        st.markdown(user_message)

    # Build context: MOVIE_PERSONA + last 10 messages
    context = [{"role": "system", "content": MOVIE_PERSONA}]
    for m in current_session["messages"][-10:]:
        context.append({"role": m["role"], "content": m["content"]})

    # Assistant Response with Streamlit write_stream
    with st.chat_message("assistant"):
        client = get_openai_client()

        def _call_api():
            return client.chat.completions.create(
                model=model_choice,
                messages=context,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9,
                stream=True,
            )

        start_time = time.perf_counter()

        def stream_generator():
            try:
                stream = retry_with_backoff(_call_api)
                for chunk in stream:
                    if chunk.choices and len(chunk.choices) > 0:
                        content = chunk.choices[0].delta.content or ""
                        if content:
                            yield content
            except Exception as e:
                yield f"\n\n⚠️ **Có lỗi khi kết nối API:** {str(e)}"

        # Display streaming response
        full_response = st.write_stream(stream_generator())
        latency = round(time.perf_counter() - start_time, 2)

        # Calculate metrics
        cost_info = estimate_cost(user_message, full_response, model=model_choice)
        total_tokens = (
            cost_info["prompt_tokens"] + cost_info["completion_tokens"]
        )

        st.caption(
            f"⚡ {latency}s | 🔢 {total_tokens} tokens | 🏷️ ${cost_info['total_cost']:.5f}"
        )

        # Append assistant message to session history
        current_session["messages"].append(
            {
                "role": "assistant",
                "content": full_response,
                "timestamp": time.time(),
                "cost_info": cost_info,
                "latency": latency,
            }
        )

        # Update Session totals
        current_session["total_cost"] = round(
            current_session.get("total_cost", 0.0) + cost_info["total_cost"], 6
        )
        current_session["total_tokens"] = (
            current_session.get("total_tokens", 0) + total_tokens
        )

        # Persist to disk
        save_sessions(st.session_state.sessions)
