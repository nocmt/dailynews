#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日新闻简报 - 主程序
执行命令: python main.py
"""

import os
import sys
import logging
import dotenv
from datetime import datetime

# 加载环境变量
dotenv.load_dotenv('./.env')

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from news_fetcher import NewsFetcher
from ai_analyzer import ZhipuAnalyzer
from report_generator import ReportGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 可配置参数
MAX_NEWS_COUNT = 100  # 最大处理新闻数量
TARGET_LANGUAGE = os.environ.get('TARGET_LANGUAGE', 'zh-CN')  # 翻译目标语言，默认简体中文


def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("开始生成每日新闻简报")
    logger.info(f"目标语言: {TARGET_LANGUAGE}")
    logger.info(f"最大新闻数: {MAX_NEWS_COUNT}")
    logger.info("=" * 50)
    
    start_time = datetime.now()
    
    # 1. 获取新闻
    logger.info("[1/3] 正在获取新闻...")
    fetcher = NewsFetcher()
    news_list = fetcher.fetch_all_news()
    
    if not news_list:
        logger.warning("未获取到任何新闻")
        return
    
    logger.info(f"获取到 {len(news_list)} 篇原始新闻")
    
    # 2. AI分析
    logger.info("[2/3] 正在分析新闻...")
    api_key = os.environ.get('ZHIPU_API_KEY', '')
    
    if not api_key:
        logger.warning("未设置 ZHIPU_API_KEY 环境变量，请设置后再运行")
        logger.warning("可以使用: export ZHIPU_API_KEY=your_api_key")
    
    # 传入目标语言参数
    analyzer = ZhipuAnalyzer(api_key=api_key, target_language=TARGET_LANGUAGE)
    analyzed_news = analyzer.batch_analyze(news_list, max_items=MAX_NEWS_COUNT)
    
    logger.info(f"分析完成，筛选出 {len(analyzed_news)} 条重点新闻")
    
    # 3. 生成报告
    logger.info("[3/3] 正在生成报告...")
    generator = ReportGenerator()
    md_path, html_path = generator.save_report(analyzed_news)
    
    # 输出统计
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("=" * 50)
    logger.info(f"简报生成完成！")
    logger.info(f"用时: {duration:.1f} 秒")
    logger.info(f"报告路径: {html_path}")
    logger.info("=" * 50)
    
    # 打印报告内容
    print("\n" + "=" * 50)
    print("新闻简报内容预览:")
    print("=" * 50)
    print(generator.generate_markdown(analyzed_news))
    
    # 返回HTML文件路径供外部调用
    return html_path


if __name__ == '__main__':
    html_path = main()
    if html_path:
        print(f"\n生成的HTML报告: {html_path}")
