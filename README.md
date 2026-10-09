# RAG 智能问答系统

一个基于 FastAPI 的 RAG（检索增强生成）系统，支持多种文档格式的解析、向量存储和智能问答。

## 功能特性

- **多格式文档解析**：支持 PDF、DOCX、Markdown、HTML 等多种文档格式
- **向量存储**：基于 ChromaDB 的向量数据库，支持语义搜索
- **智能问答**：基于 LLM 的问答系统，支持普通和流式输出
- **现代化前端**：基于 Vue 3 + Element Plus 的响应式界面
- **多模型支持**：默认 DeepSeek，也支持智谱 AI、通义千问，三家都走 OpenAI 兼容接口
- **本地向量化**：sentence-transformers 本地跑 BGE 中文模型，支持完全离线（无需 embedding API）

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
├── models/
│   └── cache/              # 本地嵌入模型缓存（BAAI/bge-small-zh-v1.5）
├── certs/
│   └── win-roots.pem       # 本机 TLS 代理根证书（给 Python 做证书校验用）
├── scripts/                # 辅助脚本（如周报生成）
├── tests/                  # 测试（多数可直接 uv run tests/xxx.py 运行）
├── pyproject.toml          # 项目配置与依赖
├── uv.lock                 # 依赖锁定文件
├── .python-version         # Python 版本（3.10）
└── .env                    # 环境配置
```

## 快速开始

### 1. 环境准备

确保已安装 Python 3.10+ 和 [uv](https://github.com/astral-sh/uv)：

```bash
# 检查 Python 版本
python --version

# 安装 uv (如果尚未安装)
pip install uv
# 或使用官方安装脚本
curl -LsSf https://astral.sh/uv/install.sh | sh
```

> 本项目使用 uv 进行依赖管理，`.python-version` 固定为 **3.10**，支持 PyTorch CUDA 12.6 加速。

### 2. 安装依赖

```bash
# 安装依赖（uv sync 会一并安装 dev 依赖组）
uv sync
```

> **3.10 专属约束**：`onnxruntime` 从 1.24 起不再提供 cp310 的 wheel，而它是 chromadb 的传递依赖，
> 所以 `pyproject.toml` 里固定了 `onnxruntime==1.23.2; python_full_version < '3.11'`，
> 锁文件里该包会分成 `1.23.2`（3.10）和 `1.24.4`（3.11+）两个分支，升级依赖时别把它删掉。

#### 安装源（国内镜像）

`pyproject.toml` 里已把索引换成国内镜像，不需要额外配置环境变量或 `~/.config/uv`：

| 索引 | 地址 | 用途 |
|------|------|------|
| `tuna`（`default = true`） | https://pypi.tuna.tsinghua.edu.cn/simple | 除 PyTorch 外的全部依赖 |
| `pytorch-cu126`（`explicit = true`） | https://mirror.sjtu.edu.cn/pytorch-wheels/cu126 | torch / torchvision 的 CUDA 12.6 wheel |

**安全性**：`uv.lock` 为每个 wheel 记录了 sha256，安装时逐个校验，镜像若返回不一致的文件会直接报 hash mismatch 中止。已实测这两个镜像下发的 wheel 与官方源（`pypi.org` / `download.pytorch.org`）**逐字节一致**（106 个 wheel 哈希全等）。

临时改用其它镜像（阿里云 / 中科大 / 华为云）：

```bash
uv sync --default-index https://mirrors.aliyun.com/pypi/simple/
```

镜像同步有延迟，若某个包在镜像里还没有，可临时回退官方源：`--default-index https://pypi.org/simple`。

> **PyTorch 版本上限**：`torch>=2.10.0,<2.11`、`torchvision>=0.25.0,<0.26`。
> 更换索引会让 uv 重新解析依赖，不加限会直接跳到 `2.14.1+cu126`（多下一次 2.4GB）；
> 这两条上限锁住当前已验证可用的 `2.10.0+cu126`，要升级时放宽即可。

### 3. 配置环境变量

`.env` 已在仓库外维护（被 `.gitignore` 忽略），当前实际内容如下，**只需填 `DEEPSEEK_API_KEY`**：

