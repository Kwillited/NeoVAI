<template>
  <!-- 代码编辑区域 -->
  <div id="codeEditorMainContent" class="flex-1 flex flex-col overflow-hidden">


    <!-- 上下分栏布局 -->
    <div ref="resizeContainer" class="flex-1 flex flex-col overflow-hidden pt-0 pl-0 pr-0 pb-4 gap-0">
      <!-- 上部分：文件内容显示编辑区域 -->
      <div 
        class="bg-white dark:bg-dark-700 rounded-t-lg shadow-sm border border-gray-200 dark:border-dark-500 overflow-hidden flex flex-col transition-all duration-300 ease-out"
        :style="{ flexBasis: editorHeightRatio * 100 + '%', flexGrow: 0, flexShrink: 0 }"
      >
        <!-- 编辑器选项卡 -->
        <div class="editor-tabs bg-gray-50 dark:bg-dark-600 border-b border-gray-200 dark:border-dark-500 flex items-center">
          <!-- 选项卡列表 -->
          <div class="flex items-center h-full">
            <!-- 隐藏左侧面板按钮 -->
            <ActionButton 
              icon="bars"
              title="隐藏左侧面板"
              @click="handleSideMenuToggle"
              class="mr-2 ml-1 text-sm"
            />
            <div 
              v-for="(tab, index) in editorTabs" 
              :key="tab.id"
              class="editor-tab flex items-center px-3 py-2 cursor-pointer transition-colors"
              :class="{
                'bg-white dark:bg-dark-700 text-gray-800 dark:text-white border-b-2 border-blue-500': activeEditorTab === index,
                'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-dark-500': activeEditorTab !== index
              }"
              @click="activeEditorTab = index"
            >
              <span class="tab-name text-sm">{{ tab.name }}</span>
              <button 
                class="ml-2 text-xs text-gray-500 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors"
                @click.stop="closeEditorTab(index)"
                title="关闭选项卡"
              >
                <i class="fa-solid fa-times"></i>
              </button>
            </div>
            <!-- 新建选项卡按钮 -->
            <button 
              class="editor-tab-btn px-3 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-dark-500 transition-colors"
              @click="addEditorTab"
              title="新建选项卡"
            >
              <i class="fa-solid fa-plus"></i>
            </button>
          </div>
          
          <!-- 右侧工具栏 -->
          <div class="ml-auto flex items-center space-x-2 p-2">
            <ActionButton 
              icon="save"
              title="保存"
              class="text-sm"
            />
            <ActionButton 
              icon="copy"
              title="复制"
              class="text-sm"
            />
            <ActionButton 
              icon="trash"
              title="清空"
              class="text-sm"
            />
            <ActionButton 
              icon="terminal"
              title="切换命令行"
              @click="toggleCommandLine"
              class="text-sm"
            />
            <ActionButton 
              icon="play"
              title="运行"
              class="text-sm"
            />
          </div>
        </div>
        <!-- 编辑器内容区域 -->
        <div class="flex-1 p-4 font-mono text-sm bg-gray-50 dark:bg-dark-800 overflow-auto">
          <textarea 
            class="w-full h-full bg-transparent border-none outline-none resize-none"
            placeholder="在此输入代码..."
            spellcheck="false"
            v-model="editorTabs[activeEditorTab].content"
          ></textarea>
        </div>
      </div>
      
      <!-- 拖拽分隔条 -->
      <div 
        v-if="showCommandLine"
        class="resize-handle h-2 bg-gray-200 dark:bg-dark-500 cursor-row-resize hover:bg-gray-300 dark:hover:bg-dark-400 transition-colors duration-200 relative"
        @mousedown="startResize"
        @touchstart="startResize"
      >
        <div class="absolute left-1/2 transform -translate-x-1/2 w-12 h-1 bg-gray-400 dark:bg-dark-300 rounded-full opacity-0 hover:opacity-100 transition-opacity duration-200"></div>
      </div>
      
      <!-- 下部分：Command Line Overlay -->
      <div v-if="showCommandLine" class="bg-[#1e1e1e] rounded-b-lg shadow-sm border-x border-b border-gray-200 dark:border-dark-500 overflow-hidden flex flex-col flex-grow min-h-[100px] transition-all duration-300 ease-out">
        <!-- 选项卡导航 -->
        <div class="command-line-tabs bg-[#2d2d2d] border-b border-[#3e3e3e]">
          <!-- 选项卡列表 -->
          <div class="flex items-center h-full">
            <div 
              v-for="(tab, index) in commandTabs" 
              :key="index"
              class="command-line-tab flex items-center px-3 py-1 cursor-pointer transition-colors"
              :class="{
                'bg-[#1e1e1e] text-white border-b-2 border-[#569cd6]': activeTabIndex === index,
                'text-[#cccccc] hover:bg-[#3e3e3e]': activeTabIndex !== index
              }"
              @click="activeTabIndex = index"
            >
              <span class="tab-name">{{ tab.name }}</span>
              <button 
                class="ml-2 text-xs text-[#858585] hover:text-white transition-colors"
                @click.stop="closeTab(index)"
              >
                <i class="fa-solid fa-times"></i>
              </button>
            </div>
            <!-- 新建选项卡按钮 -->
            <button 
              class="command-line-btn mx-2" 
              @click="addTab"
              title="新建选项卡"
            >
              <i class="fa-solid fa-plus"></i>
            </button>
          </div>
        </div>
        <!-- 命令行内容区域 -->
        <div class="command-line-body flex-1">
          <div class="command-line-output" ref="outputContainer">
            <div v-for="(entry, index) in commandHistory" :key="index" class="command-entry">
              <div class="command-input">
              <span class="prompt">{{ currentTabPath }}{{ prompt }}</span>
              <span class="command-text">{{ entry.command }}</span>
            </div>
              <div v-if="entry.response" class="command-response">{{ entry.response }}</div>
            </div>
            <div class="command-input active">
              <span class="prompt">{{ currentTabPath }}{{ prompt }}</span>
              <input 
                v-model="currentCommand" 
                ref="commandInput" 
                @keydown.enter="executeCommand" 
                @keydown.up="navigateHistory(-1)" 
                @keydown.down="navigateHistory(1)"
                class="command-input-field"
                placeholder="输入命令..."
                autocomplete="off"
                spellcheck="false"
              />
              <span class="cursor" :class="{ blinking: showCursor }"></span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue';
