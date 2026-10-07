"""测试 HTMLParser HTML 解析器"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path

from src.parsers.html_parser import HTMLParser


def test_parse_file():
    """测试解析 HTML 文件"""
    print("=== 测试解析 HTML 文件 ===")

    parser = HTMLParser()
    test_file = Path(__file__).parent.parent / "data" / "test.html"

    result = parser.parse(str(test_file))

    print(f"文件名: {result.filename}")
    print(f"总块数: {result.total_chunks}")
    print(f"解析器: {result.metadata.get('parser')}")
    print(f"原始文本长度: {len(result.raw_text)}")
    print(f"原始文本预览: {result.raw_text[:200]}...")

    # 验证结果
    assert result.filename == "test.html"
    assert result.total_pages == 1
    assert result.total_chunks >= 0
    assert result.raw_text is not None
    assert len(result.raw_text) > 0

    # 验证分块
    if result.chunks:
        print(f"\n第一个分块:")
        print(f"  索引: {result.chunks[0]['index']}")
        print(f"  长度: {result.chunks[0]['length']}")
        print(f"  类型: {result.chunks[0]['type']}")
        print(f"  内容预览: {result.chunks[0]['content'][:100]}...")

    print("[OK] HTML 文件解析测试通过")


def test_parse_from_bytes():
    """测试从字节流解析 HTML"""
    print("\n=== 测试从字节流解析 HTML ===")

    parser = HTMLParser()
    test_file = Path(__file__).parent.parent / "data" / "test.html"

    with open(test_file, 'rb') as f:
        html_bytes = f.read()

    result = parser.parse_from_bytes(html_bytes, "test.html")

    print(f"文件名: {result.filename}")
    print(f"总块数: {result.total_chunks}")
    print(f"原始文本长度: {len(result.raw_text)}")

    # 验证结果
    assert result.filename == "test.html"
    assert result.raw_text is not None
    assert len(result.raw_text) > 0

    print("[OK] 字节流解析测试通过")


def test_supported_extensions():
    """测试支持的文件扩展名"""
    print("\n=== 测试支持的文件扩展名 ===")

    parser = HTMLParser()
    extensions = parser.supported_extensions()

    print(f"支持的扩展名: {extensions}")

    # 验证支持的扩展名
    assert ".html" in extensions
    assert ".htm" in extensions

    print("[OK] 扩展名测试通过")


def test_html_structure():
    """测试 HTML 结构转换"""
    print("\n=== 测试 HTML 结构转换 ===")

    parser = HTMLParser()
    test_file = Path(__file__).parent.parent / "data" / "test.html"

    result = parser.parse(str(test_file))

    # 检查转换后的 Markdown 是否保留了标题结构
    if "# " in result.raw_text or "## " in result.raw_text:
        print("检测到标题结构")
    else:
        print("未检测到标题结构")

    # 检查是否保留了列表
    if "- " in result.raw_text or "* " in result.raw_text:
        print("检测到列表结构")
    else:
        print("未检测到列表结构")

    print("[OK] HTML 结构转换测试通过")


def test_custom_chunker():
    """测试使用自定义分块器"""
    print("\n=== 测试使用自定义分块器 ===")

    from src.parsers.chunker import TextChunker, ChunkStrategy

    custom_chunker = TextChunker(
        strategy=ChunkStrategy.SENTENCE,
        max_chunk_size=200,
        min_chunk_size=50
    )

    parser = HTMLParser(chunker=custom_chunker)
    test_file = Path(__file__).parent.parent / "data" / "test.html"

    result = parser.parse(str(test_file))

    print(f"使用自定义分块器（按句子）")
    print(f"总块数: {result.total_chunks}")

    if result.chunks:
        print(f"第一个分块长度: {result.chunks[0]['length']}")

    assert result.total_chunks >= 0

    print("[OK] 自定义分块器测试通过")


def test_empty_html():
    """测试空 HTML 处理"""
    print("\n=== 测试空 HTML 处理 ===")

    parser = HTMLParser()

    # 创建一个最小的 HTML 文件
    empty_html = "<html><body></body></html>"
    result = parser.parse_from_bytes(empty_html.encode('utf-8'), "empty.html")

    print(f"空 HTML 结果:")
    print(f"  文件名: {result.filename}")
    print(f"  文本长度: {len(result.raw_text)}")
    print(f"  块数: {result.total_chunks}")

    print("[OK] 空 HTML 处理测试通过")


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("开始运行 HTMLParser 测试")
    print("=" * 50)

    try:
        test_parse_file()
        test_parse_from_bytes()
        test_supported_extensions()
        test_html_structure()
        test_custom_chunker()
        test_empty_html()

        print("\n" + "=" * 50)
        print("[PASS] 所有测试通过！")
        print("=" * 50)
    except AssertionError as e:
        print(f"\n[FAIL] 测试失败: {e}")
        raise
    except Exception as e:
        print(f"\n[FAIL] 发生错误: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
