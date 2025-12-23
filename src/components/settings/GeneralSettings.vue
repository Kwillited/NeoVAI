<template>
  <div class="space-y-6 max-w-2xl mx-auto">
    <div class="card p-5 depth-1 hover:depth-2 transition-all duration-300">
      <div class="flex items-center">
        <img
          src="https://picsum.photos/id/64/60/60"
          alt="用户头像"
          class="w-14 h-14 rounded-full mr-4 border-2 border-white shadow-sm"
        />
        <div>
          <div class="font-medium">Administrator</div>
          <div class="text-sm text-neutral">Administrator@example.com</div>
        </div>
      </div>
    </div>

    <div class="card depth-1 hover:depth-2 transition-all duration-300">
      <!-- 选项卡导航 -->
      <div class="border-b">
        <div class="flex">
          <button
            class="px-6 py-3 text-sm font-medium border-b-2 transition-colors"
            :class="activeTab === 'chat' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
            @click="activeTab = 'chat'"
          >
            对话设置
          </button>
          <button
            class="px-6 py-3 text-sm font-medium border-b-2 transition-colors"
            :class="activeTab === 'style' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
            @click="activeTab = 'style'"
          >
            样式设置
          </button>
          <button
            class="px-6 py-3 text-sm font-medium border-b-2 transition-colors"
            :class="activeTab === 'knowledgeGraph' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
            @click="activeTab = 'knowledgeGraph'"
          >
            <i class="fa-solid fa-network-wired mr-2"></i>知识图谱样式
          </button>
        </div>
      </div>
      
      <!-- 对话设置选项卡内容 -->
      <div v-show="activeTab === 'chat'" class="p-4">
        <div class="space-y-4">

          <div class="setting-item p-3 rounded-lg">
            <div class="flex justify-between items-center">
              <div>
                <div class="font-medium text-sm">启用流式输出</div>
                <div class="text-xs text-neutral mt-0.5">启用后，对话将以流式方式输出，而不是等待全部生成完成</div>
              </div>
              <label class="toggle-switch">
                <input type="checkbox" :checked="settingsStore.systemSettings.streamingEnabled" @change="toggleStreaming" />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>

          <div class="setting-item p-3 rounded-lg">
            <div>
              <div class="font-medium text-sm">默认模型</div>
              <div class="text-xs text-neutral mt-0.5">新对话默认使用的AI模型</div>

              <!-- 自定义下拉框实现 -->
              <div class="relative">
                <!-- 当没有模型时，显示一个只读的输入框 -->
                <input
                  v-if="!isLoading && allModelVersions.length === 0"
                  type="text"
                  value="请先配置模型"
                  class="input-field w-full text-sm px-2 py-1.5 mt-2 focus:outline-none bg-gray-50 text-gray-500 cursor-not-allowed"
                  readonly
                />
                <!-- 正常的下拉框 -->
                <select
                  v-else
                  class="input-field w-full text-sm px-2 py-1.5 mt-2 focus:outline-none focus:ring-1 focus:ring-primary"
                  v-model="defaultModel"
                  @change="setDefaultModel"
                >
                  <option v-if="isLoading" value="">加载中...</option>
                  <option v-else-if="allModelVersions.length > 0" :value="''" disabled>选择默认模型</option>
                  <option v-for="version in allModelVersions" :key="version.id" :value="version.id">{{ version.displayName }}</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 样式设置选项卡内容 -->
      <div v-show="activeTab === 'style'" class="p-4">
        <div class="space-y-4">
          <div class="setting-item p-3 rounded-lg">
            <div class="flex justify-between items-center">
              <div>
                <div class="font-medium text-sm">深色模式</div>
                <div class="text-xs text-neutral mt-0.5">启用后，界面将切换到深色主题，减轻夜间使用时的视觉疲劳</div>
              </div>
              <label class="toggle-switch">
                <input type="checkbox" :checked="settingsStore.systemSettings.darkMode" @change="toggleDarkMode" />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
          <div class="setting-item p-3 rounded-lg">
            <div>
              <div class="font-medium text-sm">对话样式</div>
              <div class="text-xs text-neutral mt-0.5">选择对话界面的显示样式</div>

              <div class="flex gap-3 mt-2">
                <button
                  id="chatStyleBubble"
                  class="chat-style-btn flex-1 py-2 px-3 text-sm border rounded-lg transition-all duration-300 hover:bg-gray-50"
                  :class="settingsStore.systemSettings.chatStyleDocument ? 'border-gray-200 bg-white text-gray-700' : 'border-primary bg-primary/10 text-primary active'"
                  @click="setChatStyle('bubble')"
                >
                  <i class="fa-regular fa-comment mr-2"></i>气泡模式
                </button>
                <button
                  id="chatStyleDocument"
                  class="chat-style-btn flex-1 py-2 px-3 text-sm border rounded-lg transition-all duration-300 hover:bg-gray-50"
                  :class="settingsStore.systemSettings.chatStyleDocument ? 'border-primary bg-primary/10 text-primary active' : 'border-gray-200 bg-white text-gray-700'"
                  @click="setChatStyle('document')"
                >
                  <i class="fa-regular fa-file-lines mr-2"></i>文档样式
                </button>
              </div>
            </div>
          </div>

          <div class="setting-item p-3 rounded-lg">
            <div>
              <div class="font-medium text-sm">文件视图模式</div>
              <div class="text-xs text-neutral mt-0.5">选择RAG文件管理界面的显示方式</div>

              <div class="flex gap-3 mt-2">
                <button
                  id="viewModeGrid"
                  class="chat-style-btn flex-1 py-2 px-3 text-sm border rounded-lg transition-all duration-300 hover:bg-gray-50"
                  :class="settingsStore.systemSettings.viewMode === 'grid' ? 'border-primary bg-primary/10 text-primary active' : 'border-gray-200 bg-white text-gray-700'"
                  @click="setViewMode('grid')"
                >
                  <i class="fa-solid fa-th mr-2"></i>网格视图
                </button>
                <button
                  id="viewModeList"
                  class="chat-style-btn flex-1 py-2 px-3 text-sm border rounded-lg transition-all duration-300 hover:bg-gray-50"
                  :class="settingsStore.systemSettings.viewMode === 'list' ? 'border-primary bg-primary/10 text-primary active' : 'border-gray-200 bg-white text-gray-700'"
                  @click="setViewMode('list')"
                >
                  <i class="fa-solid fa-list mr-2"></i>列表视图
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 知识图谱样式选项卡内容 -->
      <div v-show="activeTab === 'knowledgeGraph'" class="p-4">
        <div class="space-y-4">
          <div class="setting-item p-3 rounded-lg">
            <div>
              <div class="font-medium text-sm">知识图谱布局</div>
              <div class="text-xs text-neutral mt-0.5">选择知识图谱的展示布局方式</div>

              <div class="flex gap-3 mt-2">
                <button
                  id="graphLayoutForce"
                  class="chat-style-btn flex-1 py-2 px-3 text-sm border rounded-lg transition-all duration-300 hover:bg-gray-50"
                  :class="settingsStore.systemSettings.graphLayout === 'force' ? 'border-primary bg-primary/10 text-primary active' : 'border-gray-200 bg-white text-gray-700'"
                  @click="setGraphLayout('force')"
                >
                  <i class="fa-solid fa-arrows-rotate mr-2"></i>力导向布局
                </button>
                <button
                  id="graphLayoutHierarchical"
                  class="chat-style-btn flex-1 py-2 px-3 text-sm border rounded-lg transition-all duration-300 hover:bg-gray-50"
                  :class="settingsStore.systemSettings.graphLayout === 'hierarchical' ? 'border-primary bg-primary/10 text-primary active' : 'border-gray-200 bg-white text-gray-700'"
                  @click="setGraphLayout('hierarchical')"
                >
                  <i class="fa-solid fa-sitemap mr-2"></i>层次布局
                </button>
              </div>
            </div>
          </div>

          <div class="setting-item p-3 rounded-lg">
            <div>
              <div class="font-medium text-sm">节点大小</div>
              <div class="text-xs text-neutral mt-0.5">调整知识图谱中节点的显示大小</div>
              
              <div class="mt-2">
                <input
                  type="range"
                  min="20"
                  max="80"
                  step="5"
                  v-model="graphNodeSize"
                  @input="updateGraphNodeSize"
                  class="w-full accent-primary"
                />
                <div class="flex justify-between text-xs text-neutral mt-1">
                  <span>小</span>
                  <span>{{ graphNodeSize }}px</span>
                  <span>大</span>
                </div>
              </div>
            </div>
          </div>

          <div class="setting-item p-3 rounded-lg">
            <div class="flex justify-between items-center">
              <div>
                <div class="font-medium text-sm">显示节点标签</div>
                <div class="text-xs text-neutral mt-0.5">在节点上显示标签文本</div>
              </div>
              <label class="toggle-switch">
                <input type="checkbox" :checked="settingsStore.systemSettings.showGraphNodeLabels" @change="toggleGraphNodeLabels" />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>

          <div class="setting-item p-3 rounded-lg">
            <div class="flex justify-between items-center">
              <div>
                <div class="font-medium text-sm">动画效果</div>
                <div class="text-xs text-neutral mt-0.5">为知识图谱添加动态布局效果</div>
              </div>
              <label class="toggle-switch">
                <input type="checkbox" :checked="settingsStore.systemSettings.graphAnimations" @change="toggleGraphAnimations" />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useSettingsStore } from '../../store/settingsStore.js';