import ActionButton from '../../components/common/ActionButton.vue';
import { useSettingsStore } from '../../store/settingsStore.js';
import { invoke } from '@tauri-apps/api/core';

// 初始化store
const settingsStore = useSettingsStore();

// 编辑器选项卡相关状态
const activeEditorTab = ref(0);
const editorTabs = ref([
  {
    name: '文件 1.js',
    language: 'javascript',
    content: '',
    id: 1
  }
]);

// 命令行相关状态
const showCommandLine = ref(true);
const outputContainer = ref(null);
const commandInput = ref(null);
const resizeContainer = ref(null);
const currentCommand = ref('');
const historyIndex = ref(-1);
const historyBuffer = ref([]);
const showCursor = ref(true);
const prompt = ref('> ');
const currentPath = ref('');

// 命令行选项卡相关状态
const activeTabIndex = ref(0);
const commandTabs = ref([
  {
    name: '终端 1',
    commandHistory: [],
    currentPath: ''
  }
]);

// 拖拽调整大小相关状态
const editorHeightRatio = ref(0.7); // 编辑器高度占父容器的比例，终端初始占比30%
let isResizing = ref(false);
let startY = ref(0);
let startRatio = ref(0);
let resizeObserver = null;

// 防抖函数
const debounce = (func, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(null, args), delay);
  };
};

// 开始拖拽
const startResize = (e) => {
  isResizing.value = true;
  startY.value = e.clientY || e.touches[0].clientY;
  startRatio.value = editorHeightRatio.value;
  
  // 添加事件监听器
  document.addEventListener('mousemove', resize);
  document.addEventListener('mouseup', stopResize);
  document.addEventListener('touchmove', resize);
  document.addEventListener('touchend', stopResize);
  
  // 防止默认行为
  e.preventDefault();
};

