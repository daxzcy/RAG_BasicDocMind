"""测试 OpenAIEmbedding 嵌入模型"""
import sys
import os
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv


from src.embeddings.openai_embedding import OpenAIEmbedding

load_dotenv()

def cosine_similarity(vec1, vec2):
    """计算余弦相似度"""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def print_vector_stats(vector, name="向量"):
    """打印向量统计信息"""
    arr = np.array(vector)
    print(f"  {name}统计:")
    print(f"    维度: {len(vector)}")
    print(f"    最小值: {arr.min():.6f}")
    print(f"    最大值: {arr.max():.6f}")
    print(f"    均值: {arr.mean():.6f}")
    print(f"    标准差: {arr.std():.6f}")


def test_dashscope_embedding():
    """测试 DashScope 向量化"""
    print("\n" + "=" * 50)
    print("测试 DashScope 向量化")
    print("=" * 50)

    # 从环境变量获取 API Key
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("[SKIP] 未设置 DASHSCOPE_API_KEY 环境变量")
        print("请在 .env 文件中添加: DASHSCOPE_API_KEY=your-key")
        return False

    # 初始化
    print("\n初始化模型...")
    embedder = OpenAIEmbedding(
        model="text-embedding-v4",
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    print(f"  模型: {embedder.get_model_name()}")
    print(f"  向量维度: {embedder.get_dimension()}")

    # 测试1: 单条文本向量化
    print("\n--- 测试1: 单条文本向量化 ---")
    text = "人工智能是计算机科学的一个分支"
    vector = embedder.embed_text(text)
    print(f"  输入文本: {text}")
    print(f"  向量前10个值: {np.array(vector[:10]).round(6)}")
    print_vector_stats(vector)

    # 测试2: 批量文本向量化
    print("\n--- 测试2: 批量文本向量化 ---")
    texts = [
        "苹果是一种水果",
        "香蕉是黄色的水果",
        "汽车是一种交通工具"
    ]
    vectors = embedder.embed_batch(texts)

    for i, (text, vec) in enumerate(zip(texts, vectors), 1):
        print(f"\n  文本{i}: {text}")
        print(f"    向量前5个值: {np.array(vec[:5]).round(6)}")

    # 测试3: 相似度计算
    print("\n--- 测试3: 文本相似度计算 ---")
    # 苹果 vs 香蕉 (都是水果，应该相似)
    sim_fruit = cosine_similarity(vectors[0], vectors[1])
    # 苹果 vs 汽车 (不同类别，应该不相似)
    sim_cross = cosine_similarity(vectors[0], vectors[2])
    # 苹果 vs 自己 (应该完全相同)
    sim_self = cosine_similarity(vectors[0], vectors[0])

    print(f"  '苹果' vs '香蕉' (同类):     {sim_fruit:.6f}")
    print(f"  '苹果' vs '汽车' (跨类):     {sim_cross:.6f}")
    print(f"  '苹果' vs '苹果' (自身):     {sim_self:.6f}")

    # 验证
    assert abs(sim_self - 1.0) < 0.0001, "自身相似度应为1.0"
    assert sim_fruit > sim_cross, "同类相似度应大于跨类相似度"

    print("\n[OK] 所有测试通过")
    return True


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("OpenAIEmbedding 测试")
    print("=" * 50)

    success = test_dashscope_embedding()

    print("\n" + "=" * 50)
    if success:
        print("[PASS] 测试完成")
    else:
        print("[SKIP] 测试跳过")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()