```ini
# ==================== 网络 / TLS ====================
# 本机走 TLS 代理，Python 的 certifi 里没有代理根证书，需要显式指定系统根证书，
# 否则 httpx/requests 会报 CERTIFICATE_VERIFY_FAILED（DeepSeek 接口也会连不上）
SSL_CERT_FILE=./certs/win-roots.pem
REQUESTS_CA_BUNDLE=./certs/win-roots.pem
# HuggingFace 直连被墙，走国内镜像
HF_ENDPOINT=https://hf-mirror.com

# ==================== LLM 配置 ====================
# DeepSeek（默认模型，去 https://platform.deepseek.com 申请 key 后填在这里）
DEEPSEEK_API_KEY=
DEEPSEEK_MODEL=deepseek-chat
DEFAULT_MODEL=deepseek

# 智谱 AI（可选）
# ZHIPU_API_KEY=
# ZHIPU_MODEL=glm-4-flash

# 通义千问 / DashScope（可选）
# DASHSCOPE_API_KEY=
# DASHSCOPE_MODEL=qwen-plus

# ==================== 嵌入模型 ====================
# 本地运行，需要模型已缓存到 EMBEDDING_CACHE_DIR
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
EMBEDDING_DEVICE=cpu
EMBEDDING_CACHE_DIR=./models/cache

# 强制离线加载本地模型缓存（首次下载模型时注释掉这两行）
HF_HUB_OFFLINE=1
TRANSFORMERS_OFFLINE=1

# ==================== 检索配置 ====================
# 注意：ENABLE_SEARCH_CACHE 必须存在，deps.py 对 None 调用 .lower() 会报错
ENABLE_SEARCH_CACHE=true
SEARCH_CACHE_TTL=300
SEARCH_CACHE_MAXSIZE=100

# ==================== 向量库 ====================
CHROMA_DB_PATH=./data/chroma_db
```

> 换模型只需改 `DEFAULT_MODEL`（取值 `deepseek` / `zhipu` / `qwen`），
> 或在请求体里传 `{"model": "zhipu"}` 单次覆盖 —— 前端界面不传该字段，走 `DEFAULT_MODEL`。

### 4. 准备嵌入模型（首次运行）

`HF_HUB_OFFLINE=1` 要求模型已在本地，首次使用需先下载一次（约 92 MB）：

```bash
# HF 直连被墙，走 .env 里的 HF_ENDPOINT 镜像
uv run python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-zh-v1.5', cache_folder='./models/cache', device='cpu')"
```

下载完成后 `models/cache` 会出现 `models--BAAI--bge-small-zh-v1.5` 目录，之后即可离线启动。

### 5. 启动服务

```bash
# 使用 uv 运行 (推荐，务必在项目根目录执行：.env 里的证书路径是相对路径)
uv run uvicorn src.api.main:app --reload --port 8000

# 或直接运行
uv run src/api/main.py

# 或使用 python
python -m src.api.main
```

### 6. 访问界面

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
| `/api/document/list` | GET | 列出集合里已入库的文件及块数 |
| `/api/document/{filename}` | DELETE | 删除某个文件的全部向量（处理过时知识，更新文档＝先删后加） |
| `/api/document/supported-formats` | GET | 获取支持的格式列表 |

### 聊天问答

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/chat/` | POST | 普通聊天模式 |
| `/api/chat/stream` | POST | 流式聊天模式 |

### 健康检查

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/health/` | GET | 服务健康状态 |

## 配置说明

### 文件上传配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| MAX_FILE_SIZE | 150MB | 最大文件大小 |
| ALLOWED_EXTENSIONS | .pdf, .md, .html, .docx | 支持的文件扩展名 |
| UPLOAD_DIR | data/uploads | 上传文件存储目录 |

### LLM 配置

`src/api/config.py` 的 `LLM_PROVIDERS` 定义可用厂商，`get_llm()` 按名字取配置创建 OpenAI 兼容客户端：

| provider | base_url | 默认模型 | 环境变量 |
|----------|----------|----------|----------|
| `deepseek`（默认） | https://api.deepseek.com/v1 | deepseek-chat | `DEEPSEEK_API_KEY` / `DEEPSEEK_MODEL` |
| `zhipu` | https://open.bigmodel.cn/api/paas/v4 | glm-4-flash | `ZHIPU_API_KEY` / `ZHIPU_MODEL` |
| `qwen` | https://dashscope.aliyuncs.com/compatible-mode/v1 | qwen-plus | `DASHSCOPE_API_KEY` / `DASHSCOPE_MODEL` |

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| DEFAULT_MODEL | deepseek | 默认 provider，请求体 `model` 字段可单次覆盖 |
| LLM_TEMPERATURE | 0.7 | 生成温度（代码内固定，非环境变量） |
| LLM_MAX_TOKEN | 2000 | 模型单次生成的最大 token 数（代码内固定，非环境变量） |
| LLM_MAX_CONTEXT_CHARS | 2000 | 拼进提示词的上下文总字符上限，与 `LLM_MAX_TOKEN` 解耦（代码内固定，非环境变量） |

