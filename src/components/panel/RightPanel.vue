<template>
  <div 
    id="rightPanel" 
    class="h-full flex-shrink-0 z-40 overflow-hidden bg-white dark:bg-dark-bg-secondary mr-0 max-w-[370px]"
    :class="{ 'transition-all duration-300': !isInitialLoading }"
    :style="{ width: settingsStore.rightPanelVisible ? savedWidth : '0px', display: settingsStore.rightPanelVisible ? 'block' : 'none', flexShrink: 0 }"
  >
    <!-- 右侧面板标题 -->
    <div class="panel-header p-3 flex justify-between items-center">
      <h2 class="text-lg font-bold text-dark dark:text-white">工具面板</h2>
      <ActionButton
        icon="fa-times"
        title="关闭面板"
        @click="settingsStore.toggleRightPanel()"
      />
    </div>
    
    <!-- 右侧面板内容 -->
    <div class="p-3 space-y-4">
      <!-- 面板功能区示例 -->
      <div class="panel-section">
        <h3 class="text-sm font-semibold text-gray-500 mb-2">会话信息</h3>
        <div class="bg-gray-50 dark:bg-dark-bg-tertiary p-3 rounded-lg">
          <p class="text-sm text-gray-600 dark:text-dark-text-secondary mb-1">当前会话: {{ chatStore.currentChat?.title || '无' }}</p>
          <p class="text-sm text-gray-600 dark:text-dark-text-secondary">消息数: {{ chatStore.currentChat?.messages?.length || 0 }}</p>
        </div>
      </div>
      
      <div class="panel-section">
        <h3 class="text-sm font-semibold text-gray-500 mb-2">模型信息</h3>
        <div class="bg-gray-50 dark:bg-dark-bg-tertiary p-3 rounded-lg">
          <p class="text-sm text-gray-600 dark:text-dark-text-secondary mb-1">当前模型: {{ modelStore.currentSelectedModel }}</p>
          <p class="text-sm text-gray-600 dark:text-dark-text-secondary">温度: {{ modelStore.currentModelParams.temperature }}</p>
        </div>
      </div>
      
      <!-- 可以根据需要添加更多功能区域 -->
    </div>
  </div>
</template>

<script setup>
import { useSettingsStore } from '../../store/settingsStore.js';
import { useModelSettingStore } from '../../store/modelSettingStore.js';
import { useChatStore } from '../../store/chatStore.js';
import ActionButton from '../common/ActionButton.vue';

// 定义props
const props = defineProps({
  savedWidth: {
    type: String,
    default: '200px'
  },
  isInitialLoading: {
    type: Boolean,
    default: true
  }
});

// 初始化stores
const settingsStore = useSettingsStore();
const modelStore = useModelSettingStore();
const chatStore = useChatStore();
</script>

<style scoped>
.panel-section {
  margin-bottom: 1rem;
}
</style>