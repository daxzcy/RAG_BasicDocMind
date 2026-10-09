# 解析数据 -> 向量 - > 存储向量 -> 检索向量 -> 获取结果
from typing import Optional,List,Dict,Any
import uuid

from src.embeddings.base import BaseEmbedding
from src.embeddings.chroma_store import ChromaVectorStore
from src.parsers.base import ParseResult
from src.embeddings.vector_store import Document

class DocumentStore:
    def __init__(self, 
                 embedding_model: BaseEmbedding,
                 vector_store: Optional[ChromaVectorStore]=None,
                 collection_name: str ='rag_documents',
                 ):
        self.embedding = embedding_model
        self.vector_store = vector_store or ChromaVectorStore(collection_name=collection_name)

    def add_parse_result(self, parse_result: ParseResult,namespace:str='default') -> List[str]:
        '''
        向量存储
        '''
        documents =[]
        texts_to_embed = []

        # 遍历文件内容
        for chunk in parse_result.chunks:
            doc_id = f'{namespace}_{parse_result.filename}_{chunk["index"]}'
            metadata = {
                "filename": parse_result.filename,
                "chunk_index": chunk["index"],
                "chunk_type": chunk.get('type', 'text'),
                "namespace": namespace,
                "length":chunk['length']
            }

            # 如果是表格，添加页面
            if chunk.get('type') == 'table' and 'page'in chunk:
                metadata['page'] = chunk['page']

            documents.append(
                Document(
                    id=doc_id, 
                    content=chunk['content'], 
                    metadata=metadata)
            )
            # 需要转换为向量内容
            texts_to_embed.append(chunk['content'])
        embeddings = self.embedding.embed_batch(texts_to_embed)
        # add to vector store
        doc_ids = self.vector_store.add_documents(documents,embeddings)
        return doc_ids
    def search(self, query: str, top_k: int = 5, namespace: Optional[str]=None):
        '''
        语义搜索
        Args:
            query (str): 查询内容
            top_k (int, optional): 搜索结果数量. Defaults to 5.
            namespace (Optional[str], optional): 命名空间. Defaults to None.

        '''
        # 生成向量
        query_embedding = self.embedding.embed_text(query)
        # 构造过滤条件
        filter_conditions = { "namespace": namespace} if namespace else None

        results = self.vector_store.search(query_embedding, top_k, filter_conditions)

        return [
            {
                'id':rs.document.id,
                'content':rs.document.content,
                'metadata':rs.document.metadata,
                'score':rs.score
            } for rs in results
        ]
        
    def add_documents(self, texts: list[str],metadatas:List[Dict[str,Any]],namespace:str='default') -> list[str]:
        '''
        直接追加文档向量
        '''
        documents =[]
        for i,text in enumerate(texts):
            doc_id = f'{namespace}_{uuid.uuid4().hex[:8]}'
            metadata = metadatas[i] if i<len(metadatas) else {}
            metadata['namespace'] =namespace

            documents.append(
                Document(
                    id=doc_id, 
                    content=text, 
                    metadata=metadata)
            )
        embeddings = self.embedding.embed_batch(texts)

        return self.vector_store.add_documents(documents,embeddings)
    
    def delete_document(self, filename: str, namespace: Optional[str] = None) -> int:
        '''
        删除某个文件在该集合里的全部向量
        源文件被删除、或需要重新索引时调用，避免「过时知识」继续被检索出来
        '''
        return self.vector_store.delete(where=self._file_where(filename, namespace))

    def has_document(self, filename: str, namespace: Optional[str] = None) -> bool:
        '''该集合里是否已有这个文件的向量（判断要不要写入，比按磁盘文件判重更准）'''
        return bool(self.vector_store.list_metadatas(where=self._file_where(filename, namespace)))

    def list_documents(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        '''列出集合里的文件及各自的块数'''
        where = {"namespace": namespace} if namespace else None
        counter: Dict[str, int] = {}
        for meta in self.vector_store.list_metadatas(where=where):
            name = (meta or {}).get("filename", "?")
            counter[name] = counter.get(name, 0) + 1
        return [{"filename": k, "chunks": v} for k, v in sorted(counter.items())]

    @staticmethod
    def _file_where(filename: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        '''构造"按文件名（可选命名空间）"的过滤条件'''
        if namespace:
            return {"$and": [{"filename": filename}, {"namespace": namespace}]}
        return {"filename": filename}

    def get_stats(self) -> dict[str, int]:
        '''
        获取存储统计信息
        '''
        stats = self.vector_store.get_collection_stats()
        stats['embedding_dim'] = self.embedding.get_dimension()
        stats['embedding_model'] = self.embedding.get_model_name()
        return stats