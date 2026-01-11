<template>
  <!-- 自定义通知组件 -->
  <div v-if="showNotification" class="notification-overlay fixed bottom-4 right-4 z-50">
    <div class="notification-card bg-white dark:bg-dark-700 shadow-lg rounded-lg p-4 min-w-[300px] transition-all duration-300 ease-in-out transform translate-y-0 opacity-100">
      <div class="flex items-start">
        <div class="flex-shrink-0 mt-1">
          <i v-if="notificationType === 'success'" class="fa-solid fa-check-circle text-green-500"></i>
          <i v-else-if="notificationType === 'error'" class="fa-solid fa-exclamation-circle text-red-500"></i>
          <i v-else-if="notificationType === 'info'" class="fa-solid fa-info-circle text-blue-500"></i>
          <i v-else class="fa-solid fa-bell text-gray-500"></i>
        </div>
        <div class="ml-3 w-0 flex-1 pt-0.5">
          <p class="text-sm font-medium text-gray-900 dark:text-white">{{ notificationTitle }}</p>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ notificationMessage }}</p>
        </div>
        <div class="ml-4 flex-shrink-0 flex">
          <button @click="hideNotification" class="bg-white dark:bg-dark-700 rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            <span class="sr-only">关闭</span>
            <i class="fa-solid fa-times"></i>
          </button>
        </div>
      </div>
      <!-- 倒计时进度条 -->
      <div class="mt-3 h-1 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
        <div class="notification-progress h-full bg-primary rounded-full transition-all duration-[2900ms] ease-linear" :style="{ width: '0%' }"></div>
      </div>
    </div>
  </div>
  
  <!-- 聊天输入区域 - 在切换到图谱视图时添加顶部padding -->
  <div id="MessageInputArea" class="border-t-0 pb-4 px-6 transition-colors duration-300 ease-in-out" :class="{ 'pt-4': activeView !== 'grid' }">
    <div class="relative w-full max-w-4xl mx-auto">
      <div class="card focus-ring depth-1 focus-within:depth-2 transition-all duration-300 ease-in-out bg-white dark:bg-dark-700">
        <div
          v-if="uploadedFiles.length > 0"
          class="grid grid-cols-[repeat(auto-fill,minmax(80px,1fr))] gap-2 p-2 border-b border-gray-200 pb-3"
        >
          <!-- 显示已上传的文件 -->
          <div
            v-for="(file, index) in uploadedFiles"
            :key="index"
            class="flex items-center justify-between p-2 bg-gray-50 dark:bg-dark-600 rounded-lg text-xs mb-2 group transition-colors duration-300 ease-in-out"
          >
            <div class="flex items-center gap-1 truncate max-w-[50px]">
              <i :class="['fa', getFileIcon(file.name), 'text-gray-500']"></i>
              <span class="truncate">{{ file.name }}</span>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-gray-400 text-[10px]">{{ formatFileSize(file.size) }}</span>
              <button
                class="text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                @click="removeUploadedFile(index)"
              >
                <i class="fa-solid fa-circle-xmark"></i>
              </button>
            </div>
          </div>
        </div>
        <div
          ref="dragDropArea"
          class="p-3 pt-4 pb-1 relative"
          @dragover.prevent="isDragOver = true"
          @dragleave="isDragOver = false"
          @drop.prevent="handleDrop"
        >
          <textarea
            v-model="messageInput"
            placeholder="Message Or UploadFile For Chato..."
            class="w-full resize-none border-none focus:ring-0 focus:outline-none text-base leading-relaxed placeholder-gray-400 dark:text-white dark:placeholder-gray-500 bg-transparent transition-all duration-300 ease-in-out"
            rows="2"
            @keydown.enter.exact.prevent="handleSendMessage"
            @keydown.enter.shift=""
          ></textarea>
          <div
            v-if="isDragOver"
            class="absolute inset-0 flex flex-col items-center justify-center bg-primary/5 border-2 border-dashed border-primary/30 rounded-lg opacity-100 pointer-events-none transition-all duration-300 z-10"
          >
            <i class="fa-solid fa-cloud-arrow-up text-primary text-4xl mb-2"></i>
            <span class="text-primary font-medium">释放文件以上传</span>
            <span class="text-sm text-gray-500 mt-1">或点击上传附件按钮</span>
          </div>
        </div>
        <div class="flex items-center justify-between px-3 py-2 gap-2">
          <div class="flex items-center gap-3">
            <!-- 上传文件按钮 -->
            <Tooltip content="上传文件">
              <button
                  class="btn-secondary w-8 h-8 flex items-center justify-center rounded-lg transition-all duration-300 ease-in-out"
                  :class="{ 
                      'text-gray-500 dark:text-gray-300 bg-gray-50 dark:bg-dark-700 hover:bg-gray-100 dark:hover:bg-dark-600 hover:text-primary': uploadedFiles.length === 0, 
                      'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-900/40': uploadedFiles.length > 0 
                    }"
                @click="triggerFileUpload"
              >
                <i class="fa-solid fa-paperclip"></i>
              </button>
            </Tooltip>
            <!-- 隐藏的文件输入 -->
            <input
              ref="fileInput"
              type="file"
              class="hidden"
              @change="handleFileInputChange"
              multiple
              accept=".txt,.pdf,.doc,.docx,.md,.jpg,.jpeg,.png,.gif,.csv,.xlsx,.pptx"
            >
            <!-- 深度思考切换按钮 -->
            <Tooltip content="深度思考模式">
              <button
                class="btn-secondary flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-300 ease-in-out"
                :class="{ 
                    'text-gray-500 dark:text-gray-300 bg-gray-50 dark:bg-dark-700 hover:bg-gray-100 dark:hover:bg-dark-600 hover:text-primary': !isDeepThinking, 
                    'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-900/40': isDeepThinking 
                  }"
                @click="toggleDeepThinking"
              >
                <i class="fa-solid fa-lightbulb"></i>
              </button>
            </Tooltip>
            <!-- 联网搜索切换按钮 -->
            <Tooltip content="联网搜索">
              <button
                class="btn-secondary flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-300 ease-in-out"
                :class="{ 
                    'text-gray-500 dark:text-gray-300 bg-gray-50 dark:bg-dark-700 hover:bg-gray-100 dark:hover:bg-dark-600 hover:text-primary': !isWebSearchEnabled, 
                    'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-900/40': isWebSearchEnabled 
                  }"
                @click="toggleWebSearch"
              >
                <i class="fa-solid fa-globe"></i>
              </button>
            </Tooltip>
            <div class="relative">
              <Tooltip :content="availableModels.length > 1 ? '选择AI模型' : '只有一个可用模型'">
                <button
                  class="h-8 flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-dark-700 px-3 rounded-lg transition-all duration-300 ease-in-out"
                  :class="{
                    'btn-secondary hover:bg-gray-100 hover:text-primary cursor-pointer': availableModels.length > 1,
                    'cursor-default opacity-70': availableModels.length <= 1
                  }"
                  @click="toggleModelDropdown"
                >
                  <span>{{ currentModelDisplayName }}</span>
                  <i v-if="availableModels.length > 1" class="fa-solid fa-chevron-down text-xs text-neutral"></i>
                </button>
              </Tooltip>
              <div
                ref="modelDropdown"
                class="dropdown dropdown-content absolute left-0 bottom-full mb-2 w-48 bg-white z-50 depth-2"
                :class="{ 'hidden': !showModelDropdown }"
                style="z-index: 1000 !important"
              >
                <div class="py-1">
                  <button
                    v-for="model in orderedModels"
                    :key="model.value"
                    class="model-option w-full text-left px-4 py-2 text-sm hover:bg-gray-100 transition-colors"
                    :class="{ 'text-blue-600 bg-blue-50 dark:text-blue-400 dark:bg-blue-900/30': model.value === currentModel }"
                    @click="selectModel(model.value)"
                  >
                    {{ model.displayName }}
                  </button>
                </div>
              </div>
            </div>
          </div>
          <button
              v-if="!hasActiveStreaming"
              class="w-8 h-8 flex items-center justify-center text-white bg-primary hover:bg-secondary rounded-full transition-all duration-300 ease-in-out hover-scale"
            @click="handleSendMessage"
          >
            <i class="fa-solid fa-arrow-up"></i>
          </button>
          <Tooltip v-else content="终止输出">
            <button
              class="w-8 h-8 flex items-center justify-center text-white bg-red-500 hover:bg-red-600 rounded-full transition-all duration-300 ease-in-out hover-scale"
              @click="handleCancelStreaming"
            >
              <i class="fa-solid fa-stop"></i>
            </button>
          </Tooltip>
        </div>
      </div>
      <div v-if="showShortcutHint" class="text-center text-xs text-gray-400 dark:text-gray-500 mt-[18px] transition-opacity duration-300">
        按Shift+Enter换行，Enter发送
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { StorageManager } from '../../store/utils.js';
import Tooltip from '../common/Tooltip.vue';