### 检索与向量库配置

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| ENABLE_SEARCH_CACHE | 无（**必须设置**） | `true/1/yes` 时启用 TTL 检索缓存；不设置会因 `None.lower()` 报错 |
| SEARCH_CACHE_TTL | 300 | 缓存过期秒数 |
| SEARCH_CACHE_MAXSIZE | 100 | 缓存条目上限 |
| SEARCH_TOP_K | 3 | 返回结果数量（`config.py` 内硬编码，`.env` 里写无效） |
| EMBEDDING_MODEL | BAAI/bge-small-zh-v1.5 | 本地嵌入模型（HuggingFace 名称） |
| EMBEDDING_DEVICE | cpu | 嵌入模型运行设备，有 N 卡可改 `cuda` |
| EMBEDDING_CACHE_DIR | ./models/cache | 模型缓存目录（配合 `HF_HUB_OFFLINE=1` 离线加载） |
| CHROMA_DB_PATH | ./data/chroma_db | ChromaDB 持久化目录 |

### 网络相关

| 环境变量 | 说明 |
|----------|------|
| SSL_CERT_FILE / REQUESTS_CA_BUNDLE | 本机 TLS 代理的根证书路径，不设会让 httpx/requests 报 `CERTIFICATE_VERIFY_FAILED` |
| HF_ENDPOINT | HuggingFace 镜像地址（https://hf-mirror.com） |
| HF_HUB_OFFLINE / TRANSFORMERS_OFFLINE | 设为 1 强制离线加载本地模型缓存 |

## 开发

### 运行测试

```bash
# 运行所有测试（共 86 个用例）
uv run pytest

# 运行特定测试文件
uv run pytest tests/test_chunker.py

# 部分测试是带 main 的独立脚本，需要直接运行（依赖项目内的相对导入）
uv run tests/test_llm.py
```

> 未配置对应 API key 时，`test_llm.py` / `test_zhipu_embedding.py` 等联网用例会自动跳过；
> `test_document_store.py`、`test_search_service.py` 是集成测试，需要可用的 ChromaDB 路径与已缓存的嵌入模型。

### 项目依赖管理

```bash
# 添加新依赖（走 pyproject.toml 里配置的国内镜像）
uv add <package-name>

# 添加开发依赖
uv add --group dev <package-name>

# 更新依赖
uv sync --upgrade
```

> 镜像地址写在 `pyproject.toml` 的 `[[tool.uv.index]]` 段里，`uv add` / `uv lock` / `uv sync` 都自动遵循；
> 换源后务必跑一次 `uv lock` 让锁文件记录新的 registry 与哈希。

## 技术栈

- **后端**：FastAPI, Python 3.10
- **前端**：Vue 3, Element Plus
- **向量数据库**：ChromaDB
- **LLM**：DeepSeek, 智谱 AI, 通义千问
- **文档解析**：Docling, python-docx, markdown
- **向量嵌入**：sentence-transformers (BAAI/bge-small-zh-v1.5)，本地 CPU/GPU 推理
- **深度学习**：PyTorch with CUDA 12.6
- **包管理**：uv（默认索引为清华 TUNA 镜像，PyTorch wheel 走上海交大镜像）

## 常见问题

**1. `CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate`**

本机 HTTPS 走了 TLS 代理，`certifi` 里没有代理根证书。把系统根证书导出给 Python，路径写进 `.env` 的 `SSL_CERT_FILE`：

```powershell
Get-ChildItem Cert:\LocalMachine\Root, Cert:\CurrentUser\Root | ForEach-Object {
  "-----BEGIN CERTIFICATE-----"
  [Convert]::ToBase64String($_.RawData, 'InsertLineBreaks')
  "-----END CERTIFICATE-----"
} | Set-Content certs\win-roots.pem -Encoding Ascii
```

代理更换或证书过期后重跑一次即可。该文件与机器相关，已被 `.gitignore` 忽略。

**2. `AttributeError: 'NoneType' object has no attribute 'lower'`**

`.env` 里缺少 `ENABLE_SEARCH_CACHE`（`src/api/deps.py` 直接对它调用 `.lower()`），补上 `ENABLE_SEARCH_CACHE=true` 或 `false`。

**3. 前端换模型没反应**

`ChatInterface.js` 不传 `model` 字段，一律使用 `.env` 的 `DEFAULT_MODEL`。要临时切换就改 `.env`，或直接调 API：`POST /api/chat/` 带上 `{"model": "qwen", ...}`。

**4. `uv lock` / `uv sync` 解析失败**

改动 `pyproject.toml` 里的 `onnxruntime==1.23.2; python_full_version < '3.11'` 会导致 3.10 装不上（1.24+ 无 cp310 wheel），保留该约束。

**5. PowerShell 5.1 里看 `.env` 是乱码**

文件是 UTF-8，5.1 默认按 ANSI 解码。用 `Get-Content .env -Encoding UTF8` 查看（应用侧 python-dotenv 默认按 UTF-8 读，不受影响）。

**6. `uv` 报 `Failed to initialize cache`**

缓存目录不可写时，把 `UV_CACHE_DIR` 指到可写目录：`$env:UV_CACHE_DIR="$env:TEMP\uv-cache"`。

