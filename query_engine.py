import logging
from typing import Optional, Dict, Any, List

from llama_index.core import VectorStoreIndex
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.prompts import PromptTemplate

import config
from document_processor import DocumentProcessor

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 默认的查询提示模板
DEFAULT_QUERY_TEMPLATE = PromptTemplate(
    """
    {system_prompt}
    
    上下文信息:
    {context_str}
    
    用户问题: {query_str}
    
    请基于上下文信息回答用户问题。如果上下文中没有足够的信息，请说明你无法回答此问题。
    回答:
    """
)

class QueryEngine:
    def __init__(self,
                 document_processor: Optional[DocumentProcessor] = None,
                 system_prompt: str = config.SYSTEM_PROMPT,
                 query_template: Optional[PromptTemplate] = None):
        """
        初始化查询引擎
        
        Args:
            document_processor: 文档处理器实例
            system_prompt: 系统提示
            query_template: 查询提示模板
        """
        self.document_processor = document_processor or DocumentProcessor()
        self.system_prompt = system_prompt
        self.query_template = query_template or DEFAULT_QUERY_TEMPLATE
        self.index = None
        self.query_engine = None
        
        # 尝试加载索引
        self._load_or_create_index()
        
    def _load_or_create_index(self) -> None:
        """加载或创建索引"""
        # 尝试加载索引
        self.index = self.document_processor.load_index()
        
        # 如果索引不存在，创建新索引
        if self.index is None:
            logger.info("索引不存在，尝试创建新索引")
            self.index = self.document_processor.process_documents()
            
        if self.index is not None:
            self._create_query_engine()
    
    def _create_query_engine(self) -> None:
        """创建查询引擎"""
        if self.index is None:
            logger.warning("尝试创建查询引擎，但索引不存在")
            return
        
        # 创建检索器
        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=config.TOP_K,
        )
        
        # 创建响应合成器
        response_synthesizer = get_response_synthesizer(
            response_mode="compact",
            text_qa_template=self.query_template,
        )
        
        # 创建查询引擎
        self.query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
        )
        
        logger.info("查询引擎创建成功")
    
    def update_prompt(self, system_prompt: Optional[str] = None, 
                     query_template: Optional[PromptTemplate] = None) -> None:
        """
        更新提示词
        
        Args:
            system_prompt: 新的系统提示
            query_template: 新的查询提示模板
        """
        if system_prompt is not None:
            self.system_prompt = system_prompt
            
        if query_template is not None:
            self.query_template = query_template
            
        # 重新创建查询引擎以应用新提示
        self._create_query_engine()
        logger.info("提示词已更新")
    
    def query(self, query_text: str) -> str:
        """
        查询知识库
        
        Args:
            query_text: 查询文本
            
        Returns:
            查询结果
        """
        if self.query_engine is None:
            logger.error("查询引擎不可用")
            return "系统错误：查询引擎不可用。请确保已正确加载或创建索引。"
        
        logger.info(f"查询: {query_text}")
        
        # 执行查询
        response = self.query_engine.query(
            query_text,
            similarity_cutoff=config.SIMILARITY_THRESHOLD
        )
        
        # 如果没有找到相关内容
        if not response.source_nodes or len(response.source_nodes) == 0:
            return "抱歉，我在知识库中没有找到与您问题相关的信息。"
        
        return str(response) 