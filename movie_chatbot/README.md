# 🎬 CineBrain AI - Streamlit Movie Chatbot WebApp

Ứng dụng Web Chatbot Hỏi Đáp & Tư Vấn Phim Ảnh bằng **Streamlit** dựa trên nền tảng `template.py` của Bài Lab LLM API.

---

## 🌟 Tính năng Nổi bật

1. **Native Streaming (Streamlit `st.write_stream`)**: Phản hồi token-by-token mượt mà, thời gian phản hồi cực nhanh với `gemini-3.6-flash`.
2. **Quản lý Lịch sử Chat (Session & Persistence)**:
   - Lưu vết tự động mọi phiên trò chuyện vào `history_data.json`.
   - Sidebar chọn và quản lý các phiên chat cũ: Tạo chat mới, đổi phiên chat, xóa phiên hiện tại, xóa toàn bộ lịch sử.
3. **Ước tính Token & Chi phí API**:
   - Sử dụng `tiktoken` đếm số token thật.
   - Tính toán chi phí USD chính xác theo bảng giá từng model.
   - Tự động thử lại khi gặp sự cố tạm thời (`retry_with_backoff`).
4. **Giao diện Cinematic UI**:
   - Dark mode màu sắc điện ảnh sang trọng.
   - Các gợi ý nhanh (Quick Prompts) hỗ trợ hỏi nhanh theo tâm trạng, thể loại, phân tích cốt truyện và so sánh tác phẩm.
   - Tùy chỉnh tham số trực tiếp trên Sidebar (Model selector, Temperature, Max Tokens).

---

## 🚀 Hướng dẫn Cài đặt & Chạy ứng dụng

### 1. Cài đặt các thư viện cần thiết
Đảm bảo đã kích hoạt môi trường Python ảo (`.venv`), sau đó chạy:
```bash
pip install -r requirements.txt
```

*(Lưu ý: Ứng dụng tự động đọc các thông số `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `LAB_MODEL` từ file `.env` ở thư mục gốc).*

### 2. Khởi chạy Web Application
Bạn có thể khởi chạy bằng 1 trong 2 cách sau:

#### Cách 1: Sử dụng script `run.py`
```bash
python run.py
```

#### Cách 2: Sử dụng Streamlit CLI trực tiếp
```bash
streamlit run app.py
```

### 3. Trải nghiệm
Truy cập trình duyệt theo địa chỉ:
👉 **[http://localhost:8501](http://localhost:8501)**
