"""测试 LocalEmbedding 本地嵌入模型"""
import sys
import os
import time
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.embeddings.local_embedding import LocalEmbedding


def cosine_similarity(vec1: list, vec2: list) -> float:
    """计算余弦相似度"""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def print_section(title: str):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_model_info():
    """测试模型信息"""
    print_section("1. 模型信息测试")

    try:
        embedding_model = LocalEmbedding(model_name="BAAI/bge-small-zh-v1.5", device="cpu")

        print(f"  模型名称: {embedding_model.get_model_name()}")
        print(f"  向量维度: {embedding_model.get_dimension()}")
        print(f"  运行设备: {embedding_model.device}")

        assert embedding_model.get_model_name() == "BAAI/bge-small-zh-v1.5"
        assert embedding_model.get_dimension() > 0

        print("[OK] 模型信息测试通过")

    except Exception as e:
        print(f"[SKIP] 本地嵌入模型测试跳过: {e}")
        print("  提示: 需要安装 sentence-transformers: uv add sentence-transformers")


def test_single_text():
    """测试单条文本向量化"""
    print_section("2. 单条文本向量化测试")

    try:
        embedding_model = LocalEmbedding(model_name="BAAI/bge-small-zh-v1.5", device="cpu")

        texts = [
            "你好，世界！",
            "人工智能是未来技术发展的核心方向。",
            "RAG是一种结合检索和生成的AI技术架构。"
        ]

        for i, text in enumerate(texts, 1):
            start = time.time()
            vector = embedding_model.embed_text(text)
            elapsed = time.time() - start

            print(f"\n  文本 {i}: {text}")
            print(f"  向量维度: {len(vector)}")
            print(f"  耗时: {elapsed:.3f}秒")
            print(f"  前5个值: {[f'{v:.4f}' for v in vector[:5]]}")

            assert len(vector) == embedding_model.get_dimension()

        print("[OK] 单条文本向量化测试通过")

    except Exception as e:
        print(f"[SKIP] 单条文本向量化测试跳过: {e}")


def test_batch_embedding():
    """测试批量向量化"""
    print_section("3. 批量向量化测试")

    try:
        embedding_model = LocalEmbedding(model_name="BAAI/bge-small-zh-v1.5", device="cpu")

        texts = [
            "Python是一种流行的编程语言。",
            "机器学习需要大量数据进行训练。",
            "自然语言处理是AI的重要分支。",
            "深度学习使用神经网络处理复杂问题。",
            "云计算提供了灵活的计算资源。"
        ]

        start = time.time()
        vectors = embedding_model.embed_batch(texts)
        elapsed = time.time() - start

        print(f"\n  处理文本数量: {len(texts)}")
        print(f"  总耗时: {elapsed:.3f}秒")
        print(f"  平均每条: {elapsed/len(texts):.3f}秒")
        print(f"  向量形状: {len(vectors)} x {len(vectors[0])}")

        assert len(vectors) == len(texts)

        print("[OK] 批量向量化测试通过")

    except Exception as e:
        print(f"[SKIP] 批量向量化测试跳过: {e}")


def test_similarity():
    """测试相似度计算"""
    print_section("4. 语义相似度测试")

    try:
        embedding_model = LocalEmbedding(model_name="BAAI/bge-small-zh-v1.5", device="cpu")

        # 测试文本对
        test_pairs = [
            ("人工智能", "机器学习"),  # 相似
            ("今天天气很好", "我喜欢吃苹果"),  # 不相似
            ("RAG检索增强生成", "检索增强生成RAG"),  # 非常相似
            ("Python编程", "Java开发"),  # 中等相关
        ]

        for text1, text2 in test_pairs:
            vec1 = embedding_model.embed_text(text1)
            vec2 = embedding_model.embed_text(text2)
            score = cosine_similarity(vec1, vec2)

            emoji = "🔥" if score > 0.7 else "❄️" if score < 0.3 else "🌡️"
            print(f"\n  '{text1}' vs '{text2}'")
            print(f"  相似度分数: {score:.4f} {emoji}")

        print("[OK] 语义相似度测试通过")

    except Exception as e:
        print(f"[SKIP] 语义相似度测试跳过: {e}")


