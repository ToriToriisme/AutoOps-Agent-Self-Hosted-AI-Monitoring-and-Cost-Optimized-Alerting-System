from pydantic import BaseModel, Field
from typing import Optional

class AITriageResponse(BaseModel):
    severity_assessment: str = Field(description="Đánh giá mức độ: SMALL, MEDIUM, CRITICAL")
    root_cause_analysis: str = Field(description="Giải thích ngắn gọn nguyên nhân cảnh báo")
    suggested_action: Optional[str] = Field(description="Tên script (chọn từ whitelist) hoặc để trống")