// 拖拽中
const resize = (e) => {
  if (!isResizing.value || !resizeContainer.value) return;
  
  const currentY = e.clientY || e.touches[0].clientY;
  const deltaY = currentY - startY.value;
  
  // 获取容器高度
  const containerRect = resizeContainer.value.getBoundingClientRect();
  const containerHeight = containerRect.height;
  
  if (containerHeight > 0) {
    const minCommandLineHeight = 100; // 命令行最小高度
    const minEditorHeight = 100; // 编辑器最小高度
    
    // 计算新的比例
    const deltaRatio = deltaY / containerHeight;
    let newRatio = startRatio.value + deltaRatio;
    
    // 计算最小和最大比例
    const minRatio = minEditorHeight / containerHeight;
    const maxRatio = (containerHeight - minCommandLineHeight) / containerHeight;
    
    // 确保比例在合理范围内
    newRatio = Math.max(minRatio, Math.min(maxRatio, newRatio));
    
    // 更新比例
    editorHeightRatio.value = newRatio;
  }
};

// 停止拖拽
const stopResize = () => {
  isResizing.value = false;
  
  // 移除事件监听器
  document.removeEventListener('mousemove', resize);
  document.removeEventListener('mouseup', stopResize);
  document.removeEventListener('touchmove', resize);
  document.removeEventListener('touchend', stopResize);
};

// 初始化ResizeObserver监听容器高度变化（仅用于边界检查）
const initResizeObserver = () => {
  if (resizeContainer.value && typeof ResizeObserver !== 'undefined') {
    // 使用防抖处理，减少计算频率
    const debouncedUpdate = debounce(() => {
      const containerRect = resizeContainer.value.getBoundingClientRect();
      const containerHeight = containerRect.height;
      const minCommandLineHeight = 100;
      const minEditorHeight = 100;
      
      // 确保比例始终在合理范围内
      const minRatio = minEditorHeight / containerHeight;
      const maxRatio = (containerHeight - minCommandLineHeight) / containerHeight;
      
      if (editorHeightRatio.value < minRatio) {
        editorHeightRatio.value = minRatio;
      } else if (editorHeightRatio.value > maxRatio) {
        editorHeightRatio.value = maxRatio;
      }
    }, 100);
    
    resizeObserver = new ResizeObserver(debouncedUpdate);
    resizeObserver.observe(resizeContainer.value);
  }
};

// 清理ResizeObserver
const cleanupResizeObserver = () => {
  if (resizeObserver) {
    resizeObserver.disconnect();
    resizeObserver = null;
  }
};

// 计算当前激活选项卡的命令历史
const commandHistory = computed(() => {
  return commandTabs.value[activeTabIndex.value]?.commandHistory || [];
});

// 计算当前激活选项卡的路径
const currentTabPath = computed(() => {
  return commandTabs.value[activeTabIndex.value]?.currentPath || currentPath.value;
});

// 处理隐藏左侧面板
const handleSideMenuToggle = () => {
  // 直接使用store提供的方法切换左侧导航栏的可见性
  settingsStore.toggleLeftNav();
};

// 切换命令行显示/隐藏
const toggleCommandLine = () => {
  showCommandLine.value = !showCommandLine.value;
};

// 添加编辑器选项卡
const addEditorTab = () => {
  const tabCount = editorTabs.value.length + 1;
  editorTabs.value.push({
    name: `文件 ${tabCount}.js`,
    language: 'javascript',
    content: '',
    id: Date.now() // 使用时间戳作为唯一ID
  });
  activeEditorTab.value = editorTabs.value.length - 1;
};

// 关闭编辑器选项卡
const closeEditorTab = (index) => {
  if (editorTabs.value.length <= 1) {
    // 至少保留一个选项卡
    return;
  }
  
  editorTabs.value.splice(index, 1);
  
  // 如果关闭的是当前活动选项卡，切换到前一个选项卡
  if (activeEditorTab.value === index) {
    activeEditorTab.value = Math.max(0, index - 1);
  } else if (activeEditorTab.value > index) {
    // 如果关闭的是当前活动选项卡之前的选项卡，调整索引
    activeEditorTab.value--;
  }
};

// 添加新选项卡
const addTab = async () => {
  const tabCount = commandTabs.value.length + 1;
  commandTabs.value.push({
    name: `终端 ${tabCount}`,
    commandHistory: [],
    currentPath: currentPath.value
  });
  activeTabIndex.value = commandTabs.value.length - 1;
  
  // 初始化新选项卡的路径
  await getCurrentPath();
};

