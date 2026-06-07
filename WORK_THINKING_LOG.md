# WORK_THINKING_LOG

## 🕒 2026-06-06 (Asia/Saigon)
### 🎯 Task Objective
- Người dùng yêu cầu mô tả toàn bộ những gì đang có trong dự án hiện tại (cấu trúc, thành phần, luồng chạy, entrypoints, cấu hình).

### 🧩 Input Signals
- Codebase tại `c:\Users\Admin\Downloads\Paracetamol_E2`
- Các file chính được rà soát: `pyproject.toml`, `README.md`, `backend/app/main.py`, `backend/app/video_score_generator.py`, `frontend/app.py`, `env.example`, `.python-version`

### 🧠 Feature Engineering Trace
- Không tạo feature ML mới trong bước này.
- Trích xuất “feature mô tả hệ thống” phục vụ audit:
  - Tech stack (FastAPI/Streamlit/LangChain/OpenCV)
  - Contract API (`/score-video`) + schema output (7 dimensions)
  - Quy tắc sampling frame (0–3s, tối đa 9 frames)
  - Nguồn cấu hình LLM (`DOLA_API_KEY`, `DOLA_BASE_URL`)

### 🧪 Model Thinking (IMPORTANT)
- Không chạy inference hay huấn luyện.
- Tập trung đánh giá tính đầy đủ của pipeline: input video → trích frame → gói multimodal → gọi LLM → parse JSON → trả response model.

### ⚖️ Decision Layer
- Chọn mô tả theo “kiến trúc + luồng dữ liệu + entrypoints + dependency” để người đọc có thể chạy và debug.
- Ghi nhận các dependency chưa được dùng (supabase, deepagents) để giảm nhiễu khi vận hành.

### 📊 Output Produced
- Bản mô tả đầy đủ dự án: cấu trúc thư mục, backend, frontend, pipeline chấm điểm, biến môi trường, cách chạy theo README.

### 🚨 Risk / Weakness Analysis
- `.python-version` yêu cầu Python >= 3.14 có thể khó khớp môi trường thực tế.
- LLM response parsing dựa vào tìm `{}` trong text; nếu model trả text ngoài JSON có thể fail.
- Chỉ chấm dựa trên frames 3 giây đầu (hook) + metadata; body frames hiện để trống → bias về hook.
- `DOLA_API_KEY` mặc định là placeholder nếu thiếu `.env` → dễ lỗi runtime.

### 🔧 Next Improvement Step
- Bổ sung sampling frames toàn video (body_frames_b64) + audio/trend extraction tự động.
- Thêm validation và fallback robust cho LLM JSON (function calling/structured output nếu SDK hỗ trợ).
- Thêm script/devcontainer/docker để tái lập môi trường.

### 🏷 Tags
- #feature-engineering #llm-scoring #fusion-model #e2-viral

## 🕒 2026-06-06 (Asia/Saigon)
### 🎯 Task Objective
- Chạy dự án end-to-end: cài dependencies, khởi chạy backend FastAPI và frontend Streamlit để người dùng truy cập UI và test upload video.

### 🧩 Input Signals
- Môi trường Windows, thư mục dự án `c:\Users\Admin\Downloads\Paracetamol_E2`
- Lệnh chạy theo README: uvicorn cho backend, streamlit cho frontend
- Biến môi trường dự kiến: `DOLA_API_KEY`, `DOLA_BASE_URL`, `API_URL`

### 🧠 Feature Engineering Trace
- Không thay đổi feature/model.
- Chỉ cấu hình runtime:
  - Install deps: `uv sync`
  - Backend: `uv run uvicorn backend.app.main:app --port 8000`
  - Frontend: set `API_URL=http://localhost:8000` rồi `uv run streamlit run frontend/app.py --server.port 8501`

### 🧪 Model Thinking (IMPORTANT)
- Không chạy scoring thật (phụ thuộc key/endpoint DOLA).
- Chỉ xác nhận backend sống bằng `GET /` trả 200 JSON.

