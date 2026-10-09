"""回归测试：上下文预算必须与输出长度解耦（第 0005 课修掉的缺陷）

原始缺陷：`generate_answer` 里写成 `format_context(results, max_token)`，
把「模型最大输出 token 数」当成了「拼进提示词的上下文字符上限」。
后果：调用方只要调小 max_token（比如为了短答案设成 200），检索到的上下文就会被
砍到 200 字符甚至 0 字符，模型拿不到资料，只能回答“不知道”。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.llm.rag import format_context, generate_answer


class FakeLLM:
    """假的 LLM：只记录收到的提示词，不发网络请求。"""

    def __init__(self):
        self.last_prompt = None

    def generate(self, messages, temperature=0.7, max_token=2000):
        self.last_prompt = messages[-1]["content"]
        return {
            "content": "假答案",
            "finish_reason": "stop",
            "token_used": {"total": 1, "prompt": 1, "completion": 0},
            "model": "fake",
        }


def make_results():
    return [
        {"content": "A" * 900, "doc_id": "1", "score": 0.9},
        {"content": "B" * 900, "doc_id": "2", "score": 0.8},
        {"content": "C" * 900, "doc_id": "3", "score": 0.7},
    ]


def test_format_context_respects_char_budget():
    """format_context 的第二个参数是字符上限，不是 token 数。"""
    ctx = format_context(make_results(), 1000)
    assert len(ctx) == 900, f"应只装得下 1 段 900 字，实际 {len(ctx)}"

    ctx = format_context(make_results(), 2000)
    assert len(ctx) == 1802, f"应装得下 2 段（900+2+900），实际 {len(ctx)}"


def test_context_budget_is_independent_of_max_token():
    """核心回归：把 max_token 调到很小，上下文不应被砍掉。"""
    llm = FakeLLM()
    result = generate_answer(
        llm=llm,
        question="测试问题",
        results=make_results(),
        temperature=0.7,
        max_token=50,             # 只想要短答案
        max_context_chars=2000,   # 但仍然要两段资料
    )
    assert len(result["context"]) == 1802, f"上下文被 max_token 影响了：{len(result['context'])}"
    assert llm.last_prompt and result["context"] in llm.last_prompt


def test_context_budget_can_be_tightened():
    """显式收紧上下文预算时，只保留能装下的片段（这里是 1 段）。"""
    llm = FakeLLM()
    result = generate_answer(
        llm=llm,
        question="测试问题",
        results=make_results(),
        max_context_chars=1000,
    )
    assert len(result["context"]) == 900, f"实际 {len(result['context'])}"


def test_empty_results_short_circuit():
    """没有检索结果时不调用模型，直接回答“不知道”。"""
    llm = FakeLLM()
    result = generate_answer(llm=llm, question="测试问题", results=[])
    assert result["answer"] == "我不知道"
    assert llm.last_prompt is None, "不应在没有上下文时调用模型"


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  [OK] {name}")
    print("上下文预算回归测试全部通过")
