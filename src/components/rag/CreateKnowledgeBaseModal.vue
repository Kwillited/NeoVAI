<template>
  <div v-if="visible" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50" @click="handleBackdropClick">
    <div class="bg-white dark:bg-gray-800 dark:text-white rounded-lg shadow-xl dark:shadow-panel-dark p-6 w-full max-w-md mx-4 transform transition-all duration-300 scale-100" @click.stop>
      <div class="mb-4 flex justify-between items-center">
        <h3 class="text-lg font-semibold text-gray-800 dark:text-white">新建知识库</h3>
        <button 
          @click="handleCancel"
          class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
        >
          <i class="fa-solid fa-times"></i>
        </button>
      </div>
      
      <div class="mb-4">
        <label for="knowledgeBaseName" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">知识库名称</label>
        <input
          id="knowledgeBaseName"
          v-model="knowledgeBaseName"
          type="text"
          placeholder="请输入知识库名称"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-md focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-colors"
          @keyup.enter="handleCreate"
          ref="inputRef"
        />
        <p v-if="error" class="text-red-500 text-xs mt-1">{{ error }}</p>
      </div>
      
      <div class="flex justify-end space-x-3">
        <button 
          @click="handleCancel"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600 rounded-md hover:bg-gray-200 transition-colors"
        >
          取消
        </button>
        <button 
          @click="handleCreate"
          :disabled="!knowledgeBaseName.trim() || ragStore.loading"
          class="px-4 py-2 text-sm font-medium text-white bg-primary rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="!ragStore.loading">创建</span>
          <span v-else>创建中...</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import { useRagStore } from '../../store/ragStore.js';
import { showNotification } from '../../services/notificationUtils.js';

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
});

// Emits
const emit = defineEmits(['close', 'created']);

// Store
const ragStore = useRagStore();

// Refs
const knowledgeBaseName = ref('');
const error = ref('');
const inputRef = ref(null);

// 处理创建知识库
const handleCreate = async () => {
  // 重置错误信息
  error.value = '';
  
  // 验证输入
  if (!knowledgeBaseName.value.trim()) {
    error.value = '请输入知识库名称';
    return;
  }
  
  try {
    // 通过ragStore创建知识库
    const result = await ragStore.createKnowledgeBase(knowledgeBaseName.value.trim());
    if (result.success) {
      // 显示成功提示
      showNotification(`已成功创建知识库: ${knowledgeBaseName.value.trim()}`, 'success');
      
      // 触发创建成功事件
      emit('created', result);
      
      // 重置表单并关闭模态框
      resetForm();
      emit('close');
    } else {
      throw new Error(result.error || '创建知识库失败');
    }
  } catch (error) {
    // 显示错误提示
    error.value = `创建失败: ${error.message || String(error)}`;
    showNotification(`创建知识库失败: ${error.message || String(error)}`, 'error');
  }
};

// 处理取消
const handleCancel = () => {
  resetForm();
  emit('close');
};

// 处理背景点击
const handleBackdropClick = () => {
  handleCancel();
};

// 重置表单
const resetForm = () => {
  knowledgeBaseName.value = '';
  error.value = '';
};

// 当模态框显示时，自动聚焦输入框
const focusInput = async () => {
  if (props.visible && inputRef.value) {
    await nextTick();
    inputRef.value.focus();
  }
};

// 处理ESC键关闭模态框
const handleKeyDown = (event) => {
  if (event.key === 'Escape' && props.visible) {
    handleCancel();
  }
};

// 监听visible属性变化
onMounted(() => {
  focusInput();
  document.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown);
});
</script>

<style scoped>
/* 动画效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: scale(0.95);
}
</style>