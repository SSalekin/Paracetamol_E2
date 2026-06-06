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
        "analyzing": "Analyzing video...",
        "score_title": "Viral Score",
        "score_error": "Could not score video",
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
        "analyzing": "Đang phân tích video...",
        "score_title": "Điểm Viral",
        "score_error": "Không thể chấm điểm video",
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

if "viral_score_result" not in st.session_state:
    st.session_state.viral_score_result = None

if "scored_video_name" not in st.session_state:
    st.session_state.scored_video_name = None

if "last_score_message_video_name" not in st.session_state:
    st.session_state.last_score_message_video_name = None


def format_score_summary(score):
    overall_score = score.get("overall_score", 0)
    reach = score.get("predicted_reach_range", "No reach estimate returned.")
    hook = score.get("hook_strength", {})
    completion = score.get("completion_rate", {})
    fix = hook.get("actionable_fix") or completion.get("actionable_fix") or "No fix returned."

    return (
        f"## {LANGUAGES[st.session_state.language]['score_title']}: {overall_score}/100\n\n"
        f"**Predicted reach:** {reach}\n\n"
        f"**Hook Strength:** {hook.get('score', 0)}/100\n\n"
        f"**Completion Rate:** {completion.get('score', 0)}/100\n\n"
        f"**Recommended fix:** {fix}"
    )


def raise_for_backend_error(response):
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        try:
            detail = response.json().get("detail")
        except ValueError:
            detail = response.text
        if detail:
            raise RuntimeError(detail) from exc
        raise


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

        if st.session_state.scored_video_name != uploaded_video.name:
            st.session_state.viral_score_result = None

        if st.session_state.viral_score_result is None:
            with st.spinner(LANGUAGES[st.session_state.language]["analyzing"]):
                try:
                    uploaded_video.seek(0)
                    file_bytes = uploaded_video.getvalue()
                    response = requests.post(
                        f"{API_URL}/score-video",
                        files={
                            "video": (
                                uploaded_video.name,
                                file_bytes,
                                uploaded_video.type or "video/mp4",
                            )
                        },
                        timeout=120,
                    )
                    raise_for_backend_error(response)
                    st.session_state.viral_score_result = response.json()
                    st.session_state.scored_video_name = uploaded_video.name
                except Exception as e:
                    st.error(f"{LANGUAGES[st.session_state.language]['score_error']}: {e}")

        if st.session_state.viral_score_result:
            result = st.session_state.viral_score_result
            st.metric(
                LANGUAGES[st.session_state.language]["score_title"],
                f"{result.get('overall_score', 0)}/100",
            )
            if st.session_state.last_score_message_video_name != uploaded_video.name:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": format_score_summary(result),
                })
                st.session_state.last_score_message_video_name = uploaded_video.name

    st.divider()
    if st.button(LANGUAGES[st.session_state.language]["clear_chat"]):
        st.session_state.messages = []
        st.session_state.viral_score_result = None
        st.session_state.scored_video_name = None
        st.session_state.last_score_message_video_name = None
        st.session_state.uploader_key += 1  # Increment key to reset file_uploader
        st.rerun()

# Main Chat Interface
st.title(f"💊 {LANGUAGES[st.session_state.language]['title']}")
st.caption(LANGUAGES[st.session_state.language]["caption"])

if st.session_state.viral_score_result:
    score = st.session_state.viral_score_result
    st.subheader(f"{LANGUAGES[st.session_state.language]['score_title']}: {score.get('overall_score', 0)}/100")
    st.write(score.get("predicted_reach_range", ""))

    dimensions = [
        ("Hook Strength", "hook_strength"),
        ("Completion Rate", "completion_rate"),
        ("Shares/Saves", "shares_saves_probability"),
        ("Sound Trend", "sound_trend_timing"),
        ("Search Keywords", "search_keyword_relevance"),
        ("Early Engagement", "early_engagement_velocity"),
        ("Niche Fit", "content_niche_fit"),
    ]
    cols = st.columns(2)
    for index, (label, key) in enumerate(dimensions):
        dimension = score.get(key, {})
        with cols[index % 2]:
            st.metric(label, f"{dimension.get('score', 0)}/100")
            st.caption(dimension.get("actionable_fix", ""))

    if score.get("retention_drop_zones"):
        st.write("Retention drop zones")
        st.dataframe(score["retention_drop_zones"], use_container_width=True)

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
            if st.session_state.viral_score_result:
                full_response = format_score_summary(st.session_state.viral_score_result)
            elif uploaded_video:
                full_response = f"{LANGUAGES[st.session_state.language]['analyzing']} Please wait for the backend viral score."
            else:
                response = requests.get(API_URL)
                response.raise_for_status()
                data = response.json()
                backend_msg = data.get('message', 'No message')
                full_response = f"{LANGUAGES[st.session_state.language]['backend_responded']}: {backend_msg}"

            message_placeholder.markdown(full_response)

        except Exception as e:
            full_response = f"{LANGUAGES[st.session_state.language]['error_backend']}: {e}"
            st.error(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
