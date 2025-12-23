<template>
  <!-- 聊天内容区域 -->
  <div id="sendMessageContent" class="flex-1 flex flex-col overflow-hidden w-full">
    <!-- 顶部导航 -->
    <div class="panel-header p-3 flex flex-wrap items-center justify-end gap-4 relative transition-all duration-300 border-b-0">
      <!-- 左侧按钮组 -->
        <div class="absolute left-3 flex space-x-2">
          <!-- 隐藏左侧面板按钮 -->
          <ActionButton 
            icon="bars"
            title="隐藏左侧面板"
            @click="handleSideMenuToggle"
          />
          <!-- 新增会话按钮 -->
          <ActionButton 
            id="newChat"
            icon="comment-dots"
            title="新对话"
            @click="handleNewChat"
          />
        </div>
      
  
      <!-- 按钮区域靠右对齐 -->
      <div class="flex items-center space-x-4">
      </div>
    </div>

    <!-- 消息输入区域 - 使用固定宽度容器包裹 -->
    <div class="w-full max-w-4xl mx-auto px-4 flex-1 flex flex-col justify-center mt-[-5%]">
      <h3 class="text-2xl font-semibold text-dark dark:text-white mb-4 text-center transition-colors duration-300">今天有什么可以帮助你的？</h3>
      <MessageInputArea @sendMessage="handleSendMessage" :showShortcutHint="false" />
    </div>
  </div>
</template>

<script setup>
import { useChatStore } from '../../store/chatStore.js';

// 导入必要的子组件
import MessageInputArea from '../../components/chat/MessageInputArea.vue';
import ActionButton from '../../components/common/ActionButton.vue';

// 处理侧边菜单切换
const handleSideMenuToggle = () => {
  // 侧边菜单切换逻辑
  if (window.toggleSidePanel) {
    window.toggleSidePanel();
  }
};

// 初始化stores
const chatStore = useChatStore();

// 处理新对话点击事件
const handleNewChat = () => {
  // 取消当前会话的激活状态
  chatStore.currentChatId = null;
  
  // 清除所有对话的未读标记
  chatStore.chats = chatStore.chats.map(chat => ({
    ...chat,
    hasUnreadMessage: false
  }));
  
  // 切换到发送消息视图
  if (window.setActiveContent) {
    window.setActiveContent('sendMessage');
  }
};

// 处理发送消息事件
const handleSendMessage = async (message, model) => {
  if (message.trim()) {
    // 先确保有当前对话（如果没有则创建）
    if (!chatStore.currentChatId) {
      await chatStore.createNewChat(model);
    }
    
    // 立即切换到ChatContent视图，以便显示打字动画和流式输出
    if (window.setActiveContent) {
      window.setActiveContent('chat');
    }
    
    // 然后发送消息（此时视图已切换，用户可以看到实时效果）
    chatStore.sendMessage(message, model);
  }
};
</script>

<style scoped>
/* 移除顶部导航的边框和伪元素效果 */
.panel-header {
  border-bottom: none !important;
}

.panel-header::after {
  display: none !important;
  content: none !important;
}
</style>
