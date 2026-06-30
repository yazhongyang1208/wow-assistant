# 🧙 艾泽拉斯百晓生 —— 你的魔兽世界智能问答助手

基于 LangChain 构建的智能问答系统，专为《魔兽世界》玩家设计。支持文本和图片提问，通过实时检索游戏维基、社区攻略和官方数据，为你提供准确、及时的游戏资讯和攻略解答。

## ✨ 功能特性

- **🤖 智能问答**：基于大语言模型（支持阿里云百炼、DeepSeek 等），理解自然语言问题。
- **🌐 实时检索**：集成 Tavily 搜索工具，可自动检索互联网上的最新攻略、论坛讨论和官方数据。
- **🖼️ 多模态支持**（规划中）：支持图片提问（例如上传装备截图、地图等），通过视觉模型识别并回答。
- **💬 对话记忆**：基于 LangGraph 的 MemorySaver，支持多轮对话，记住上下文。

## 🛠️ 技术栈

- **后端框架**：FastAPI + Uvicorn
- **AI 框架**：LangChain + LangGraph
- **大模型**：阿里云百炼（通义千问）/ DeepSeek / 其他兼容 OpenAI API 的模型
- **搜索工具**：Tavily Search API
- **向量数据库**：Chroma（用于本地知识库，可选）
- **前端**：原生 HTML + CSS + JavaScript（内嵌于 FastAPI）

## 📦 快速开始

### 前提条件
- Python 3.9+
- pip
- （可选）虚拟环境（推荐）

### 1. 克隆项目
```bash
git clone https://github.com/yazhongyang1208/wow-assistant.git
cd wow-assistant
