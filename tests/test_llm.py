"""测试 LLM 和 RAG 模块 - 使用真实模型"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

from src.llm.llm import LLM
from src.llm.rag import format_context, build_prompt, generate_answer


def test_llm_basic():
    """测试基础 LLM 调用"""
    print("\n--- 测试 LLM 基础调用 ---")

    # 从环境变量读取配置
    model = os.getenv("ZHIPU_MODEL", "glm-4-flash")
    api_key = os.getenv("ZHIPU_API_KEY")
    base_url = os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")

    if not api_key:
        print("  跳过：未配置 ZHIPU_API_KEY")
        return

    llm = LLM(model=model, api_key=api_key, base_url=base_url)

    result = llm.generate(
        messages=[{"role": "user", "content": "你好，请简单介绍一下 Python"}],
        temperature=0.7,
        max_token=100
    )

    print(f"  模型: {result['model']}")
    print(f"  回复: {result['content'][:100]}...")
    print(f"  Tokens: {result['token_used']}")

    assert result["content"]
    print("[OK] LLM 基础调用测试通过")


def test_format_context():
    """测试上下文格式化"""
    print("\n--- 测试上下文格式化 ---")

    docs = [
        {"content": "Python 是一种高级编程语言，由 Guido van Rossum 创建", "doc_id": "1", "score": 0.95},
        {"content": "Python 简单易学，语法清晰", "doc_id": "2", "score": 0.88},
        {"content": "Python 广泛应用于数据分析、AI 等领域", "doc_id": "3", "score": 0.85},
        {"content": "Python 是一种高级编程语言，由 Guido van Rossum 创建", "doc_id": "4", "score": 0.80},  # 重复
    ]

    context = format_context(docs, max_chars=200)

    print(f"  原始文档数: {len(docs)}")
    print(f"  上下文长度: {len(context)} 字符")
    print(f"  上下文内容:\n{context}")

    assert "Python" in context
    # 验证去重
    assert context.count("Guido van Rossum") == 1
    print("[OK] 上下文格式化测试通过")


def test_build_prompt():
    """测试 Prompt 构建"""
    print("\n--- 测试 Prompt 构建 ---")

    context = "Python 是一种编程语言"
    question = "什么是 Python？"

    prompt = build_prompt(context, question)

    print(f"  Prompt 长度: {len(prompt)} 字符")
    print(f"  Prompt 内容:\n{prompt}")

    assert "上下文" in prompt
    assert "问题" in prompt
    assert context in prompt
    assert question in prompt
    print("[OK] Prompt 构建测试通过")


def test_generate_answer():
    """测试 RAG 生成答案"""
    print("\n--- 测试 RAG 生成答案 ---")

    # 从环境变量读取配置
    model = os.getenv("ZHIPU_MODEL", "glm-4-flash")
    api_key = os.getenv("ZHIPU_API_KEY")
    base_url = os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")

    if not api_key:
        print("  跳过：未配置 ZHIPU_API_KEY")
        return

    llm = LLM(model=model, api_key=api_key, base_url=base_url)

    # 模拟检索结果
    results = [
        {"content": "Python 是一种高级编程语言，由 Guido van Rossum 于 1991 年首次发布。", "doc_id": "1", "score": 0.95},
        {"content": "Python 设计强调代码的可读性和简洁的语法。", "doc_id": "2", "score": 0.88},
    ]

    question = "Python 是谁创建的？"

    result = generate_answer(
        llm=llm,
        question=question,
        results=results,
        temperature=0.7,
        max_token=200
    )

    print(f"  问题: {result['question']}")
    print(f"  答案: {result['answer']}")
    print(f"  上下文: {result['context'][:100]}...")
    print(f"  Tokens: {result['token_used']}")

    assert result["answer"]
    assert "Guido" in result["answer"] or "不知道" in result["answer"]
    print("[OK] RAG 生成答案测试通过")


def test_qwen_llm():
    """测试通义千问 LLM"""
    print("\n--- 测试通义千问 LLM ---")

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("  跳过：未配置 DASHSCOPE_API_KEY")
        return

    llm = LLM(
        model=os.getenv("QWEN_MODEL", "qwen-turbo"),
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    result = llm.generate(
        messages=[{"role": "user", "content": "你好"}],
        temperature=0.7,
        max_token=50
    )

    print(f"  模型: {result['model']}")
    print(f"  回复: {result['content'][:50]}...")

    assert result["content"]
    print("[OK] 通义千问 LLM 测试通过")


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("LLM & RAG 模块测试 (真实模型)")
    print("=" * 50)

    # 测试 RAG 工具函数（不需要 API）
    test_format_context()
    test_build_prompt()

    # 测试需要 API 的功能
    print("\n" + "=" * 50)
    print("需要 API Key 的测试:")
    print("=" * 50)

    test_llm_basic()
    test_generate_answer()
    test_qwen_llm()

    print("\n" + "=" * 50)
    print("[PASS] 所有测试通过")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()
