import streamlit as st
import requests
import os

# Internationalization (i18n)
LANGUAGES = {
    "EN": {
        "title": "ViralScore AI",
        "sidebar_title": "🎬 ViralScore Settings",
        "upload_label": "Upload a video for analysis",
        "upload_success": "Video uploaded successfully!",
        "clear_chat": "Clear Chat History",
        "caption": "Analyze your videos for viral potential with AI",
        "chat_placeholder": "Ask me something about your video...",
        "backend_responded": "Backend responded!",
        "error_backend": "Error connecting to backend",
        "assistant_says": "Assistant says",
        "uploaded_notice": "I see you've uploaded",
    },
    "VN": {
        "title": "ViralScore AI",
        "sidebar_title": "🎬 Cài đặt ViralScore",
        "upload_label": "Tải lên video để phân tích",
        "upload_success": "Tải video lên thành công!",
        "clear_chat": "Xóa lịch sử trò chuyện",
        "caption": "Phân tích tiềm năng lan truyền video của bạn với AI",
        "chat_placeholder": "Hỏi tôi bất cứ điều gì về video của bạn...",
        "backend_responded": "Máy chủ đã phản hồi!",
        "error_backend": "Lỗi kết nối với máy chủ",
        "assistant_says": "Trợ lý phản hồi",
        "uploaded_notice": "Tôi thấy bạn đã tải lên",
    }
}

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="ViralScore AI",
    page_icon="🎬",
    layout="wide"
)

# Initialize session state for language
if "language" not in st.session_state:
    st.session_state.language = "EN"

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize session state for uploader key to allow resetting it
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# Sidebar for Video Upload and Settings
with st.sidebar:
    st.title(LANGUAGES[st.session_state.language]["sidebar_title"])

    # Language Selector
    def on_lang_change():
        st.session_state.language = st.session_state.lang_selector

    st.selectbox(
        "Language / Ngôn ngữ",
        options=["EN", "VN"],
        index=0 if st.session_state.language == "EN" else 1,
        key="lang_selector",
        on_change=on_lang_change
    )

    uploaded_video = st.file_uploader(
        LANGUAGES[st.session_state.language]["upload_label"],
        type=["mp4", "mov", "avi"],
        key=f"video_uploader_{st.session_state.uploader_key}"
    )

    if uploaded_video is not None:
        st.video(uploaded_video)
        st.success(LANGUAGES[st.session_state.language]["upload_success"])

    st.divider()
    if st.button(LANGUAGES[st.session_state.language]["clear_chat"]):
        st.session_state.messages = []
        st.session_state.uploader_key += 1  # Increment key to reset file_uploader
        st.rerun()

# Main Chat Interface
st.title(f"💊 {LANGUAGES[st.session_state.language]['title']}")
st.caption(LANGUAGES[st.session_state.language]["caption"])

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "video" in message:
            st.video(message["video"])

# React to user input
if prompt := st.chat_input(LANGUAGES[st.session_state.language]["chat_placeholder"]):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Call backend
            response = requests.get(API_URL)
            response.raise_for_status()
            data = response.json()

            # Simulated response for now based on backend output
            backend_msg = data.get('message', 'No message')
            if uploaded_video:
                full_response = f"{LANGUAGES[st.session_state.language]['backend_responded']}: {backend_msg} \n\n{LANGUAGES[st.session_state.language]['uploaded_notice']} `{uploaded_video.name}`"
            else:
                full_response = f"{LANGUAGES[st.session_state.language]['backend_responded']}: {backend_msg}"

            message_placeholder.markdown(full_response)

        except Exception as e:
            full_response = f"{LANGUAGES[st.session_state.language]['error_backend']}: {e}"
            st.error(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
