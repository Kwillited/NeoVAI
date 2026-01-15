# app/models/ollama_model.py
from app.models.base_model import BaseModel
import json
from typing import Dict, Any, Generator, List


class OllamaModel(BaseModel):
    def _initialize_llm(self) -> None:
        """初始化langchain的Ollama LLM实例"""
        from langchain_ollama import ChatOllama
        
        # 检查多个可能的版本名称字段，解决'name'错误问题
        selected_version = self.version_config.get('version_name') or self.version_config.get('custom_name') or self.version_config.get('name')
        base_url = self.version_config.get('api_base_url', self.version_config.get('base_url', 'http://localhost:11434'))
        
        # 创建ChatOllama实例
        self.llm = ChatOllama(
            model=selected_version,
            base_url=base_url,
            temperature=0.7,  # 默认温度，会在调用时被覆盖
            timeout=180,  # 超时设置
            think_thought=True
        )

    def chat(self, messages: List[Dict[str, str]], temperature: float, stream: bool = False) -> Dict[str, Any]:
        """非流式调用Ollama API (使用langchain)"""
        
        # 转换消息格式
        langchain_messages = self._convert_to_langchain_messages(messages)
        
        # 打印转换后的langchain_messages
        print(f"[Ollama Model] 转换后的langchain_messages: {langchain_messages}")
        
        # 更新LLM温度参数
        self.llm.temperature = temperature
        
        # 调用LLM
        response = self.llm.invoke(langchain_messages)
        
        # 提取回复内容
        content = response.content
        return self._format_response(content)

    def chat_stream(self, messages: List[Dict[str, str]], temperature: float) -> Generator[str, None, None]:
        """流式调用Ollama API (使用langchain)"""
        
        # 转换消息格式
        langchain_messages = self._convert_to_langchain_messages(messages)
        
        # 打印转换后的langchain_messages
        print(f"[Ollama Model] 转换后的langchain_messages: {langchain_messages}")
        
        # 更新LLM温度参数
        self.llm.temperature = temperature
        
        # 使用流式调用
        chunks = self.llm.stream(langchain_messages)
        
        # 处理流式响应
        for chunk in chunks:
            if hasattr(chunk, 'content') and chunk.content:
                response_data = {
                    'chunk': chunk.content,
                    'content_struct': None
                }
                yield f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'
        
        # 结束流式传输
        response_data = {'done': True}
        yield f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'