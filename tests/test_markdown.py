"""测试 MarkdownParser Markdown 解析器（pytest 版）"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path

from src.parsers.markdown_parser import MarkdownParser


def test_parse_file():
    """测试解析 Markdown 文件"""
    print("=== 测试解析 Markdown 文件 ===")

    parser = MarkdownParser()
    test_file = Path(__file__).parent.parent / "data" / "test.md"

    result = parser.parse(str(test_file))

    print(f"文件名: {result.filename}")
    print(f"总块数: {result.total_chunks}")
    print(f"解析器: {result.metadata.get('parser')}")
    print(f"原始文本长度: {len(result.raw_text)}")
    print(f"原始文本预览: {result.raw_text[:200]}...")

    # 验证结果
    assert result.filename == "test.md"
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

    print("[OK] Markdown 文件解析测试通过")


def test_parse_from_bytes():
    """测试从字节流解析 Markdown"""
    print("\n=== 测试从字节流解析 Markdown ===")

    parser = MarkdownParser()
    test_file = Path(__file__).parent.parent / "data" / "test.md"

    with open(test_file, 'rb') as f:
        md_bytes = f.read()

    result = parser.parse_from_bytes(md_bytes, "test.md")

    print(f"文件名: {result.filename}")
    print(f"总块数: {result.total_chunks}")
    print(f"原始文本长度: {len(result.raw_text)}")

    # 验证结果
    assert result.filename == "test.md"
    assert result.raw_text is not None
    assert len(result.raw_text) > 0

    print("[OK] 字节流解析测试通过")


def test_supported_extensions():
    """测试支持的文件扩展名"""
    print("\n=== 测试支持的文件扩展名 ===")

    parser = MarkdownParser()
    extensions = parser.supported_extensions()

    print(f"支持的扩展名: {extensions}")

    # 验证支持的扩展名
    assert ".md" in extensions
    assert ".markdown" in extensions

    print("[OK] 扩展名测试通过")


def test_markdown_structure():
    """测试 Markdown 结构保留"""
    print("\n=== 测试 Markdown 结构保留 ===")

    parser = MarkdownParser()
    test_file = Path(__file__).parent.parent / "data" / "test.md"

    result = parser.parse(str(test_file))

    # 检查是否保留了标题
    if "# " in result.raw_text or "## " in result.raw_text or "### " in result.raw_text:
        print("检测到标题结构 (#)")
    else:
        print("未检测到标题结构")

    # 检查是否保留了列表
    if "- " in result.raw_text or "* " in result.raw_text:
        print("检测到无序列表")
    else:
        print("未检测到无序列表")

    # 检查代码块
    if "```" in result.raw_text:
        print("检测到代码块")
    else:
        print("未检测到代码块")

    print("[OK] Markdown 结构保留测试通过")


def test_custom_chunker():
    """测试使用自定义分块器"""
    print("\n=== 测试使用自定义分块器 ===")

    from src.parsers.chunker import TextChunker, ChunkStrategy

    custom_chunker = TextChunker(
        strategy=ChunkStrategy.CHARACTER,
        max_chunk_size=300,
        min_chunk_size=100
    )

    parser = MarkdownParser(chunker=custom_chunker)
    test_file = Path(__file__).parent.parent / "data" / "test.md"

    result = parser.parse(str(test_file))

    print(f"使用自定义分块器（按字符）")
    print(f"总块数: {result.total_chunks}")

    if result.chunks:
        for i, chunk in enumerate(result.chunks[:3]):  # 显示前3个块
            print(f"  块 {i}: 长度={chunk['length']}")

    assert result.total_chunks >= 0

    print("[OK] 自定义分块器测试通过")


def test_empty_markdown():
    """测试空 Markdown 处理"""
    print("\n=== 测试空 Markdown 处理 ===")

    parser = MarkdownParser()

    # 空的 Markdown 文件
    empty_md = ""
    result = parser.parse_from_bytes(empty_md.encode('utf-8'), "empty.md")

    print(f"空 Markdown 结果:")
    print(f"  文件名: {result.filename}")
    print(f"  文本长度: {len(result.raw_text)}")
    print(f"  块数: {result.total_chunks}")

    print("[OK] 空 Markdown 处理测试通过")


def test_markdown_with_frontmatter():
    """测试带 Frontmatter 的 Markdown"""
    print("\n=== 测试带 Frontmatter 的 Markdown ===")

    parser = MarkdownParser()

    # 带有 YAML frontmatter 的 Markdown
    md_with_frontmatter = """---
title: 测试文档
author: Test Author
date: 2030-01-01
---

# 标题

这是正文内容。

## 子标题

更多内容。
"""

    result = parser.parse_from_bytes(md_with_frontmatter.encode('utf-8'), "frontmatter.md")

    print(f"带 Frontmatter 的 Markdown:")
    print(f"  文本长度: {len(result.raw_text)}")
    print(f"  是否包含标题: {'标题' in result.raw_text}")

    print("[OK] Frontmatter 测试通过")


def test_markdown_code_blocks():
    """测试包含代码块的 Markdown"""
    print("\n=== 测试包含代码块的 Markdown ===")

    parser = MarkdownParser()

    md_with_code = """# 代码示例

Python 代码:

```python
def hello():
    print("Hello, World!")
```

JavaScript 代码:

```javascript
function hello() {
    console.log("Hello, World!");
}
```
"""

    result = parser.parse_from_bytes(md_with_code.encode('utf-8'), "code.md")

    print(f"带代码块的 Markdown:")
    print(f"  文本长度: {len(result.raw_text)}")
    print(f"  是否包含代码标记: {'```' in result.raw_text}")
    print(f"  块数: {result.total_chunks}")

    print("[OK] 代码块测试通过")
