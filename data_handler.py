import json
import os
from datetime import datetime

class DataHandler:
    def __init__(self, data_file="history_events.json", stats_file="user_stats.json"):
        self.data_file = data_file
        self.stats_file = stats_file
        self.events = {}
        self.user_stats = {}
        # Use the data file name as the key to isolate stats for different sources
        self.source_key = os.path.basename(data_file)
        self.load_data()
        self.load_stats()
    
    def load_data(self):
        """从JSON文件加载历史事件数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.events = json.load(f)
            else:
                # 创建示例数据
                self.events = {
                    "鸦片战争": "1840 年 - 1842 年",
                    "太平天国运动": "1851 年 - 1864 年",
                    "第二次鸦片战争": "1856 年 - 1860 年",
                    "甲午中日战争": "1894 年 - 1895 年",
                    "戊戌变法": "1898 年",
                    "武昌起义": "1911 年",
                    "中华民国成立，清帝退位": "1912 年",
                    "五四运动爆发": "1919 年",
                    "中共一大召开，中共成立": "1921 年",
                    "国民党一大召开，国共第一次合作实现": "1924 年",
                    "南昌起义、秋收起义": "1927 年",
                    "九一八事变": "1931 年",
                    "红军长征": "1934 年 - 1936 年",
                    "七七事变，全民族抗战开始": "1937 年",
                    "抗战胜利": "1945 年",
                    "国民党发动全面内战": "1946 年",
                    "新中国成立": "1949 年"
                }
                self.save_data()
        except Exception as e:
            print(f"加载数据时出错: {e}")
            self.events = {}
    
    def save_data(self):
        """保存历史事件数据到JSON文件"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.events, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存数据时出错: {e}")
    
    def load_stats(self):
        """加载用户学习统计数据"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    all_stats = json.load(f)
                
                # Get stats for this specific data source
                if self.source_key in all_stats:
                    self.user_stats = all_stats[self.source_key]
                else:
                    self.user_stats = {}
            else:
                # Create new stats file with empty dict
                with open(self.stats_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
                self.user_stats = {}
        except Exception as e:
            print(f"加载统计数据时出错: {e}")
            self.user_stats = {}
    
    def save_stats(self):
        """保存用户学习统计数据"""
        try:
            # Load all stats
            all_stats = {}
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    all_stats = json.load(f)
            
            # Update stats for this source
            all_stats[self.source_key] = self.user_stats
            
            # Save back to file
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(all_stats, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存统计数据时出错: {e}")
    
    def update_question_stats(self, question, is_correct, time_taken):
        """更新问题的统计数据"""
        # Use file-scoped stats
        if question not in self.user_stats:
            self.user_stats[question] = {
                "total_attempts": 0,
                "correct_attempts": 0,
                "wrong_attempts": 0,
                "avg_time": 0,
                "last_review": datetime.now().isoformat(),
                "next_review": datetime.now().isoformat(),
                "interval": 1,  # 以天为单位的间隔
                "ease_factor": 2.5  # 难度系数
            }
        
        stats = self.user_stats[question]
        stats["total_attempts"] += 1
        
        if is_correct:
            stats["correct_attempts"] += 1
        else:
            stats["wrong_attempts"] += 1
        
        # 更新平均时间
        stats["avg_time"] = ((stats["avg_time"] * (stats["total_attempts"] - 1)) + time_taken) / stats["total_attempts"]
        
        # 保存更新后的统计数据
        self.save_stats()
    
    def get_question_stats(self, question):
        """获取问题的统计数据"""
        if question in self.user_stats:
            return self.user_stats[question]
        return None
    
    def get_all_events(self):
        """获取所有历史事件"""
        return self.events
    
    def get_all_stats(self):
        """获取所有统计数据"""
        # 返回当前数据源的所有统计信息
        return self.user_stats
