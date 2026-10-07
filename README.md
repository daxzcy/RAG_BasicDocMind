# RAG 智能问答系统

一个基于 FastAPI 的 RAG（检索增强生成）系统，支持多种文档格式的解析、向量存储和智能问答。

## 功能特性

- **多格式文档解析**：支持 PDF、DOCX、Markdown、HTML 等多种文档格式
- **向量存储**：基于 ChromaDB 的向量数据库，支持语义搜索
- **智能问答**：基于 LLM 的问答系统，支持普通和流式输出
- **现代化前端**：基于 Vue 3 + Element Plus 的响应式界面
- **多模型支持**：支持智谱 AI、通义千问等多种 LLM 提供商

## 项目结构

```shell
rag_project/
├── src/
│   ├── api/                # API 接口层
│   │   ├── routers/        # 路由模块
│   │   │   ├── chat.py     # 聊天接口
│   │   │   ├── document.py # 文档上传接口
│   │   │   └── health.py   # 健康检查
│   │   ├── config.py       # 配置管理
│   │   ├── deps.py         # 依赖注入
│   │   └── main.py         # FastAPI 主应用
│   ├── llm/                # LLM 模块
│   │   ├── llm.py          # LLM 基类
│   │   └── rag.py          # RAG 生成逻辑
│   ├── embeddings/         # 向量嵌入模块
│   │   ├── base.py         # 嵌入基类
│   │   ├── openai_embedding.py
│   │   ├── local_embedding.py
│   │   ├── vector_store.py # 向量存储接口
│   │   └── chroma_store.py # ChromaDB 实现
│   ├── parsers/            # 文档解析模块
│   │   ├── base.py         # 解析器基类
│   │   ├── pdf_parse.py    # PDF 解析
│   │   ├── word_parser.py  # DOCX 解析
│   │   ├── markdown_parser.py
│   │   ├── html_parser.py
│   │   ├── table_parser.py
│   │   ├── chunker.py      # 文本分块
│   │   └── cleaner.py      # 文本清理
│   ├── retrieval/          # 检索模块
│   │   └── search_service.py
│   └── database/           # 数据存储
│       └── document_store.py
├── frontend/               # 前端界面
│   ├── index.html
│   └── js/
│       ├── api/            # API 封装
│       ├── components/     # Vue 组件
│       │   ├── ChatInterface.js
│       │   ├── DocumentUpload.js
│       │   └── DocumentList.js
│       ├── utils/          # 工具函数
│       └── app.js          # 主应用
├── data/                   # 数据目录
│   ├── uploads/            # 上传文件
│   └── chroma_db/          # 向量数据库
├── pyproject.toml          # 项目配置与依赖
├── uv.lock                 # 依赖锁定文件
└── .env                    # 环境配置
```

## 快速开始

### 1. 环境准备

确保已安装 Python 3.12+ 和 [uv](https://github.com/astral-sh/uv)：

```bash
# 检查 Python 版本
python --version

# 安装 uv (如果尚未安装)
pip install uv
# 或使用官方安装脚本
curl -LsSf https://astral.sh/uv/install.sh | sh
```

> 本项目使用 uv 进行依赖管理，支持 PyTorch CUDA 12.6 加速。

### 2. 安装依赖

```bash
# 使用 uv 安装依赖
uv sync

# 安装开发依赖
uv sync --group dev
```

### 3. 配置环境变量

创建 `.env` 文件并配置以下变量：

```bash
# LLM 配置
ZHIPU_API_KEY=your_zhipu_api_key
ZHIPU_MODEL=glm-4-flash
DASHSCOPE_API_KEY=your_dashscope_api_key
DASHSCOPE_MODEL=qwen-plus
DEFAULT_MODEL=zhipu

# 检索配置
SEARCH_TOP_K=3
```

### 4. 启动服务

```bash
# 使用 uv 运行 (推荐)
uv run uvicorn src.api.main:app --reload --port 8000

# 或直接运行
uv run src/api/main.py

# 或使用 python
python -m src.api.main
```

### 5. 访问界面

打开浏览器访问 `http://localhost:8000` 或直接打开 `frontend/index.html`

## API 文档

启动服务后，访问以下地址查看 API 文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 主要 API 端点

### 文档管理

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/document/upload` | POST | 上传并解析文档 |
| `/api/document/parse-path` | POST | 按路径解析文档 |
| `/api/document/supported-formats` | GET | 获取支持的格式列表 |

### 聊天问答

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/chat/` | POST | 普通聊天模式 |
| `/api/chat/stream` | POST | 流式聊天模式 |

### 健康检查

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 服务健康状态 |

## 配置说明

### 文件上传配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| MAX_FILE_SIZE | 150MB | 最大文件大小 |
| ALLOWED_EXTENSIONS | .pdf, .md, .html, .docx | 支持的文件扩展名 |

### LLM 配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| LLM_TEMPERATURE | 0.7 | 生成温度 |
| LLM_MAX_TOKEN | 2000 | 最大 token 数 |

### 检索配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| SEARCH_TOP_K | 3 | 返回结果数量 |

## 开发

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest tests/test_api.py
```

### 项目依赖管理

```bash
# 添加新依赖
uv add <package-name>

# 添加开发依赖
uv add --group dev <package-name>

# 更新依赖
uv sync --upgrade
```

## 技术栈

- **后端**：FastAPI, Python 3.12
- **前端**：Vue 3, Element Plus
- **向量数据库**：ChromaDB
- **LLM**：智谱 AI, 通义千问
- **文档解析**：Docling, python-docx, markdown
- **向量嵌入**：sentence-transformers (BAAI/bge-small-zh-v1.5)
- **深度学习**：PyTorch with CUDA 12.6
- **包管理**：uv

