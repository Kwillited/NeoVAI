"""RAG相关API路由"""
from flask import Blueprint, request, jsonify, current_app

# 导入RAG服务层
from app.services.rag_service import RAGService, set_rag_instance

# 创建RAG API蓝图（前缀统一为 /api/rag）
rag_bp = Blueprint('rag', __name__, url_prefix='/api/rag')

# RAG实例通过从rag_service导入的函数进行管理

# 上传文档
@rag_bp.route('/upload', methods=['POST'])
def upload_document():
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有文件上传'
            }), 400
        
        file = request.files['file']
        folder_id = request.form.get('folder_id', '')
        
        # 调用服务层方法，传递folder_id参数
        result = RAGService.upload_document(file, folder_id=folder_id)
        
        return jsonify({
            'success': True,
            'message': result['message'],
            'file_path': result['file_path']
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        print(f"❌ 上传文件失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 获取文档列表
@rag_bp.route('/documents', methods=['GET'])
def get_documents():
    try:
        # 调用服务层方法获取文档列表
        documents = RAGService.get_documents()
        
        # 获取所有文件夹信息，建立id到name的映射
        folders = RAGService.get_folders()
        folder_id_to_name = {folder['id']: folder['name'] for folder in folders if folder['id']}
        
        # 直接返回文档列表和文件夹ID映射
        return jsonify({
            'success': True,
            'documents': documents,
            'folder_id_map': folder_id_to_name  # 返回ID到名称的映射供前端使用
        })
    except Exception as e:
        print(f"❌ 获取文档列表失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 获取文件夹列表
@rag_bp.route('/folders', methods=['GET'])
def get_folders():
    try:
        # 调用服务层方法
        folders = RAGService.get_folders()
        
        return jsonify({
            'success': True,
            'folders': folders
        })
    except Exception as e:
        print(f"❌ 获取文件夹列表失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 创建文件夹/知识库
@rag_bp.route('/folders', methods=['POST'])
def create_folder():
    try:
        data = request.json
        folder_name = data.get('name')
        
        # 调用服务层方法
        result = RAGService.create_folder(folder_name)
        
        return jsonify({
            'success': True,
            'message': result['message'],
            'id': result['id'],
            'name': result['name'],
            'path': result['path']
        })
    except ValueError as e:
        status_code = 409 if str(e) == '文件夹已存在' else 400
        return jsonify({
            'success': False,
            'error': str(e)
        }), status_code
    except Exception as e:
        print(f"❌ 创建文件夹失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 获取指定文件夹中的文件(通过folder_id)
@rag_bp.route('/folders/by-id/<folder_id>/files', methods=['GET'])
def get_files_in_folder_by_id(folder_id):
    try:
        # 调用服务层方法，使用folder_id获取文件夹内容
        files = RAGService.get_files_in_folder_by_id(folder_id)
        
        return jsonify({
            'success': True,
            'files': files,
            'folder_id': folder_id
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        print(f"❌ 通过folder_id获取文件夹中的文件失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 搜索文件内容
@rag_bp.route('/search', methods=['GET'])
def search_file_content():
    try:
        query = request.args.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': '搜索关键词不能为空'
            }), 400
        
        # 调用服务层方法
        results = RAGService.search_file_content(query)
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        print(f"❌ 搜索文件内容失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 获取文件详情
@rag_bp.route('/documents/<file_id>', methods=['GET'])
def get_document_details(file_id):
    try:
        # 调用服务层方法
        details = RAGService.get_document_details(file_id)
        
        return jsonify({
            'success': True,
            'details': details
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        print(f"❌ 获取文件详情失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 删除文档
@rag_bp.route('/<foldername>/<filename>', methods=['DELETE'])
def delete_document(foldername, filename):
    try:
        # 调用服务层方法，传递foldername参数
        result = RAGService.delete_document(filename, foldername)
        
        return jsonify({
            'success': True,
            'message': result['message'],
            'deleted_file': result['deleted_file'],
            'folder': result['folder']
        })
    except ValueError as e:
        status_code = 404 if str(e) == '文件不存在' else 400
        return jsonify({
            'success': False,
            'error': str(e)
        }), status_code
    except Exception as e:
        print(f"❌ 删除文档失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 删除文件夹/知识库
@rag_bp.route('/folders', methods=['DELETE'])
def delete_folder():
    try:
        # 从查询参数中获取folder_id
        folder_id = request.args.get('folder_id')
        
        # 调用服务层方法，现在使用folder_id参数
        result = RAGService.delete_folder_by_id(folder_id)
        
        return jsonify({
            'success': True,
            'message': result['message'],
            'deleted_folder': result['deleted_folder'],
            'folder_id': folder_id
        })
    except ValueError as e:
        status_code = 404 if str(e) == '文件夹不存在' else 400
        return jsonify({
            'success': False,
            'error': str(e)
        }), status_code
    except Exception as e:
        print(f"❌ 删除文件夹失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 删除所有文档
@rag_bp.route('/documents/delete-all', methods=['DELETE'])
def delete_all_documents():
    try:
        # 调用服务层方法
        result = RAGService.delete_all_documents()
        
        return jsonify({
            'success': True,
            'message': result['message'],
            'deleted_count': result['deleted_count']
        })
    except Exception as e:
        print(f"❌ 删除所有文档失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500