<template>
  <div 
    class="app-container h-screen flex flex-col overflow-hidden bg-light text-dark dark:bg-dark-primary dark:text-light"
    :class="{ 'transition-all duration-300': !isInitialLoading }"
  >
    <!-- 1. 顶部导航栏 -->
    <TopNav data-tauri-drag-region/>

    <!-- 主内容区域：显示区域 -->
    <div class="flex flex-1 overflow-hidden">
      <!-- 3. 显示区域容器 -->
      <DisplayArea 
        :active-content="settingsStore.activeContent" 
        :saved-right-panel-width="settingsStore.rightPanelWidth" 
        :is-initial-loading="isInitialLoading"
      />
    </div>

    <!-- 模型版本表单（支持添加和编辑） -->
    <ModelVersionForm />

    <!-- 模型配置抽屉 -->
    <ModelSettingsDrawer />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import TopNav from './components/layout/TopNav.vue';
import ModelVersionForm from './components/models/ModelVersionForm.vue';
import ModelSettingsDrawer from './components/models/ModelSettingsDrawer.vue';
import DisplayArea from './components/layout/DisplayArea.vue';
import { useChatStore } from './store/chatStore.js';
import { useSettingsStore } from './store/settingsStore.js';
import { useModelSettingStore } from './store/modelSettingStore.js';

// 初始化stores
const chatStore = useChatStore();
const settingsStore = useSettingsStore();
const modelSettingStore = useModelSettingStore();

// 初始加载状态，用于控制首次加载时的动画
const isInitialLoading = ref(true);

// 监听activePanel变化，同步更新activeContent
watch(
  () => settingsStore.activePanel,
  (newPanel) => {
    // 当切换到任何面板时，自动展开左侧面板
    settingsStore.leftNavVisible = true;
    
    // 只有当前视图不是sendMessage时，才根据activePanel更新视图
    if (settingsStore.activeContent !== 'sendMessage') {
      if (newPanel === 'settings') {
        settingsStore.setActiveContent('settings');
      } else {
        // 当面板不是settings时，切换回chat内容
        settingsStore.setActiveContent('chat');
      }
    }
  }
);

// 初始化应用
onMounted(async () => {
  // 加载用户设置和数据
  settingsStore.loadSettings();
  
  // 加载模型数据
  try {
    await modelSettingStore.loadModels();
  } catch (error) {
    console.error('初始化加载模型数据失败:', error);
  }

  // 异步加载对话历史（非阻塞方式）
  chatStore.loadChatHistory().catch(error => {
    console.error('初始化加载对话历史失败，但应用继续运行:', error);
  });

  // 初始化默认面板
  if (!settingsStore.activePanel) {
    settingsStore.setActivePanel('history');
  }

  console.log('AIClient应用已初始化，使用Pinia状态管理');
  
  // 初始化完成，启用动画
  isInitialLoading.value = false;
});
</script>

<style>
.resizer.resizing {
  background-color: #94a3b8;
}

/* 添加面板过渡动画 */
#panelContainer {
  transition: width 0.3s ease;
  min-width: 0;
}

/* 隐藏状态样式 */
.hidden {
  display: none !important;
}

/* 不可用状态的调整器样式 */
.resizer-disabled {
  cursor: not-allowed !important;
  opacity: 0.5;
  pointer-events: none;
}
</style>
