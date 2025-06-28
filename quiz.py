import random
import time
from datetime import datetime

class Quiz:
    def __init__(self, data_handler, review_system):
        self.data_handler = data_handler
        self.review_system = review_system
        self.current_session = {
            "start_time": datetime.now(),
            "questions_asked": 0,
            "correct_answers": 0,
            "wrong_answers": 0,
            "total_time": 0
        }
    
    def generate_multiple_choice(self, question, correct_answer):
        """生成选择题"""
        all_events = list(self.data_handler.get_all_events().values())
        
        # 确保不重复选项
        options = [correct_answer]
        while len(options) < 4:
            option = random.choice(all_events)
            if option not in options:
                options.append(option)
        
        # 随机排序选项
        random.shuffle(options)
        
        return {
            "question": f"以下哪个是{question}发生的时间？",
            "options": options,
            "correct_index": options.index(correct_answer)
        }
    
    def generate_fill_blank(self, question, correct_answer):
        """生成填空题"""
        return {
            "question": f"{question}发生于哪一年？",
            "answer": correct_answer
        }
    
    def normalize_answer(self, answer):
        """标准化答案，移除所有非数字字符并处理常见格式"""
        # 移除所有非数字字符
        normalized = ''.join(char for char in answer if char.isdigit())
        
        # 如果是年份范围，拆分处理
        if len(normalized) > 8:  # 年份范围，如18511864
            start_year = normalized[:4]
            end_year = normalized[4:]
            return f"{start_year}-{end_year}"
        
        return normalized
    
    def ask_question(self, question_type="random"):
        """提问一个问题"""
        # 获取待复习的问题
        due_questions = self.review_system.get_due_questions(limit=10)
        
        if not due_questions:
            print("没有需要复习的问题！")
            return None
        
        # 随机选择一个问题
        question = random.choice(due_questions)
        correct_answer = self.data_handler.get_all_events()[question]
        
        # 确定问题类型
        if question_type == "random":
            question_type = random.choice(["multiple_choice", "fill_blank"])
        
        # 生成问题
        if question_type == "multiple_choice":
            quiz_data = self.generate_multiple_choice(question, correct_answer)
        else:  # fill_blank
            quiz_data = self.generate_fill_blank(question, correct_answer)
        
        # 记录开始时间
        start_time = time.time()
        
        # 显示问题
        print("\n" + "=" * 50)
        print(quiz_data["question"])
        
        if question_type == "multiple_choice":
            for i, option in enumerate(quiz_data["options"]):
                print(f"{chr(65+i)}. {option}")
            
            # 获取用户答案
            valid_inputs = [chr(65+i) for i in range(len(quiz_data["options"]))]
            user_input = ""
            while user_input not in valid_inputs:
                user_input = input("\n请选择 (A/B/C/D): ").upper()
            
            user_answer_index = ord(user_input) - 65
            is_correct = user_answer_index == quiz_data["correct_index"]
        else:  # fill_blank
            # 获取用户答案
            user_input = input("\n请输入答案: ")
            
            # 标准化处理用户输入和正确答案
            normalized_user = self.normalize_answer(user_input.strip())
            normalized_correct = self.normalize_answer(quiz_data["answer"])
            
            is_correct = normalized_user == normalized_correct
        
        # 计算用时
        end_time = time.time()
        time_taken = end_time - start_time
        
        # 显示结果
        if is_correct:
            print("\n✓ 回答正确！")
            performance = 5 - min(4, int(time_taken / 5))  # 根据用时调整表现评分
        else:
            print("\n✗ 回答错误！")
            print(f"正确答案是: {correct_answer}")
            performance = 2  # 错误但记得一些内容
        
        # 更新统计数据
        self.data_handler.update_question_stats(question, is_correct, time_taken)
        
        # 计算下次复习时间
        next_review = self.review_system.calculate_next_review(question, performance)
        
        # 更新当前会话数据
        self.current_session["questions_asked"] += 1
        if is_correct:
            self.current_session["correct_answers"] += 1
        else:
            self.current_session["wrong_answers"] += 1
        self.current_session["total_time"] += time_taken
        
        return {
            "question": question,
            "is_correct": is_correct,
            "time_taken": time_taken,
            "next_review": next_review
        }
    
    def start_session(self, num_questions=10, question_type="random"):
        """开始一个学习会话"""
        print("\n开始历史大事年表背诵会话！")
        print(f"本次会话将包含 {num_questions} 个问题。")
        print("按 Ctrl+C 随时结束会话。\n")
        
        # 重置会话数据
        self.current_session = {
            "start_time": datetime.now(),
            "questions_asked": 0,
            "correct_answers": 0,
            "wrong_answers": 0,
            "total_time": 0
        }
        
        try:
            for _ in range(num_questions):
                result = self.ask_question(question_type)
                if not result:
                    break
                
                # 显示下次复习时间
                next_review_date = result["next_review"].strftime("%Y-%m-%d %H:%M")
                print(f"下次复习时间: {next_review_date}")
                
                # 每道题之间暂停一下
                input("\n按回车键继续...")
        except KeyboardInterrupt:
            print("\n会话已中断。")
        
        # 显示会话总结
        self.show_session_summary()
    
    def show_session_summary(self):
        """显示当前会话的总结"""
        session = self.current_session
        total_questions = session["questions_asked"]
        
        if total_questions == 0:
            print("\n本次会话没有回答任何问题。")
            return
        
        correct = session["correct_answers"]
        wrong = session["wrong_answers"]
        accuracy = (correct / total_questions) * 100
        avg_time = session["total_time"] / total_questions
        
        print("\n" + "=" * 50)
        print("会话总结")
        print("=" * 50)
        print(f"总题数: {total_questions}")
        print(f"正确: {correct}")
        print(f"错误: {wrong}")
        print(f"正确率: {accuracy:.1f}%")
        print(f"平均用时: {avg_time:.1f} 秒/题")
        print(f"总用时: {session['total_time']:.1f} 秒")
        print("=" * 50)