"""测试 SearchService 检索服务 - 使用真实本地模型"""
import sys
import os
import tempfile
import shutil
import uuid
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retrieval.search_service import SearchService,RetrievalConfig
from src.database.document_store import DocumentStore
from src.embeddings.local_embedding import LocalEmbedding

_TEST_TEMP_DIR = None


def get_temp_dir():
    """获取临时测试目录"""
    global _TEST_TEMP_DIR
    if _TEST_TEMP_DIR is None:
        _TEST_TEMP_DIR = tempfile.mkdtemp(prefix="rag_test_")
    return _TEST_TEMP_DIR


def cleanup_temp_dir():
    """清理临时目录"""
    global _TEST_TEMP_DIR
    if _TEST_TEMP_DIR and os.path.exists(_TEST_TEMP_DIR):
        shutil.rmtree(_TEST_TEMP_DIR)
        _TEST_TEMP_DIR = None


def create_search_service():
    """创建使用真实本地模型的检索服务"""
    embedding_model = LocalEmbedding(
        model_name="BAAI/bge-small-zh-v1.5",
        device="cpu"
    )

    unique_name = f"test_{uuid.uuid4().hex[:8]}"
    store = DocumentStore(
        embedding_model=embedding_model,
        collection_name=unique_name
    )

    test_docs = [
        "苹果是一种常见的水果，富含维生素C",
        "香蕉是黄色的热带水果，富含钾元素",
        "汽车有四个轮子，是现代交通工具",
        "Python是一种流行的编程语言",
    ]

    test_metadatas = [
        {"category": "水果"},
        {"category": "水果"},
        {"category": "交通工具"},
        {"category": "编程"},
    ]

    store.add_documents(test_docs, test_metadatas, namespace="test")

    return SearchService(document_store=store)


def test_basic_search():
    """测试基本检索功能"""
    print("\n--- 测试基本检索功能 ---")

    service = create_search_service()
    config = RetrievalConfig(top_k=3, min_score=0.0)

    response = service.search("水果", config)

    print(f"  查询: '水果'")
    print(f"  返回 {response.total_results} 个结果")
    print(f"  耗时: {response.retrieval_time_ms} ms")

    for i, r in enumerate(response.results[:2], 1):
        print(f"    {i}. score={r['score']:.3f} - {r['content'][:30]}...")

    assert response.query == "水果"
    assert isinstance(response.results, list)
    assert len(response.results) > 0

    print("[OK] 基本检索功能测试通过")


def test_result_structure():
    """测试结果结构"""
    print("\n--- 测试结果结构 ---")

    service = create_search_service()
    config = RetrievalConfig(top_k=1, min_score=0.0)

    response = service.search("测试", config)

    if response.results:
        result = response.results[0]
        print(f"  字段: {list(result.keys())}")

        # 验证包含所有必需字段
        assert "content" in result
        assert "id" in result
        assert "score" in result
        assert "metadata" in result

    print("[OK] 结果结构测试通过")


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("SearchService 检索服务测试")
    print("=" * 50)

    try:
        test_basic_search()
        test_result_structure()

        print("\n" + "=" * 50)
        print("[PASS] 所有测试通过")
        print("=" * 50)
    finally:
        cleanup_temp_dir()


if __name__ == "__main__":
    run_all_tests()
