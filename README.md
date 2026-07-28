# AI教学智能体

多模态AI互动式教学智能体 —— 以教师教学思路为驱动，实现课件共创。

## 技术栈

- **前端**: Vue 3 + Vite（简洁风UI）
- **后端**: Python + FastAPI
- **AI模型**: 兼容 OpenAI API 格式（默认 DeepSeek）
- **向量检索**: 自研 numpy 向量存储
- **课件生成**: python-pptx / python-docx

## 快速启动

### 1. 配置 API Key

编辑 `backend/.env`，填入你的 API Key：

```
LLM_API_KEY=你的API-Key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

支持所有兼容 OpenAI API 的服务（DeepSeek、Qwen、GLM等）。

### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API 文档：http://localhost:8000/docs

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

浏览器访问：http://localhost:5173

### 4. Windows 一键启动

双击 `start.bat`

## 功能说明

1. **智能对话**：与AI助手多轮对话，描述教学需求，AI会主动追问澄清
2. **文件上传**：上传 PDF/Word/PPT/图片 等参考资料，自动解析入库
3. **知识库RAG**：上传的文档自动向量化，课件生成时智能检索相关内容
4. **课件生成**：一键生成 PPT + Word教案 + HTML互动问答
5. **预览下载**：右侧面板预览生成结果，一键下载

## 项目结构

```
ai-teaching-agent/
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── main.py        # 入口
│   │   ├── config.py      # 配置
│   │   ├── models/        # Pydantic 数据模型
│   │   ├── routers/       # API 路由
│   │   └── services/      # 核心服务
│   │       ├── llm_service.py      # LLM 交互
│   │       ├── rag_service.py      # 向量检索
│   │       ├── file_parser.py      # 文件解析
│   │       ├── ppt_generator.py    # PPT 生成
│   │       └── doc_generator.py    # 教案生成
│   └── requirements.txt
├── frontend/               # Vue 3 前端
│   └── src/
│       ├── App.vue
│       ├── views/Home.vue
│       └── components/
│           ├── ChatPanel.vue      # 对话面板
│           ├── FileUploader.vue   # 文件上传
│           └── PreviewPanel.vue   # 预览面板
└── knowledge_base/         # 知识库文件目录
```
