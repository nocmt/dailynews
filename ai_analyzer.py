#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI分析模块 - 使用智谱AI (GLM-4-Flash)
支持新闻分析和翻译功能
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)

# 智谱AI配置
ZHIPU_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
ZHIPU_MODEL = "glm-4-flash"


class ZhipuAnalyzer:
    """智谱AI新闻分析器"""
    
    def __init__(self, api_key: str = None, target_language: str = "zh-CN"):
        self.api_key = api_key or os.environ.get('ZHIPU_API_KEY', '')
        self.model = ZHIPU_MODEL
        self.target_language = target_language  # 目标语言，默认简体中文
    
    def _build_prompt(self, news_item: Dict[str, Any]) -> str:
        """构建分析提示词"""
        category_names = {
            'tech': '科技',
            'science': '科学', 
            'society': '社会',
            'international': '国际'
        }
        
        category = news_item.get('category', 'tech')
        category_name = category_names.get(category, '科技')
        
        return f"""你是一个专业的金融和科技新闻分析师。请分析以下新闻并按JSON格式返回分析结果。

新闻标题：{news_item.get('title', '')}
新闻来源：{news_item.get('source', '')}
新闻摘要：{news_item.get('summary', '')[:300]}
新闻分类：{category_name}

请返回以下格式的JSON（必须是合法的JSON，不要有其他内容）：
{{
    "core_point": "一句话核心要点（15-30字）",
    "fund_signal": "基金建议：买入/卖出/观望 + 具体方向（如：买入AI主题基金、卖出传统能源ETF、观望）",
    "fund_details": "简要说明基金建议的理由（30-50字）",
    "dev_impact": "对独立开发者的实际影响（30-50字）",
    "relevance_score": 评分（1-10，10分最高，基于对投资和开发者的实际价值）,
    "key_words": ["关键词1", "关键词2", "关键词3"],
    "relevance": "相关领域：用逗号分隔的领域列表（如：科技、金融、医疗、能源、政策法规、宏观经济、消费、新赛道、用户痛点、政策红利等）",
    "impact_level": "影响程度：高/中/低 + 具体说明（如：高-可能引发行业格局重大改变）",
    "timeliness": "时效性：热门/新鲜/平稳/过期 + 说明（如：新鲜-刚发布24小时内）",
    "certainty": "确定性：高/中/低 + 说明（如：高-来源权威且事实明确）",
    "opportunity_type": "机会类型：创业机会/基金机会/两者皆有/不适用 + 具体说明（如：创业机会-新赛道机会、基金机会-行业轮动机会）"
}}

注意：
1. 只返回JSON，不要有其他文字
2. 如果新闻与投资无关，fund_signal写"不适用"
3. dev_impact要从独立开发者角度分析实际影响
4. relevance_score要客观评分
5. 所有字段都必须填写完整"""
    
    def analyze_news(self, news_item: Dict[str, Any]) -> Dict[str, Any]:
        """分析单条新闻"""
        if not self.api_key:
            logger.warning("未配置智谱AI API密钥，使用默认分析")
            return self._default_analysis(news_item)
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.model,
            'messages': [
                {'role': 'user', 'content': self._build_prompt(news_item)}
            ],
            'temperature': 0.7,
        }
        
        try:
            response = requests.post(
                ZHIPU_API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # 解析JSON
                analysis = json.loads(content)
                
                return {
                    'core_point': analysis.get('core_point', '无法提取核心要点'),
                    'fund_signal': analysis.get('fund_signal', '不适用'),
                    'fund_details': analysis.get('fund_details', ''),
                    'dev_impact': analysis.get('dev_impact', '无明显影响'),
                    'relevance_score': analysis.get('relevance_score', 5),
                    'key_words': analysis.get('key_words', []),
                    'relevance': analysis.get('relevance', '待分析'),
                    'impact_level': analysis.get('impact_level', '中-待分析'),
                    'timeliness': analysis.get('timeliness', '待分析'),
                    'certainty': analysis.get('certainty', '中-待分析'),
                    'opportunity_type': analysis.get('opportunity_type', '不适用')
                }
            else:
                logger.error(f"API调用失败: {response.status_code} - {response.text}")
                return self._default_analysis(news_item)
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return self._default_analysis(news_item)
        except Exception as e:
            logger.error(f"分析失败: {e}")
            return self._default_analysis(news_item)
    
    def _default_analysis(self, news_item: Dict[str, Any]) -> Dict[str, Any]:
        """默认分析（当API不可用时）"""
        return {
            'core_point': news_item.get('title', '')[:30],
            'fund_signal': '需人工分析',
            'fund_details': '请查看原始新闻',
            'dev_impact': '请查看原始新闻',
            'relevance_score': 5,
            'key_words': [],
            'relevance': '待分析',
            'impact_level': '中-待分析',
            'timeliness': '待分析',
            'certainty': '中-待分析',
            'opportunity_type': '不适用'
        }
    
    def translate_title(self, title: str) -> Optional[str]:
        """翻译非中文标题到目标语言"""
        if not title:
            return None
        
        # 检查是否包含中文字符
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in title)
        if has_chinese:
            return None  # 已经是中文，不需要翻译
        
        if not self.api_key:
            logger.warning("未配置智谱AI API密钥，无法翻译")
            return None
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # 根据目标语言设置翻译提示
        lang_map = {
            'zh-CN': '简体中文',
            'zh-TW': '繁体中文', 
            'en': '英语',
            'ja': '日语',
            'ko': '韩语'
        }
        target_name = lang_map.get(self.target_language, '简体中文')
        
        payload = {
            'model': self.model,
            'messages': [
                {'role': 'user', 'content': f'请将以下标题翻译成{target_name}，只返回翻译结果，不要有任何解释或其他内容：\n\n{title}'}
            ],
            'temperature': 0.3,
            'max_tokens': 200
        }
        
        try:
            response = requests.post(
                ZHIPU_API_URL,
                headers=headers,
                json=payload,
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                translated = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                return translated if translated else None
            else:
                logger.error(f"翻译API调用失败: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"翻译失败: {e}")
            return None
    
    def batch_analyze(self, news_list: List[Dict[str, Any]], max_items: int = 100) -> List[Dict[str, Any]]:
        """批量分析新闻"""
        analyzed_news = []
        
        logger.info(f"开始分析 {len(news_list)} 篇新闻...")
        
        for i, news in enumerate(news_list):
            logger.info(f"分析进度: {i+1}/{len(news_list)}")
            
            # 翻译非中文标题
            original_title = news.get('title', '')
            translated_title = self.translate_title(original_title)
            if translated_title:
                news['title'] = translated_title
                news['original_title'] = original_title  # 保留原文
            
            analysis = self.analyze_news(news)
            
            # 合并原始新闻和分析结果
            combined = {**news, **analysis}
            analyzed_news.append(combined)
        
        # 按相关性评分排序，取前max_items条
        analyzed_news.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return analyzed_news[:max_items]


if __name__ == '__main__':
    # 测试代码
    test_news = {
        'title': 'OpenAI发布GPT-5新模型',
        'source': 'TechCrunch',
        'summary': 'OpenAI宣布推出新一代GPT-5模型，具备更强的推理能力和多模态理解能力...',
        'category': 'tech'
    }
    
    # 需要设置环境变量 ZHIPU_API_KEY
    analyzer = ZhipuAnalyzer()
    result = analyzer.analyze_news(test_news)
    print(json.dumps(result, ensure_ascii=False, indent=2))