import { useModelSettingStore } from '../../store/modelSettingStore.js';
import { eventBus } from '../../services/eventBus.js';
import { showNotification } from '../../services/notificationUtils.js';

const settingsStore = useSettingsStore();
const modelStore = useModelSettingStore();

// 状态管理
const isLoading = ref(false);
const models = ref([]);
const defaultModel = ref('');
const activeTab = ref('chat'); // 默认选中对话设置选项卡

// 计算属性：所有可用的模型版本
const allModelVersions = computed(() => {
  const versions = [];
  
  models.value.forEach(model => {
    if (model.configured && model.enabled && model.versions) {
      model.versions.forEach(version => {
        // 只使用version_name字段
        const versionName = version?.version_name;
        if (versionName) {
          // 构造模型版本标识，格式为 "name-versionName"
          const id = `${model.name}-${versionName}`;
          const displayName = `${model.name}-${version.custom_name || versionName}`;
          
          versions.push({
            id,
            displayName
          });
        }
      });
    }
  });
  
  return versions;
});

// 从后端加载模型列表
async function loadModels() {
  try {
    isLoading.value = true;
    
    // 从模型设置store获取模型数据
    if (modelStore.allModels && modelStore.allModels.length > 0) {
      models.value = modelStore.allModels;
    } else {
      // 如果模型数据尚未加载，则触发加载
      await modelStore.loadModels();
      models.value = modelStore.allModels;
    }
    
    // 加载系统设置中的默认模型
    defaultModel.value = settingsStore.getDefaultModel();
    
    // 如果系统设置中没有默认模型，但模型存储中有选择，则使用它
    if (!defaultModel.value && modelStore.selectedModel) {
      defaultModel.value = modelStore.selectedModel;
      settingsStore.setDefaultModel(defaultModel.value);
    }
    
    // 如果有模型但没有选择默认模型，自动选择第一个模型
    if (!defaultModel.value && allModelVersions.value.length > 0) {
      defaultModel.value = allModelVersions.value[0].id;
      settingsStore.setDefaultModel(defaultModel.value);
      modelStore.selectModel(defaultModel.value);
      eventBus.emit('modelSelected', { model: defaultModel.value });
    }
    
    // 确保在没有模型时，默认显示为空字符串，这样可以显示disabled的提示选项
    if (allModelVersions.value.length === 0) {
      defaultModel.value = '';
    }
  } catch (error) {
    console.error('加载模型列表失败:', error);
  } finally {
    isLoading.value = false;
  }
}