### ⚖️ Decision Layer
- Dùng `uv run ...` để đảm bảo chạy đúng interpreter/venv mà dự án quản lý.
- Chạy backend và frontend ở 2 process tách biệt để tránh kill lẫn nhau.

### 📊 Output Produced
- Backend chạy tại `http://localhost:8000` (healthcheck OK).
- Frontend Streamlit chạy tại `http://localhost:8501` (UI sẵn sàng upload video).

### 🚨 Risk / Weakness Analysis
- Nếu `.env` thiếu `DOLA_API_KEY`/`DOLA_BASE_URL`, thao tác chấm điểm `/score-video` có thể lỗi runtime khi gọi LLM.
- Một số video codec (HEVC) có thể yêu cầu ffmpeg/codec bổ sung trên Windows.

### 🔧 Next Improvement Step
- Thêm healthcheck cho cấu hình DOLA (startup validation) và thông báo lỗi rõ ràng hơn ở UI.
- Bổ sung script chạy 1 lệnh (dev script) để khởi động cả 2 service.

### 🏷 Tags
- #runtime #fastapi #streamlit #e2-viral

## 🕒 2026-06-06 (Asia/Saigon)
### 🎯 Task Objective
- Đề xuất cách tăng accuracy cho hệ thống ViralScore (feature quality, modeling, evaluation, guardrails) dựa trên pipeline hiện tại.

### 🧩 Input Signals
- Pipeline hiện tại: lấy tối đa 9 frames trong 3 giây đầu, không có audio/OCR/ASR, `body_frames_b64` rỗng.
- Output contract: 7-dimension scores + drop zones + reach range.
- LLM: ChatOpenAI-compatible endpoint (`DOLA_API_KEY`, `DOLA_BASE_URL`) + prompt ép JSON.

### 🧠 Feature Engineering Trace
- Đề xuất nhóm tín hiệu cần bổ sung:
  - Temporal coverage: frames toàn video + shot-change + motion/pace.
  - Audio: loudness/beat alignment + speech rate + music trend fingerprint.
  - Text: OCR on-screen captions + ASR transcript auto + keyword density.
  - Structure: hook pattern, cliffhangers, CTA timing, outro cues.
  - Metadata: niche/audience/posting_time chuẩn hoá và taxonomy.

### 🧪 Model Thinking (IMPORTANT)
- Accuracy mục tiêu nên đo theo “views-based metric”/reach và/hoặc retention thực tế.
- Khuyến nghị kiến trúc hybrid:
  - LLM làm judge có rubric + self-check
  - Model tabular (GBDT/logreg) để calibrate overall_score/reach trên dữ liệu thật
  - Ensemble để giảm variance theo prompt.

### ⚖️ Decision Layer
- Ưu tiên tăng coverage tín hiệu (video+audio+text) trước khi tinh chỉnh model, vì lỗi lớn nhất hiện tại là missing signals.
- Ưu tiên thiết kế evaluation set + calibration để biến điểm LLM thành thang đo ổn định.

### 📊 Output Produced
- Roadmap cải tiến accuracy theo 4 lớp: Input signals → Feature extraction → Scoring/LLM robustness → Offline evaluation & calibration.

### 🚨 Risk / Weakness Analysis
- Nếu chỉ dựa LLM, điểm dễ drift theo model/prompt và khó tái lập.
- Trend context thủ công gây nhiễu; cần tự động hoá hoặc chuẩn hoá.
- Overfitting theo niche nếu taxonomy không rõ.

### 🔧 Next Improvement Step
- Implement sampling body frames + ASR/OCR baseline; log toàn bộ intermediate features.
- Thu thập dataset (video, metadata, outcome views/retention) và huấn luyện calibration model.
- Thêm self-consistency (n lần chấm) + median/trim-mean, kèm confidence.

### 🏷 Tags
- #feature-engineering #evaluation #calibration #llm-scoring #e2-viral
