# 🌍 智能旅行助手 (HelloAgents Trip Planner)

> 基于 **Multi-Agent 协作**与 **MCP 协议** 的一站式智能行程规划系统。让 AI 制订旅行计划。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Vue](https://img.shields.io/badge/Vue-3.x-brightgreen.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![HelloAgents](https://img.shields.io/badge/HelloAgents-Framework-orange.svg)

---

## ✨ 项目简介

**智能旅行助手** 是一款融合了 AI Agent 技术的旅行规划应用。不同于传统的关键词搜索，它通过模拟人类"旅行规划师"的思维模式，协调多个 AI 智能体分工合作。

用户只需用自然语言输入需求（如："我想去北京玩3天，喜欢历史文化，预算中等"），系统即可自动调度地图搜索、天气查询、酒店比价等工具，生成包含 **景点路线、酒店预订、天气预报、预算估算** 的完整行程方案，并支持 **地图可视化** 与 **PDF/图片导出**。

### 核心亮点

- 🤖 **多智能体协作 (Multi-Agent)**：由规划、景点、酒店、天气四个专家 Agent 协作完成。

- 🔌 **MCP 协议集成**：采用 Anthropic 提出的 Model Context Protocol 集成高德地图服务。

- 🗺️ **交互式地图**：生成的行程实时在地图上打点连线，直观呈现。

- 📊 **智能预算估算**：根据实时数据自动计算门票、住宿及餐饮预算。

- 📄 **高清导出**：支持将行程一键导出为精美的 PDF 或长图。

  > 注：
  >
  > 本项目属于人工智能原理课程的大作业，早期版本的“作业”性质较厚，Vibe Coding项目，有许多不足的地方，请多包涵。
  >
  > 如果您愿意花一些时间体验这个项目并提出批评与改进意见，将会对我帮助很大。
  >
  > 感谢。

---

## 🧠 技术架构与工作原理

本项目采用经典的 **前后端分离** 架构，引入了 **Agent Mesh** 协作模式。

### 系统架构

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        External Tools (MCP & API)                           │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐  │
│  │  高德地图 MCP Server │  │  Unsplash 图片服务  │  │   高德开放平台       │  │
│  └──────────▲──────────┘  └──────────▲──────────┘  └──────────▲──────────┘  │
│             │ MCP Protocol           │ HTTP                   │ API         │
└─────────────┼────────────────────────┼────────────────────────┼─────────────┘
              │                        │                        │
┌─────────────┼────────────────────────┼────────────────────────┼─────────────┐
│             │    AI Agent Team (HelloAgents Framework)        │             │
│  ┌──────────┴──────────┬─────────────┴─────────────┬──────────┴──────────┐  │
│  │ 🏰 景点搜索 Agent   │  🏨 酒店推荐 Agent        │  ☀️ 天气查询 Agent  │  │
│  └──────────▲──────────┴─────────────▲─────────────┴──────────▲──────────┘  │
│             │ 调度                   │ 调度                   │ 调度        │
│             └────────────────────────┼────────────────────────┘             │
│                           ┌──────────┴──────────┐                           │
│                           │  🧠 规划总控 Agent  │                           │
│                           └──────────▲──────────┘                           │
└──────────────────────────────────────┼──────────────────────────────────────┘
                                       │ 任务分发
┌──────────────────────────────────────┼──────────────────────────────────────┐
│                           ┌──────────┴──────────┐                           │
│                           │   后端 FastAPI      │                           │
│                           └──────────▲──────────┘                           │
│                                      │ REST API                             │
│                           ┌──────────┴──────────┐                           │
│                           │   前端 Vue3 UI      │                           │
│                           └──────────▲──────────┘                           │
│                                      │                                      │
│                           ┌──────────┴──────────┐                           │
│                           │       用户          │                           │
│                           └─────────────────────┘                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 智能体分工

| Agent 角色 | 职责说明 | 关键技术 |
|------------|----------|----------|
| **Planner Agent** | 大脑与总控。负责理解用户意图，拆解任务，汇总各方信息，生成最终 JSON 结构化行程。 | Context Management, Reasoning |
| **Attraction Agent** | 景点专家。根据偏好（如"亲子"、"人文"）精准搜索 POI。 | Tool Use (Search) |
| **Hotel Agent** | 住宿专家。根据预算和位置筛选最合适的酒店。 | Tool Use (Search) |
| **Weather Agent** | 气象员。查询目的地未来几天的天气，辅助行程决策。 | Tool Use (Weather) |

---

## 🛠️ 技术栈

- **Frontend**: Vue 3, TypeScript, Ant Design Vue, Amap JS API (高德地图), html2canvas, jsPDF
- **Backend**: Python 3.10+, FastAPI, Pydantic
- **AI Core**: HelloAgents (自研 Agent 框架), DeepSeek / OpenAI LLM
- **Integration**: Model Context Protocol (MCP), Unsplash API
- **DevOps**: Docker, Docker Compose

---

## 🚀 快速开始 (Docker 部署)

这是运行本项目最简单的方式。确保本地已安装 Docker 和 Docker Compose。

### 1. 克隆项目

```bash
git clone https://github.com/your-username/helloagents-trip-planner.git
cd helloagents-trip-planner
```

### 2. 配置环境变量

项目根目录下创建或修改 `.env` 文件。你需要填入 LLM 和高德地图的 Key。

```bash
# 复制示例配置 (backend/.env.example 的内容)
# 建议直接在根目录创建 .env，docker-compose 会自动读取
```

`.env` 文件示例：

```env
# --- LLM 服务配置 ---
LLM_MODEL_ID=deepseek-chat
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxx
LLM_BASE_URL=https://api.deepseek.com

# --- 外部 API 配置 ---
# 高德地图 Web 服务 Key (用于后端 MCP 工具调用)
AMAP_API_KEY=your_amap_web_service_key

# Unsplash 图片服务 (可选，留空则不显示景点图)
UNSPLASH_ACCESS_KEY=your_unsplash_key
```

> **注意**：前端地图显示还需要一个高德地图 JS API Key，请在 `frontend/src/views/ResultView.vue` 或前端环境变量中配置。

### 3. 一键启动

```bash
docker-compose up -d --build
```

### 4. 访问应用

- **Web 界面**: 打开浏览器访问 `http://localhost:3000`
- **API 文档**: 访问 `http://localhost:18080/docs`

---

## 💻 本地开发指南

如果你想修改代码或进行二次开发：

### 后端 (Backend)

```bash
cd backend

# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 .env (参考上文)

# 4. 启动服务 (需确保本地已安装 Node.js 以运行 MCP server)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端 (Frontend)

```bash
cd frontend

# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev
```

---

## 📂 目录结构

```text
helloagents-trip-planner/
├── backend/                    # 后端核心代码
│   ├── app/
│   │   ├── agents/             # AI 智能体实现 (Prompt & Logic)
│   │   ├── api/routes/         # REST API 路由
│   │   ├── models/             # Pydantic 数据模型
│   │   └── services/           # 业务逻辑服务
│   ├── .env.example            # 环境变量示例
│   └── requirements.txt        # Python 依赖
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── views/              # 页面组件 (HomeView, ResultView)
│   │   ├── components/         # 可复用组件
│   │   ├── services/           # API 封装
│   │   └── types/              # TypeScript 类型定义
│   └── package.json            # Node.js 依赖
└── README.md                   # 项目说明文档
```

---

## 🤝 贡献与反馈

本项目是**人工智能原理课程**的期末大作业成果。

完成的过程比较匆忙。一开始本来打算加入展示小红书笔记卡片的功能，但是尝试了爬取和RSS订阅，效果都不太好，对用户的门槛也比较高，迫于时间就先没实现了。主要还是为了完成作业，侧重于学习与展示Agent的基础知识，所以一些功能和细节上还是比较粗糙。

- 但如果你觉得这个项目有价值，依旧欢迎给一个(*´∀`)~⭐️ Star！

- 如果你发现 Bug 或有新的想法，欢迎提交 Issue 或 Pull Request。我会积极学习和改进的www

---

## 📄 License

[MIT License](LICENSE)
