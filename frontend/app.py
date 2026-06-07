import streamlit as st
import requests
import os
import re
import textwrap
from datetime import datetime

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

if "scored_video_signature" not in st.session_state:
    st.session_state.scored_video_signature = None

if "last_score_message_video_name" not in st.session_state:
    st.session_state.last_score_message_video_name = None

if "last_score_message_video_signature" not in st.session_state:
    st.session_state.last_score_message_video_signature = None

if "generated_reports" not in st.session_state:
    st.session_state.generated_reports = []


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


def sanitize_report_filename(video_name):
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", video_name).strip("_")
    safe_name = safe_name or "video"
    return f"{safe_name}_{datetime.now().strftime('%Y-%m-%d')}.pdf"


def pdf_escape(text):
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )


def build_pdf_report(video_name, score, generated_at):
    dimensions = [
        ("Hook Strength", "hook_strength"),
        ("Completion Rate", "completion_rate"),
        ("Shares/Saves Probability", "shares_saves_probability"),
        ("Sound Trend Timing", "sound_trend_timing"),
        ("Search Keyword Relevance", "search_keyword_relevance"),
        ("Early Engagement Velocity", "early_engagement_velocity"),
        ("Content Niche Fit", "content_niche_fit"),
    ]

    lines = [
        "ViralScore AI Report",
        f"Video: {video_name}",
        f"Generated: {generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Overall Score: {score.get('overall_score', 0)}/100",
        f"Predicted Reach: {score.get('predicted_reach_range', 'Not returned')}",
        "",
        "Dimension Scores",
    ]

    for label, key in dimensions:
        dimension = score.get(key, {})
        lines.extend(
            [
                "",
                f"{label}: {dimension.get('score', 0)}/100",
                f"Explanation: {dimension.get('explanation', 'Not returned')}",
                f"Actionable Fix: {dimension.get('actionable_fix', 'Not returned')}",
            ]
        )

    lines.append("")
    lines.append("Retention Drop Zones")
    for zone in score.get("retention_drop_zones", []) or []:
        lines.extend(
            [
                "",
                f"Time: {zone.get('timestamp_range', 'Not returned')}",
                f"Severity: {zone.get('severity', 'Not returned')}",
                f"Reason: {zone.get('reason', 'Not returned')}",
            ]
        )

    if score.get("suggested_script_variant"):
        lines.extend(["", "Suggested Script Variant", score["suggested_script_variant"]])

    wrapped_lines = []
    for line in lines:
        if not line:
            wrapped_lines.append("")
            continue
        wrapped_lines.extend(textwrap.wrap(str(line), width=92) or [""])

    pages = []
    current_page = []
    max_lines_per_page = 48
    for line in wrapped_lines:
        current_page.append(line)
        if len(current_page) >= max_lines_per_page:
            pages.append(current_page)
            current_page = []
    if current_page:
        pages.append(current_page)

    objects = []
    page_refs = []

    def add_object(content):
        objects.append(content)
        return len(objects)

    catalog_id = add_object("<< /Type /Catalog /Pages 2 0 R >>")
    pages_id = add_object("")
    font_id = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    for page in pages:
        text_commands = ["BT", "/F1 10 Tf", "14 TL", "50 790 Td"]
        for line in page:
            text_commands.append(f"({pdf_escape(line)}) Tj")
            text_commands.append("T*")
        text_commands.append("ET")
        stream = "\n".join(text_commands)
        content_id = add_object(f"<< /Length {len(stream.encode('latin-1', 'replace'))} >>\nstream\n{stream}\nendstream")
        page_id = add_object(
            f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {content_id} 0 R >>"
        )
        page_refs.append(page_id)

    objects[pages_id - 1] = f"<< /Type /Pages /Kids [{' '.join(f'{page_id} 0 R' for page_id in page_refs)}] /Count {len(page_refs)} >>"

    pdf_parts = ["%PDF-1.4\n"]
    offsets = []
    for index, content in enumerate(objects, start=1):
        offsets.append(sum(len(part.encode("latin-1", "replace")) for part in pdf_parts))
        pdf_parts.append(f"{index} 0 obj\n{content}\nendobj\n")

    xref_offset = sum(len(part.encode("latin-1", "replace")) for part in pdf_parts)
    pdf_parts.append(f"xref\n0 {len(objects) + 1}\n")
    pdf_parts.append("0000000000 65535 f \n")
    for offset in offsets:
        pdf_parts.append(f"{offset:010d} 00000 n \n")
    pdf_parts.append(
        f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF"
    )

    return "".join(pdf_parts).encode("latin-1", "replace")


def add_generated_report(video_name, score):
    generated_at = datetime.now()
    report = {
        "id": f"report_{len(st.session_state.generated_reports)}",
        "video_name": video_name,
        "file_name": sanitize_report_filename(video_name),
        "created_label": generated_at.strftime("%Y-%m-%d %H:%M:%S"),
        "pdf_bytes": build_pdf_report(video_name, score, generated_at),
    }
    st.session_state.generated_reports.append(report)
    return report


def get_report(report_id):
    for report in st.session_state.generated_reports:
        if report["id"] == report_id:
            return report
    return None


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
        uploaded_video_signature = f"{uploaded_video.name}:{getattr(uploaded_video, 'size', 'unknown')}"
        st.video(uploaded_video)
        st.success(LANGUAGES[st.session_state.language]["upload_success"])

        if st.session_state.scored_video_signature != uploaded_video_signature:
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
                    st.session_state.scored_video_signature = uploaded_video_signature
                except Exception as e:
                    st.error(f"{LANGUAGES[st.session_state.language]['score_error']}: {e}")

        if st.session_state.viral_score_result:
            result = st.session_state.viral_score_result
            st.metric(
                LANGUAGES[st.session_state.language]["score_title"],
                f"{result.get('overall_score', 0)}/100",
            )
            if st.session_state.last_score_message_video_signature != uploaded_video_signature:
                report = add_generated_report(uploaded_video.name, result)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": format_score_summary(result),
                    "report_id": report["id"],
                })
                st.session_state.last_score_message_video_name = uploaded_video.name
                st.session_state.last_score_message_video_signature = uploaded_video_signature

    st.divider()
    if st.button(LANGUAGES[st.session_state.language]["clear_chat"]):
        st.session_state.messages = []
        st.session_state.viral_score_result = None
        st.session_state.scored_video_name = None
        st.session_state.scored_video_signature = None
        st.session_state.last_score_message_video_name = None
        st.session_state.last_score_message_video_signature = None
        st.session_state.generated_reports = []
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
        if "report_id" in message:
            report = get_report(message["report_id"])
            if report:
                st.download_button(
                    "Download PDF report",
                    data=report["pdf_bytes"],
                    file_name=report["file_name"],
                    mime="application/pdf",
                    key=f"download_{report['id']}",
                )
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
