from pathlib import Path

from .base import BaseParser,ParseResult
from .pdf_parse import PDFParser
from .html_parser import HTMLParser
from .markdown_parser import MarkdownParser
from .word_parser import WordParser

class ParserFactory:
    '''解析器工厂'''
    _parsers = {
        '.pdf':PDFParser,
        '.html':HTMLParser,
        '.md':MarkdownParser,
        '.docx':WordParser
    }
    @classmethod
    def get_parser(cls,file_path:str) -> BaseParser:
        '''
        根据文件扩展名获取对应的解析器
        Args:
            file_path (str): 文件路径
        Returns:
            BaseParser: 解析器实例
        '''
        # 获取文件扩展名
        ext = Path(file_path).suffix.lower()

        # 判断是不是支持的格式
        if ext not in cls._parsers:
            raise ValueError(f'不支持的文件类型: {ext}')
        # 获取对应的解析器
        return cls._parsers[ext]()
    

    @classmethod
    def register_parser(cls,ext:str,parser:BaseParser):
        '''
        注册解析器
        Args:
            ext (str): 文件扩展名
            parser (BaseParser): 解析器实例
        '''
        cls._parsers[ext.lower()] = parser

    @classmethod
    def supported_extensions(cls) -> list[str]:
        '''
        获取支持的扩展名
        Returns:
            list[str]: 支持的扩展名
        '''
        return list(cls._parsers.keys())
    
# 调用函数
def parse_file(file_path:str) -> ParseResult:
    '''
    自动识别文件类型并解析
    Args:
        file_path (str): 文件路径
    Returns:
        ParseResult: 解析结果
    '''
    parser = ParserFactory.get_parser(file_path)
    return parser.parse(file_path)