// 接收从父组件传递的视图状态
const props = defineProps({
  activeView: {
    type: String,
    required: true
  },
  showShortcutHint: {
    type: Boolean,
    default: true
  }
});
import { useChatStore } from '../../store/chatStore.js';
import { useSettingsStore } from '../../store/settingsStore.js';
import { useModelSettingStore } from '../../store/modelSettingStore.js';

// 定义存储键
const STORAGE_KEYS = {
  DEEP_THINKING: 'deepThinkingMode',
  WEB_SEARCH: 'webSearchEnabled'
};

// 初始化stores
const chatStore = useChatStore();
const settingsStore = useSettingsStore();
const modelStore = useModelSettingStore();

// 使用ref引用DOM元素
const dragDropArea = ref(null);
const fileInput = ref(null);
const modelDropdown = ref(null);

// 本地UI状态
const isDragOver = ref(false);
const showModelDropdown = ref(false);
// 新增状态：检查是否有活动的流式输出
const hasActiveStreaming = ref(false);
// 深度思考模式状态 - 从存储加载
const isDeepThinking = ref(StorageManager.getItem(STORAGE_KEYS.DEEP_THINKING, false));
// 联网搜索状态 - 从存储加载
const isWebSearchEnabled = ref(StorageManager.getItem(STORAGE_KEYS.WEB_SEARCH, false));

