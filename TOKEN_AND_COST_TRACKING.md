# Tracking Token và Chi phí

Mục tiêu của dự án là **0 VND** chi phí API [27].
- Bắt thuộc tính Token từ phản hồi của LLM: Trích xuất `prompt_tokens` và `completion_tokens` [26].
- Tính toán Cost: `Tổng Token * 0$` (Do Self-host model Llama/Mistral).
- Lưu vào CSDL và tạo một biểu đồ trên Grafana để chứng minh việc tự chạy nội bộ giúp tiết kiệm bao nhiêu tiền so với dùng OpenAI.
