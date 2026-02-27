#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日新闻简报系统
每天10:00自动获取过去24小时内的科技、科学、社会、国际重点新闻
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import feedparser
import requests
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 新闻源配置 - 扩展版
NEWS_SOURCES = {
   "tech": [
      "https://techcrunch.com/feed/",
      "https://www.wired.com/feed/rss",
      "https://stackoverflow.blog/feed/",
      "https://www.theverge.com/rss/index.xml",
      "https://www.techradar.com/rss",
      "https://www.ithome.com/rss/",
      "https://www.zdnet.com/news/rss.xml",
      "https://www.cnet.com/rss/news/",
      "https://www.leiphone.com/feed",
      "https://tech.meituan.com/feed/",
      "https://feeds.arstechnica.com/arstechnica/index",
      "https://www.engadget.com/rss.xml",
      "https://www.producthunt.com/feed"
   ],
   "science": [
      "https://www.nature.com/nature.rss",
      "https://www.newscientist.com/feed/home",
      "https://www.sciencedaily.com/rss/all.xml",
      "https://www.science.org/rss/current.xml",
      "https://journals.plos.org/plosone/feed/atom",
      "https://www.popsci.com/feed/",
      "https://www.nasa.gov/rss/dyn/breaking_news.rss"
   ],
   "society": [
      "https://feeds.bbci.co.uk/news/rss.xml",
      "https://www.ithome.com/rss/"
   ],
   "international": [
      "https://www.aljazeera.com/xml/rss/all.xml",
      "https://www.bbc.com/news/rss.xml",
      "https://www.theguardian.com/world/rss",
      "https://www.nytimes.com/services/xml/rss/nyt/World.xml",
      "https://www.propublica.org/feeds/propublica/main"
   ]
}


# 去重和过滤配置
MAX_NEWS_PER_SOURCE = 15
MAX_TOTAL_NEWS = 100  # 扩展到100篇


class NewsFetcher:
    """新闻获取器"""
    
    def __init__(self):
        self.seen_titles = set()
    
    def fetch_feed(self, url: str, category: str) -> List[Dict[str, Any]]:
        """获取单个RSS源的内容"""
        articles = []
        try:
            logger.info(f"正在获取: {url}")
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:MAX_NEWS_PER_SOURCE]:
                # 提取文章信息
                title = entry.get('title', '').strip()
                link = entry.get('link', '')
                published = entry.get('published', entry.get('updated', ''))
                summary = entry.get('summary', entry.get('description', ''))
                
                # 清理HTML标签
                summary = self._clean_html(summary)
                
                # 去重检查
                if title.lower() in self.seen_titles:
                    continue
                
                # 简单相似度去重
                is_duplicate = False
                for seen in self.seen_titles:
                    if self._is_similar(title, seen):
                        is_duplicate = True
                        break
                
                if is_duplicate:
                    continue
                
                self.seen_titles.add(title.lower())
                
                # 解析发布时间
                pub_date = self._parse_date(published)
                
                # 过滤24小时内的新闻
                if pub_date:
                    time_diff = datetime.now(pub_date.tzinfo) - pub_date
                    if time_diff > timedelta(hours=24):
                        continue
                
                articles.append({
                    'title': title,
                    'link': link,
                    'summary': summary[:500],  # 限制摘要长度
                    'published': published,
                    'category': category,
                    'source': feed.feed.get('title', url)
                })
                
        except Exception as e:
            logger.error(f"获取 {url} 失败: {e}")
        
        return articles
    
    def _clean_html(self, text: str) -> str:
        """清理HTML标签"""
        soup = BeautifulSoup(text, 'html.parser')
        return soup.get_text().strip()
    
    def _parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        if not date_str:
            return None
        
        # 尝试多种日期格式
        formats = [
            '%a, %d %b %Y %H:%M:%S %z',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
        ]
        
        for fmt in formats:
            try:
                # 移除星期几的中文
                date_str = date_str.replace('GMT', '+0000')
                return datetime.strptime(date_str[:len('2024-01-01T12:00:00+0000')], fmt.replace('%z', '+0000'))
            except:
                try:
                    return datetime.strptime(date_str[:len('2024-01-01T12:00:00')], fmt.replace('%z', ''))
                except:
                    continue
        
        return None
    
    def _is_similar(self, title1: str, title2: str, threshold: float = 0.7) -> bool:
        """简单的相似度检查"""
        title1 = title1.lower().replace(' ', '')
        title2 = title2.lower().replace(' ', '')
        
        if title1 in title2 or title2 in title1:
            return True
        
        # 计算字符集重叠
        set1 = set(title1)
        set2 = set(title2)
        if len(set1) == 0 or len(set2) == 0:
            return False
        
        overlap = len(set1 & set2) / min(len(set1), len(set2))
        return overlap > threshold
    
    def fetch_all_news(self) -> List[Dict[str, Any]]:
        """获取所有来源的新闻"""
        all_articles = []
        
        for category, sources in NEWS_SOURCES.items():
            for source in sources:
                articles = self.fetch_feed(source, category)
                all_articles.extend(articles)
                logger.info(f"从 {category}/{source} 获取了 {len(articles)} 篇文章")
        
        # 按发布时间排序
        all_articles.sort(key=lambda x: x.get('published', ''), reverse=True)
        
        logger.info(f"共获取 {len(all_articles)} 篇新闻")
        return all_articles[:MAX_TOTAL_NEWS]


if __name__ == '__main__':
    fetcher = NewsFetcher()
    news = fetcher.fetch_all_news()
    print(f"获取到 {len(news)} 篇新闻")
    for item in news[:3]:
        print(f"- {item['title']}")