// 自定义通知组件状态
const showNotification = ref(false);
const notificationTitle = ref('');
const notificationMessage = ref('');
const notificationType = ref('info');
let notificationTimer = null;
let notificationProgressTimer = null;

// 切换深度思考模式
const toggleDeepThinking = () => {
  isDeepThinking.value = !isDeepThinking.value;
  StorageManager.setItem(STORAGE_KEYS.DEEP_THINKING, isDeepThinking.value);
};

// 切换联网搜索模式
const toggleWebSearch = () => {
  isWebSearchEnabled.value = !isWebSearchEnabled.value;
  StorageManager.setItem(STORAGE_KEYS.WEB_SEARCH, isWebSearchEnabled.value);
};

// 从store获取当前聊天的模型，默认使用settingsStore中的默认模型
// 注意：聊天界面选择模型不会修改系统默认设置，只影响当前聊天
const currentModel = ref(settingsStore.systemSettings.defaultModel);

// 监听系统默认模型变化，更新当前模型（如果用户没有手动选择过）
let userHasSelectedModel = false;

watch(
  () => settingsStore.systemSettings.defaultModel,
  (newDefaultModel) => {
    if (!userHasSelectedModel && newDefaultModel) {
      currentModel.value = newDefaultModel;
    }
  }
);

