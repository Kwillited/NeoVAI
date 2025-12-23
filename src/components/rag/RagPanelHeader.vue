<template>
  <div class="panel-header p-3 flex justify-between items-center transition-all duration-300">
    <div class="flex items-center">
      <h2 class="text-lg font-bold text-dark">{{ currentFolder ? currentFolder.name : 'RAG知识库' }}</h2>
    </div>
    <!-- 按钮区域 - 保持相同位置 -->
    <div class="flex items-center">
      <!-- 二级菜单时显示返回上一级按钮 -->
      <ActionButton
        v-if="currentFolder"
        icon="fa-chevron-left"
        title="返回上一级"
        @click="handleBackToParent"
      />
      <!-- 一级菜单时显示返回聊天按钮 -->
      <ActionButton
        v-else
        icon="fa-arrow-left"
        title="返回聊天"
        @click="handleBackToChat"
      />
    </div>
  </div>
</template>

<script setup>
import { useSettingsStore } from '../../store/settingsStore.js';
import ActionButton from '../common/ActionButton.vue';

const props = defineProps({
  currentFolder: {
    type: Object,
    default: null
  }
});

const settingsStore = useSettingsStore();

// 处理返回上一级
const handleBackToParent = () => {
  // 触发事件通知父组件
  const event = new CustomEvent('backToParent');
  window.dispatchEvent(event);
};

// 处理返回聊天按钮点击事件
const handleBackToChat = () => {
  settingsStore.setActivePanel('history');

  // 如果App.vue中有activeContent状态，也需要更新
  if (window.setActiveContent) {
    window.setActiveContent('chat');
  }
};
</script>

<style scoped>
/* 组件特定样式 */
.panel-header {
  position: relative;
}
</style>