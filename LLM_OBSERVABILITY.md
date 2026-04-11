# Giám sát và Log Hành vi AI (LLM Observability)

Phải theo dõi AI Agent để đảm bảo tính ổn định và bảo mật.
- Bật tính năng `return_intermediate_steps` trong LangChain/n8n [25].
- Lưu mảng `JSON.steps` chứa danh sách các Tool AI đã gọi, tham số và kết quả phản hồi của Tool đó [26]. Điều này giúp Admin audit lại quá trình suy luận của AI.