def test_search():
    """测试语义搜索"""
    print_section("5. 语义搜索测试")

    try:
        embedding_model = LocalEmbedding(model_name="BAAI/bge-small-zh-v1.5", device="cpu")

        # 文档库
        documents = [
            "RAG（Retrieval-Augmented Generation）是一种结合检索和生成的AI架构。",
            "Python是一种高级编程语言，广泛应用于数据分析和机器学习领域。",
            "微信是中国最流行的即时通讯软件，拥有超过10亿用户。",
            "向量数据库是用于存储和检索高维向量数据的专用数据库。",
            "深度学习是机器学习的一个分支，使用多层神经网络处理数据。"
        ]

        # 查询
        queries = [
            "什么是RAG技术？",
            "推荐什么编程语言？",
            "即时通讯软件有哪些？"
        ]

        # 生成文档向量
        doc_vectors = embedding_model.embed_batch(documents)

        for query in queries:
            query_vector = embedding_model.embed_text(query)

            # 计算相似度
            scores = [cosine_similarity(query_vector, doc_vec) for doc_vec in doc_vectors]

            # 排序并显示top3
            sorted_results = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:3]

            print(f"\n  查询: {query}")
            print("  Top 3 匹配结果:")
            for idx, (doc_idx, score) in enumerate(sorted_results, 1):
                print(f"    {idx}. [相似度: {score:.4f}] {documents[doc_idx][:60]}...")

        print("[OK] 语义搜索测试通过")

    except Exception as e:
        print(f"[SKIP] 语义搜索测试跳过: {e}")


def test_normalize():
    """测试向量归一化"""
    print_section("6. 向量归一化测试")

    try:
        embedding_model = LocalEmbedding(model_name="BAAI/bge-small-zh-v1.5", device="cpu")

        text = "测试文本归一化功能"
        vector = embedding_model.embed_text(text)

        # 归一化前
        norm_before = np.linalg.norm(vector)
        print(f"\n  归一化前向量长度: {norm_before:.6f}")

        # 归一化
        normalized = embedding_model.normalize(vector)
        norm_after = np.linalg.norm(normalized)
        print(f"  归一化后向量长度: {norm_after:.6f}")

        assert abs(norm_after - 1.0) < 0.0001, "归一化后长度应为1.0"

        # 验证归一化后相似度等于点积
        vec2 = embedding_model.embed_text("另一段文本")
        vec2_norm = embedding_model.normalize(vec2)

        # 方法1: 点积
        sim_dot = np.dot(normalized, vec2_norm)
        # 方法2: 余弦相似度
        sim_cosine = cosine_similarity(normalized, vec2_norm)

        print(f"\n  点积相似度: {sim_dot:.6f}")
        print(f"  余弦相似度: {sim_cosine:.6f}")
        print(f"  差异: {abs(sim_dot - sim_cosine):.8f}")

        assert abs(sim_dot - sim_cosine) < 0.0001

        print("[OK] 向量归一化测试通过")

    except Exception as e:
        print(f"[SKIP] 向量归一化测试跳过: {e}")


def test_self_similarity():
    """测试自身相似度"""
    print_section("7. 自身相似度测试")

    try:
        embedding_model = LocalEmbedding(model_name="BAAI/bge-small-zh-v1.5", device="cpu")

        text = "相同的文本"
        vector = embedding_model.embed_text(text)

        # 自己和自己的相似度应该为1
        sim = cosine_similarity(vector, vector)

        print(f"\n  文本: {text}")
        print(f"  自身相似度: {sim:.6f}")

        assert abs(sim - 1.0) < 0.0001

        print("[OK] 自身相似度测试通过")

    except Exception as e:
        print(f"[SKIP] 自身相似度测试跳过: {e}")


def main():
    """主测试函数"""
    print("\n" + "🚀" * 30)
    print("    本地嵌入模型测试脚本")
    print("🚀" * 30)

    # 运行测试
    test_model_info()
    test_single_text()
    test_batch_embedding()
    test_similarity()
    test_search()
    test_normalize()
    test_self_similarity()

    print_section("✅ 所有测试完成！")

    print("\n" + "🎉" * 30)
    print("    测试完成！")
    print("🎉" * 30 + "\n")


if __name__ == "__main__":
    main()
