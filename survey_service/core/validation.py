from models import survey as models
from typing import Any

# Hàm validate nâng cao cho từng câu trả lời
# Trả về (True, None) nếu hợp lệ, (False, error_message) nếu không hợp lệ
def validate_answer(question: models.SurveyQuestion, answer: Any):
    # Kiểm tra bắt buộc
    if question.is_required and (answer is None or (isinstance(answer, str) and not answer)):
        return False, f"Câu hỏi '{question.question_text}' là bắt buộc."

    # Kiểm tra loại câu hỏi
    if question.question_type == "single_choice":
        if answer not in question.options:
            return False, f"Đáp án không hợp lệ cho câu hỏi '{question.question_text}'."
    elif question.question_type == "multiple_choice":
        if not isinstance(answer, list):
            return False, f"Câu hỏi '{question.question_text}' yêu cầu chọn nhiều đáp án."
        for a in answer:
            if a not in question.options:
                return False, f"Một đáp án không hợp lệ cho câu hỏi '{question.question_text}'."
    elif question.question_type == "number":
        try:
            val = float(answer)
        except Exception:
            return False, f"Câu hỏi '{question.question_text}' yêu cầu nhập số."
        # Có thể bổ sung kiểm tra min/max nếu cần
    elif question.question_type == "text":
        if not isinstance(answer, str):
            return False, f"Câu hỏi '{question.question_text}' yêu cầu nhập text."
        # Có thể bổ sung kiểm tra độ dài nếu cần
    # Có thể mở rộng thêm các loại khác
    return True, None 