// 获取当前模型的显示名称，与默认模型下拉框显示规则保持一致
const currentModelDisplayName = computed(() => {
  // 当没有可用模型时显示提示信息
  if ((!availableModels.value || availableModels.value.length === 0)) {
    return '暂无可用模型';
  }
  
  if (!currentModel.value || !modelStore.allModels.length) {
    return currentModel.value;
  }
  
  // 遍历所有模型，找到匹配的模型
  for (const model of modelStore.allModels) {
    if (model.versions) {
      for (const version of model.versions) {
        // 构建select组件使用的模型ID格式：model.name-version_name
        const selectModelId = `${model.name}-${version.version_name}`;
        // 同时检查select组件格式和直接匹配version_name/custom_name
        if (selectModelId === currentModel.value || 
            version.version_name === currentModel.value || 
            version.custom_name === currentModel.value) {
          // 使用模型的name
          const modelDisplay = model.name;
          // 优先使用版本的custom_name，否则使用版本的version_name
          const versionDisplay = version.custom_name || version.version_name;
          // 返回格式：name-versionDisplay（与默认模型下拉框保持一致）
          return `${modelDisplay}-${versionDisplay}`;
        }
      }
    }
  }
  
  return currentModel.value;
});

// 获取格式化后的模型列表（包含displayName和原始model值），与默认模型下拉框显示规则保持一致
const formattedModels = computed(() => {
  // 确保availableModels是数组
  const modelsList = availableModels.value || [];
  
  if (!modelStore.allModels.length) {
    return modelsList.map(model => ({ 
      value: model, 
      displayName: model 
    }));
  }
  
  const result = [];
  
  // 遍历availableModels中的每个模型名
  for (const modelName of modelsList) {
    let found = false;
    
    // 遍历所有模型和版本，找到匹配的模型
    for (const model of modelStore.allModels) {
      if (model.versions) {
        for (const version of model.versions) {
          // 构建select组件使用的模型ID格式：model.name-version_name
          const selectModelId = `${model.name}-${version.version_name}`;
          // 同时检查select组件格式和直接匹配version_name/custom_name
          if (selectModelId === modelName || 
              version.version_name === modelName || 
              version.custom_name === modelName) {
            // 使用模型的name
            const modelDisplay = model.name;
            // 优先使用版本的custom_name，否则使用版本的version_name
            const versionDisplay = version.custom_name || version.version_name;
            // 返回格式：name-versionDisplay（与默认模型下拉框保持一致）
            result.push({
              value: modelName,
              displayName: `${modelDisplay}-${versionDisplay}`
            });
            found = true;
            break;
          }
        }
        if (found) break;
      }
    }
    
    // 如果没找到匹配的模型，使用原始名称
    if (!found) {
      result.push({ value: modelName, displayName: modelName });
    }
  }
  
  return result;
});

// 获取可用模型列表，确保始终返回数组
const availableModels = computed(() => modelStore.availableModelList || []);

// 排序模型列表，使当前选中的模型在最底部
const orderedModels = computed(() => {
  // 确保formattedModels是数组
  const models = [...(formattedModels.value || [])];
  const currentModelIndex = models.findIndex(m => m.value === currentModel.value);
  
  if (currentModelIndex !== -1) {
    // 保存当前选中的模型
    const currentModelObj = models[currentModelIndex];
    // 从数组中移除当前选中的模型
    models.splice(currentModelIndex, 1);
    // 将当前选中的模型添加到数组末尾
    models.push(currentModelObj);
  }
  
  return models;
});

const messageInput = computed({
  get: () => chatStore.messageInput,
  set: (value) => chatStore.updateMessageInput(value),
});

// 从store直接获取响应式数据
const uploadedFiles = computed(() => chatStore.uploadedFiles);

// 定义事件
const emit = defineEmits(['sendMessage']);

