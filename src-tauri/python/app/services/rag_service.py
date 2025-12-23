"""RAG服务层模块 - 封装RAG相关的业务逻辑"""
import os
import json
import shutil
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid
from app.core.config import config_manager
from app.utils.RagUtils.document_loader import DocumentLoader
from app.utils.RagUtils.text_splitter import TextSplitter
from app.utils.RagUtils.vector_service import VectorService
from app.services.vector_store_service import VectorStoreService

# 使用config_manager获取标准用户数据目录
user_data_dir = config_manager.get_user_data_dir()

RAG_DIR = os.path.join(user_data_dir, 'Retrieval-Augmented Generation')
DATA_DIR = os.path.join(RAG_DIR, 'files')
VECTOR_DB_PATH = os.path.join(RAG_DIR, 'vectorDb')  # 与其他地方保持一致，使用vectorDb

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# 全局向量存储服务实例
vector_store_service = None

# 全局函数，供外部模块直接调用 - 保持API兼容性
def set_rag_instance(instance):
    """设置全局RAG实例 (兼容旧接口)"""
    global vector_store_service
    # 从旧实例中提取必要的配置信息
    if instance:
        # 创建新的向量存储服务实例
        embedder_model = getattr(instance, 'embedder_model', 'all-MiniLM-L6-v2')
        vector_db_path = getattr(instance, 'vector_db_path', VECTOR_DB_PATH)
        vector_store_service = VectorStoreService(
            vector_db_path=vector_db_path,
            embedder_model=embedder_model
        )

# 获取向量存储服务实例
def get_vector_store_service():
    """获取或创建向量存储服务实例"""
    global vector_store_service
    # 如果服务实例未初始化，创建一个默认实例
    if vector_store_service is None:
        try:
            vector_store_service = VectorStoreService(
                vector_db_path=VECTOR_DB_PATH,
                embedder_model=config_manager.get('rag.embedder_model', 'all-MiniLM-L6-v2')
            )
            print(f"✅ 向量存储服务实例已成功创建")
        except Exception as e:
            print(f"❌ 创建向量存储服务实例失败: {str(e)}")
            vector_store_service = None
    return vector_store_service

