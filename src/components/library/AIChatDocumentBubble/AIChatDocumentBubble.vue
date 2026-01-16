<template>
  <div class="w-full max-w-2xl bg-transparent dark:bg-transparent rounded-xl p-4 overflow-hidden">
    <div class="markdown-content text-gray-800 dark:text-gray-100 leading-relaxed" v-html="formattedContent"></div>
    
    <!-- 错误状态显示 -->
    <div v-if="messageValue.error" class="chat-error mt-2">
      <i class="fa-solid fa-circle-exclamation text-red-500 mr-1"></i>
      <span>{{ messageValue.error }}</span>
    </div>
    
    <!-- 打字动画 -->
    <Loading 
      v-if="messageValue.isTyping" 
      type="typing" 
      size="small" 
      color="var(--text-color-secondary, #9ca3af)" 
      containerClass="mt-2"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import Loading from '../../common/Loading.vue'
// 导入集中化的markdown插件
import { marked } from '../../../plugins/markdown.js'

const props = defineProps({
  message: {
    type: [Object, Function], // 支持普通对象和ref包装的对象
    required: true,
    default: () => ({})
  }
})

// 访问ref包装的消息对象
const messageValue = computed(() => {
  // 如果是ref包装的对象，通过value访问，否则直接返回
  return props.message?.value || props.message || {}
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
</script>

<style scoped>
/* 深色模式切换过渡效果 */
.bg-transparent.dark\:bg-transparent,
.markdown-content {
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* 错误提示样式 */
.chat-error {
  color: #ef4444;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
}
</style>