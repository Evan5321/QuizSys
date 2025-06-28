import os
import sys
import argparse
from datetime import datetime, timedelta

from data_handler import DataHandler
from review_system import ReviewSystem
from quiz import Quiz
import config

def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """打印程序标题"""
    print("\n" + "=" * 50)
    print(f"{config.APP_NAME} v{config.APP_VERSION}")
    print("=" * 50)

def print_stats(data_handler):
    """打印学习统计信息"""
    all_stats = data_handler.get_all_stats()
    all_events = data_handler.get_all_events()
    
    total_events = len(all_events)
    studied_events = sum(1 for q in all_events if q in all_stats)
    
    print(f"\n总事件数: {total_events}")
    print(f"已学习事件: {studied_events} ({studied_events/total_events*100:.1f}%)")
    
    if studied_events > 0:
        # 计算正确率
        total_attempts = sum(stats["total_attempts"] for stats in all_stats.values())
        correct_attempts = sum(stats["correct_attempts"] for stats in all_stats.values())
        
        if total_attempts > 0:
            accuracy = (correct_attempts / total_attempts) * 100
            print(f"总正确率: {accuracy:.1f}%")
        
        # 计算今天需要复习的事件数
        now = datetime.now()
        today_end = datetime(now.year, now.month, now.day, 23, 59, 59)
        
        due_today = 0
        for question, stats in all_stats.items():
            if question in all_events:  # 确保问题仍然存在于事件列表中
                next_review = datetime.fromisoformat(stats["next_review"])
                if next_review <= today_end:
                    due_today += 1
        
        print(f"今天待复习: {due_today}")

def add_new_event(data_handler):
    """添加新的历史事件"""
    print("\n添加新的历史事件")
    print("=" * 50)
    
    event = input("请输入历史事件名称: ").strip()
    if not event:
        print("事件名称不能为空！")
        return
    
    date = input("请输入事件发生的时间: ").strip()
    if not date:
        print("事件时间不能为空！")
        return
    
    # 获取现有事件
    events = data_handler.get_all_events()
    
    # 添加新事件
    events[event] = date
    
    # 保存数据
    data_handler.events = events
    data_handler.save_data()
    
    print(f"\n已添加: {event} - {date}")

def view_all_events(data_handler):
    """查看所有历史事件"""
    events = data_handler.get_all_events()
    
    if not events:
        print("\n没有历史事件数据！")
        return
    
    print("\n所有历史事件")
    print("=" * 50)
    
    # 按事件名称排序
    sorted_events = sorted(events.items())
    
    for i, (event, date) in enumerate(sorted_events, 1):
        print(f"{i}. {event}: {date}")

def main_menu():
    """主菜单"""
    # 初始化数据处理器和复习系统
    current_data_file = config.DATA_FILE  # Track current data file
    data_handler = DataHandler(current_data_file, config.STATS_FILE)
    review_system = ReviewSystem(data_handler)
    quiz = Quiz(data_handler, review_system)
    
    while True:
        clear_screen()
        print_header()
        print_stats(data_handler)
        
        print(f"\n当前题库文件: {current_data_file}")
        print("主菜单:")
        print("1. 开始背诵 (选择题)")
        print("2. 开始背诵 (填空题)")
        print("3. 开始背诵 (混合模式)")
        print("4. 添加新的历史事件")
        print("5. 查看所有历史事件")
        print("6. 切换题库文件")
        print("0. 退出程序")
        
        choice = input("\n请选择 (0-6): ").strip()
        
        if choice == "1":
            num_questions = int(input("请输入题目数量: ") or config.DEFAULT_SESSION_QUESTIONS)
            quiz.start_session(num_questions, "multiple_choice")
        elif choice == "2":
            num_questions = int(input("请输入题目数量: ") or config.DEFAULT_SESSION_QUESTIONS)
            quiz.start_session(num_questions, "fill_blank")
        elif choice == "3":
            num_questions = int(input("请输入题目数量: ") or config.DEFAULT_SESSION_QUESTIONS)
            quiz.start_session(num_questions, "random")
        elif choice == "4":
            add_new_event(data_handler)
            input("\n按回车键返回主菜单...")
        elif choice == "5":
            view_all_events(data_handler)
            input("\n按回车键返回主菜单...")
        elif choice == "6":
            new_file = input("\n请输入新的题库文件路径 (默认显示当前目录下的JSON文件): ").strip() or None
            
            if new_file is None:
                # 显示当前目录下所有JSON文件
                json_files = [f for f in os.listdir('.') if f.endswith('.json')]
                if not json_files:
                    print("\n没有找到其他JSON格式的题库文件！")
                    input("按回车键继续...")
                    continue
                
                print("\n可选的题库文件:")
                for i, filename in enumerate(json_files, 1):
                    print(f"{i}. {filename}")
                
                try:
                    choice = int(input("\n请选择要切换的题库文件编号: "))
                    if 1 <= choice <= len(json_files):
                        new_file = json_files[choice - 1]
                    else:
                        print("\n无效的选择！")
                        input("按回车键继续...")
                        continue
                except ValueError:
                    print("\n请输入有效的数字！")
                    input("按回车键继续...")
                    continue
            
            if os.path.exists(new_file) and new_file.endswith('.json'):
                if new_file != current_data_file:
                    current_data_file = new_file
                    data_handler = DataHandler(current_data_file, config.STATS_FILE)
                    review_system = ReviewSystem(data_handler)
                    quiz = Quiz(data_handler, review_system)
                    print(f"\n已切换题库文件至: {current_data_file}")
                else:
                    print(f"\n已经是当前题库文件: {current_data_file}")
            else:
                print(f"\n文件不存在或不是有效的JSON文件: {new_file}")
            
            input("按回车键继续...")
        elif choice == "0":
            print("\n感谢使用历史大事年表背诵助手！再见！")
            sys.exit(0)
        else:
            print("\n无效的选择，请重试！")
            input("按回车键继续...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"{config.APP_NAME} v{config.APP_VERSION}")
    parser.add_argument("-q", "--questions", type=int, default=config.DEFAULT_SESSION_QUESTIONS,
                        help=f"每次会话的问题数量 (默认: {config.DEFAULT_SESSION_QUESTIONS})")
    parser.add_argument("-t", "--type", choices=["multiple_choice", "fill_blank", "random"],
                        default="random", help="问题类型 (默认: random)")
    
    args = parser.parse_args()
    
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n程序已中断。再见！")
        sys.exit(0)