// 关闭选项卡
const closeTab = (index) => {
  if (commandTabs.value.length <= 1) {
    // 至少保留一个选项卡
    return;
  }
  
  commandTabs.value.splice(index, 1);
  
  // 如果关闭的是当前活动选项卡，切换到前一个选项卡
  if (activeTabIndex.value === index) {
    activeTabIndex.value = Math.max(0, index - 1);
  } else if (activeTabIndex.value > index) {
    // 如果关闭的是当前活动选项卡之前的选项卡，调整索引
    activeTabIndex.value--;
  }
};

// 命令执行函数
const executeCommand = async () => {
  const command = currentCommand.value.trim();
  if (!command) return;

  // 添加到当前选项卡的历史记录
  const currentTab = commandTabs.value[activeTabIndex.value];
  currentTab.commandHistory.push({ command, response: null });
  
  // 保存到历史缓冲区
  const historyBufferCopy = [...historyBuffer.value];
  historyBufferCopy.push(command);
  historyBuffer.value = historyBufferCopy;
  
  // 清空当前命令
  const executedCommand = command;
  currentCommand.value = '';
  historyIndex.value = -1;

  // 滚动到底部
  await nextTick();
  if (outputContainer.value) {
    outputContainer.value.scrollTop = outputContainer.value.scrollHeight;
  }

  // 执行命令并获取响应
  let response = '';
  try {
    response = await handleCommand(executedCommand);
  } catch (error) {
    response = `错误: ${error.message}`;
  }

  // 更新响应
  const lastEntry = currentTab.commandHistory[currentTab.commandHistory.length - 1];
  lastEntry.response = response;

  // 再次滚动到底部
  await nextTick();
  if (outputContainer.value) {
    outputContainer.value.scrollTop = outputContainer.value.scrollHeight;
  }
};

// 获取当前工作路径
const getCurrentPath = async () => {
  try {
    const path = await invoke('execute_command', { command: 'cd' });
    // 清理路径输出，Windows系统的cd命令输出格式为"当前目录为: X:\path"
    let newPath = 'C:';
    if (path.includes('当前目录为:')) {
      newPath = path.split('当前目录为:')[1].trim();
    } else {
      newPath = path.trim();
    }
    
    // 更新全局路径和当前选项卡路径
    currentPath.value = newPath;
    commandTabs.value[activeTabIndex.value].currentPath = newPath;
  } catch (error) {
    const defaultPath = 'C:';
    currentPath.value = defaultPath;
    commandTabs.value[activeTabIndex.value].currentPath = defaultPath;
  }
};

// 命令处理函数
const handleCommand = async (command) => {
  const [cmd, ...args] = command.split(' ');
  
  // 检查是否是cd命令，如果是则特殊处理
  if (cmd.toLowerCase() === 'cd') {
    try {
      const newPath = args.join(' ');
      await invoke('execute_command', { command: `cd ${newPath}` });
      // 更新当前路径
      await getCurrentPath();
      return `已切换到: ${commandTabs.value[activeTabIndex.value].currentPath}`;
    } catch (error) {
      return `切换目录失败: ${error.message}`;
    }
  }
  
  switch (cmd.toLowerCase()) {
    case 'help':
      return `
可用命令列表:
  help              - 显示此帮助信息
  clear             - 清除命令行历史
  exit              - 关闭命令行窗口
  list-models       - 列出可用的模型
  echo [text]       - 显示文本
  version           - 显示NeoVAI版本信息
          `;
          
    case 'clear':
      commandTabs.value[activeTabIndex.value].commandHistory = [];
      return '命令历史已清除';
          
    case 'exit':
      toggleCommandLine();
      return '正在关闭命令行...';
          
    case 'list-models':
      try {
        // 这里可以从modelSettingStore获取模型列表
        return '可用模型: OpenAI GPT-4, Claude 3, Gemini, 本地模型';
      } catch (error) {
        return '无法获取模型列表: ' + error.message;
      }
          
    case 'echo':
      return args.join(' ');
          
    case 'version':
      return 'NeoVAI v0.1.0 - AI助手应用';
          
    default:
      try {
        // 尝试通过Tauri调用系统命令
        const result = await invoke('execute_command', { command: command });
        return result;
      } catch (error) {
        return `未知命令: ${cmd}`;
      }
  }
};

