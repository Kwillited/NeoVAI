<template>
  <div v-if="message">
    <!-- 默认样式 -->
    <div v-if="!chatStyleDocument" class="flex" :class="{ 'justify-end': isUserMessage }">
      <!-- AI消息气泡 -->
      <AIChatBubble 
        v-if="!isUserMessage" 
        :message="message" 
        :chatStyleDocument="chatStyleDocument"
      />
      
      <!-- 用户消息气泡 -->
      <UserChatBubble 
        v-else 
        :message="message" 
        :chatStyleDocument="chatStyleDocument"
        @editMessage="handleEditMessage"
      />
    </div>
    
    <!-- 文档模式样式 -->
    <div v-else>
      <!-- AI消息气泡 - 使用文档样式 -->
      <div v-if="!isUserMessage" class="mb-4 w-full">
        <AIChatBubble 
          :message="message" 
          :chatStyleDocument="chatStyleDocument"
        />
      </div>
      
      <!-- 用户消息气泡 - 保持气泡样式 -->
      <div v-else class="flex justify-end mb-4 w-full">
        <UserChatBubble 
          :message="message" 
          :chatStyleDocument="false"
          @editMessage="handleEditMessage"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import AIChatBubble from '../library/AIChatBubble/AIChatBubble.vue'
import UserChatBubble from '../library/UserChatBubble/UserChatBubble.vue'
import Loading from '../common/Loading.vue'
// 导入集中化的markdown插件
import { marked } from '../../plugins/markdown.js'

const props = defineProps({
  message: {
    type: [Object, Function], // 支持普通对象和ref包装的对象
    required: true,
    default: () => ({})
  },
  chatStyleDocument: {
    type: Boolean,
    default: false
  }
})

// 访问ref包装的消息对象
const messageValue = computed(() => {
  // 如果是ref包装的对象，通过value访问，否则直接返回
  return props.message?.value || props.message || {}
})

// 判断是否为用户消息
const isUserMessage = computed(() => {
  return messageValue.value.role === 'user' || messageValue.value.isUser
})

// 获取消息内容
const messageContent = computed(() => {
  return messageValue.value.content || messageValue.value.text || ''
})

// 格式化消息内容（支持Markdown）
const formattedContent = computed(() => {
  if (!messageContent.value) return ''

  // 处理AI回复中的思考标签（</think>）
  let contentToParse = messageContent.value;
  const thinkingTagRegex = /^\s*\<think>[\s\S]*?\<\/think>\s*/;
  contentToParse = contentToParse.replace(thinkingTagRegex, '');
  
  // 使用集中化配置的marked库转换Markdown为HTML
  try {
    return marked.parse(contentToParse);
  } catch (error) {
    console.error('Markdown解析错误:', error);
    return contentToParse.replace(/\n/g, '<br>');
  }
})

// 用于触发更新的key值
const updateKey = computed(() => {
  return `${messageContent.value.length}-${messageValue.value.lastUpdate || Date.now()}`
})

// 编辑消息（用户消息）
const handleEditMessage = (editData) => {
  // 发射编辑事件给父组件处理
  emit('editMessage', editData)
}

// 事件委托处理代码块复制按钮点击
const handleCodeCopyClick = (event) => {
  const button = event.target.closest('.copy-code-btn');
  if (button) {
    const codeBlockId = button.getAttribute('data-code-block-id');
    if (codeBlockId) {
      // 这里不需要实现，因为复制逻辑已经移到子组件中
    }
  }
};

// 监听组件挂载后的点击事件
onMounted(() => {
  document.addEventListener('click', handleCodeCopyClick);
});

// 组件卸载时清理事件监听器
onUnmounted(() => {
  document.removeEventListener('click', handleCodeCopyClick);
});

// 定义发射事件
const emit = defineEmits(['editMessage'])
</script>

<style scoped>
/* 全局样式已在外部引入 */
/* 这里可以添加组件特定的样式 */

/* 错误提示样式 */
.chat-error {
  color: #ef4444;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
}

/* markdown内容样式 */
.markdown-content {
  transition: color 0.3s ease;
}
</style>
