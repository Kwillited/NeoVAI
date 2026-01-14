<template>
  <div v-if="message">
    <!-- 默认样式 -->
    <div v-if="!chatStyleDocument || isUserMessage" class="flex" :class="{ 'justify-end': isUserMessage }">
      <div class="flex items-start max-w-[85%]">
        <!-- 头像 -->
        <div v-if="!isUserMessage" class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mr-2 mt-1 flex-shrink-0">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707-.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
          </svg>
        </div>
        
        <div class="relative group">
          <!-- 模型名称 -->
          <div v-if="!isUserMessage" class="text-xs text-gray-500 dark:text-gray-400 mb-1 ml-1">{{ messageValue.model || 'Chato' }}</div>
          
          <!-- 思考内容 -->
          <div v-if="!isUserMessage && messageValue.thinking" class="relative mb-2">
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
          <div :class="isUserMessage 
            ? 'bg-primary/20 text-gray-800 rounded-2xl px-5 py-3 shadow-lg overflow-hidden' 
            : 'bg-white dark:bg-dark-bg-tertiary rounded-2xl rounded-tl-none px-5 py-3 shadow-lg dark:border dark:border-dark-border overflow-hidden'">
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
            <span v-if="!isUserMessage">{{ formatTime(messageValue.timestamp || messageValue.time) }}</span>
            <div class="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              <!-- 编辑按钮 - 仅对用户消息显示 -->
              <Tooltip v-if="isUserMessage && !messageValue.isTyping" content="编辑消息">
                <button class="edit-btn text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 p-2 rounded-full transition-all duration-200" @click="startEditMessage">
                  <i class="fa-solid fa-pen"></i>
                </button>
              </Tooltip>
              <Tooltip content="复制消息内容">
                <button class="copy-btn text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 p-2 rounded-full transition-all duration-200" @click="copyMessageContent">
                  <i class="fa-solid fa-copy"></i>
                </button>
              </Tooltip>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 居中样式 - 仅对AI消息生效 - 优化后减少了嵌套层级 -->
    <div v-else class="flex justify-center my-4">
      <div class="w-full max-w-2xl bg-transparent dark:bg-transparent rounded-xl p-4 overflow-hidden">
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
          containerClass="mt-2 flex justify-center"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import Tooltip from '../common/Tooltip.vue'
import Loading from '../common/Loading.vue'
// 导入marked库和highlight.js
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

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
  const match = contentToParse.match(thinkingTagRegex);
  
  // 使用导入的marked库转换Markdown为HTML
  try {
    // 配置marked，自定义代码块渲染
    const renderer = new marked.Renderer();
    
    // 保存原始的codeblock渲染方法
    const originalCode = renderer.code;
    
    // 自定义代码块渲染
    renderer.code = function(code, language) {
      // 如果没有语言或语言为'text'，则显示为'plaintext'
      const displayLanguage = language && language !== 'text' ? language : 'plaintext';
      
      // 创建唯一ID用于复制功能
      const codeBlockId = `code-block-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      
      // 返回带头部的代码块HTML
      return `
        <div class="code-container">
          <div class="code-header">
            <span class="code-language">${displayLanguage}</span>
            <button 
              class="copy-code-btn"
              data-code-block-id="${codeBlockId}"
              @click="copyCodeToClipboard('${codeBlockId}')"
              title="复制代码"
            >
              <i class="fa-solid fa-copy"></i>
            </button>
          </div>
          <pre><code id="${codeBlockId}">${code}</code></pre>
        </div>
      `;
    };
    
    // 设置marked配置
    marked.setOptions({
      renderer: renderer,
      breaks: true,
      gfm: true
    });
    
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

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  // 计算分钟、小时、天的差值
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  // 根据差值返回不同的时间格式
  if (minutes < 1) {
    return '刚刚'
  } else if (minutes < 60) {
    return `${minutes}分钟前`
  } else if (hours < 24) {
    return `${hours}小时前`
  } else if (days < 7) {
    return `${days}天前`
  } else {
    // 超过一周显示具体日期
    return date.toLocaleDateString('zh-CN')
  }
}

// 复制消息内容到剪贴板
const copyMessageContent = async () => {
  try {
    // 移除思考标签（</think>和</think>）后再复制
    let contentToCopy = messageContent.value;
    const thinkingTagRegex = /^\s*\<think>[\s\S]*?\<\/think\>\s*/;
    if (thinkingTagRegex.test(contentToCopy)) {
      contentToCopy = contentToCopy.replace(thinkingTagRegex, '');
    }
    await navigator.clipboard.writeText(contentToCopy)
    // 可以在这里添加一个临时的提示，告知用户复制成功
  } catch (error) {
    console.error('复制失败:', error)
  }
}

// 复制代码到剪贴板
const copyCodeToClipboard = async (codeBlockId) => {
  try {
    const codeElement = document.getElementById(codeBlockId);
    if (codeElement) {
      const codeText = codeElement.textContent;
      await navigator.clipboard.writeText(codeText);
      
      // 更改复制按钮图标为成功状态
      const button = document.querySelector(`button[data-code-block-id="${codeBlockId}"]`);
      if (button) {
        const originalIcon = button.innerHTML;
        button.innerHTML = '<i class="fa-solid fa-check"></i>';
        button.classList.add('text-green-400');
        
        // 2秒后恢复原状
        setTimeout(() => {
          button.innerHTML = originalIcon;
          button.classList.remove('text-green-400');
        }, 2000);
      }
    }
  } catch (error) {
    console.error('复制代码失败:', error);
  }
};

// 编辑消息（用户消息）
const startEditMessage = () => {
  // 发射编辑事件给父组件处理
  emit('editMessage', {
    id: messageValue.value.id,
    content: messageValue.value.content
  })
}

// 定义发射事件
const emit = defineEmits(['editMessage'])
</script>

<style scoped>
/* 全局样式已在外部引入 */
/* 这里可以添加组件特定的样式 */

/* 深色模式切换过渡效果 */
.bg-primary\/20,
.bg-white.dark\:bg-gray-800,
.dark\:border.dark\:border-gray-700,
.markdown-content {
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}

/* 确保操作按钮组的容器是相对定位，以便提示框可以绝对定位 */
.edit-btn, .copy-btn {
  position: relative;
}

/* 编辑提示框样式 */
.edit-tooltip {
  animation: fadeIn 0.2s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 错误提示样式 */
.chat-error {
  color: #ef4444;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
}

/* 动画 */
.animate-bounce {
  animation: bounce 1.4s infinite ease-in-out both;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

/* 居中样式特定样式 */
.max-w-2xl {
  max-width: 42rem;
}

.my-4 {
  margin-top: 1rem;
  margin-bottom: 1rem;
}

.justify-center {
  justify-content: center;
}

.dark .bg-gray-700\/50 {
  background-color: rgba(55, 65, 81, 0.5);
}
</style>