// 历史导航
const navigateHistory = (direction) => {
  if (historyBuffer.value.length === 0) return;
  
  // 保存当前输入（如果是新命令）
  if (historyIndex.value === -1) {
    historyBuffer.value.push(currentCommand.value);
  }
  
  // 更新索引
  historyIndex.value += direction;
  
  // 边界检查
  if (historyIndex.value < 0) {
    historyIndex.value = historyBuffer.value.length - 1;
  } else if (historyIndex.value >= historyBuffer.value.length) {
    historyIndex.value = 0;
  }
  
  // 设置当前命令
  currentCommand.value = historyBuffer.value[historyIndex.value];
};

// 生命周期
onMounted(async () => {
  // 光标闪烁效果
  cursorInterval = setInterval(() => {
    showCursor.value = !showCursor.value;
  }, 500);
  // 获取初始路径
  await getCurrentPath();
  
  // 初始化ResizeObserver
  initResizeObserver();
});

onUnmounted(() => {
  if (cursorInterval) {
    clearInterval(cursorInterval);
  }
  
  // 清理ResizeObserver
  cleanupResizeObserver();
});

// 光标闪烁定时器
let cursorInterval;
</script>

<style scoped>
/* 代码编辑器特定样式 */
#codeEditorMainContent {
  transition: all 0.3s ease;
}

/* 编辑器选项卡样式 */
.editor-tabs {
  height: 36px;
  overflow: hidden;
}

.editor-tab {
  font-size: 12px;
  white-space: nowrap;
  border-radius: 4px 4px 0 0;
  margin-right: 1px;
}

.editor-tab:hover {
    background-color: #f3f4f6;
  }

  .dark .editor-tab:hover {
    background-color: var(--dark-500);
  }

  .editor-tab.active {
    background-color: #ffffff;
    border-bottom: 2px solid #3b82f6;
  }

  .dark .editor-tab.active {
    background-color: var(--dark-700);
  }

.editor-tab-btn {
  font-size: 14px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 4px 4px 0 0;
}

.editor-tab-btn:hover {
    background-color: #f3f4f6;
  }

  .dark .editor-tab-btn:hover {
    background-color: var(--dark-500);
  }

.tab-name {
  font-size: 12px;
  font-weight: 500;
}

/* 选项卡样式 */
.command-line-tabs {
  background-color: #2d2d2d;
  border-bottom: 1px solid #3e3e3e;
  height: 28px;
}

.command-line-tab {
  font-size: 12px;
}

.command-line-tab .tab-name {
  font-size: 12px;
}

.command-line-tab button {
  font-size: 10px;
}

.command-line-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: none;
  color: #cccccc;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.command-line-btn:hover {
  background-color: #404040;
}

.command-line-body {
  overflow: hidden;
  background-color: #1e1e1e;
}

.command-line-output {
  height: 100%;
  overflow-y: auto;
  padding: 16px;
  color: #d4d4d4;
  font-size: 14px;
  line-height: 1.5;
}

.command-entry {
  margin-bottom: 8px;
}

.command-input {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
}

.command-input.active {
  position: relative;
}

.prompt {
  color: #569cd6;
  font-weight: 600;
  margin-right: 4px;
}

.command-text {
  color: #d4d4d4;
}

.command-input-field {
  flex: 1;
  background: none;
  border: none;
  color: #d4d4d4;
  font-family: inherit;
  font-size: inherit;
  outline: none;
  padding: 0;
}

.command-response {
  color: #9cdcfe;
  margin-left: 20px;
  white-space: pre-wrap;
  word-break: break-word;
}

.cursor {
  width: 8px;
  height: 16px;
  background-color: #d4d4d4;
  margin-left: 2px;
  display: inline-block;
}

.cursor.blinking {
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* 滚动条样式 */
.command-line-output::-webkit-scrollbar {
  width: 10px;
}

.command-line-output::-webkit-scrollbar-track {
  background: #1e1e1e;
}

.command-line-output::-webkit-scrollbar-thumb {
  background: #404040;
  border-radius: 5px;
}

.command-line-output::-webkit-scrollbar-thumb:hover {
  background: #505050;
}
</style>