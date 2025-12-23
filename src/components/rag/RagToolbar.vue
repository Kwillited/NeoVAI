<template>
  <div class="toolbar flex justify-between items-center mb-3 p-2 bg-gray-50 dark:bg-gray-800 dark:border-gray-700 rounded-lg border border-gray-100 transition-all duration-300">
    <ActionButton
      id="createKnowledgeBaseBtn"
      icon="fa-folder-plus"
      title="新建知识库"
      @click="handleCreateKnowledgeBase"
    />

    <ActionButton
      id="deleteAllBtn"
      icon="fa-trash-can"
      title="删除所有文件夹"
      @click="handleDeleteAll"
      :disabled="loading"
      iconClass="text-neutral hover:text-red-500 hover:bg-red-50"
    />
    <ActionButton
      :id="isRagManagementView ? '返回对话' : '切换到RAG文件管理'"
      :icon="isRagManagementView ? 'fa-comment' : 'fa-folder-tree'"
      :title="isRagManagementView ? '返回对话' : '切换到RAG文件管理'"
      @click="handleViewToggle"
    />
  </div>
  
  <!-- 搜索框 -->
  <SearchBar v-model="searchQuery" placeholder="搜索知识库..." @input="handleSearch" />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import ActionButton from '../common/ActionButton.vue';
import SearchBar from '../common/SearchBar.vue';

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
});

// 搜索查询
const searchQuery = ref('');
// 当前是否处于RAG文件管理视图
const isRagManagementView = ref(false);

// 处理新建知识库
const handleCreateKnowledgeBase = () => {
  const event = new CustomEvent('createKnowledgeBase');
  window.dispatchEvent(event);
};

// 处理删除所有文件
const handleDeleteAll = () => {
  const event = new CustomEvent('deleteAll');
  window.dispatchEvent(event);
};

// 处理视图切换
const handleViewToggle = () => {
  if (window.setActiveContent) {
    if (isRagManagementView.value) {
      window.setActiveContent('chat');
      isRagManagementView.value = false;
    } else {
      window.setActiveContent('ragManagement');
      isRagManagementView.value = true;
    }
  }
};

// 监听视图变化事件
const handleContentChanged = (event) => {
  if (event.detail && event.detail.contentType) {
    isRagManagementView.value = event.detail.contentType === 'ragManagement';
  }
};

// 初始化当前视图状态
const initializeViewState = () => {
  // 尝试通过不同方式判断当前是否处于RAG管理视图
  // 1. 检查是否有特定的class或元素标识RAG管理视图
  const ragManagementElement = document.querySelector('.rag-management-container, #ragManagement');
  if (ragManagementElement) {
    isRagManagementView.value = true;
    return;
  }
  
  // 2. 检查当前URL路径或其他可能的标识
  const currentPath = window.location.pathname;
  if (currentPath.includes('rag') || currentPath.includes('management')) {
    isRagManagementView.value = true;
    return;
  }
  
  // 3. 作为备选方案，检查当前活动内容
  if (window.activeContentType) {
    isRagManagementView.value = window.activeContentType === 'ragManagement';
    return;
  }
  
  // 默认值
  isRagManagementView.value = false;
};

onMounted(() => {
  initializeViewState();
  window.addEventListener('contentChanged', handleContentChanged);
});

onUnmounted(() => {
  window.removeEventListener('contentChanged', handleContentChanged);
});

// 处理搜索
const handleSearch = () => {
  const event = new CustomEvent('searchKnowledgeBase', {
    detail: searchQuery.value
  });
  window.dispatchEvent(event);
};
</script>

<style scoped>
/* 工具栏样式 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 8px;
  background-color: #f9fafb;
  border-radius: 0.5rem;
  border: 1px solid #f3f4f6;
}

/* 夜间模式工具栏样式 */
.dark .toolbar {
  background-color: #1f2937;
  border-color: #374151;
}

/* 禁用状态样式 */
button:disabled {
  opacity: 0.5;
  cursor: not-allowed !important;
}

button:disabled:hover {
  background-color: transparent !important;
}
</style>