// 处理发送消息事件
const handleSendMessage = async () => {
  if (messageInput.value.trim()) {
    // 先保存当前需要发送的消息内容和模型
    const messageToSend = messageInput.value;
    const modelToUse = currentModel.value;
    const deepThinking = isDeepThinking.value;
    const webSearchEnabled = isWebSearchEnabled.value;
    
    // 立即发送消息，不等待Ollama服务检查
    emit('sendMessage', messageToSend, modelToUse, deepThinking, webSearchEnabled);
    // 发送消息后立即检查是否有流式输出
    checkForActiveStreaming();
    
    // 如果是Ollama模型，在后台异步检查和启动服务
    if (modelToUse.includes('Ollama')) {
      // 使用setTimeout将检查操作放入事件队列，避免阻塞UI
      setTimeout(async () => {
        try {
          // 动态导入Tauri API，避免在非Tauri环境中出错
          const { invoke } = await import('@tauri-apps/api/core');
          
          // 检查Ollama服务状态
          const ollamaStatus = await invoke('check_ollama_service');
          
          if (!ollamaStatus.installed) {
            // Ollama未安装，显示提示
            displayNotification('error', '提示', 'Ollama未安装，请先安装Ollama后再使用该模型', 3000);
          } else if (!ollamaStatus.running) {
            // 如果服务没有运行，启动它
            await invoke('start_ollama_service');
            // 显示服务正在启动的提示
            displayNotification('info', '提示', 'Ollama服务正在启动，请稍候...', 3000);
          }
        } catch (error) {
          console.error('Ollama服务管理失败:', error);
          // 显示更具体的错误信息
          displayNotification('error', '错误', `Ollama服务管理失败: ${error.message || error}`, 3000);
        }
      }, 0);
    }
  }
};

// 监听当前聊天变化，重置用户选择标志
watch(
  () => chatStore.currentChatId,
  () => {
    // 新聊天时，重置用户选择标志，使用系统默认模型
    userHasSelectedModel = false;
    currentModel.value = settingsStore.systemSettings.defaultModel || modelStore.currentSelectedModel;
  }
);

// 处理取消流式输出
const handleCancelStreaming = () => {
  chatStore.cancelStreaming();
  hasActiveStreaming.value = false;
};

// 显示通知
const displayNotification = (type = 'info', title = '', message = '', duration = 3000) => {
  // 清除之前的定时器
  hideNotification();
  
  // 设置通知内容
  notificationType.value = type;
  notificationTitle.value = title;
  notificationMessage.value = message;
  
  // 显示通知
  showNotification.value = true;
  
  // 触发进度条动画
  setTimeout(() => {
    const progressBar = document.querySelector('.notification-progress');
    if (progressBar) {
      // 重置进度条
      progressBar.style.width = '100%';
      progressBar.style.transition = 'none';
      
      // 触发重排
      void progressBar.offsetWidth;
      
      // 设置动画
      progressBar.style.transition = `width ${duration - 100}ms ease-linear`;
      progressBar.style.width = '0%';
    }
  }, 10);
  
  // 设置自动关闭定时器
  notificationTimer = setTimeout(() => {
    hideNotification();
  }, duration);
};

// 隐藏通知
const hideNotification = () => {
  if (notificationTimer) {
    clearTimeout(notificationTimer);
    notificationTimer = null;
  }
  
  showNotification.value = false;
};

// 检查是否有活动的流式输出
const checkForActiveStreaming = () => {
  if (!settingsStore.systemSettings.streamingEnabled) {
    hasActiveStreaming.value = false;
    return;
  }
  
  const currentMessages = chatStore.currentChatMessages;
  if (currentMessages.length > 0) {
    const lastMessage = currentMessages[currentMessages.length - 1];
    const messageData = lastMessage?.value || lastMessage;
    hasActiveStreaming.value = messageData?.status === 'streaming' || messageData?.isTyping === true;
  } else {
    hasActiveStreaming.value = false;
  }
};

// 监听聊天消息变化，检查流式输出状态
watch(
  () => chatStore.currentChatMessages,
  () => {
    checkForActiveStreaming();
  },
  { deep: true }
);

// 监听isLoading状态变化，检查流式输出状态
watch(
  () => chatStore.isLoading,
  (newVal) => {
    if (!newVal) {
      // 加载完成后，流式输出也应该结束
      setTimeout(() => {
        checkForActiveStreaming();
      }, 100);
    }
  }
);

