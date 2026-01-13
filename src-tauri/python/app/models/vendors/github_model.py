# app/models/github_model.py
from app.models.base_model import BaseModel
from langchain_openai import ChatOpenAI
import json
from typing import Dict, Any, Generator, List


class GitHubModel(BaseModel):
    def _initialize_llm(self) -> None:
        """初始化langchain的OpenAI兼容LLM实例"""
        # 检查多个可能的版本名称字段，确保兼容性
        selected_version_id = self.version_config.get('name') or \
                             self.version_config.get('version_name') or \
                             self.version_config.get('custom_name') or \
                             'openai/gpt-4.1'  # 默认值
        api_key = self.version_config.get('api_key')
        api_url = self.version_config.get('api_base_url', 'https://models.github.ai/inference/chat/completions')
        
        if not api_key:
            raise Exception('GitHub模型API密钥未配置')
        
        # 创建ChatOpenAI实例，用于兼容OpenAI API格式的服务
        self.llm = ChatOpenAI(
            model=selected_version_id,
            api_key=api_key,
            base_url=api_url,
            temperature=0.7,  # 默认温度，会在调用时被覆盖
            timeout=180  # 超时设置
        )

    def chat(self, messages: List[Dict[str, str]], temperature: float, stream: bool = False) -> Dict[str, Any]:
        """非流式调用GitHub模型API (使用langchain)"""
        # 转换消息格式
        langchain_messages = self._convert_to_langchain_messages(messages)
        
        # 更新LLM温度参数
        self.llm.temperature = temperature
        
        # 调用LLM
        response = self.llm.invoke(langchain_messages)
        
        # 提取回复内容
        content = response.content
        return self._format_response(content)

    def chat_stream(self, messages: List[Dict[str, str]], temperature: float) -> Generator[str, None, None]:
        """流式调用GitHub模型API (使用langchain)"""
        # 转换消息格式
        langchain_messages = self._convert_to_langchain_messages(messages)
        
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