import os
from pathlib import Path
import time
from typing import Optional
import hashlib

from fastapi import APIRouter,UploadFile,File,HTTPException,Form

from src.api.config import settings
from src.parsers import ParserFactory,parse_file
from src.database.document_store import DocumentStore
from src.api.deps import get_embedding_model


router = APIRouter(prefix='/document',tags=['文件解析'])

def _get_file_hash(file_bytes:bytes) -> str:
    '''计算文件哈希值'''
    return hashlib.sha256(file_bytes).hexdigest()
def _save_file_with_hash(file_bytes:bytes,original_filename:str,upload_dir:Path) ->tuple[str,bool]:
    '''
    保存文件，用哈希值作为文件名
    返回：文件路径，是否已存在 True表示已存在 False表示不存在
    '''
    file_hash = _get_file_hash(file_bytes)
    ext = Path(original_filename).suffix.lower()  # 文件扩展名
    hash_name = f'{file_hash[:16]}{ext}'  # 文件名
    file_path = upload_dir/hash_name  # 文件路径

    # 检查文件是否存在
    if file_path.exists():
        return str(file_path),True
    # 不存在
    with open(file_path,'wb') as f:
        f.write(file_bytes)

    return str(file_path),False
def _generate_filename(filename:str) -> str:
    ''' 生成文件名 '''
    name,ext = os.path.splitext(filename)
    timpestamp = time.time()
    return f"{name}_{timpestamp}{ext}"

@router.post('/upload')
async def upload_document(
    file:UploadFile=File(...),
    collection_name:Optional[str] = Form(None),
    ):
    '''
    上传并解析文档
    支持的格式：PDF、DOCX、MD、HTML
    '''

    ext = os.path.splitext(file.filename or "")[-1].lower()
    file_bytes = await file.read()
    # 判断文件大小
    if len(file_bytes) > settings.MAX_FILE_SIZE:
        size_mb = settings.MAX_FILE_SIZE / 1024 / 1024
        raise HTTPException(status_code=400,detail=f"文件过大,最大允许{size_mb}MB")
    # 判断文件格式
    if ext not in ParserFactory.supported_extensions():
        raise HTTPException(status_code=400,detail=f"不支持的文件格式{ext}")
    
    # 数据保存
    upload_dir = _ensure_upload_dir()
    file_path, is_duplicate =  _save_file_with_hash(file_bytes,file.filename,upload_dir)

    try:
        # 获取解析器
        parser = ParserFactory.get_parser(file.filename)
        # 解析
        rs = parser.parse_from_bytes(file_bytes,file.filename)
        # 保存到向量数据库
        if collection_name and not is_duplicate:  # 存储到向量数据库
            # 创建向量模型
            embedding_model = get_embedding_model()
            # 创建向量存储实例
            store = DocumentStore(embedding_model=embedding_model,collection_name=collection_name)
            # 保存数据
            doc_ids = store.add_parse_result(rs,namespace=collection_name)
            return {
                'success': True,
                'filename':rs.filename,
                'stored':True,
                'doc_count':len(doc_ids),
                'duplicate':False
            }
        elif is_duplicate:  # 忽略重复文件
            return {
                'success': True,
                'filename':rs.filename,
                'stored':False,
                'doc_count':0,
                'duplicate':True,
                'message':'文件已存在,跳过重复处理'
            }
        else:
            return {
                "success": True,
                "filename": rs.filename,
                'stored':False,
                'doc_count':rs.total_chunks,
                'duplicate':False
            }
    except Exception as e:
        raise HTTPException(status_code=500,detail=f'文件解析失败:{str(e)}')

from pydantic import BaseModel
class ParsePathRequest(BaseModel):
    file_path: str

def _ensure_upload_dir():
    ''' 确保上传目录存在 '''
    upload_dir = Path(settings.UPLOAD_DIR)  # 获取上传目录
    upload_dir.mkdir(parents=True,exist_ok=True)  # 创建目录
    return upload_dir
@router.post('/parse-path')
async def parse_document_by_path(body:ParsePathRequest):
    ''' 按服务器本地路径解析文档（用于已有文件或批处理）'''

    path = body.file_path
    # 判断path是否是完整路径
    if os.path.dirname(path):
        target_path = path
    else:
        # 只传递了文件的名称
        upload_dir = _ensure_upload_dir()
        target_path = str(upload_dir/path)

    # 判断文件是否存在
    if not os.path.isfile(target_path):
        raise HTTPException(status_code=400,detail=f"文件不存在:{target_path}")
    
    try:
        rs = parse_file(target_path)
        return {
            "message": "文档处理成功",
            "filename": rs.filename,
            "total_pages": rs.total_pages,
            "chunks_count": rs.total_chunks,
            "tables_count": rs.table_count,
            "chunks": rs.chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=f'文件解析失败:{str(e)}')
    
@router.get('/supported-formats')
async def supported_formats():
    ''' 获取支持的格式列表 '''
    return {
        "formats": ParserFactory.supported_extensions()
    }