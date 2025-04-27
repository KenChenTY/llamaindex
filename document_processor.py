import os
import logging
from typing import List, Optional
from pathlib import Path

from llama_index.core import Settings, SimpleDirectoryReader, Document
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.llms.openai import OpenAI

import config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, 
                 documents_dir: str = config.DOCUMENTS_DIR,
                 vector_store_dir: str = config.VECTOR_STORE_DIR):
        """
        初始化文档处理器
        
        Args:
            documents_dir: 文档目录路径
            vector_store_dir: 向量存储目录路径
        """
        self.documents_dir = documents_dir
        self.vector_store_dir = vector_store_dir
        
        # 确保目录存在
        os.makedirs(documents_dir, exist_ok=True)
        os.makedirs(vector_store_dir, exist_ok=True)
        
        # 设置LlamaIndex默认参数
        Settings.llm = OpenAI(model=config.MODEL_NAME, api_key=config.OPENAI_API_KEY)
        
    def load_documents(self, directory: Optional[str] = None) -> List[Document]:
        """
        从指定目录加载文档
        
        Args:
            directory: 要加载的目录路径，默认为配置的文档目录
            
        Returns:
            Document列表
        """
        if directory is None:
            directory = self.documents_dir
            
        logger.info(f"从 {directory} 加载文档")
        
        if not os.path.exists(directory) or not os.listdir(directory):
            logger.warning(f"目录 {directory} 不存在或为空")
            return []
        
        reader = SimpleDirectoryReader(directory)
        documents = reader.load_data()
        logger.info(f"已加载 {len(documents)} 个文档")
        return documents
    
    def process_documents(self, documents: List[Document] = None) -> VectorStoreIndex:
        """
        处理文档并创建向量索引
        
        Args:
            documents: 要处理的文档列表，如果为None则从默认目录加载
            
        Returns:
            创建的向量索引
        """
        if documents is None:
            documents = self.load_documents()
            
        if not documents:
            logger.warning("没有文档可处理")
            return None
        
        logger.info("开始向量化文档...")
        
        # 创建FAISS向量存储
        vector_store = FaissVectorStore(self.vector_store_dir)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # 创建索引
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
        )
        
        # 持久化索引
        index.storage_context.persist()
        logger.info(f"索引已创建并保存到 {self.vector_store_dir}")
        
        return index
    
    def load_index(self) -> Optional[VectorStoreIndex]:
        """
        加载现有的向量索引
        
        Returns:
            加载的向量索引，如果不存在则返回None
        """
        if not os.path.exists(self.vector_store_dir) or not os.listdir(self.vector_store_dir):
            logger.warning(f"向量存储目录 {self.vector_store_dir} 不存在或为空")
            return None
        
        logger.info(f"从 {self.vector_store_dir} 加载索引")
        
        # 加载FAISS向量存储
        vector_store = FaissVectorStore.from_persist_dir(self.vector_store_dir)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # 加载索引
        index = VectorStoreIndex.from_vector_store(
            vector_store,
            storage_context=storage_context,
        )
        
        logger.info("索引加载成功")
        return index 