// 设置默认模型
function setDefaultModel() {
  if (!defaultModel.value) return;
  
  try {
    // 设置到系统设置中
    settingsStore.setDefaultModel(defaultModel.value);
    
    // 同步到模型设置store
    modelStore.selectModel(defaultModel.value);
    
    // 发送模型选择变更事件
    eventBus.emit('modelSelected', { model: defaultModel.value });
    
    // 显示成功提示
    showNotification('默认模型已设置', 'success');
  } catch (error) {
    console.error('设置默认模型失败:', error);
    showNotification('设置失败: ' + error.message, 'error');
  }
}

// 监听模型列表更新
function handleModelsUpdated({ models: updatedModels }) {
  models.value = updatedModels;
  
  // 检查当前默认模型是否仍然存在于可用模型中
  const isDefaultModelStillAvailable = allModelVersions.value.some(
    version => version.id === defaultModel.value
  );
  
  // 如果默认模型不再可用，且还有其他可用模型，则自动选择第一个可用模型
  if (!isDefaultModelStillAvailable && allModelVersions.value.length > 0) {
    defaultModel.value = allModelVersions.value[0].id;
    settingsStore.setDefaultModel(defaultModel.value);
    modelStore.selectModel(defaultModel.value);
    eventBus.emit('modelSelected', { model: defaultModel.value });
    showNotification('默认模型已更新为: ' + allModelVersions.value[0].displayName, 'success');
  } else if (!isDefaultModelStillAvailable && allModelVersions.value.length === 0) {
    // 如果没有可用模型，清除默认模型设置
    defaultModel.value = '';
    settingsStore.setDefaultModel('');
    modelStore.selectModel('');
  }
}

