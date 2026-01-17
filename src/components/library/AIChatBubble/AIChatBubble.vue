<template>
  <div class="flex items-start max-w-[85%]">
    <!-- 头像 -->
    <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mr-2 mt-1 flex-shrink-0">
      <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707-.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
      </svg>
    </div>
    <div class="relative group">
      <!-- 模型名称 -->
      <div class="text-xs text-gray-500 dark:text-gray-400 mb-1 ml-1">{{ messageValue.model || 'Chato' }}</div>
      
      <!-- 思考内容 -->
      <div v-if="messageValue.thinking" class="relative mb-2">
        <div class="bg-gray-50 dark:bg-dark-bg-quaternary rounded-2xl rounded-tl-none px-5 py-3 shadow-sm dark:border dark:border-dark-border overflow-hidden">
          <div class="flex items-start gap-3">
            <svg class="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707-.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
            </svg>
            <div class="text-sm text-gray-600 dark:text-gray-300 leading-relaxed" v-html="formatThinkingContent(messageValue.thinking)"></div>
          </div>
        </div>
      </div>
      
      <!-- 消息内容气泡 - 添加了禁止触发滚动条的样式 -->
      <div :class="[
        'bg-white dark:bg-dark-bg-tertiary rounded-2xl rounded-tl-none px-5 py-3 shadow-lg dark:border dark:border-dark-border overflow-hidden',
        // 始终根据内容自动调整宽度，但不超过max-w-full
        'w-fit',
        // 最大宽度限制
        'max-w-full'
      ]">
        <div class="markdown-content text-gray-800 dark:text-gray-100 leading-relaxed" v-html="formattedContent" :key="updateKey"></div>
        
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
      
      <!-- 时间戳和操作按钮 -->
      <div class="text-sm text-gray-500 dark:text-gray-400 mt-3 ml-3 flex items-center justify-between">
        <span>{{ formatTime(messageValue.timestamp || messageValue.time) }}</span>
        <div class="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <Tooltip content="复制消息内容">
            <button class="copy-btn text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 p-2 rounded-full transition-all duration-200" @click="copyMessageContent">
              <i class="fa-solid fa-copy"></i>
            </button>
          </Tooltip>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Tooltip } from '../index.js'
import Loading from '../../common/Loading.vue'
// 导入集中化的markdown插件
import { marked } from '../../../plugins/markdown.js'
// 导入公共工具函数
import { formatTime, copyToClipboard } from '../../../store/utils.js'

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

// 格式化思考内容
const formatThinkingContent = (thinking) => {
  if (!thinking) return ''
  
  // 简单的换行处理
  return thinking.replace(/\n/g, '<br>')
}

// 用于触发更新的key值
const updateKey = computed(() => {
  return `${messageContent.value.length}-${messageValue.value.lastUpdate || Date.now()}`
})

// 复制消息内容到剪贴板
const copyMessageContent = async () => {
  try {
    // 移除思考标签（</think>和</think>）后再复制
    let contentToCopy = messageContent.value;
    const thinkingTagRegex = /^\s*\<think>[\s\S]*?\<\/think>\s*/;
    if (thinkingTagRegex.test(contentToCopy)) {
      contentToCopy = contentToCopy.replace(thinkingTagRegex, '');
    }
    await copyToClipboard(contentToCopy)
    // 可以在这里添加一个临时的提示，告知用户复制成功
  } catch (error) {
    console.error('复制失败:', error)
  }
}
</script>

<style scoped>
/* 深色模式切换过渡效果 */
.bg-white.dark\:bg-gray-800,
.dark\:border.dark\:border-gray-700,
.markdown-content {
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}

/* 确保操作按钮组的容器是相对定位，以便提示框可以绝对定位 */
.copy-btn {
  position: relative;
}

/* 错误提示样式 */
.chat-error {
  color: #ef4444;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
}
</style>