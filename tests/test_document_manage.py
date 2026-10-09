"""回归测试：文档删除 / 清单 / 入库判重（第 0007 课）

覆盖三个真实问题：
1. 语料被删除后，向量仍留在库里（过时知识）——需要显式删除接口。
2. 项目原本没有删除/更新文档的接口。
3. 上传接口按「磁盘上有没有同样的字节」判重，导致把同一份文件存进第二个集合时
   被静默跳过（本测试用 has_document 的集合级判重替代它）。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# 必须在导入 src.* / sentence_transformers 之前加载 .env：
# 否则 HF_HUB_OFFLINE / HF_ENDPOINT 不生效，模型加载会去连被墙的 huggingface.co
#（重试约 60 秒，最后退化成一个随机初始化的模型，测试结果完全不可信）。
from dotenv import load_dotenv  # noqa: E402

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from src.database.document_store import DocumentStore  # noqa: E402
from src.embeddings.local_embedding import LocalEmbedding  # noqa: E402
from src.parsers import parse_file  # noqa: E402

COLLECTION = "test_document_manage"
README = Path(__file__).resolve().parent.parent / "README.md"


def _store() -> DocumentStore:
    embedding = LocalEmbedding(model_name="BAAI/bge-small-zh-v1.5", device="cpu")
    return DocumentStore(embedding_model=embedding, collection_name=COLLECTION)


def test_delete_removes_vectors_and_unblocks_reindex():
    store = _store()
    # 从干净状态开始
    store.vector_store.clear()

    parsed = parse_file(str(README))
    ids = store.add_parse_result(parsed, namespace=COLLECTION)
    assert len(ids) == parsed.total_chunks > 0

    # 清单里能看到这个文件，且判重为真
    docs = store.list_documents(namespace=COLLECTION)
    assert docs == [{"filename": README.name, "chunks": parsed.total_chunks}], docs
    assert store.has_document(README.name, namespace=COLLECTION) is True

    # 检索得到结果
    hits = store.search("怎么启动服务", top_k=3)
    assert hits, "索引后应能检索到内容"

    # 删除：返回删除条数，向量与清单都清空
    deleted = store.delete_document(README.name, namespace=COLLECTION)
    assert deleted == parsed.total_chunks, deleted
    assert store.search("怎么启动服务", top_k=3) == []
    assert store.has_document(README.name, namespace=COLLECTION) is False
    assert store.list_documents(namespace=COLLECTION) == []

    # 删除后可以重新入库（这是「更新文档」的正确姿势：先删后加）
    ids2 = store.add_parse_result(parsed, namespace=COLLECTION)
    assert len(ids2) == parsed.total_chunks
    store.vector_store.clear()


def test_delete_missing_document_returns_zero():
    store = _store()
    store.vector_store.clear()
    assert store.delete_document("不存在的文件.md", namespace=COLLECTION) == 0


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  [OK] {name}")
    print("文档管理回归测试全部通过")
