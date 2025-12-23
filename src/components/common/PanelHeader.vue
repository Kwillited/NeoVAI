<template>
  <div class="panel-header p-3 flex justify-between items-center transition-all duration-300">
    <h2 class="text-lg font-bold text-dark dark:text-white">{{ title }}</h2>
    <div class="flex gap-2" v-if="!hideDefaultActions">
      <!-- 自定义按钮插槽 -->
      <slot name="actions"></slot>
      
      <!-- 默认返回按钮（如果有返回按钮配置） -->
      <ActionButton
        v-if="showBackButton"
        :id="backButtonId"
        icon="fa-arrow-left"
        title="返回聊天"
        @click="handleBack"
      />
    </div>
  </div>
</template>

<script setup>
import ActionButton from '../common/ActionButton.vue';
import { useSettingsStore } from '../../store/settingsStore.js';

// 定义props
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  showBackButton: {
    type: Boolean,
    default: true
  },
  backButtonId: {
    type: String,
    default: 'backToChatBtn'
  },
  hideDefaultActions: {
    type: Boolean,
    default: false
  }
});

// 使用store
const settingsStore = useSettingsStore();

// 处理返回按钮点击
const handleBack = () => {
  settingsStore.setActivePanel('history');
  
  // 触发自定义事件，允许父组件覆盖默认行为
  const event = new CustomEvent('backToChat');
  window.dispatchEvent(event);
};
</script>

<style scoped>
</style>