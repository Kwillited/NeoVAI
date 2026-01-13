"""测试RAG优化功能"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.langchain_rag_service import LangChainRAGService
from app.services.vector_store_service import VectorStoreService
from app.utils.callback_manager import register_callback


# 注册回调函数来监控测试过程
def test_callback(**kwargs):
    """测试回调函数"""
    print(f"📢 回调事件: {kwargs}")

# 注册关键事件的回调
register_callback('rag_chain_start', test_callback)
register_callback('rag_chain_end', test_callback)
register_callback('search_start', test_callback)
register_callback('search_end', test_callback)
register_callback('error', test_callback)


def test_rag_optimization():
    """测试RAG优化功能"""
    print("🚀 开始测试RAG优化功能...")
    
    try:
        # 1. 测试向量存储服务初始化
        print("\n1. 测试向量存储服务初始化...")
        vector_service = VectorStoreService.get_instance()
        print(f"   ✅ 向量存储服务初始化成功: {vector_service.vector_store}")
        
        # 2. 测试LangChain RAG服务初始化
        print("\n2. 测试LangChain RAG服务初始化...")
        rag_service = LangChainRAGService.get_instance()
        print("   ✅ LangChain RAG服务初始化成功")
        
        # 3. 测试增强提示生成
        print("\n3. 测试增强提示生成...")
        test_question = "什么是RAG？"
        enhanced_prompt = rag_service.get_enhanced_prompt(test_question, {"enabled": True})
        print(f"   ✅ 增强提示生成成功")
        print(f"   原始问题: {test_question}")
        print(f"   增强提示: {enhanced_prompt[:100]}...")
        
        # 4. 测试搜索功能
        print("\n4. 测试搜索功能...")
        search_results = vector_service.search_documents("RAG", k=3, search_type="mmr")
        print(f"   ✅ 搜索功能测试成功，找到 {len(search_results)} 个结果")
        for i, result in enumerate(search_results[:2]):
            print(f"   结果 {i+1}: {result.page_content[:50]}...")
        
        # 5. 测试不同搜索类型
        print("\n5. 测试不同搜索类型...")
        for search_type in ["similarity", "mmr"]:
            results = vector_service.search_documents("RAG", k=2, search_type=search_type)
            print(f"   ✅ {search_type} 搜索成功，找到 {len(results)} 个结果")
        
        print("\n🎉 所有RAG优化功能测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_rag_optimization()
    sys.exit(0 if success else 1)
