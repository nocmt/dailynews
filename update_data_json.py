#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 docs/data.json 文件
在生成新报告后运行，将新报告信息追加到 data.json 中
"""

import os
import json
import re
from datetime import datetime

# 配置文件路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(PROJECT_ROOT, 'docs')
REPORTS_DIR = os.path.join(DOCS_DIR, 'reports')
DATA_JSON_PATH = os.path.join(DOCS_DIR, 'data.json')

def update_data_json():
    """扫描 reports 目录并更新 data.json"""
    print(f"正在更新 {DATA_JSON_PATH}...")
    
    # 1. 获取所有 HTML 报告文件
    if not os.path.exists(REPORTS_DIR):
        print(f"错误: 报告目录不存在 {REPORTS_DIR}")
        return

    reports_list = []
    files = os.listdir(REPORTS_DIR)
    
    # 正则匹配文件名: news_report_YYYY-MM-DD.html
    pattern = re.compile(r'news_report_(\d{4}-\d{2}-\d{2})\.html')
    
    for filename in files:
        match = pattern.match(filename)
        if match:
            date_str = match.group(1)
            reports_list.append({
                "date": date_str,
                "htmlUrl": f"./reports/{filename}",
                "mdUrl": f"./reports/{filename.replace('.html', '.md')}",
                "jsonUrl": f"./reports/{filename.replace('.html', '.json')}"
            })
    
    # 2. 按日期倒序排序
    reports_list.sort(key=lambda x: x['date'], reverse=True)
    
    # 3. 写入 data.json
    try:
        with open(DATA_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(reports_list, f, indent=4, ensure_ascii=False)
        print(f"✅ 成功更新 data.json，共包含 {len(reports_list)} 份报告")
    except Exception as e:
        print(f"❌ 写入 data.json 失败: {e}")

if __name__ == "__main__":
    update_data_json()
