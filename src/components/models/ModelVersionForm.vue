<template>
  <!-- 模型版本表单模态框 - 支持添加和编辑 -->
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 hidden" ref="modelVersionModal">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg dark:shadow-panel-dark w-full max-w-md max-h-[90vh] overflow-hidden">
      <div class="panel-header p-3 flex justify-between items-center border-b dark:border-gray-700">
        <h3 class="text-lg font-semibold dark:text-white">{{ isEditMode ? '编辑模型版本' : '添加模型版本' }}</h3>
        <button @click="hideModal" class="btn-secondary p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full text-neutral dark:text-gray-300">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <div class="p-6 overflow-y-auto max-h-[calc(90vh-100px)]">
        <form @submit.prevent="handleSubmit">
          <input type="hidden" v-model="versionId" />
          <div class="space-y-6">
            <div>
              <label class="block text-sm font-medium mb-2 dark:text-gray-300">模型名称</label>
              <input
                type="text"
                v-model="modelName"
                :class="['input-field w-full px-3 py-2 focus:outline-none focus:ring-1', errors.modelName ? 'border-red-500 focus:ring-red-500' : 'focus:ring-primary', 'dark:bg-gray-700 dark:text-white dark:border-gray-600']"
                readonly
                @input="errors.modelName = ''"
              />
              <p v-if="errors.modelName" class="text-xs text-red-500 mt-1">{{ errors.modelName }}</p>
            </div>

            <div>
              <label class="block text-sm font-medium mb-2 dark:text-gray-300">模型版本 <span class="text-red-500">*</span></label>
              <input
                type="text"
                v-model="modelVersion"
                :class="['input-field w-full px-3 py-2 focus:outline-none focus:ring-1', errors.modelVersion ? 'border-red-500 focus:ring-red-500' : 'focus:ring-primary', 'dark:bg-gray-700 dark:text-white dark:border-gray-600']"
                :placeholder="isEditMode ? '' : '例如：gpt-4, gpt-3.5-turbo, claude-3-opus-20240229等'"
                :readonly="isEditMode"
                @input="errors.modelVersion = ''"
              />
              <p v-if="errors.modelVersion" class="text-xs text-red-500 mt-1">{{ errors.modelVersion }}</p>
            </div>

            <div>
              <label class="block text-sm font-medium mb-2 dark:text-gray-300">自定义名字</label>
              <input
                type="text"
                v-model="modelCustomName"
                class="input-field w-full px-3 py-2 focus:outline-none focus:ring-1 focus:ring-primary dark:bg-gray-700 dark:text-white dark:border-gray-600"
                placeholder="为模型设置用于显示的名字"
              />
            </div>

            <div>
              <label class="block text-sm font-medium mb-2 dark:text-gray-300">API 密钥 <span v-if="!isOllama" class="text-red-500">*</span></label>
              <input
                type="password"
                v-model="apiKey"
                :class="['input-field w-full px-3 py-2 focus:outline-none focus:ring-1', errors.apiKey ? 'border-red-500 focus:ring-red-500' : 'focus:ring-primary', 'dark:bg-gray-700 dark:text-white dark:border-gray-600']"
                :placeholder="isOllama ? 'Ollama不需要密钥' : 'sk-...'"
                @input="errors.apiKey = ''"
                :disabled="isOllama"
              />
              <p v-if="errors.apiKey" class="text-xs text-red-500 mt-1">{{ errors.apiKey }}</p>
              <p v-else-if="isOllama" class="text-xs text-green-500 mt-1">Ollama不需要API密钥</p>
            </div>

            <div>
              <label class="block text-sm font-medium mb-2 dark:text-gray-300">API 基础 URL <span class="text-red-500">*</span></label>
              <input
                type="text"
                v-model="apiBaseUrl"
                :class="['input-field w-full px-3 py-2 focus:outline-none focus:ring-1', errors.apiBaseUrl ? 'border-red-500 focus:ring-red-500' : 'focus:ring-primary', 'dark:bg-gray-700 dark:text-white dark:border-gray-600']"
                placeholder="https://api.openai.com"
                @input="errors.apiBaseUrl = ''"
              />
              <p v-if="errors.apiBaseUrl" class="text-xs text-red-500 mt-1">{{ errors.apiBaseUrl }}</p>
            </div>

            <div class="pt-4 border-t border-gray-100 dark:border-gray-700">
              <label class="flex items-center">
                <input type="checkbox" v-model="streamingConfig" class="rounded text-primary focus:ring-primary dark:bg-gray-700 dark:border-gray-600" />
                <span class="ml-2 text-sm dark:text-gray-300">是否支持流式响应</span>
              </label>
            </div>
          </div>

          <div class="mt-8 flex justify-end gap-3">
            <button
              type="button"
              @click="hideModal"
              class="btn btn-secondary px-4 py-2 rounded-lg text-sm hover:bg-gray-50 dark:hover:bg-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-600 transition-colors hover-scale"
            >
              取消
            </button>
            <button
              type="submit"
              class="btn btn-primary px-4 py-2 text-white rounded-lg text-sm hover:bg-[#4338ca] hover:shadow-md transform hover:-translate-y-0.5 transition-all hover-scale"
            >
              保存
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useModelSettingStore } from '../../store/modelSettingStore.js';
import { eventBus } from '../../services/eventBus.js';
import { showNotification } from '../../services/notificationUtils.js';

// 定义组件名称
defineOptions({
  name: 'ModelVersionForm'
});

// 初始化store
const modelStore = useModelSettingStore();

