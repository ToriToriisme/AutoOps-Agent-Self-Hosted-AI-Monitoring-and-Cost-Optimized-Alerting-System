# Tiêu chuẩn Đánh giá AI (Evaluation)

Kiểm thử agent rất quan trọng vì một lỗi nhỏ có thể phá hỏng cả chuỗi hành động [21].
- **Công cụ gợi ý:** Sử dụng DeepEval hoặc Promptfoo [22, 23] (Mã nguồn mở).
- **Metrics (Chỉ số đo lường):**
  - *Tool Call Accuracy:* AI có gọi đúng Tool cho đúng lỗi không? [24].
  - *Hallucination Rate:* Tỷ lệ AI tự bịa ra lệnh sai.