class RAGService:
    """RAG服务类 - 封装所有RAG相关的业务逻辑"""
    
    @staticmethod
    def upload_document(file, folder_id=''):
        """上传文档到RAG系统并进行向量化处理"""
        # 检查文件名是否为空
        if file.filename == '':
            raise ValueError('文件名不能为空')
        
        # 确保文件类型合法
        allowed_extensions = set(DocumentLoader.get_supported_extensions())
        if '.' not in file.filename or \
           file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            raise ValueError('只支持txt、pdf、doc、docx格式的文件')
        
        # 安全保存文件
        filename = secure_filename(file.filename)
        
        # 确定保存路径
        folder_name = ''
        if folder_id:
            # 如果提供了folder_id，查找对应的文件夹
            folders = RAGService.get_folders()
            for folder in folders:
                if folder.get('id') == folder_id:
                    folder_name = folder['name']
                    break
        
        # 构建完整文件路径
        file_path = RAGService._get_file_save_path(filename, folder_name)
        
        # 保存文件
        file.save(file_path)
        
        # 执行RAG处理流程
        document_info, chunk_info, vector_info = RAGService._process_document_for_rag(file_path)
        
        # 打印向量后的文本信息
        print(f"\n=== 向量处理后的文本信息 ===")
        print(f"文件名: {filename}")
        print(f"文档ID: {document_info.get('document_id')}")
        print(f"分割后的文档数量: {document_info.get('split_documents_count', 0)}")
        if 'sample_chunks' in document_info and document_info['sample_chunks']:
            print(f"前2个文本片段示例:")
            for i, chunk in enumerate(document_info['sample_chunks'][:2]):
                print(f"\n片段 {i+1}:")
                # 只打印前100个字符作为预览
                preview = chunk[:100] + '...' if len(chunk) > 100 else chunk
                print(f"{preview}")
        
        # 检查向量数据库数据
        print(f"\n=== 向量数据库数据检查 ===")
        
        # 获取向量存储服务实例
        vector_service = get_vector_store_service()
        print(f"向量存储服务状态: {'已初始化' if vector_service else '未初始化'}")
        
        if vector_service:
            print(f"向量存储服务类型: {type(vector_service).__name__}")
            print(f"嵌入模型: {vector_service.embedder_model}")
            
            # 获取向量库统计信息
            try:
                stats = vector_service.get_vector_statistics()
                print(f"向量库状态: {stats.get('status')}")
                print(f"向量总数: {stats.get('total_vectors', 0)}")
                print(f"向量存储类型: {stats.get('vector_store_type', '未知')}")
                print(f"向量存储路径: {stats.get('vector_store_path', '未知')}")
                
                if stats['total_vectors'] > 0:
                    print(f"\n✅ 向量库中包含 {stats['total_vectors']} 个向量，文档已成功存储！")
                else:
                    print(f"\n⚠️  向量库中暂无向量数据")
                    
            except Exception as stats_error:
                print(f"获取向量库统计信息时出错: {str(stats_error)}")
        else:
            print("未找到有效的向量存储服务实例")
            # 尝试检查全局向量数据库路径
            print(f"向量数据库路径: {VECTOR_DB_PATH}")
            print(f"向量数据库路径存在: {os.path.exists(VECTOR_DB_PATH)}")
            if os.path.exists(VECTOR_DB_PATH):
                print(f"向量数据库目录内容: {os.listdir(VECTOR_DB_PATH)}")
        
        return {
            'filename': filename,
            'message': f'文件 {filename} 上传成功',
            'file_path': filename,
            'document_info': document_info,
            'full_path': file_path,
            'folder_name': folder_name,
            'chunk_info': chunk_info,
            'vector_info': vector_info
        }
    
    @staticmethod
    def _get_file_save_path(filename, folder_name):
        """构建文件保存路径"""
        if folder_name:
            # 如果指定了文件夹，保存到该文件夹
            folder_path = os.path.join(DATA_DIR, secure_filename(folder_name))
            os.makedirs(folder_path, exist_ok=True)
            return os.path.join(folder_path, filename)
        else:
            # 否则保存到根目录
            return os.path.join(DATA_DIR, filename)
    
    @staticmethod
    def _process_document_for_rag(file_path):
        """处理文档并执行RAG相关操作（加载、分割、向量化）"""
        # 加载文档
        document_info = DocumentLoader.load_document(file_path)
        
        # 初始化处理信息
        chunk_info = {
            'total_chunks': 0,
            'chunk_size': 1000,
            'chunk_overlap': 200
        }
        
        vector_info = {
            'vectorized': False,
            'vector_count': 0,
            'embedding_model': None,
            'vector_store_type': None
        }
        
        # 检查是否有文档数据
        if 'documents' in document_info and document_info['documents']:
            # 执行文本分割
            split_result = RAGService._split_document(document_info['documents'], chunk_info)
            
            # 更新document_info
            document_info['split_documents_count'] = split_result['split_documents_count']
            document_info['chunk_size'] = split_result['chunk_size']
            document_info['chunk_overlap'] = split_result['chunk_overlap']
            document_info['sample_chunks'] = split_result['sample_chunks']
            
            # 如果分割失败，记录错误
            if not split_result['success']:
                document_info['split_error'] = split_result['error']
                print(f"文本分割失败: {split_result['error']}")
            else:
                # 执行向量化处理
                RAGService._vectorize_documents(
                    split_result['split_documents'],
                    split_result['document_id'],
                    file_path,
                    document_info,
                    vector_info
                )
            
            # 移除原始documents列表，只保留元数据信息
            del document_info['documents']
        
        # 如果向量化失败，记录错误
        if not vector_info['vectorized']:
            document_info['vector_info'] = vector_info
            print(f"⚠️  文档向量化失败，将在后续批量处理中尝试重新加载")
        
        return document_info, chunk_info, vector_info
    
    @staticmethod
    def _split_document(documents, chunk_info):
        """执行文档分割操作"""
        # 使用文本分割工具类进行分割
        split_result = TextSplitter.split_documents(
            documents=documents,
            chunk_size=chunk_info['chunk_size'],
            chunk_overlap=chunk_info['chunk_overlap']
        )
        
        # 更新chunk_info
        chunk_info['total_chunks'] = split_result['split_documents_count']
        chunk_info['document_id'] = split_result['document_id']
        
        return split_result
    
    @staticmethod
    def _vectorize_documents(split_documents, document_id, source_file, document_info, vector_info):
        """执行文档向量化操作"""
        try:
            # 验证文档是否适合向量化
            validation = VectorService.validate_vectors(split_documents)
            if not validation['is_valid']:
                document_info['validation_errors'] = validation['errors']
                if validation['errors']:
                    vector_info['error'] = f"文档验证失败: {', '.join(validation['errors'][:3])}"
                    print(f"文档验证失败: {validation['errors']}")
                else:
                    # 只有警告，继续向量化
                    document_info['validation_warnings'] = validation['warnings']
                    if validation['warnings']:
                        print(f"文档验证警告: {validation['warnings']}")
            
            # 获取向量存储服务实例
            vector_service = get_vector_store_service()
            
            # 执行向量化操作
            vectorized = vector_service.add_documents(split_documents)
            
            # 更新向量化信息
            vector_info['vectorized'] = vectorized
            vector_info['vector_count'] = len(split_documents) if vectorized else 0
            vector_info['embedding_model'] = vector_service.embedder_model
            vector_info['vector_store_type'] = 'chroma'
            
            # 创建并添加向量化元数据
            vector_metadata = VectorService.create_vector_metadata(
                documents=split_documents,
                source_file=source_file,
                document_id=document_id
            )
            document_info['vector_metadata'] = vector_metadata
            document_info['vector_info'] = vector_info
            
        except Exception as e:
            vector_info['error'] = str(e)
            document_info['vector_info'] = vector_info
            print(f"向量化处理失败: {str(e)}")
    
    @staticmethod
    def get_documents():
        """获取文档列表"""
        # 直接读取目录获取文档列表
        documents = []
        if os.path.exists(DATA_DIR):
            # 递归遍历所有文件
            for root, _, files in os.walk(DATA_DIR):
                for file in files:
                    if os.path.isfile(os.path.join(root, file)) and \
                       not file.startswith('.') and file != 'Thumbs.db':
                        # 计算相对路径
                        relative_path = os.path.relpath(root, DATA_DIR)
                        folder_name = relative_path if relative_path != '.' else ''
                        
                        documents.append({
                            'name': file,
                            'folder': folder_name,
                            'path': os.path.join(root, file)
                        })
        return documents
    
    @staticmethod
    def delete_document(filename, folder_name=''):
        """删除指定文档/文件
        
        Args:
            filename: 文件名
            folder_name: 文件夹名称，如果为空则在根目录查找
            
        Returns:
            dict: 删除操作的结果
        """
        # 参数验证
        if not filename:
            raise ValueError('文件名不能为空')
        
        # 安全验证文件名
        filename = secure_filename(filename)
        
        # 构建文件路径
        if folder_name:
            # 如果指定了文件夹，构建完整路径
            folder_name = secure_filename(folder_name)
            folder_path = os.path.join(DATA_DIR, folder_name)
            file_path = os.path.join(folder_path, filename)
        else:
            # 在根目录查找文件
            file_path = os.path.join(DATA_DIR, filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            raise ValueError('文件不存在')
        
        # 删除文件
        os.remove(file_path)
        
        # 从缓存中移除文件
        DocumentLoader.remove_from_cache(file_path)
        
        # 重新加载向量库
        RAGService.reload_documents()
        
        # 返回结果
        return {
            'deleted_file': filename,
            'folder': folder_name,
            'message': f'文档 {filename} 已成功删除'
        }
    
    @staticmethod
    def get_folders():
        """获取文件夹列表"""
        # 读取DATA_DIR目录下的所有文件夹
        folders = []
        if os.path.exists(DATA_DIR):
            for item in os.listdir(DATA_DIR):
                item_path = os.path.join(DATA_DIR, item)
                if os.path.isdir(item_path) and not item.startswith('.') and item != 'Thumbs.db':
                    # 尝试从标记文件中读取id
                    folder_id = None
                    marker_file_path = os.path.join(item_path, '.kb_marker.json')
                    if os.path.exists(marker_file_path):
                        try:
                            with open(marker_file_path, 'r', encoding='utf-8') as f:
                                marker_data = json.load(f)
                                folder_id = marker_data.get('id')
                        except Exception:
                            pass
                    
                    folders.append({
                        'id': folder_id,
                        'name': item,
                        'path': item_path
                    })
        return folders
    
    @staticmethod
    def create_folder(folder_name):
        """创建文件夹/知识库"""
        if not folder_name:
            raise ValueError('文件夹名称不能为空')
        
        # 安全验证文件夹名称
        folder_name = secure_filename(folder_name)
        
        # 创建文件夹
        folder_path = os.path.join(DATA_DIR, folder_name)
        if os.path.exists(folder_path):
            raise ValueError('文件夹已存在')
        
        os.makedirs(folder_path, exist_ok=True)
        
        # 生成唯一ID
        folder_id = str(uuid.uuid4())[:8]
        
        # 创建标记文件
        marker_file_path = os.path.join(folder_path, '.kb_marker.json')
        with open(marker_file_path, 'w', encoding='utf-8') as f:
            json.dump({
                'id': folder_id,
                'name': folder_name,
                'created_at': datetime.now().isoformat(),
                'version': '1.0'
            }, f, ensure_ascii=False, indent=2)
        
        return {
            'id': folder_id,
            'name': folder_name,
            'path': folder_path,
            'message': f'文件夹 {folder_name} 创建成功'
        }
    
    @staticmethod
    def get_files_in_folder(folder_name):
        """获取指定文件夹中的文件"""
        # 构建文件夹路径
        folder_path = os.path.join(DATA_DIR, folder_name)
        
        # 检查文件夹是否存在
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            raise ValueError('文件夹不存在')
        
        # 读取文件夹中的文件
        files = []
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path) and not file.startswith('.') and file != 'Thumbs.db':
                files.append({
                    'name': file,
                    'path': file_path,
                    'size': os.path.getsize(file_path),
                    'modified_at': os.path.getmtime(file_path)
                })
        return files
    
    @staticmethod
    def get_files_in_folder_by_id(folder_id):
        """通过folder_id获取指定文件夹中的文件"""
        # 重用get_folders方法查找文件夹
        folders = RAGService.get_folders()
        target_folder_name = None
        for folder in folders:
            if folder.get('id') == folder_id:
                target_folder_name = folder['name']
                break
        
        # 如果没有找到匹配的文件夹，抛出ValueError
        if not target_folder_name:
            raise ValueError('指定ID的文件夹不存在')
        
        # 调用现有的方法获取文件列表
        return RAGService.get_files_in_folder(target_folder_name)
    
    @staticmethod
    def delete_all_documents():
        """删除所有文档，包括所有文件夹和文件，并清空向量数据库"""
        # 先检查DATA_DIR是否存在
        if not os.path.exists(DATA_DIR):
            # 即使目录不存在，也执行清空向量库操作
            vector_service = get_vector_store_service()
            vector_service.clear_vector_store()
            return {'deleted_count': 0, 'message': '没有文档需要删除，但已清空向量数据库'}
        
        # 统计删除的文件数量
        deleted_count = 0
        
        # 递归删除所有文件和文件夹
        for root, dirs, files in os.walk(DATA_DIR, topdown=False):
            # 先删除所有文件
            for file in files:
                if not file.startswith('.') and file != 'Thumbs.db':
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except Exception as e:
                        print(f"删除文件 {file_path} 时出错: {e}")
            
            # 然后删除所有子目录
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    shutil.rmtree(dir_path)
                except Exception as e:
                    print(f"删除目录 {dir_path} 时出错: {e}")
        
        # 直接清空向量库，而不是依赖reload_documents
        vector_service = get_vector_store_service()
        vector_service.clear_vector_store()
        
        # 清除文档缓存
        DocumentLoader.clear_cache()
        
        # 重新初始化DATA_DIR目录（如果被删除）
        os.makedirs(DATA_DIR, exist_ok=True)
        
        return {
            'deleted_count': deleted_count,
            'message': f'已删除 {deleted_count} 个文件和所有文件夹，并清空了向量数据库'
        }
    
    @staticmethod
    def search_file_content(query):
        """搜索文件内容"""
        if not query or not query.strip():
            raise ValueError('搜索关键词不能为空')
        
        # 这里简单实现文件内容搜索
        results = []
        query = query.strip().lower()
        
        # 递归遍历DATA_DIR中的所有文件
        for root, _, files in os.walk(DATA_DIR):
            for file in files:
                if file.startswith('.') or file == 'Thumbs.db':
                    continue
                
                file_path = os.path.join(root, file)
                try:
                    # 尝试读取文本文件内容进行搜索
                    if file.lower().endswith(('.txt', '.md', '.csv')):
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if query in content.lower():
                                results.append({
                                    'file': file,
                                    'path': file_path,
                                    'folder': os.path.relpath(root, DATA_DIR)
                                })
                    # 对于其他类型的文件，只搜索文件名
                    elif query in file.lower():
                        results.append({
                            'file': file,
                            'path': file_path,
                            'folder': os.path.relpath(root, DATA_DIR)
                        })
                except Exception as file_error:
                    print(f"读取文件 {file} 时出错: {file_error}")
        
        return results
    
    @staticmethod
    def get_document_details(file_id):
        """获取文件详情"""
        # 这里简化处理，直接将file_id视为文件名
        file_name = file_id
        
        # 先在根目录查找
        file_path = os.path.join(DATA_DIR, file_name)
        if not os.path.exists(file_path):
            # 再在子目录中查找
            found = False
            for root, _, files in os.walk(DATA_DIR):
                if file_name in files:
                    file_path = os.path.join(root, file_name)
                    found = True
                    break
            
            if not found:
                raise ValueError('文件不存在')
        
        # 获取文件详情
        file_stats = os.stat(file_path)
        file_details = {
            'id': file_name,
            'name': file_name,
            'path': file_path,
            'size': file_stats.st_size,
            'created_at': file_stats.st_ctime,
            'modified_at': file_stats.st_mtime,
            'folder': os.path.relpath(os.path.dirname(file_path), DATA_DIR)
        }
        
        return file_details
    
    @staticmethod
    def delete_folder_by_id(folder_id):
        """通过folder_id删除文件夹/知识库"""
        if not folder_id:
            raise ValueError('文件夹ID不能为空')
        
        # 遍历DATA_DIR中的所有子目录，查找匹配的folder_id
        found_folder = None
        for item in os.listdir(DATA_DIR):
            item_path = os.path.join(DATA_DIR, item)
            if os.path.isdir(item_path):
                # 检查是否有.kb_marker.json文件
                marker_path = os.path.join(item_path, '.kb_marker.json')
                if os.path.exists(marker_path):
                    try:
                        with open(marker_path, 'r', encoding='utf-8') as f:
                            marker_data = json.load(f)
                            if marker_data.get('id') == folder_id:
                                found_folder = item
                                break
                    except (json.JSONDecodeError, IOError):
                        # 如果无法读取标记文件，跳过该文件夹
                        continue
        
        if not found_folder:
            raise ValueError('文件夹不存在')
        
        # 调用原有的delete_folder方法进行删除
        return RAGService.delete_folder(found_folder)
    
    @staticmethod
    def delete_folder(folder_name):
        """删除文件夹/知识库"""
        if not folder_name:
            raise ValueError('文件夹名称不能为空')
        
        # 安全验证文件夹名称
        folder_name = secure_filename(folder_name)
        
        # 构建文件夹路径
        folder_path = os.path.join(DATA_DIR, folder_name)
        
        # 检查文件夹是否存在
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            raise ValueError('文件夹不存在')
        
        # 删除文件夹及其所有内容
        shutil.rmtree(folder_path)
        
        # 重新加载向量库
        RAGService.reload_documents()
        
        return {
            'deleted_folder': folder_name,
            'message': f'文件夹 {folder_name} 已成功删除'
        }
    
    @staticmethod
    def reload_documents():
        """重新加载文档到向量库"""
        try:
            # 获取向量存储服务实例
            vector_service = get_vector_store_service()
            if not vector_service:
                print("❌ 向量存储服务未初始化")
                return False
            
            # 先清空向量库
            vector_service.clear_vector_store()
            
            # 加载、分割和向量化所有文档
            loaded_chunks = 0
            processed_files = 0
            failed_files = 0
            
            # 递归遍历所有文件
            for root, _, files in os.walk(DATA_DIR):
                for file in files:
                    if file.startswith('.') or file == 'Thumbs.db':
                        continue
                    
                    file_path = os.path.join(root, file)
                    processed_files += 1
                    
                    try:
                        # 1. 加载文档
                        document_info = DocumentLoader.load_document(file_path)
                        if 'documents' in document_info and document_info['documents']:
                            # 2. 分割文档
                            chunk_info = {'chunk_size': 1000, 'chunk_overlap': 200}
                            split_result = RAGService._split_document(document_info['documents'], chunk_info)
                            
                            if split_result['success']:
                                # 3. 向量化并添加到向量库
                                success = vector_service.add_documents(split_result['split_documents'])
                                if success:
                                    loaded_chunks += split_result['split_documents_count']
                                else:
                                    failed_files += 1
                                    print(f"⚠️  向量化文件 {file} 失败")
                    except Exception as file_error:
                        failed_files += 1
                        print(f"❌ 处理文件 {file} 时出错: {file_error}")
            
            # 输出统计信息
            print(f"✅ 重新加载文档完成:")
            print(f"   - 处理文件数: {processed_files}")
            print(f"   - 成功加载: {processed_files - failed_files}")
            print(f"   - 加载失败: {failed_files}")
            print(f"   - 总向量数: {loaded_chunks}")
            
            return True
        except Exception as e:
            print(f"❌ 重新加载文档失败: {e}")
            return False