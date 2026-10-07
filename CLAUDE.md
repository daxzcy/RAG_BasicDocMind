# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

RAG 智能问答系统 — 用户上传文档（PDF/DOCX/Markdown/HTML），系统解析、分块、向量化存入 ChromaDB，用户用自然语言提问时，检索相关段落作为上下文发给 LLM 生成回答。前后端分离，FastAPI 后端 + Vue 3 CDN 前端。

## 常用命令

```bash
# 安装依赖
uv sync
uv sync --group dev          # 含 pytest

# 启动开发服务器
uv run uvicorn src.api.main:app --reload --port 8000

# 运行测试
uv run pytest                              # 全部测试
uv run pytest tests/test_chunker.py        # 单个测试文件

# 添加依赖
uv add <package>
uv add --group dev <package>
```

## 核心架构

### 数据流（文档上传 → 问答）

```
文件上传 → ParserFactory(按扩展名选解析器) → ParseResult(chunks + tables)
  → DocumentStore → LocalEmbedding(向量化) → ChromaVectorStore(持久化)
  → 用户提问 → SearchService → ChromaDB检索 → format_context + build_prompt
  → LLM.generate() → 返回答案（支持普通/流式）
```

### 关键模块

- **`src/api/deps.py`** — 依赖注入层，`get_embedding_model()` 用 `@lru_cache(maxsize=1)` 保证全局单例（模型只加载一次），`get_llm(model)` 根据请求中指定的模型名查 `settings.LLM_PROVIDERS` 动态创建实例。
- **`src/parsers/__init__.py`** — `ParserFactory` 维护扩展名→解析器映射（`.pdf→PDFParser`, `.docx→WordParser`, `.md→MarkdownParser`, `.html→HTMLParser`），提供了 `parse_file()` 便捷函数。
- **`src/parsers/chunker.py`** — 四种分块策略：`PARAGRAPH`（默认，按段落分割）、`SENTENCE`、`CHARACTER`、`SEMANTIC`（占位未实现）。超长段落会先按句分割再字符滑动窗口切分。
- **`src/retrieval/search_service.py`** — `CachedSearchService` 是装饰器模式，用 `TTLCache` 缓存检索结果（通过 `.env` 中的 `ENABLE_SEARCH_CACHE` 控制开关）。
- **`src/llm/rag.py`** — RAG 核心逻辑：`format_context()` 去重 + 截断拼接上下文，`build_prompt()` 构建中文指令模板，`generate_answer()` / `generate_answer_stream()` 编排整个检索→生成流程。
- **`src/embeddings/`** — 两类嵌入实现：`LocalEmbedding`（sentence-transformers 本地运行 BGE 模型）和 `OpenAIEmbedding`（调用 OpenAI 兼容 API，含 tenacity 重试）。

### 前端

Vue 3 通过 CDN 加载（非构建工具），`frontend/index.html` 直接打开即可。三个组件：`DocumentUpload`（拖拽上传+集合名称）、`DocumentList`（读取 localStorage）、`ChatInterface`（支持流式，使用 Fetch API ReadableStream）。

## 配置要点

所有配置通过 `.env` 文件管理，`src/api/config.py` 的 `Settings` 类读取：

- **LLM 提供商**：`LLM_PROVIDERS` 字典从 `.env` 中以 `_API_KEY` / `_BASE_URL` / `_MODEL` 后缀规则自动解析，新增 LLM 只需在 `.env` 中按相同命名规则添加即可
- **嵌入模型**：默认 `BAAI/bge-small-zh-v1.5`，本地运行；`HF_HUB_OFFLINE=1` + `TRANSFORMERS_OFFLINE=1` 强制离线模式（模型需已缓存到 `./models/cache`）
- **PyTorch**：专门配置了 CUDA 12.6 索引 (`pytorch-cu126`)，仅对 Linux/Windows 生效

## 测试注意事项

- 测试文件使用 `uv run tests/test_xxx.py` 直接运行，依赖项目源码的相对导入
- 部分测试（如 `test_document_store.py`、`test_search_service.py`）是集成测试，需要有效的 ChromaDB 路径和嵌入模型
- `test_pdf.md` 是 PDF 解析参考输出，用于对比验证
