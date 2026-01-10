<template>
  <div id="displayArea" class="flex-1 flex p-0 pl-0 pr-0 pt-0 mt-8 bg-light dark:bg-dark-primary h-[calc(100vh-2rem)] overflow-hidden" :class="{ 'transition-all duration-300': !isInitialLoading }">
    <!-- 2. 历史对话/设置选项面板 -->
    <div 
      id="panelContainer" 
      class="h-full flex-shrink-0 z-40 overflow-hidden transition-all duration-300" 
      :style="{
        width: settingsStore.leftNavVisible ? settingsStore.leftNavWidth : '0px',
        minWidth: settingsStore.leftNavVisible ? '200px' : '0px',
        maxWidth: settingsStore.leftNavVisible ? '370px' : '0px',
        flexShrink: 0
      }"
    >
      <!-- 面板内容 - 使用复合组件简化逻辑 -->
      <PanelContent :active-panel="settingsStore.activePanel" />
    </div>

    <!-- 面板与主内容区之间的分隔线 -->
    <div 
      id="LeftResizer" 
      class="resizer transition-all duration-300" 
      :class="{
        'resizer-disabled': !settingsStore.leftNavVisible
      }"
    ></div>

    <!-- 3. 主内容区域 -->
    <div id="mainContent" class="flex-1 flex flex-col overflow-hidden bg-[#F8FAFC] dark:bg-dark-primary" :class="{ 'transition-all duration-300': !isInitialLoading }">
      <!-- 根据activeContent动态切换内容组件 -->
      <ChatContent v-if="activeContent === 'chat'" />
      <SettingsContent v-if="activeContent === 'settings'" />
      <RagManagementContent v-if="activeContent === 'ragManagement'" />
      <KnowledgeGraphContent v-if="activeContent === 'knowledgeGraph'" />
      <SendMessageContent v-if="activeContent === 'sendMessage'" />

    </div>

    <!-- 新增的分隔div -->
    <div id="RightResizer" class="resizer transition-all duration-300"></div>

    <!-- 右侧工具内容区域 -->
    <RightPanel :saved-width="savedRightPanelWidth" :is-initial-loading="isInitialLoading" />
  </div>
</template>

<script setup>

import PanelContent from '../panel/PanelContent.vue'; // 使用PanelContent复合组件
import ChatContent from '../../views/ChatContent.vue'; // 移动到views目录
import SettingsContent from '../../views/SettingsContent.vue'; // 移动到views目录
import RagManagementContent from '../../views/RagManagementContent.vue'; // 移动到views目录
import KnowledgeGraphContent from '../../views/KnowledgeGraphContent.vue'; // 新增视图组件
import SendMessageContent from '../../views/SendMessageContent.vue'; // 新增发送消息视图组件

import RightPanel from '../panel/RightPanel.vue';
import { useSettingsStore } from '../../store/settingsStore.js';

// 定义props
defineProps({
  activeContent: {
    type: String,
    default: 'sendMessage' // 默认值改为sendMessage，避免空白chatMainContent
  },
  savedRightPanelWidth: {
    type: String,
    default: '256px'
  },
  isInitialLoading: {
    type: Boolean,
    default: true
  }
});

// 初始化store
const settingsStore = useSettingsStore();
</script>