# models/base_model.py
from abc import ABC, abstractmethod
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import BaseMessage
from typing import List, Dict, Any, Optional, Generator


class BaseModel(ABC):
    def __init__(self, model_config: Dict[str, Any], version_config: Dict[str, Any]):
        self.model_config = model_config
        self.version_config = version_config
        self.llm: Optional[BaseLanguageModel] = None
        self._initialize_llm()

    @abstractmethod
    def _initialize_llm(self) -> None:
        """初始化langchain的LLM实例"""
        pass

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], temperature: float, stream: bool = False) -> Dict[str, Any]:
        """非流式对话 - 返回统一的回复格式"""
        pass

    @abstractmethod
    def chat_stream(self, messages: List[Dict[str, str]], temperature: float) -> Generator[str, None, None]:
        """流式对话 - 返回统一的生成器"""
        pass

    def _format_response(self, content: str, content_struct: Optional[Any] = None) -> Dict[str, Any]:
        """统一响应格式"""
        return {
            'content': content,
            'content_struct': content_struct
        }

    def _convert_to_langchain_messages(self, messages: List[Dict[str, str]]) -> List[BaseMessage]:
        """将内部消息格式转换为langchain消息格式"""
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
        
        langchain_messages = []
        for msg in messages:
            role = msg['role'].lower()
            content = msg['content']
            
            if role == 'system':
                langchain_messages.append(SystemMessage(content=content))
            elif role == 'user':
                langchain_messages.append(HumanMessage(content=content))
            elif role == 'assistant':
                langchain_messages.append(AIMessage(content=content))
            # 其他角色暂时保留为HumanMessage
            else:
                langchain_messages.append(HumanMessage(content=content))
        
        return langchain_messages