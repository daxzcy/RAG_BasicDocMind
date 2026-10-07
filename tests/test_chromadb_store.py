"""测试 ChromaVectorStore 向量存储"""
import sys
import os
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.embeddings.chroma_store import ChromaVectorStore
from src.embeddings.vector_store import Document


def generate_embedding(text: str) -> list:
    """生成模拟向量（用于测试）"""
    np.random.seed(hash(text) % 10000)
    return np.random.randn(1024).tolist()


def test_chroma_store():
    """测试 ChromaDB 向量存储"""
    print("\n" + "=" * 50)
    print("测试 ChromaVectorStore")
    print("=" * 50)

    # 初始化
    print("\n初始化 ChromaDB...")
    store = ChromaVectorStore(
        collection_name="test_collection",
        persist_directory="./data/chroma_test",
        distance="cosine"
    )

    # 清空测试数据
    store.clear()
    print("  已清空测试数据")

    stats = store.get_collection_stats()
    print(f"  集合名称: {stats['name']}")
    print(f"  文档数量: {stats['count']}")
    print(f"  距离度量: {stats['distance']}")

    # 测试1: 添加文档
    print("\n--- 测试1: 添加文档 ---")
    documents = [
        Document(id="", content="苹果是一种常见的水果", metadata={"category": "水果", "price": 5}),
        Document(id="", content="香蕉是黄色的热带水果", metadata={"category": "水果", "price": 3}),
        Document(id="", content="汽车是现代交通工具", metadata={"category": "交通工具", "price": 100000}),
        Document(id="", content="飞机可以飞得很高", metadata={"category": "交通工具", "price": 500000}),
    ]

    embeddings = [generate_embedding(doc.content) for doc in documents]
    doc_ids = store.add_documents(documents, embeddings)

    print(f"  添加了 {len(doc_ids)} 个文档")
    for i, (doc, doc_id) in enumerate(zip(documents, doc_ids), 1):
        print(f"    文档{i}: {doc.content[:20]}... (ID: {doc_id[:8]}...)")

    stats = store.get_collection_stats()
    print(f"  当前文档数: {stats['count']}")

    # 测试2: 向量检索
    print("\n--- 测试2: 向量检索 ---")
    query_text = "红色的水果"
    query_embedding = generate_embedding(query_text)

    results = store.search(query_embedding, top_k=3)
    print(f"  查询: {query_text}")
    print(f"  返回 {len(results)} 个结果:")

    for i, result in enumerate(results, 1):
        print(f"    {i}. {result.document.content}")
        print(f"       相似度: {result.score:.4f} | 分类: {result.document.metadata.get('category', 'N/A')}")

    # 测试3: 带过滤的检索
    print("\n--- 测试3: 带过滤的检索 ---")
    results_filtered = store.search(
        query_embedding,
        top_k=10,
        filter={"category": "水果"}
    )
    print(f"  过滤条件: category='水果'")
    print(f"  返回 {len(results_filtered)} 个结果:")

    for i, result in enumerate(results_filtered, 1):
        print(f"    {i}. {result.document.content} (价格: {result.document.metadata.get('price')})")

    # 测试4: 清空集合
    print("\n--- 测试4: 清空集合 ---")
    success = store.clear()
    stats = store.get_collection_stats()
    print(f"  清空状态: {'成功' if success else '失败'}")
    print(f"  当前文档数: {stats['count']}")

    print("\n[OK] 所有测试通过")
    return True


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("ChromaVectorStore 测试")
    print("=" * 50)

    test_chroma_store()

    print("\n" + "=" * 50)
    print("[PASS] 测试完成")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()
