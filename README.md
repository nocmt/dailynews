# 📊 每日重点新闻简报系统 (AI Powered Daily News Brief)

这是一个基于 Python 的自动化新闻聚合与分析系统。它每天定时从全球权威科技、科学、社会、国际媒体获取新闻，利用智谱 AI (GLM-4-Flash) 进行深度分析，生成包含核心要点、投资建议和开发者视角的简报。

## ✨ 功能特点

- 🚀 **多源聚合**: 支持 TechCrunch, Nature, Reuters, BBC, Ars Technica 等 30+ 个权威 RSS 源
- 🤖 **AI 智能分析**: 使用智谱 AI 提取核心摘要，过滤无关信息
- 🌐 **多语言支持**: 支持自动翻译成简体中文 (默认)、繁体中文、英文、日文等
- 💰 **价值评估**: 自动评估新闻的商业/投资价值
- 👨‍💻 **开发者视角**: 专门分析技术新闻对独立开发者的实际影响
- � **自动报告**: 生成精美的 HTML 和 Markdown 格式日报，并自动在浏览器打开
- ⏰ **定时任务**: 提供 macOS LaunchAgent 和 Linux Crontab 两种定时运行方案

## 📂 文件结构

```text
.
├── main.py                 # 主程序入口
├── news_fetcher.py         # 新闻抓取模块 (RSS解析)
├── ai_analyzer.py          # AI 分析模块 (调用智谱API)
├── report_generator.py     # 报告生成模块 (HTML/Markdown)
├── verify_rss_sources.py   # RSS 源有效性检测工具
├── requirements.txt        # Python 依赖列表
├── .env.example            # 环境变量配置模板
├── run_daily.sh.example    # 执行脚本模板
├── crontab.txt.example     # Linux Crontab 配置参考
├── logs/                   # 运行日志
└── reports/                # 生成的历史报告
```

## 🚀 快速开始

### 1. 克隆项目与安装依赖

```bash
git clone <your-repo-url>
cd daily-news-brief
pip install -r requirements.txt
```

### 2. 配置环境

复制 `.env.example` 为 `.env` 并填入你的配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```ini
# 智谱 AI API Key (必填)
ZHIPU_API_KEY=your_api_key_here

# 目标语言 (可选: zh-CN, zh-TW, en, ja, ko)
TARGET_LANGUAGE=zh-CN
```

### 3. 配置执行脚本

复制 `run_daily.sh.example` 为 `run_daily.sh` 并修改路径：

```bash
cp run_daily.sh.example run_daily.sh
chmod +x run_daily.sh
```

打开 `run_daily.sh`，确保 `PROJECT_DIR` 和 `PYTHON_PATH` 指向正确的路径。

### 4. 运行测试

```bash
./run_daily.sh
```

如果配置正确，脚本将自动抓取新闻、生成报告并在浏览器中打开。

## ⏰ 定时任务配置

参考 `crontab.txt.example` 配置：

```bash
crontab -e
# 添加如下行 (每天 10:00 执行)
0 10 * * * 项目存放路径/run_daily.sh
```

## 🛠️ 工具脚本

**检查 RSS 源有效性**

随着时间推移，部分 RSS 源可能会失效。可以使用此脚本进行检测：

```bash
python3 verify_rss_sources.py
```

## 📝 输出示例

生成的报告将保存在 `reports/` 目录下，包含：

*   **HTML 报告**: `news_report_YYYY-MM-DD.html` (富文本，适合阅读)
*   **Markdown 报告**: `news_report_YYYY-MM-DD.md` (适合归档)
*   **JSON 数据**: `news_report_YYYY-MM-DD.json` (原始数据)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进此项目！

## 📄 许可证

MIT License
