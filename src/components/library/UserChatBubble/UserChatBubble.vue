<template>
  <div class="flex justify-end max-w-[85%]">
    <div class="relative group flex flex-col items-end">
      <!-- 消息内容气泡 - 添加了禁止触发滚动条的样式 -->
      <div :class="[
        'bg-primary/20 text-gray-800 rounded-2xl rounded-tr-none px-5 py-3 shadow-lg overflow-hidden',
        // 始终根据内容自动调整宽度，但不超过max-w-full
        'w-fit',
        // 最大宽度限制
        'max-w-full'
      ]">
        <!-- 文字内容 -->
        <div v-if="messageContent" class="markdown-content text-gray-800 dark:text-gray-100 leading-relaxed mb-3" v-html="formattedContent" :key="updateKey"></div>
        
        <!-- 文件列表 -->
        <div v-if="messageValue.files && messageValue.files.length > 0" class="flex flex-wrap gap-2">
          <div 
            v-for="(file, index) in messageValue.files" 
            :key="index"
            class="flex items-center justify-between p-2 bg-white/80 dark:bg-dark-600 rounded-lg text-xs group transition-colors duration-300 ease-in-out max-w-[150px]"
          >
            <div class="flex items-center gap-1 truncate max-w-[80px]">
              <i :class="['fa', getFileIcon(file.name), 'text-gray-500']"></i>
              <span class="truncate">{{ file.name }}</span>
            </div>
            <span class="text-gray-400 text-[10px]">{{ formatFileSize(file.size) }}</span>
          </div>
        </div>
        
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
      
      <!-- 操作按钮 -->
      <div class="text-sm text-gray-500 dark:text-gray-400 mt-3 ml-3 flex items-center justify-end w-full max-w-[85%]">
        <div class="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <!-- 编辑按钮 - 仅对用户消息显示 -->
          <Tooltip v-if="!messageValue.isTyping" content="编辑消息">
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
</template>

<script setup>
import { computed } from 'vue'
import Tooltip from '../../common/Tooltip.vue'
import Loading from '../../common/Loading.vue'
// 导入集中化的markdown插件
import { marked } from '../../../plugins/markdown.js'
// 导入公共工具函数
import { copyToClipboard } from '../../../store/utils.js'

const props = defineProps({
  message: {
    type: [Object, Function], // 支持普通对象和ref包装的对象
    required: true,
    default: () => ({})
  }
})

// 定义发射事件
const emit = defineEmits(['editMessage'])

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

  // 使用集中化配置的marked库转换Markdown为HTML
  try {
    return marked.parse(messageContent.value);
  } catch (error) {
    console.error('Markdown解析错误:', error);
    return messageContent.value.replace(/\n/g, '<br>');
  }
})

// 用于触发更新的key值
const updateKey = computed(() => {
  return `${messageContent.value.length}-${messageValue.value.lastUpdate || Date.now()}`
})

// 复制消息内容到剪贴板
const copyMessageContent = async () => {
  try {
    await copyToClipboard(messageContent.value)
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
      await copyToClipboard(codeText);
      
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

// 事件委托处理代码块复制按钮点击
const handleCodeCopyClick = (event) => {
  const button = event.target.closest('.copy-code-btn');
  if (button) {
    const codeBlockId = button.getAttribute('data-code-block-id');
    if (codeBlockId) {
      copyCodeToClipboard(codeBlockId);
    }
  }
};

// 获取文件图标
const getFileIcon = (fileName) => {
  const extension = fileName.split('.').pop().toLowerCase();
  
  const iconMap = {
    txt: 'fa-file-lines',
    pdf: 'fa-file-pdf',
    doc: 'fa-file-word',
    docx: 'fa-file-word',
    md: 'fa-file-lines',
    jpg: 'fa-file-image',
    jpeg: 'fa-file-image',
    png: 'fa-file-image',
    gif: 'fa-file-image',
    csv: 'fa-file-excel',
    xlsx: 'fa-file-excel',
    pptx: 'fa-file-powerpoint'
  };
  
  return iconMap[extension] || 'fa-file';
};

// 格式化文件大小
const formatFileSize = (size) => {
  if (size === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(size) / Math.log(k));
  
  return parseFloat((size / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};
</script>

<style scoped>
/* 深色模式切换过渡效果 */
.bg-primary\/20,
.markdown-content {
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}

/* 确保操作按钮组的容器是相对定位，以便提示框可以绝对定位 */
.edit-btn, .copy-btn {
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