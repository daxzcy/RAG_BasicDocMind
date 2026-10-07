"""测试 ParserFactory 解析器工厂"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parsers import ParserFactory, parse_file


def test_supported_extensions():
    """测试支持的文件类型"""
    print("\n--- 测试支持的文件类型 ---")

    extensions = ParserFactory.supported_extensions()
    print(f"支持的文件扩展名: {extensions}")

    expected = [".pdf", ".docx", ".md", ".html"]
    for ext in expected:
        assert ext in extensions, f"缺少支持的扩展名: {ext}"

    print("[OK] 支持的文件类型正确")


def test_get_parser():
    """测试获取解析器"""
    print("\n--- 测试获取解析器 ---")

    test_cases = [
        ("test.pdf", "PDFParser"),
        ("test.docx", "WordParser"),
        ("test.md", "MarkdownParser"),
        ("test.html", "HTMLParser"),
    ]

    for file_path, expected_parser in test_cases:
        parser = ParserFactory.get_parser(file_path)
        parser_type = type(parser).__name__
        print(f"  {file_path} -> {parser_type}")
        assert parser_type == expected_parser, f"应为 {expected_parser}，实际为 {parser_type}"

    print("[OK] 获取解析器正确")


def test_unsupported_file():
    """测试不支持的文件类型"""
    print("\n--- 测试不支持的文件类型 ---")

    try:
        ParserFactory.get_parser("test.xyz")
        assert False, "应该抛出 ValueError"
    except ValueError as e:
        print(f"  捕获预期错误: {e}")
        assert "不支持的文件类型" in str(e)

    print("[OK] 不支持文件类型处理正确")


def test_case_insensitive():
    """测试扩展名大小写不敏感"""
    print("\n--- 测试扩展名大小写不敏感 ---")

    test_cases = ["test.PDF", "test.Pdf", "test.DOCX", "test.Md"]

    for file_path in test_cases:
        parser = ParserFactory.get_parser(file_path)
        print(f"  {file_path} -> {type(parser).__name__}")

    print("[OK] 大小写不敏感处理正确")


def test_register_parser():
    """测试注册自定义解析器"""
    print("\n--- 测试注册自定义解析器 ---")

    from src.parsers.base import BaseParser

    class CustomParser(BaseParser):
        def supported_extensions(self):
            return [".custom"]

        def parse(self, file_path):
            pass

        def parse_from_bytes(self, file_bytes, filename):
            pass

    # 注册前
    assert ".custom" not in ParserFactory.supported_extensions()

    # 注册
    ParserFactory.register_parser(".custom", CustomParser)
    print(f"  注册后支持的类型: {ParserFactory.supported_extensions()}")

    # 验证
    assert ".custom" in ParserFactory.supported_extensions()
    parser = ParserFactory.get_parser("test.custom")
    assert isinstance(parser, CustomParser)
    print("  自定义解析器注册成功")

    # 清理
    del ParserFactory._parsers[".custom"]

    print("[OK] 自定义解析器注册正确")


def test_parse_pdf():
    """测试解析 PDF 文件"""
    print("\n--- 测试解析 PDF 文件 ---")

    file_path = "data/test.pdf"
    if not os.path.exists(file_path):
        print(f"  [SKIP] 文件不存在: {file_path}")
        return

    result = parse_file(file_path)
    print(f"  文件: {result.filename}")
    print(f"  总页数: {result.total_pages}")
    print(f"  总块数: {result.total_chunks}")
    print(f"  表格数: {result.table_count}")
    print(f"  文本长度: {len(result.raw_text)}")

    assert result.filename == "test.pdf"
    assert len(result.raw_text) > 0

    print("[OK] PDF 解析正确")


def test_parse_markdown():
    """测试解析 Markdown 文件"""
    print("\n--- 测试解析 Markdown 文件 ---")

    file_path = "data/test.md"
    if not os.path.exists(file_path):
        print(f"  [SKIP] 文件不存在: {file_path}")
        return

    result = parse_file(file_path)
    print(f"  文件: {result.filename}")
    print(f"  文本长度: {len(result.raw_text)}")
    print(f"  内容预览: {result.raw_text[:100]}...")

    assert result.filename == "test.md"
    assert len(result.raw_text) > 0

    print("[OK] Markdown 解析正确")


def test_parse_html():
    """测试解析 HTML 文件"""
    print("\n--- 测试解析 HTML 文件 ---")

    file_path = "data/test.html"
    if not os.path.exists(file_path):
        print(f"  [SKIP] 文件不存在: {file_path}")
        return

    result = parse_file(file_path)
    print(f"  文件: {result.filename}")
    print(f"  文本长度: {len(result.raw_text)}")
    print(f"  内容预览: {result.raw_text[:100]}...")

    assert result.filename == "test.html"
    assert len(result.raw_text) > 0

    print("[OK] HTML 解析正确")


def test_parse_word():
    """测试解析 Word 文件"""
    print("\n--- 测试解析 Word 文件 ---")

    file_path = "data/test.docx"
    if not os.path.exists(file_path):
        print(f"  [SKIP] 文件不存在: {file_path}")
        return

    result = parse_file(file_path)
    print(f"  文件: {result.filename}")
    print(f"  文本长度: {len(result.raw_text)}")
    print(f"  内容预览: {result.raw_text[:100]}...")

    assert result.filename == "test.docx"
    assert len(result.raw_text) > 0

    print("[OK] Word 解析正确")


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("ParserFactory 测试")
    print("=" * 50)

    # 工厂类测试
    test_supported_extensions()
    test_get_parser()
    test_unsupported_file()
    test_case_insensitive()
    test_register_parser()

    # 实际文件解析测试
    test_parse_pdf()
    test_parse_markdown()
    test_parse_html()
    test_parse_word()

    print("\n" + "=" * 50)
    print("[PASS] 测试完成")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()
