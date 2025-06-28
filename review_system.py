import datetime
import random
from datetime import datetime, timedelta

class ReviewSystem:
    def __init__(self, data_handler):
        self.data_handler = data_handler
    
    def calculate_next_review(self, question, performance):
        """计算下一次复习的时间
        
        参数:
            question (str): 问题内容
            performance (int): 表现评分 (0-5)，0表示完全不会，5表示非常熟练
        """
        stats = self.data_handler.get_question_stats(question)
        
        if not stats:
            return datetime.now() + timedelta(days=1)
        
        # 根据SM-2算法调整间隔和难度系数
        if performance >= 3:  # 如果回答正确
            if stats["interval"] == 1:
                interval = 1
            elif stats["interval"] == 2:
                interval = 6
            else:
                interval = stats["interval"] * stats["ease_factor"]
            
            # 根据表现调整难度系数
            ease_factor = stats["ease_factor"] + (0.1 - (5 - performance) * (0.08 + (5 - performance) * 0.02))
            if ease_factor < 1.3:
                ease_factor = 1.3
        else:  # 如果回答错误
            interval = 1
            ease_factor = stats["ease_factor"]
            if ease_factor >= 1.3:
                ease_factor -= 0.2
        
        # 更新统计数据
        stats["interval"] = interval
        stats["ease_factor"] = ease_factor
        stats["last_review"] = datetime.now().isoformat()
        stats["next_review"] = (datetime.now() + timedelta(days=interval)).isoformat()
        
        self.data_handler.save_stats()
        
        return datetime.now() + timedelta(days=interval)
    
    def get_due_questions(self, limit=10):
        """获取当前需要复习的问题"""
        all_stats = self.data_handler.get_all_stats()
        all_events = self.data_handler.get_all_events()
        
        due_questions = []
        now = datetime.now()
        
        # 首先添加从未复习过的问题
        for event in all_events:
            if event not in all_stats:
                due_questions.append(event)
        
        # 然后添加到期需要复习的问题
        for question, stats in all_stats.items():
            if question in all_events:  # 确保问题仍然存在于事件列表中
                next_review = datetime.fromisoformat(stats["next_review"])
                if next_review <= now:
                    due_questions.append(question)
        
        # 如果到期问题不足，添加一些错误率高或平均用时长的问题
        if len(due_questions) < limit:
            remaining_questions = [q for q in all_events if q not in due_questions]
            
            # 按错误率和平均用时排序
            def question_priority(q):
                if q not in all_stats:
                    return (0, 0)  # 未尝试过的问题优先级低
                
                stats = all_stats[q]
                error_rate = stats["wrong_attempts"] / stats["total_attempts"] if stats["total_attempts"] > 0 else 0
                avg_time = stats["avg_time"]
                
                return (error_rate, avg_time)
            
            sorted_questions = sorted(remaining_questions, key=question_priority, reverse=True)
            due_questions.extend(sorted_questions[:limit - len(due_questions)])
        
        # 随机打乱问题顺序
        random.shuffle(due_questions)
        
        return due_questions[:limit]