// 表单数据
const isEditMode = ref(false);
const versionId = ref('');
const modelName = ref('');
const modelVersion = ref('');
const modelCustomName = ref('');
const apiKey = ref('');
const apiBaseUrl = ref('');
const streamingConfig = ref(false);

// 判断是否为Ollama模型
const isOllama = computed(() => {
  return modelName.value && modelName.value.toLowerCase() === 'ollama';
});

// 错误状态对象
const errors = ref({
    modelName: '',
    modelVersion: '',
    apiKey: '',
    apiBaseUrl: ''
  });

// 模态框引用
const modelVersionModal = ref(null);

// 显示模态框（添加模式）
const showAddModal = (modelNameValue) => {
  isEditMode.value = false;
  versionId.value = '';
  modelName.value = modelNameValue || '';
  modelVersion.value = '';
  modelCustomName.value = '';
  apiKey.value = '';
  apiBaseUrl.value = '';
  streamingConfig.value = false;
  clearErrors();
  
  if (modelVersionModal.value) {
    modelVersionModal.value.classList.remove('hidden');
  }
};

// 显示模态框（编辑模式）
const showEditModal = (data) => {
  isEditMode.value = true;
  populateFormData(data);
  clearErrors();
  
  if (modelVersionModal.value) {
    modelVersionModal.value.classList.remove('hidden');
  }
};

// 隐藏模态框
const hideModal = () => {
  if (modelVersionModal.value) {
    modelVersionModal.value.classList.add('hidden');
  }
};

// 清除错误信息
const clearErrors = () => {
  errors.value.modelName = '';
  errors.value.modelVersion = '';
  errors.value.apiKey = '';
  errors.value.apiBaseUrl = '';
};

// 处理表单提交
const handleSubmit = async () => {
  try {
    // 清除之前的错误
    clearErrors();
    
    // 表单验证
    let hasError = false;
    
    if (!modelName.value) {
      errors.value.modelName = '模型名称不能为空';
      hasError = true;
    }
    
    if (!modelVersion.value) {
      errors.value.modelVersion = '请输入模型版本';
      hasError = true;
    }
    
    if (!isOllama.value && !apiKey.value.trim()) {
      errors.value.apiKey = '请输入API密钥';
      hasError = true;
    }
    
    if (!apiBaseUrl.value.trim()) {
      errors.value.apiBaseUrl = '请输入API基础URL';
      hasError = true;
    }
    
    if (hasError) {
      return;
    }

    // 构建请求数据
    const versionConfig = {
      customName: modelCustomName.value,
      apiKey: apiKey.value,
      apiBaseUrl: apiBaseUrl.value,
      versionName: modelVersion.value,
      streamingConfig: streamingConfig.value
    };

    if (isEditMode.value) {
      // 使用modelStore更新模型版本
      await modelStore.updateModelVersion(modelName.value, modelVersion.value, versionConfig);
    } else {
      // 使用modelStore添加模型版本
      await modelStore.addModelVersion(modelName.value, versionConfig);
    }

    // 显示成功提示
    showNotification('模型版本配置已保存', 'success');
    
    // 清除错误
    clearErrors();

    // 隐藏模态框
    hideModal();

    // 通过事件总线通知模型已更新
    eventBus.emit('modelUpdated');
  } catch (error) {
    console.error('保存模型版本配置失败:', error);
    showNotification(`保存失败: ${error.message || '未知错误'}`, 'error');
  }
};

// 填充表单数据
const populateFormData = (data) => {
  versionId.value = data.id || '';
  modelName.value = data.modelName || '';
  // 处理modelVersion可能是对象的情况
  if (typeof data.modelVersion === 'object' && data.modelVersion !== null) {
    // 只显示name属性
    modelVersion.value = data.modelVersion.version_name;
  } else {
    modelVersion.value = data.modelVersion || '';
  }
  modelCustomName.value = data.customName || '';
  apiKey.value = data.apiKey || '';
  apiBaseUrl.value = data.apiBaseUrl || 'https://api.openai.com';
  streamingConfig.value = data.streaming || false;
};

// 暴露方法给父组件
defineExpose({
  showAddModal,
  showEditModal,
  hideModal,
  handleSubmit,
  populateFormData
});
</script>

<style scoped>
/* 组件特定样式 */
.panel-header {
  border-bottom: 1px solid #e5e7eb;
}

.dark .panel-header {
  border-bottom-color: #374151;
}

.input-field {
  transition: all 0.2s ease;
  border: 1px solid #e2e8f0;
  background-color: white;
  border-radius: 6px;
}

.dark .input-field {
  border-color: #374151;
  background-color: #1f2937;
  color: white;
}

.input-field:focus {
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
  transform: translateY(-0.5px);
}

.dark .input-field:focus {
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2);
}

.btn {
  border-radius: 0.375rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-primary {
  background-color: #4f46e5;
  color: white;
}

.btn-primary:hover {
  background-color: #3b82f6;
}

.btn-secondary {
  background-color: white;
  color: #64748b;
  border-color: #e2e8f0;
}

.btn-secondary:hover {
  background-color: #f8fafc;
  border-color: #cbd5e1;
  transform: translateY(-1px);
}

.dark .btn-secondary {
  background-color: #1f2937;
  color: #d1d5db;
  border-color: #374151;
}

.dark .btn-secondary:hover {
  background-color: #374151;
  border-color: #4b5563;
}

.hover-scale {
  transition: transform 0.2s ease;
}

.hover-scale:hover {
  transform: scale(1.02);
}
</style>
