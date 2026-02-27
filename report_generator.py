#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成模块 - 生成杂志风格HTML和Markdown格式的新闻简报
支持可点击新闻卡片弹窗和增强分析维度
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# 分类emoji映射
CATEGORY_ICONS = {
    'tech': '🚀',
    'science': '🔬',
    'society': '🏛️',
    'international': '🌍'
}

CATEGORY_NAMES = {
    'tech': '科技',
    'science': '科学',
    'society': '社会',
    'international': '国际'
}

CATEGORY_COLORS = {
    'tech': '#2563EB',
    'science': '#7C3AED',
    'society': '#DC2626',
    'international': '#059669'
}


class ReportGenerator:
    """新闻简报生成器"""
    
    def __init__(self):
        self.today = datetime.now().strftime('%Y-%m-%d')
    
    def generate_html(self, news_list: List[Dict[str, Any]]) -> str:
        """生成杂志风格HTML格式的简报"""
        
        # 按分类分组
        categorized = self._categorize_news(news_list)
        
        # 统计
        stats = {}
        for cat in ['tech', 'science', 'society', 'international']:
            stats[cat] = len(categorized.get(cat, []))
        
        # 构建HTML
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日重点新闻简报 - {self.today}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&family=Noto+Sans+SC:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --bg-paper: #FAFAF9;
            --text-primary: #18181B;
            --text-secondary: #52525B;
            --text-muted: #A1A1AA;
            --accent-tech: #2563EB;
            --accent-science: #7C3AED;
            --accent-society: #DC2626;
            --accent-international: #059669;
            --fund-buy: #059669;
            --fund-sell: #DC2626;
            --fund-hold: #F59E0B;
            --border-light: #E4E4E7;
            --card-bg: #FFFFFF;
        }}
        
        body {{
            font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-paper);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        /* 杂志头版 */
        .masthead {{
            padding: 40px 0 30px;
            border-bottom: 3px solid var(--text-primary);
            margin-bottom: 40px;
        }}
        
        .masthead-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            font-size: 12px;
            color: var(--text-muted);
            letter-spacing: 1px;
        }}
        
        .masthead-title {{
            font-family: 'Noto Serif SC', serif;
            font-size: clamp(32px, 6vw, 56px);
            font-weight: 700;
            text-align: center;
            letter-spacing: 8px;
            color: var(--text-primary);
        }}
        
        .masthead-subtitle {{
            text-align: center;
            font-size: 14px;
            color: var(--text-secondary);
            margin-top: 8px;
            letter-spacing: 2px;
        }}
        
        /* 分类导航 */
        .category-nav {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            justify-content: center;
            margin-bottom: 40px;
            padding: 0 20px;
        }}
        
        .category-btn {{
            padding: 10px 24px;
            border: 1px solid var(--border-light);
            background: var(--card-bg);
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            border-radius: 4px;
            font-family: inherit;
        }}
        
        .category-btn:hover {{
            border-color: var(--text-primary);
        }}
        
        .category-btn.active {{
            background: var(--text-primary);
            color: white;
            border-color: var(--text-primary);
        }}
        
        .category-btn[data-cat="tech"].active {{ background: var(--accent-tech); border-color: var(--accent-tech); }}
        .category-btn[data-cat="science"].active {{ background: var(--accent-science); border-color: var(--accent-science); }}
        .category-btn[data-cat="society"].active {{ background: var(--accent-society); border-color: var(--accent-society); }}
        .category-btn[data-cat="international"].active {{ background: var(--accent-international); border-color: var(--accent-international); }}
        
        /* 统计栏 */
        .stats-bar {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-bottom: 50px;
            padding: 20px;
            background: var(--card-bg);
            border: 1px solid var(--border-light);
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-num {{
            font-family: 'Noto Serif SC', serif;
            font-size: 32px;
            font-weight: 700;
            color: var(--text-primary);
        }}
        
        .stat-label {{
            font-size: 12px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 4px;
        }}
        
        /* 新闻卡片网格 */
        .news-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 24px;
            margin-bottom: 60px;
        }}
        
        .news-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-light);
            padding: 24px;
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
            cursor: pointer;
        }}
        
        .news-card:hover {{
            transform: translateY(-4px);
            border-color: var(--text-primary);
            box-shadow: 0 12px 40px rgba(0,0,0,0.08);
        }}
        
        .news-card.hidden {{
            display: none;
        }}
        
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 16px;
        }}
        
        .category-tag {{
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            padding: 4px 10px;
            border-radius: 2px;
            color: white;
        }}
        
        .category-tag.tech {{ background: var(--accent-tech); }}
        .category-tag.science {{ background: var(--accent-science); }}
        .category-tag.society {{ background: var(--accent-society); }}
        .category-tag.international {{ background: var(--accent-international); }}
        
        .relevance-score {{
            font-size: 11px;
            color: var(--text-muted);
            background: var(--bg-paper);
            padding: 3px 8px;
            border-radius: 2px;
        }}
        
        .card-title {{
            font-family: 'Noto Serif SC', serif;
            font-size: 18px;
            font-weight: 600;
            line-height: 1.5;
            margin-bottom: 16px;
            color: var(--text-primary);
        }}
        
        .core-point {{
            font-size: 14px;
            color: var(--text-secondary);
            padding: 12px 16px;
            background: var(--bg-paper);
            border-left: 3px solid var(--text-primary);
            margin-bottom: 16px;
            line-height: 1.7;
        }}
        
        .insight-section {{
            margin-top: auto;
        }}
        
        .insight-row {{
            display: flex;
            gap: 12px;
            margin-bottom: 12px;
        }}
        
        .insight-box {{
            flex: 1;
            padding: 12px;
            border-radius: 4px;
            font-size: 13px;
        }}
        
        .insight-box.fund {{
            background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
            border: 1px solid #A7F3D0;
        }}
        
        .insight-box.fund.sell {{
            background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
            border: 1px solid #FECACA;
        }}
        
        .insight-box.fund.hold {{
            background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
            border: 1px solid #FDE68A;
        }}
        
        .insight-box.dev {{
            background: #F4F4F5;
            border: 1px solid var(--border-light);
        }}
        
        .insight-label {{
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 4px;
            opacity: 0.7;
        }}
        
        .insight-content {{
            font-weight: 500;
            line-height: 1.5;
        }}
        
        .keywords {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid var(--border-light);
        }}
        
        .keyword {{
            font-size: 11px;
            padding: 3px 8px;
            background: var(--bg-paper);
            color: var(--text-secondary);
            border-radius: 2px;
        }}
        
        .source-link {{
            display: flex;
            align-items: center;
            gap: 6px;
            margin-top: 16px;
            font-size: 12px;
            color: var(--text-muted);
            text-decoration: none;
            transition: color 0.2s;
        }}
        
        .source-link:hover {{
            color: var(--accent-tech);
        }}
        
        /* 底部 */
        .footer {{
            text-align: center;
            padding: 40px 20px;
            border-top: 1px solid var(--border-light);
            color: var(--text-muted);
            font-size: 13px;
        }}
        
        .disclaimer {{
            max-width: 600px;
            margin: 0 auto 20px;
            padding: 16px;
            background: #FEF3C7;
            border: 1px solid #FDE68A;
            font-size: 12px;
            color: #92400E;
        }}
        
        /* 响应式 */
        @media (max-width: 768px) {{
            .masthead-title {{
                letter-spacing: 4px;
            }}
            
            .stats-bar {{
                flex-wrap: wrap;
                gap: 20px;
            }}
            
            .news-grid {{
                grid-template-columns: 1fr;
            }}
            
            .insight-row {{
                flex-direction: column;
            }}
        }}
        
        /* 弹窗样式 */
        .modal-overlay {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        
        .modal-overlay.active {{ display: flex; }}
        
        .modal-content {{
            background: white;
            border-radius: 12px;
            max-width: 900px;
            width: 100%;
            max-height: 90vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        }}
        
        .modal-header {{
            padding: 20px 24px;
            border-bottom: 1px solid var(--border-light);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--bg-paper);
        }}
        
        .modal-title {{
            font-family: 'Noto Serif SC', serif;
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
            flex: 1;
            padding-right: 20px;
        }}
        
        .modal-close {{
            width: 32px;
            height: 32px;
            border: none;
            background: var(--bg-paper);
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            color: var(--text-secondary);
            transition: all 0.2s;
            flex-shrink: 0;
        }}
        
        .modal-close:hover {{ background: var(--text-primary); color: white; }}
        
        .modal-body {{ flex: 1; overflow-y: auto; padding: 0; }}
        .modal-body iframe {{ width: 100%; height: 75vh; border: none; }}
        
        .modal-footer {{
            padding: 16px 24px;
            border-top: 1px solid var(--border-light);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--bg-paper);
        }}
        
        .modal-source {{ font-size: 13px; color: var(--text-muted); }}
        .modal-source a {{ color: var(--accent-tech); text-decoration: none; }}
        
        .btn-open-original {{
            padding: 8px 16px;
            background: var(--text-primary);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .btn-open-original:hover {{ background: var(--accent-tech); }}
        
        /* 增强分析维度样式 */
        .analysis-dimensions {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid var(--border-light);
        }}
        
        .dimension-item {{
            font-size: 11px;
            padding: 6px 8px;
            background: #F8FAFC;
            border-radius: 4px;
            border-left: 2px solid var(--accent-tech);
        }}
        
        .dimension-label {{ font-weight: 600; color: var(--text-secondary); margin-bottom: 2px; }}
        .original-title {{ font-size: 12px; color: var(--text-muted); font-style: italic; margin-top: 4px; }}
        
        @media (max-width: 768px) {{
            .modal-content {{ max-height: 95vh; }}
            .modal-body iframe {{ height: 60vh; }}
            .analysis-dimensions {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <header class="masthead">
        <div class="container">
            <div class="masthead-top">
                <span>{datetime.now().strftime('%Y-%m-%d')}</span>
                <span>每日更新</span>
            </div>
            <h1 class="masthead-title">每日简报</h1>
            <p class="masthead-subtitle">科技 · 科学 · 社会 · 国际</p>
        </div>
    </header>
    
    <main class="container">
        <!-- 分类导航 -->
        <nav class="category-nav">
            <button class="category-btn active" data-cat="all" onclick="filterNews('all')">全部</button>
            <button class="category-btn" data-cat="tech" onclick="filterNews('tech')">🚀 科技</button>
            <button class="category-btn" data-cat="science" onclick="filterNews('science')">🔬 科学</button>
            <button class="category-btn" data-cat="society" onclick="filterNews('society')">🏛️ 社会</button>
            <button class="category-btn" data-cat="international" onclick="filterNews('international')">🌍 国际</button>
        </nav>
        
        <!-- 统计 -->
        <div class="stats-bar">
            <div class="stat-item">
                <div class="stat-num">{stats.get('tech', 0)}</div>
                <div class="stat-label">科技</div>
            </div>
            <div class="stat-item">
                <div class="stat-num">{stats.get('science', 0)}</div>
                <div class="stat-label">科学</div>
            </div>
            <div class="stat-item">
                <div class="stat-num">{stats.get('society', 0)}</div>
                <div class="stat-label">社会</div>
            </div>
            <div class="stat-item">
                <div class="stat-num">{stats.get('international', 0)}</div>
                <div class="stat-label">国际</div>
            </div>
            <div class="stat-item">
                <div class="stat-num">{len(news_list)}</div>
                <div class="stat-label">总计</div>
            </div>
        </div>
        
        <!-- 新闻列表 -->
        <div class="news-grid">
'''
        
        # 添加新闻卡片
        for i, item in enumerate(news_list):
            category = item.get('category', 'tech')
            category_name = CATEGORY_NAMES.get(category, category)
            
            # 基金建议样式
            fund_signal = item.get('fund_signal', '不适用')
            fund_details = item.get('fund_details', '')
            fund_class = 'fund'
            if '卖' in fund_signal or '卖出' in fund_signal:
                fund_class = 'fund sell'
            elif '观' in fund_signal or '观望' in fund_signal:
                fund_class = 'fund hold'
            
            # 关键词
            keywords_html = ''
            for kw in item.get('key_words', [])[:5]:
                keywords_html += f'<span class="keyword">{kw}</span>'
            
            # 原文链接
            link = item.get('link', '')
            source = item.get('source', '来源')
            
            # 原文标题（如果有翻译）
            original_title_html = ''
            if item.get('original_title'):
                original_title_html = f'<div class="original-title">原文: {item.get("original_title")}</div>'
            
            # 增强分析维度
            relevance = item.get('relevance', '待分析')
            impact_level = item.get('impact_level', '中-待分析')
            timeliness = item.get('timeliness', '待分析')
            certainty = item.get('certainty', '中-待分析')
            opportunity_type = item.get('opportunity_type', '不适用')
            
            dimensions_html = f'''
            <div class="analysis-dimensions">
                <div class="dimension-item">
                    <div class="dimension-label">📊 相关性</div>
                    <div>{relevance}</div>
                </div>
                <div class="dimension-item">
                    <div class="dimension-label">📈 影响程度</div>
                    <div>{impact_level}</div>
                </div>
                <div class="dimension-item">
                    <div class="dimension-label">⏰ 时效性</div>
                    <div>{timeliness}</div>
                </div>
                <div class="dimension-item">
                    <div class="dimension-label">✅ 确定性</div>
                    <div>{certainty}</div>
                </div>
                <div class="dimension-item" style="grid-column: span 2;">
                    <div class="dimension-label">🎯 机会类型</div>
                    <div>{opportunity_type}</div>
                </div>
            </div>'''
            
            html += f'''
            <article class="news-card" data-category="{category}" data-index="{i}" onclick="openModal({i})">
                <div class="card-header">
                    <span class="category-tag {category}">{category_name}</span>
                    <span class="relevance-score">★ {item.get('relevance_score', 5)}</span>
                </div>
                <h2 class="card-title">{item.get('title', '无标题')}</h2>
                {original_title_html}
                <div class="core-point">{item.get('core_point', '无')}</div>
                
                <div class="insight-section">
                    <div class="insight-row">
                        <div class="insight-box {fund_class}">
                            <div class="insight-label">💰 基金建议</div>
                            <div class="insight-content">{fund_signal}</div>
                        </div>
                        <div class="insight-box dev">
                            <div class="insight-label">👨‍💻 开发者影响</div>
                            <div class="insight-content">{item.get('dev_impact', '无明显影响')}</div>
                        </div>
                    </div>
                    {dimensions_html}
                </div>
                
                {keywords_html}
            </article>
'''
        
        html += '''
        </div>
    </main>
    
    <footer class="footer">
        <div class="disclaimer">
            ⚠️ 免责声明：本简报内容仅供参考，不构成任何投资建议。基金投资有风险，请谨慎决策。
        </div>
        <p>由 AI 自动生成 · 每日 10:00 更新</p>
    </footer>
    
    <!-- 弹窗 -->
    <div class="modal-overlay" id="newsModal" onclick="closeModal(event)">
        <div class="modal-content" onclick="event.stopPropagation()">
            <div class="modal-header">
                <h3 class="modal-title" id="modalTitle">新闻标题</h3>
                <button class="modal-close" onclick="closeModal()">×</button>
            </div>
            <div class="modal-body">
                <iframe id="modalIframe" src="" title="新闻原文"></iframe>
            </div>
            <div class="modal-footer">
                <div class="modal-source" id="modalSource">来源: </div>
                <button class="btn-open-original" id="modalBtn" onclick="openOriginal()">🔗 在新窗口打开</button>
            </div>
        </div>
    </div>
    
    <script>
        const newsData = '''
        
        # 添加新闻数据到JavaScript
        news_json = []
        for i, item in enumerate(news_list):
            news_json.append({
                'title': item.get('title', ''),
                'link': item.get('link', ''),
                'source': item.get('source', ''),
                'original_title': item.get('original_title', '')
            })
        
        html += json.dumps(news_json, ensure_ascii=False)
        
        html += ''';
        
        let currentIndex = 0;
        
        function filterNews(category) {
            document.querySelectorAll('.category-btn').forEach(btn => {
                btn.classList.remove('active');
                if (btn.dataset.cat === category) {
                    btn.classList.add('active');
                }
            });
            
            document.querySelectorAll('.news-card').forEach(card => {
                if (category === 'all') {
                    card.classList.remove('hidden');
                } else {
                    if (card.dataset.category === category) {
                        card.classList.remove('hidden');
                    } else {
                        card.classList.add('hidden');
                    }
                }
            });
        }
        
        function openModal(index) {
            currentIndex = index;
            const news = newsData[index];
            if (!news || !news.link) return;
            
            document.getElementById('modalTitle').textContent = news.title || '新闻详情';
            document.getElementById('modalIframe').src = news.link;
            document.getElementById('modalSource').innerHTML = news.source ? `来源: <a href="${news.link}" target="_blank">${news.source}</a>` : '';
            document.getElementById('modalBtn').onclick = function() { openOriginal(); };
            document.getElementById('newsModal').classList.add('active');
            document.body.style.overflow = 'hidden';
        }
        
        function closeModal(event) {
            if (event && event.target !== event.currentTarget) return;
            document.getElementById('newsModal').classList.remove('active');
            document.body.style.overflow = '';
        }
        
        function openOriginal() {
            const news = newsData[currentIndex];
            if (news && news.link) {
                window.open(news.link, '_blank');
            }
        }
        
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeModal();
            }
        });
    </script>
</body>
</html>'''
        
        return html
    
    def generate_markdown(self, news_list: List[Dict[str, Any]]) -> str:
        """生成Markdown格式的简报"""
        
        # 按分类分组
        categorized = self._categorize_news(news_list)
        
        # 构建报告
        report_lines = []
        
        # 标题
        report_lines.append(f"# 📊 每日重点新闻简报")
        report_lines.append(f"**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"**新闻数量**: {len(news_list)} 条")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        
        # 摘要统计
        report_lines.append("## 📈 今日概览")
        report_lines.append("")
        
        for category in ['tech', 'science', 'society', 'international']:
            count = len(categorized.get(category, []))
            icon = CATEGORY_ICONS.get(category, '📰')
            name = CATEGORY_NAMES.get(category, category)
            report_lines.append(f"- {icon} **{name}**: {count} 条")
        
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        
        # 按分类输出新闻
        for category in ['tech', 'science', 'society', 'international']:
            items = categorized.get(category, [])
            if not items:
                continue
            
            icon = CATEGORY_ICONS.get(category, '📰')
            name = CATEGORY_NAMES.get(category, category)
            
            report_lines.append(f"## {icon} {name}领域")
            report_lines.append("")
            
            for i, item in enumerate(items, 1):
                report_lines.append(self._format_news_item(i, item))
                report_lines.append("")
            
            report_lines.append("---")
            report_lines.append("")
        
        # 底部提示
        report_lines.append("## ⚠️ 免责声明")
        report_lines.append("")
        report_lines.append("本简报内容仅供参考，不构成任何投资建议。基金投资有风险，请谨慎决策。")
        report_lines.append("")
        report_lines.append("*由AI自动生成*")
        
        return '\n'.join(report_lines)
    
    def _categorize_news(self, news_list: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """按分类整理新闻"""
        categorized = {
            'tech': [],
            'science': [],
            'society': [],
            'international': []
        }
        
        for item in news_list:
            category = item.get('category', 'tech')
            if category in categorized:
                categorized[category].append(item)
        
        return categorized
    
    def _format_news_item(self, index: int, item: Dict[str, Any]) -> str:
        """格式化单条新闻"""
        lines = []
        
        # 标题
        title = item.get('title', '无标题')
        lines.append(f"### {index}. {title}")
        lines.append("")
        
        # 核心要点
        core_point = item.get('core_point', '无')
        lines.append(f"> **核心要点**: {core_point}")
        lines.append("")
        
        # 基金建议
        fund_signal = item.get('fund_signal', '不适用')
        if fund_signal and fund_signal != '不适用':
            fund_details = item.get('fund_details', '')
            lines.append(f"> **💰 基金建议**: {fund_signal}")
            if fund_details:
                lines.append(f">    {fund_details}")
            lines.append("")
        
        # 开发者影响
        dev_impact = item.get('dev_impact', '无明显影响')
        lines.append(f"> **👨‍💻 开发者影响**: {dev_impact}")
        lines.append("")
        
        # 增强分析维度
        relevance = item.get('relevance', '待分析')
        impact_level = item.get('impact_level', '待分析')
        timeliness = item.get('timeliness', '待分析')
        certainty = item.get('certainty', '待分析')
        opportunity_type = item.get('opportunity_type', '不适用')
        
        lines.append(f"> **📊 相关性**: {relevance}")
        lines.append(f"> **📈 影响程度**: {impact_level}")
        lines.append(f"> **⏰ 时效性**: {timeliness}")
        lines.append(f"> **✅ 确定性**: {certainty}")
        lines.append(f"> **🎯 机会类型**: {opportunity_type}")
        lines.append("")
        
        # 关键词
        key_words = item.get('key_words', [])
        if key_words:
            keywords_str = ' '.join([f'`{kw}`' for kw in key_words[:5]])
            lines.append(f"> **标签**: {keywords_str}")
            lines.append("")
        
        # 来源
        link = item.get('link', '')
        source = item.get('source', '')
        if link:
            lines.append(f"> **📎 来源**: [{source}]({link})")
        else:
            lines.append(f"> **📎 来源**: {source}")
        
        return '\n'.join(lines)
    
    def save_report(self, news_list: List[Dict[str, Any]], output_dir: str = None):
        """保存报告到文件"""
        
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(__file__), 'reports')
        
        # 确保目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成Markdown
        markdown = self.generate_markdown(news_list)
        
        # 保存Markdown文件
        md_filename = f"news_report_{self.today}.md"
        md_filepath = os.path.join(output_dir, md_filename)
        
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        logger.info(f"Markdown报告已保存至: {md_filepath}")
        
        # 生成HTML
        html = self.generate_html(news_list)
        
        # 保存HTML文件
        html_filename = f"news_report_{self.today}.html"
        html_filepath = os.path.join(output_dir, html_filename)
        
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"HTML报告已保存至: {html_filepath}")
        
        # 同时保存JSON备份
        json_filename = f"news_report_{self.today}.json"
        json_filepath = os.path.join(output_dir, json_filename)
        
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON数据已保存至: {json_filepath}")
        
        return md_filepath, html_filepath


if __name__ == '__main__':
    # 测试代码
    test_news = [
        {
            'title': 'OpenAI发布GPT-5新模型',
            'link': 'https://openai.com',
            'source': 'TechCrunch',
            'category': 'tech',
            'core_point': 'GPT-5具备更强推理能力',
            'fund_signal': '买入AI主题基金',
            'fund_details': 'AI技术突破将带动相关产业发展',
            'dev_impact': '新API可能改变开发者工作方式',
            'relevance_score': 9,
            'key_words': ['AI', 'GPT-5', 'OpenAI'],
            'relevance': '科技、金融',
            'impact_level': '高-可能引发行业格局重大改变',
            'timeliness': '新鲜-刚发布24小时内',
            'certainty': '高-来源权威且事实明确',
            'opportunity_type': '创业机会-新赛道机会'
        },
    ]
    
    generator = ReportGenerator()
    md_path, html_path = generator.save_report(test_news)
    print(f"报告已生成:")
    print(f"- Markdown: {md_path}")
    print(f"- HTML: {html_path}")
