import os
import json
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langchain_tavily import TavilySearch
from langchain.agents import create_agent

# ---------- 初始化智能体 ----------
def init_agent():
    # 读取提示词
    prompt_path = Path("prompt.md")
    if prompt_path.exists():
        system_prompt = prompt_path.read_text(encoding="utf-8")
    else:
        # 默认提示词
        system_prompt = "你是一名顶级的艾泽拉斯研究员，擅长深入挖掘《魔兽世界》的最新资讯、攻略和社区讨论。"

    # 大模型（阿里云百炼，兼容 OpenAI 接口）
    model = ChatOpenAI(
        model="deepseek-v4-flash",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_BASE_URL"),
    )

    # 搜索工具（Tavily）
    search_tool = TavilySearch(
        api_key=os.getenv("TAVILY_API_KEY"),
        search_depth="advanced",
        topic="general",
        max_results=5,
        include_domains=[  # 限制优先搜索的权威域名
            "wowhead.com",
            "method.gg",
            "raider.io",
            "bloodmallet.com",
            "warcraftlogs.com",
            "blizzard.com"  # 包含官方蓝贴
        ]
    )

    # 创建 Agent
    agent = create_agent(
        model=model,
        tools=[search_tool],
        checkpointer=MemorySaver(),
        system_prompt=system_prompt
    )
    return agent

agent = init_agent()

# ---------- FastAPI 应用 ----------
app = FastAPI(title="艾泽拉斯万事通 API")

# 存储会话的 thread_id（简单内存存储，生产环境建议用 Redis）
session_map = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

# 根路径返回 HTML 页面（后面我们会创建）
@app.get("/", response_class=HTMLResponse)
async def get_chat_page():
    # 返回一个简单的 HTML（稍后我们将其嵌入，或使用模板）
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

# 流式聊天接口

@app.post("/chat")
async def chat_stream(request: ChatRequest):
    """
    使用 SSE 流式返回 agent 的响应。
    """
    session_id = request.session_id or "default"
    # 为每个 session 分配一个 thread_id（用于记忆）
    if session_id not in session_map:
        session_map[session_id] = f"thread_{len(session_map)}"
    thread_id = session_map[session_id]

    config = {"configurable": {"thread_id": thread_id}}
    inputs = {"messages": [("user", request.message)]}

    async def event_generator():
        try:
            # 使用 astream_events，只监听 on_chat_model_stream 事件
            async for event in agent.astream_events(inputs, config=config, version="v1"):
                if event["event"] == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    if chunk.content:
                        yield {
                            "event": "message",
                            "data": json.dumps({"content": chunk.content}, ensure_ascii=False)
                        }
            yield {"event": "done", "data": "ok"}
        except Exception as e:
            yield {"event": "error", "data": json.dumps({"error": str(e)}, ensure_ascii=False)}

    return EventSourceResponse(event_generator())

# 可选：提供静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)