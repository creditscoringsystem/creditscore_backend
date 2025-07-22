import pandas as pd
import ast
from sqlalchemy.orm import Session
from database import QuestionsSessionLocal
from models.survey import SurveyQuestion

def import_questions_from_csv(csv_file_path: str):
    """Import câu hỏi từ file CSV vào database"""
    try:
        # Đọc file CSV
        df = pd.read_csv(csv_file_path)
        print(f"📖 Đọc được {len(df)} câu hỏi từ file CSV")
        
        # Tạo session database
        db = QuestionsSessionLocal()
        
        # Xóa tất cả câu hỏi cũ (nếu có)
        db.query(SurveyQuestion).delete()
        db.commit()
        print("🗑️ Đã xóa dữ liệu cũ")
        
        # Import từng câu hỏi
        for index, row in df.iterrows():
            try:
                # Xử lý options (chuyển từ string sang list)
                options = None
                if pd.notna(row['options']) and row['options']:
                    try:
                        options = ast.literal_eval(row['options'])
                    except:
                        options = row['options'].split(',') if ',' in row['options'] else [row['options']]
                
                # Tạo câu hỏi mới
                question = SurveyQuestion(
                    question_text=row['question_text'],
                    question_type=row['question_type'],
                    question_group=row['question_group'],
                    options=options,
                    order=int(row['order']),
                    is_required=int(row['is_required']),
                    version=int(row['version'])
                )
                
                db.add(question)
                print(f"✅ Đã thêm câu hỏi {index + 1}: {row['question_text'][:50]}...")
                
            except Exception as e:
                print(f"❌ Lỗi khi import câu hỏi {index + 1}: {e}")
                continue
        
        # Commit tất cả thay đổi
        db.commit()
        print(f"🎉 Hoàn thành import {len(df)} câu hỏi vào database!")
        
        # Đếm số câu hỏi theo nhóm
        questions = db.query(SurveyQuestion).all()
        groups = {}
        for q in questions:
            if q.question_group not in groups:
                groups[q.question_group] = 0
            groups[q.question_group] += 1
        
        print("\n📊 Thống kê theo nhóm câu hỏi:")
        for group, count in groups.items():
            print(f"  - {group}: {count} câu hỏi")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi import: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Bắt đầu import câu hỏi từ CSV...")
    success = import_questions_from_csv("sample_questions.csv")
    
    if success:
        print("✅ Import thành công!")
    else:
        print("❌ Import thất bại!") 