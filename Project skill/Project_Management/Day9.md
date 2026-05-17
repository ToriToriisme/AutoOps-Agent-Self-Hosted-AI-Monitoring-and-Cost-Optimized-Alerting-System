# Day 9 — Tích hợp Google Gemini & Tối ưu Prompt Engineering

## 1) Mục tiêu của Day 9
Ở Day 8, chúng ta đã đóng gói thành công bằng Docker và bảo mật Webhook. Hôm nay, ở ngày thứ 9 của tiến trình 14 ngày, chúng ta tập trung vào "Bộ não" của hệ thống để hình thành một vòng lặp tự động hóa khép kín (Closed-Loop Automation) cực kỳ vững chắc:

- **Chuyển đổi sang Google Gemini 3.1 Flash Lite:** Thay thế Ollama bằng Gemini qua thư viện `langchain-google-genai` là bước đi cực kỳ hợp lý để giảm tải phần cứng cục bộ, tăng tốc độ phát triển và tối ưu tài nguyên.
- **Tối ưu Prompt (Prompt Engineering):** Xây dựng Prompt Template chuẩn chỉ, yêu cầu AI đóng vai một "DevOps Senior" nhằm biến các cảnh báo thô thành phân tích kỹ thuật chất lượng cao.
- **Cơ chế Fallback an toàn (Rule-based Fallback):** Tư duy thiết kế chịu lỗi (Fault-tolerant) đảm bảo hệ thống vẫn tiếp tục chạy dựa vào bảng luật cứng nếu API của LLM gặp sự cố.

---

## 2) Đánh giá chi tiết các quyết định kiến trúc (Đã được tích hợp trong `main.py`)

### 2.1 Quyết định sử dụng Gemini 3.1 Flash Lite
Sự phù hợp của mô hình: Phiên bản Gemini 3.1 Flash-Lite vừa được Google phát hành chính thức (GA). Đây là mô hình được thiết kế đặc biệt cho các tác vụ cần tốc độ cao và nhạy cảm về chi phí.

Về mặt tối ưu chi phí, lựa chọn này đáp ứng hoàn hảo tiêu chí **NFR-C-1 (Tối ưu chi phí)** của dự án:
- **Tài khoản miễn phí:** Google AI Studio cho phép gọi mô hình Flash-Lite lên tới 15 yêu cầu/phút và 1.000 yêu cầu/ngày. Rất dư dả cho mô hình tự lưu trữ.
- **Chi phí khi scale:** Ngay cả khi nâng cấp lên bản trả phí, chi phí cực kỳ rẻ, chỉ 0.25 USD cho mỗi 1 triệu token đầu vào.

```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    google_api_key=api_key,
    temperature=0.2, # Độ sáng tạo thấp để câu trả lời chính xác, mang tính kỹ thuật
)
```

### 2.2 Tối ưu Prompt với vai trò "DevOps Senior"
Việc thiết lập PromptTemplate rõ ràng với System Prompt đóng vai (persona) là "DevOps Senior" sẽ ép mô hình trả về các văn bản mang tính kỹ thuật cao, không lan man. Nó giúp biến các cảnh báo khô khan từ Grafana (như `CPU High`, `Disk Space Low`) thành những lời giải thích nguyên nhân và đề xuất sửa lỗi (`ai_analysis`) có thể trực tiếp gửi qua Telegram để bạn đọc và hiểu ngay vấn đề.

```python
from langchain_core.prompts import PromptTemplate

prompt_template = PromptTemplate.from_template(
    "Hệ thống tôi vừa có cảnh báo [{alert_name}], trạng thái [{status}].\n"
    "Mô tả chi tiết: {description}\n\n"
    "Hãy đóng vai một DevOps Senior, giải thích ngắn gọn nguyên nhân có thể xảy ra "
    "và đề xuất hướng giải quyết (nêu rõ các bước cụ thể)."
)
```

### 2.3 Cơ chế Fallback an toàn (Fault-Tolerant System)
Đây là tư duy thiết kế hệ thống chịu lỗi bắt buộc phải có của một kỹ sư hệ thống. Trong quá trình vận hành, API của Google có thể gặp sự cố, bị quá tải (lỗi 503/429), hoặc do bạn gọi sai tên mô hình (như lỗi `404 NOT_FOUND` thường gặp khi thiết lập).

**Cách hoạt động:** Khi API của LLM sập, khối `try/except` sẽ bắt lỗi và hệ thống tự động dựa vào bảng luật cứng (`TRIAGE_POLICY` - ví dụ `Windows Server Down -> CRITICAL`) để tiếp tục vận hành. Nó đảm bảo các lỗi nghiêm trọng vẫn được "hú còi" thay vì toàn bộ tiến trình báo lỗi và bị kẹt lại.

---

## 3) Kiểm tra và Nghiệm thu (Definition of Done - DoD)
- [ ] Gắn `GOOGLE_API_KEY=xxx` vào file `.env` thành công.
- [ ] Gửi thử webhook, kiểm tra log thấy AI trả về phân tích đúng chuẩn kỹ thuật của một "DevOps Senior".
- [ ] **Kiểm tra Fallback:** Cố tình đổi sai tên mô hình trong `main.py` để ép xảy ra lỗi `404 NOT_FOUND` hoặc tắt mạng, kiểm tra xem Agent có tự động kích hoạt Rule-based Fallback và tiếp tục đẩy cảnh báo đi thành công hay không.

---
**Ghi chú:** Với những cơ chế này, hệ thống của bạn đang hình thành một vòng lặp tự động hóa khép kín (Closed-Loop Automation) rất vững chắc! Ngày mai (Day 10), chúng ta sẽ hoàn thiện luồng gửi cảnh báo thực tế qua Telegram.
