#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSS 源有效性验证脚本
功能：
1. 测试 URL 是否能返回 200 状态码
2. 验证返回内容是否为 XML 格式
3. 输出有效的 NEWS_SOURCES 配置
"""

import sys
import os
import requests
import xml.etree.ElementTree as ET
import pprint
import ast
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_news_sources_from_file(file_path):
    """从文件中提取 NEWS_SOURCES 字典，避免导入整个模块带来的依赖问题"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
            
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == 'NEWS_SOURCES':
                        # 尝试将 AST 节点转换为 Python 对象
                        return ast.literal_eval(node.value)
        print("未在文件中找到 NEWS_SOURCES 定义")
        return None
    except Exception as e:
        print(f"解析文件失败: {e}")
        return None

def check_rss(url):
    """验证单个 RSS 源"""
    try:
        # 伪装 User-Agent 防止被拦截
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
        
        # 1. 测试能不能返回 200
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return url, False, f"状态码错误: {response.status_code}"
            
        # 2. 确定返回的内容是不是 xml 格式
        content = response.content
        
        # 尝试解析 XML
        try:
            ET.fromstring(content)
            return url, True, "OK"
        except ET.ParseError:
            # 如果严格解析失败，尝试宽松检查
            content_str = content.decode('utf-8', errors='ignore').strip()
            
            # 检查头部特征
            if content_str.startswith('<?xml') or content_str.startswith('<rss') or content_str.startswith('<feed'):
                return url, True, "OK (格式检查通过)"
                
            # 检查 Content-Type
            content_type = response.headers.get('Content-Type', '').lower()
            if 'xml' in content_type or 'rss' in content_type:
                 return url, True, "OK (Header检查通过)"
            
            return url, False, "非 XML 格式内容"
            
    except requests.RequestException as e:
        return url, False, f"请求异常: {str(e)}"
    except Exception as e:
        return url, False, f"未知错误: {str(e)}"

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    news_fetcher_path = os.path.join(current_dir, 'news_fetcher.py')
    
    if not os.path.exists(news_fetcher_path):
        print(f"错误: 找不到文件 {news_fetcher_path}")
        sys.exit(1)
        
    print(f"正在读取配置: {news_fetcher_path}")
    news_sources = get_news_sources_from_file(news_fetcher_path)
    
    if not news_sources:
        print("无法加载 NEWS_SOURCES 配置，退出。")
        sys.exit(1)
    
    valid_sources = {}
    total_checked = 0
    valid_count = 0
    invalid_count = 0
    
    print(f"开始验证 RSS 源 (共 {sum(len(v) for v in news_sources.values())} 个)...")
    print("-" * 60)
    
    # 使用线程池并发验证，提高速度
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {}
        for category, urls in news_sources.items():
            valid_sources[category] = []
            for url in urls:
                futures[executor.submit(check_rss, url)] = (category, url)
                
        for future in as_completed(futures):
            category, url = futures[future]
            try:
                url_result, is_valid, reason = future.result()
            except Exception as e:
                url_result, is_valid, reason = url, False, f"执行错误: {e}"
            
            total_checked += 1
            
            if is_valid:
                status_symbol = "✅"
                valid_sources[category].append(url)
                valid_count += 1
                print(f"[{category}] {status_symbol} {url}")
            else:
                status_symbol = "❌"
                invalid_count += 1
                print(f"[{category}] {status_symbol} {url} -> {reason}")

    print("-" * 60)
    print(f"验证完成! 总计: {total_checked}, 有效: {valid_count}, 无效: {invalid_count}")
    print("=" * 60)
    
    if invalid_count > 0:
        print("\n建议更新 NEWS_SOURCES 配置如下:\n")
        # 格式化打印字典
        pprint.pprint(valid_sources, width=120, sort_dicts=False)
    else:
        print("\n所有源均有效，无需更新。")

if __name__ == "__main__":
    main()
