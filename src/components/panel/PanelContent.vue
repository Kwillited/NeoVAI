<template>
  <!-- 面板内容复合组件 - 根据activePanel动态显示对应面板 -->
  <div class="panel-content h-full">
    <!-- 历史对话面板 -->
    <HistoryPanel v-if="activePanel === 'history'" />

    <!-- 设置选项面板 -->
    <SettingsPanel v-if="activePanel === 'settings'" />

    <!-- 模型参数设置面板 -->
    <ModelParamsPanel v-if="activePanel === 'modelParams'" />

    <!-- RAG配置面板 -->
    <RagPanel v-if="activePanel === 'rag'" />

    <!-- MCP服务面板 -->
    <McpPanel v-if="activePanel === 'mcp'" />
    

  </div>
</template>

<script setup>
// 导入各个面板组件
import HistoryPanel from './HistoryPanel.vue';
import SettingsPanel from './SettingsPanel.vue';
import ModelParamsPanel from './ModelParamsPanel.vue';
import RagPanel from './RagPanel.vue';
import McpPanel from './McpPanel.vue';


// 定义props
const props = defineProps({
  activePanel: {
    type: String,
    default: 'history'
  }
});
</script>

<style scoped>
.panel-content {
  height: 100%;
  overflow: hidden;
  opacity: 1;
  transition: opacity 0.2s ease-in-out;
}
</style>