onMounted(async () => {
  // 确保深色模式立即应用
  settingsStore.applyDarkMode();
  
  // 加载模型列表和默认模型设置
  await loadModels();
  
  // 监听模型列表更新事件
  eventBus.on('modelsUpdated', handleModelsUpdated);
});

onUnmounted(() => {
  // 移除事件监听
  eventBus.off('modelsUpdated', handleModelsUpdated);
});

// 设置聊天样式
const setChatStyle = (style) => {
  settingsStore.updateSystemSettings({
    chatStyleDocument: style === 'document'
  });
};

// 设置文件视图模式
const setViewMode = (mode) => {
  settingsStore.updateSystemSettings({
    viewMode: mode
  });
};

// 切换深色模式
const toggleDarkMode = () => {
  settingsStore.toggleDarkMode();
};

// 切换流式输出设置
const toggleStreaming = () => {
  settingsStore.updateSystemSettings({
    streamingEnabled: !settingsStore.systemSettings.streamingEnabled
  });
};

// 设置知识图谱布局
const setGraphLayout = (layout) => {
  settingsStore.updateSystemSettings({
    graphLayout: layout
  });
};

// 知识图谱节点大小
const graphNodeSize = ref(settingsStore.systemSettings.graphNodeSize || 40);

// 更新知识图谱节点大小
const updateGraphNodeSize = () => {
  settingsStore.updateSystemSettings({
    graphNodeSize: parseInt(graphNodeSize.value)
  });
};

// 切换显示节点标签
const toggleGraphNodeLabels = () => {
  settingsStore.updateSystemSettings({
    showGraphNodeLabels: !settingsStore.systemSettings.showGraphNodeLabels
  });
};

// 切换知识图谱动画
const toggleGraphAnimations = () => {
  settingsStore.updateSystemSettings({
    graphAnimations: !settingsStore.systemSettings.graphAnimations
  });
};

// 监听设置变化，同步节点大小
watch(
  () => settingsStore.systemSettings.graphNodeSize,
  (newSize) => {
    if (newSize !== undefined) {
      graphNodeSize.value = newSize;
    }
  }
);
</script>
