import re
from typing import List

class TextCleaner:
    '''
    文本清洗器
    '''
    def __init__(self,custom_patterns:List[str] = None):
        '''
        Args:
            custom_patterns (List[str], optional): 自定义正则表达式列表. 
        '''
        # 常见的无意义模式
        self.patterns_to_remove = [
            r'^\s*\d+\s*$',               # 单独的页码
            r'^\s*[-=_]+\s*$',            # 分隔线
            r'^\s*第\s*\d+\s*页\s*$',     # 中文页码标记
            r'^\s*Page\s*\d+\s*$',        # 英文页码
            r'^\s*\d+\s*/\s*\d+\s*$',     # 页码格式：1/10
        ]

        # 添加自定义模式
        if custom_patterns:
            self.patterns_to_remove.extend(custom_patterns)
    def clean(self,text:str) -> str:
        '''
        清洗文版，去除无意义内容
        Args:
            text (str): 文本
        Returns:
            str: 清洗后的文本
        '''
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            # 去除空白行
            line = line.strip()
            if not line:
                continue
            # 匹配自定义模式
            for pattern in self.patterns_to_remove:
                if re.match(pattern,line):
                    break
            else:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)
    def normalize_whitespace(self,text:str) -> str:
        '''
        去除多余的空白字符
        -  合并多个空格
        -  合并多个换行
        -  去除行首行尾的空白字符
        Args:
            text (str): 输入文本
        Returns:
            str: 处理后的文本
        '''
        # 合并多个空格
        text = re.sub(r'\s+', ' ', text)
        # 合并多个换行
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        return text.strip()
    def remove_extra_chars(self,text:str) -> str:
        '''
        去除多余的字符
        Args:
            text (str): 输入文本
        Returns:
            str: 处理后的文本
        '''
        # 去除多余的字符
        text = re.sub(r'[^\u4e00-\u9fa5]', '', text)
        return text
    
    def full_clean(self,text:str) -> str:
        '''
        文本清理
        Args:
            text (str): 输入文本
        Returns:
            str: 处理后的文本
        '''
        text = self.clean(text)
        text = self.normalize_whitespace(text)
        text = self.remove_extra_chars(text)
        return text