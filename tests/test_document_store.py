"""测试 DocumentStore"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.document_store import DocumentStore
from src.embeddings.local_embedding import LocalEmbedding
from src.parsers.base import ParseResult


def get_embedding_model():
    """获取本地嵌入模型"""
    try:
        return LocalEmbedding(model_name="BAAI/bge-small-zh-v1.5", device="cpu")
    except Exception as e:
        print(f"[SKIP] 无法加载本地嵌入模型: {e}")
        print("  提示: 需要安装 sentence-transformers: uv add sentence-transformers")
        return None


def create_mock_parse_result(filename: str = "test.pdf") -> ParseResult:
    """创建模拟解析结果"""
    chunks = [
        {"index": 0, "content": "苹果是一种常见的水果", "type": "text", "length": 11},
        {"index": 1, "content": "香蕉是黄色的热带水果", "type": "text", "length": 11},
        {"index": 2, "content": "| 列1 | 列2 |\n|---|---|\n| A | B |", "type": "table", "length": 30, "page": 1},
    ]

    return ParseResult(
        filename=filename,
        total_pages=2,
        total_chunks=len(chunks),
        table_count=1,
        chunks=chunks,
        raw_text="苹果是一种常见的水果。香蕉是黄色的热带水果。",
        tables=[{"table_number": 1, "page": 1, "markdown": "| 列1 | 列2 |\n|---|---|\n| A | B |"}],
        metadata={"parser": "test"}
    )


def test_document_store_add_parse_result():
    """测试添加解析结果"""
    print("\n--- 测试添加解析结果 ---")

    embedding_model = get_embedding_model()
    if not embedding_model:
        return

    store = DocumentStore(
        embedding_model=embedding_model,
        collection_name="test_doc_store"
    )

    # 清空测试数据
    store.vector_store.clear()

    # 创建模拟解析结果
    parse_result = create_mock_parse_result("sample.pdf")

    # 添加到存储
    namespace = "test_docs"
    doc_ids = store.add_parse_result(parse_result, namespace=namespace)

    print(f"  添加了 {len(doc_ids)} 个文档块")
    print(f"  命名空间: {namespace}")

    # 验证
    assert len(doc_ids) == len(parse_result.chunks)
    for doc_id in doc_ids:
        assert namespace in doc_id

    # 获取统计
    stats = store.get_stats()
    print(f"  集合统计: {stats}")
    assert stats["count"] >= len(parse_result.chunks)

    # 清理
    store.vector_store.clear()

    print("[OK] 添加解析结果测试通过")


def test_document_store_add_documents():
    """测试直接添加文档"""
    print("\n--- 测试直接添加文档 ---")

    embedding_model = get_embedding_model()
    if not embedding_model:
        return

    store = DocumentStore(
        embedding_model=embedding_model,
        collection_name="test_doc_store"
    )

    store.vector_store.clear()

    texts = ["第一段文本", "第二段文本", "第三段文本"]
    metadatas = [
        {"source": "test1.txt", "category": "A"},
        {"source": "test2.txt", "category": "B"},
        {"source": "test3.txt", "category": "A"},
    ]

    doc_ids = store.add_documents(texts, metadatas, namespace="direct_add")

    print(f"  添加了 {len(doc_ids)} 个文档")
    for i, doc_id in enumerate(doc_ids):
        print(f"    文档{i+1}: {doc_id}")

    assert len(doc_ids) == len(texts)

    # 清理
    store.vector_store.clear()

    print("[OK] 直接添加文档测试通过")


def test_document_store_search():
    """测试语义搜索"""
    print("\n--- 测试语义搜索 ---")

    embedding_model = get_embedding_model()
    if not embedding_model:
        return

    store = DocumentStore(
        embedding_model=embedding_model,
        collection_name="test_doc_store"
    )

    store.vector_store.clear()

    # 添加测试文档
    texts = [
        "苹果是一种红色或绿色的水果",
        "香蕉是黄色的弯曲水果",
        "汽车有四个轮子",
        "飞机可以飞得很高"
    ]
    metadatas = [{"category": "水果"} if i < 2 else {"category": "交通工具"}
                  for i in range(len(texts))]

    store.add_documents(texts, metadatas, namespace="search_test")

    # 搜索水果
    results = store.search("红色的水果", top_k=3, namespace="search_test")

    print(f"  查询: '红色的水果'")
    print(f"  返回 {len(results)} 个结果:")

    for i, r in enumerate(results, 1):
        print(f"    {i}. {r['content'][:30]}...")
        print(f"       相似度: {r['score']:.4f} | 分类: {r['metadata'].get('category')}")

    # 验证结果数量
    assert len(results) > 0
    # 验证命名空间过滤
    for r in results:
        assert r['metadata']['namespace'] == 'search_test'

    # 清理
    store.vector_store.clear()

    print("[OK] 语义搜索测试通过")


def test_document_store_stats():
    """测试获取统计信息"""
    print("\n--- 测试获取统计信息 ---")

    embedding_model = get_embedding_model()
    if not embedding_model:
        return

    store = DocumentStore(
        embedding_model=embedding_model,
        collection_name="test_stats"
    )

    store.vector_store.clear()

    stats = store.get_stats()
    print(f"  统计信息:")
    print(f"    模型: {stats['embedding_model']}")
    print(f"    向量维度: {stats['embedding_dim']}")
    print(f"    文档数: {stats['count']}")
    print(f"    距离度量: {stats['distance']}")

    assert stats['embedding_model'] == "BAAI/bge-small-zh-v1.5"
    assert stats['embedding_dim'] > 0

    # 清理
    store.vector_store.clear()

    print("[OK] 获取统计信息测试通过")


def test_document_store_full_workflow():
    """测试完整工作流程"""
    print("\n--- 测试完整工作流程 ---")

    embedding_model = get_embedding_model()
    if not embedding_model:
        return

    store = DocumentStore(
        embedding_model=embedding_model,
        collection_name="test_workflow"
    )

    store.vector_store.clear()

    # 1. 添加解析结果
    parse_result = create_mock_parse_result("workflow_test.pdf")
    doc_ids = store.add_parse_result(parse_result, namespace="workflow")

    print(f"  1. 添加解析结果: {len(doc_ids)} 个文档块")

    # 2. 搜索
    results = store.search("水果", top_k=2, namespace="workflow")
    print(f"  2. 搜索 '水果': 找到 {len(results)} 个结果")

    # 3. 获取统计
    stats = store.get_stats()
    print(f"  3. 统计信息: {stats['count']} 个文档")

    # 清理
    store.vector_store.clear()

    print("[OK] 完整工作流程测试通过")


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("DocumentStore 测试")
    print("=" * 50)

    test_document_store_add_parse_result()
    test_document_store_add_documents()
    test_document_store_search()
    test_document_store_stats()
    test_document_store_full_workflow()

    print("\n" + "=" * 50)
    print("[PASS] 测试完成")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()
