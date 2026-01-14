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
import { ref, onMounted, watch } from 'vue';
import { useSettingsStore } from '../../store/settingsStore.js';
import { useRagStore } from '../../store/ragStore.js';
import { showNotification } from '../../services/notificationUtils.js';
import ActionButton from '../common/ActionButton.vue';
import SearchBar from '../common/SearchBar.vue';

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
});

// 初始化store
const settingsStore = useSettingsStore();
const ragStore = useRagStore();

// 搜索查询
const searchQuery = ref('');
// 当前是否处于RAG文件管理视图
const isRagManagementView = ref(false);

// 处理新建知识库
const handleCreateKnowledgeBase = () => {
  // 使用store方法触发创建知识库
  // 实际实现需要根据store设计调整
  showNotification('创建知识库功能待实现', 'info');
};

// 处理删除所有文件
const handleDeleteAll = () => {
  // 直接调用store方法删除所有文件
  ragStore.deleteAllFiles();
};

// 处理视图切换
const handleViewToggle = () => {
  if (isRagManagementView.value) {
    settingsStore.setActiveContent('chat');
    isRagManagementView.value = false;
  } else {
    settingsStore.setActiveContent('ragManagement');
    isRagManagementView.value = true;
  }
};

// 监听store中的activeContent变化
watch(
  () => settingsStore.activeContent,
  (newContent) => {
    isRagManagementView.value = newContent === 'ragManagement';
  },
  { immediate: true }
);

// 初始化当前视图状态
const initializeViewState = () => {
  // 直接从store获取当前活动内容
  isRagManagementView.value = settingsStore.activeContent === 'ragManagement';
};

onMounted(() => {
  initializeViewState();
});

// 处理搜索
const handleSearch = () => {
  // 直接调用store方法进行搜索
  ragStore.searchKnowledgeBase(searchQuery.value);
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