# 后端架构文档

## 1. 项目概述

ChaTo是一个AI聊天应用，支持多种AI模型和RAG（检索增强生成）功能。后端采用了分层架构设计，便于维护和扩展。

## 2. 技术栈

### 2.1 核心技术
- **语言**: Python 3.13
- **Web框架**: Flask
- **数据库**: SQLite
- **向量数据库**: Chroma
- **AI集成**: LangChain, 各种AI模型SDK

### 2.2 主要依赖
- Flask: Web框架
- Flask-CORS: 跨域支持
- uuid: 生成唯一ID
- langchain_classic: 构建RAG应用
- chromadb: 向量数据库
- platformdirs: 跨平台目录管理

## 3. 分层架构

### 3.1 架构图

```
API层 → 服务层 → DataService层 → Repository层 → 数据层
```

### 3.2 各层职责

#### 3.2.1 API层
- 处理HTTP请求和响应
- 参数验证
- 返回格式统一
- 路由定义

#### 3.2.2 服务层
- 封装业务逻辑
- 处理业务规则
- 调用DataService层和Repository层
- 所有服务类继承自BaseService

#### 3.2.3 DataService层
- 管理内存数据
- 处理脏标记机制
- 提供事务管理功能
- 封装db对象的访问

#### 3.2.4 Repository层
- 封装数据库访问
- 处理SQL查询
- 提供CRUD操作

#### 3.2.5 数据层
- 数据持久化
- 数据库连接管理
- 数据同步

## 4. 主要模块说明

### 4.1 API层

| 模块 | 功能 | 文件路径 |
| --- | --- | --- |
| chats | 处理聊天相关请求 | app/api/chats.py |
| models | 处理模型相关请求 | app/api/models.py |
| rag | 处理RAG相关请求 | app/api/rag.py |
| mcp | 处理MCP相关请求 | app/api/mcp.py |
| settings | 处理设置相关请求 | app/api/settings.py |

### 4.2 服务层

| 模块 | 功能 | 文件路径 |
| --- | --- | --- |
| ChatService | 聊天业务逻辑 | app/services/chat_service.py |
| ModelService | 模型管理逻辑 | app/services/model_service.py |
| RAGService | RAG业务逻辑 | app/services/rag_service.py |
| VectorStoreService | 向量存储管理 | app/services/vector_store_service.py |
| LangChainRAGService | LangChain RAG逻辑 | app/services/langchain_rag_service.py |
| MCPService | MCP业务逻辑 | app/services/mcp_service.py |
| SettingService | 设置管理逻辑 | app/services/setting_service.py |
| DataService | 数据管理服务 | app/services/data_service.py |

### 4.3 Repository层

| 模块 | 功能 | 文件路径 |
| --- | --- | --- |
| ChatRepository | 对话数据访问 | app/repositories/chat_repository.py |
| MessageRepository | 消息数据访问 | app/repositories/message_repository.py |
| ModelRepository | 模型数据访问 | app/repositories/model_repository.py |
| SettingRepository | 设置数据访问 | app/repositories/setting_repository.py |

### 4.4 核心模块

#### 4.4.1 ModelManager
- 统一的模型管理接口
- 支持多种AI模型
- 提供流式和非流式对话接口

#### 4.4.2 VectorStoreService
- 向量存储管理
- 文档嵌入和检索
- 查询缓存

#### 4.4.3 DataService
- 内存数据管理
- 脏标记机制
- 事务管理

## 5. 关键流程

### 5.1 聊天流程

1. API层接收聊天请求
2. ChatService处理请求，解析模型信息
3. 调用DataService获取模型配置
4. 调用ModelManager获取AI回复
5. 保存聊天记录到数据库
6. 返回响应

### 5.2 RAG增强流程

1. 文档上传到系统
2. 文档加载器加载文档
3. 文本分割器分割文档
4. 嵌入模型生成向量
5. 向量存储到Chroma
6. 用户查询时，生成查询向量
7. 检索相关文档
8. 构建增强提示
9. 调用AI模型生成回复

### 5.3 模型配置流程

1. API层接收模型配置请求
2. ModelService处理请求
3. 调用ModelRepository更新数据库
4. 调用DataService更新内存数据
5. 设置脏标记
6. 返回响应

## 6. 开发规范

### 6.1 代码风格
- 使用PEP 8代码风格
- 函数和类名采用驼峰命名法
- 变量名采用下划线命名法
- 每个函数和类都需要添加文档注释

### 6.2 分层架构规范
- API层只依赖服务层
- 服务层只依赖DataService层和Repository层
- DataService层只依赖数据层
- Repository层只依赖数据层
- 禁止跨层访问

### 6.3 日志规范
- 使用统一的日志记录器
- 日志级别：DEBUG, INFO, WARNING, ERROR
- 日志格式：`%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- 服务层使用BaseService提供的日志方法

### 6.4 错误处理
- 使用BaseService提供的handle_exception方法统一处理异常
- API层返回统一的错误格式
- 错误信息应该友好，便于前端处理

## 7. 部署说明

### 7.1 开发环境部署

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

### 7.2 生产环境部署

```bash
# 安装依赖
pip install -r requirements.txt

# 使用gunicorn启动服务
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### 7.3 配置管理
- 配置文件：使用platformdirs管理配置文件
- 配置项：app.debug, app.host, app.port, rag.enabled, mcp.enabled等
- 配置更新：通过API更新配置，会自动保存到数据库

## 8. 数据管理

### 8.1 数据库设计

| 表名 | 功能 |
| --- | --- |
| chats | 存储对话信息 |
| messages | 存储聊天消息 |
| models | 存储模型信息 |
| model_versions | 存储模型版本信息 |
| settings | 存储应用设置 |

### 8.2 内存数据管理
- 应用启动时加载数据到内存
- 内存数据变更时设置脏标记
- 定期自动保存脏数据到数据库
- 支持事务管理

## 9. 后续迭代建议

### 9.1 性能优化
- 优化向量数据库查询
- 增加缓存机制
- 优化数据库查询

### 9.2 功能扩展
- 支持更多AI模型
- 增加多语言支持
- 增加更多RAG功能
- 支持模型微调

### 9.3 架构优化
- 考虑使用异步框架（如FastAPI）
- 考虑使用ORM框架
- 增加分布式支持
- 考虑使用消息队列

### 9.4 安全性增强
- 增加API密钥验证
- 增强数据加密
- 增加访问控制
- 增加审计日志

### 9.5 测试完善
- 增加单元测试
- 增加集成测试
- 增加性能测试
- 增加安全测试

## 10. 总结

ChaTo后端采用了分层架构设计，便于维护和扩展。各层职责明确，依赖关系清晰。通过统一的服务基类和数据管理服务，提高了代码的一致性和可维护性。后续可以根据业务需求，继续优化架构和扩展功能。

## 11. 联系方式

如有问题或建议，请联系开发团队。

---

**更新时间**: 2026-01-16
**版本**: 1.0