// 切换模型下拉菜单显示状态
const toggleModelDropdown = () => {
  // 只有当可用模型数量大于1时才允许切换下拉菜单
  if (availableModels.value.length > 1) {
    showModelDropdown.value = !showModelDropdown.value;
  }
};

// 选择模型
const selectModel = (model) => {
  currentModel.value = model;
  // 设置标志，表明用户已经手动选择了模型
  userHasSelectedModel = true;
  showModelDropdown.value = false;
};

// 点击外部关闭下拉菜单
const handleClickOutside = (event) => {
  if (modelDropdown.value && !modelDropdown.value.contains(event.target) &&
      !event.target.closest('.btn-secondary') && showModelDropdown.value) {
    showModelDropdown.value = false;
  }
};

// 生命周期钩子
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

// 处理文件拖放
const handleDrop = (e) => {
  isDragOver.value = false;
  if (e.dataTransfer.files.length > 0) {
    handleFileUpload(e.dataTransfer.files);
  }
};

// 触发文件上传对话框
const triggerFileUpload = () => {
  if (fileInput.value) {
    fileInput.value.click();
  }
};

// 处理文件输入变化事件
const handleFileInputChange = (e) => {
  if (e.target.files.length > 0) {
    handleFileUpload(e.target.files);
    // 重置输入，以便可以重复上传同一个文件
    e.target.value = '';
  }
};

// 处理上传文件事件
const handleFileUpload = (files) => {
  // 将文件添加到上传列表
  Array.from(files).forEach((file) => {
    chatStore.addUploadedFile(file);
  });
};

// 移除已上传的文件
const removeUploadedFile = (index) => {
  chatStore.removeUploadedFile(index);
};

// 获取文件图标
const getFileIcon = (fileName) => {
  const extension = fileName.split('.').pop().toLowerCase();
  
  const iconMap = {
    txt: 'fa-file-lines',
    pdf: 'fa-file-pdf',
    doc: 'fa-file-word',
    docx: 'fa-file-word',
    md: 'fa-file-lines',
    jpg: 'fa-file-image',
    jpeg: 'fa-file-image',
    png: 'fa-file-image',
    gif: 'fa-file-image',
    csv: 'fa-file-excel',
    xlsx: 'fa-file-excel',
    pptx: 'fa-file-powerpoint'
  };
  
  return iconMap[extension] || 'fa-file';
};

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B';
  else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
  else return (bytes / 1048576).toFixed(1) + ' MB';
};

</script>

<style scoped>
/* 卡片阴影效果 - 增加特异性确保样式应用 */
.card {
  border-radius: 20px !important;
  border: 1px solid #e5e7eb !important;
  overflow: visible;
  transition: box-shadow 0.3s ease;
}

/* 深度效果 - 增加特异性确保样式应用 */
.depth-1 {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
}

.depth-1:hover {
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
}

.depth-2 {
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
}

/* 按钮悬停效果 */
.hover-scale:hover {
  transform: scale(1.05);
}

/* 焦点环效果 */
.focus-ring:focus {
  outline: 2px solid rgba(66, 153, 225, 0.5);
  outline-offset: 2px;
}

/* 下拉菜单动画 */
.dropdown-content {
  animation: dropdownFade 0.2s ease-in-out;
  border-radius: 8px;
}

@keyframes dropdownFade {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 模型选项样式 */
.model-option {
  border-radius: 8px;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.model-option:hover {
  background-color: #f8fafc !important;
}

/* 深色模式样式 */
.dark .dropdown-content {
  background-color: #334155 !important;
  border-color: #475569 !important;
}

.dark .model-option {
  color: #e2e8f0;
}

.dark .model-option:hover {
  background-color: #475569 !important;
}

.dark .btn-secondary {
    background-color: transparent;
    color: #e2e8f0;
  border-color: #475569;
}

.dark .btn-secondary:hover {
    background-color: transparent;
    border-color: #64748b;
}
</style>