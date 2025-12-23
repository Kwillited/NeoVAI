<template>
  <div id="topNav" class="z-50 absolute top-0 left-0 right-0 h-8 flex items-center px-4 bg-[#F8FAFC] dark:bg-dark-primary transition-all duration-300" data-tauri-drag-region="">
    <!-- 菜单栏项目 -->
    <div class="flex items-center gap-6" data-tauri-drag-region>
      <!-- Mac风格窗口控制按钮 -->
       <div class="flex gap-2.5 mr-4">
          <button class="w-3 h-3 rounded-full bg-red-500 hover:bg-red-600 transition-colors duration-200" title="关闭" @click="handleClose"></button>
          <button class="w-3 h-3 rounded-full bg-yellow-500 hover:bg-yellow-600 transition-colors duration-200" title="最小化" @click="handleMinimize"></button>
          <button class="w-3 h-3 rounded-full bg-green-500 hover:bg-green-600 transition-colors duration-200" title="最大化" @click="handleMaximize"></button>
        </div>
      <!-- NeoVAI标题已删除 -->
    </div>

    <!-- 中间：占位，确保右侧元素靠右 -->
    <div class="flex-1"></div>
    
    <!-- 应用控制按钮 -->
      <div class="flex items-center gap-4 pr-4">
        <!-- 对话与工具下拉菜单 -->
        <div class="relative hover-scale">
          <button 
            class="btn-secondary w-4 h-4 p-0 flex items-center justify-center hover:bg-gray-100 dark:hover:bg-dark-700 rounded-full text-neutral dark:text-gray-300 transition-all duration-300"
            :title="settingsStore.activePanel === 'rag' ? 'RAG模式' : '聊天模式'"
            @click.stop="toggleConversationMenu"
          >
            <i :class="['fa-solid', settingsStore.activePanel === 'rag' ? 'fa-database' : 'fa-comments', 'text-sm']" @click.stop="toggleConversationMenu"></i>
          </button>
          
          <!-- 对话与工具下拉菜单 -->
          <div 
            v-if="showConversationMenu"
            class="absolute top-full mt-2 left-1/2 transform -translate-x-1/2 w-14 rounded-lg shadow-lg border z-50 dropdown-content flex flex-col items-center py-2 bg-white border-gray-200 dark:bg-dark-800 dark:border-dark-700"
          >
            <button 
              class="w-10 h-10 rounded-full flex items-center justify-center transition-colors hover:bg-gray-100 text-gray-500 dark:hover:bg-dark-700 dark:text-gray-300"
              @click="handleBackToChat"
              title="聊天模式"
            >
              <i class="fa-solid fa-comments text-sm"></i>
            </button>
            <div class="my-1 w-8 border-t border-gray-200 dark:border-dark-700"></div>
            <button 
              class="w-10 h-10 rounded-full flex items-center justify-center transition-colors hover:bg-gray-100 text-gray-500 dark:hover:bg-dark-700 dark:text-gray-300"
              @click="handleRagTool"
              title="RAG模式"
            >
              <i class="fa-solid fa-database text-sm"></i>
            </button>
          </div>
        </div>
        
        <!-- 工具区下拉菜单 -->
        <div class="relative hover-scale">
          <button 
            class="btn-secondary w-4 h-4 p-0 flex items-center justify-center hover:bg-gray-100 dark:hover:bg-dark-700 rounded-full text-neutral dark:text-gray-300 transition-all duration-300"
            title="工具区"
            @click.stop="toggleToolMenu"
          >
            <i class="fa-solid fa-toolbox text-sm"></i>
          </button>
          
          <!-- 工具下拉菜单 -->
          <div 
            v-if="showToolMenu"
            class="absolute top-full mt-2 left-1/2 transform -translate-x-1/2 w-14 rounded-lg shadow-lg border z-50 dropdown-content flex flex-col items-center py-2 bg-white border-gray-200 dark:bg-dark-800 dark:border-dark-700"
          >
            <button 
              class="w-10 h-10 rounded-full flex items-center justify-center transition-colors hover:bg-gray-100 text-gray-500 dark:hover:bg-dark-700 dark:text-gray-300"
              @click="handleMcpService"
              title="MCP服务"
            >
              <i class="fa-solid fa-server text-sm"></i>
            </button>
            <div class="my-1 w-8 border-t border-gray-200 dark:border-dark-700"></div>
            <button 
              class="w-10 h-10 rounded-full flex items-center justify-center transition-colors hover:bg-gray-100 text-gray-500 dark:hover:bg-dark-700 dark:text-gray-300"
              @click="handleCliCommand"
              title="命令行窗口"
            >
              <i class="fa-solid fa-terminal text-sm"></i>
            </button>
            <div class="my-1 w-8 border-t border-gray-200 dark:border-dark-700"></div>
            <button 
              class="w-10 h-10 rounded-full flex items-center justify-center transition-colors hover:bg-gray-100 text-gray-500 dark:hover:bg-dark-700 dark:text-gray-300"
              @click="handleModelParamsClick"
              title="模型参数"
            >
              <i class="fa-solid fa-sliders text-sm"></i>
            </button>
            <div class="my-1 w-8 border-t border-gray-200 dark:border-dark-700"></div>
            <button 
              class="w-10 h-10 rounded-full flex items-center justify-center transition-colors hover:bg-gray-100 text-gray-500 dark:hover:bg-dark-700 dark:text-gray-300"
              @click="toggleViewPanel"
              title="视图"
            >
              <i class="fa-solid fa-columns text-sm"></i>
            </button>
            <div class="my-1 w-8 border-t border-gray-200 dark:border-dark-700"></div>
            <button 
              class="w-10 h-10 rounded-full flex items-center justify-center transition-colors hover:bg-gray-100 text-gray-500 dark:hover:bg-dark-700 dark:text-gray-300"
              @click="handlePluginClick"
              title="插件"
            >
              <i class="fa-solid fa-puzzle-piece text-sm"></i>
            </button>
          </div>
        </div>
        
        <!-- 分隔栏 -->
        <div class="h-4 w-px bg-gray-200 dark:bg-dark-700 mx-1"></div>
        
        <!-- 视图切换滑块 -->
        <div class="toggle-wrapper transition-all duration-300" 
          :class="{ 'is-active': chatStore.activeView === 'grid' }"
          @click="toggleView"
          :aria-label="`切换到${chatStore.activeView === 'grid' ? '对话' : '图谱'}视图`"
          style="width: 48px; height: 24px; display: flex; align-items: center; justify-content: center;">
          <div class="toggle-slider" :class="{ 'is-active': chatStore.activeView === 'grid' }" style="width: 20px; height: 20px;"></div>
          <span class="toggle-label grid-label" style="width: 24px; height: 24px; display: flex; align-items: center; justify-content: center;">
              <i class="fa-solid fa-project-diagram text-sm"></i>
            </span>
            <span class="toggle-label list-label" style="width: 24px; height: 24px; display: flex; align-items: center; justify-content: center;">
              <i class="fa-solid fa-comments text-sm"></i>
          </span>
        </div>
        
        <!-- 主题切换按钮 -->
        <button class="btn-secondary w-4 h-4 p-0 flex items-center justify-center hover:bg-gray-100 dark:hover:bg-dark-700 rounded-full text-neutral dark:text-gray-300 transition-all duration-300" title="切换主题" @click="handleToggleTheme">
          <i :class="['fa-regular', settingsStore.systemSettings.darkMode ? 'fa-sun' : 'fa-moon', 'text-sm']"></i>
        </button>
        

        <button class="btn-secondary w-4 h-4 p-0 flex items-center justify-center hover:bg-gray-100 dark:hover:bg-dark-700 rounded-full text-neutral dark:text-gray-300 transition-all duration-300" title="系统设置" @click="handleSystemSettingsClick">
          <i class="fa-solid fa-gear text-sm"></i>
        </button>
        
        <!-- 用户按钮带下拉菜单 -->
        <div class="relative hover-scale">
          <button 
            class="btn-secondary w-4 h-4 p-0 flex items-center justify-center hover:bg-gray-100 dark:hover:bg-dark-700 rounded-full text-neutral dark:text-gray-300 transition-all duration-300"
            title="用户"
            @click.stop="toggleUserMenu"
          >
            <i class="fa-solid fa-user-circle text-base" @click.stop="toggleUserMenu"></i>
          </button>
          
          <!-- 用户功能下拉菜单 -->
          <div 
            v-if="showUserMenu"
            class="absolute top-full mt-2 left-1/2 transform -translate-x-1/2 w-14 rounded-lg shadow-lg border z-50 dropdown-content flex flex-col items-center py-2 bg-white border-gray-200 dark:bg-dark-800 dark:border-dark-700"
          >
            <button 
              class="w-10 h-10 rounded-full flex items-center justify-center transition-colors hover:bg-gray-100 text-gray-500 dark:hover:bg-dark-700 dark:text-gray-300"
              @click="handleSwitchAccount"
              title="切换账户"
            >
              <i class="fa-solid fa-exchange"></i>
            </button>
            <div class="my-1 w-8 border-t border-gray-200 dark:border-dark-700"></div>
            <button 
              class="w-10 h-10 rounded-full flex items-center justify-center transition-colors text-red-500"
              @click="handleLogout"
              title="退出账号"
            >
              <i class="fa-solid fa-right-from-bracket"></i>
            </button>
          </div>
        </div>
      
    </div>
  </div>
  <!-- 命令行窗口组件 -->
  <CommandLine 
    :visible="showCommandLine" 
    @close="closeCommandLine"
  />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useSettingsStore } from '../../store/settingsStore.js';
import { useChatStore } from '../../store/chatStore.js';
import { Window } from '@tauri-apps/api/window';
import CommandLine from '../../components/common/CommandLine.vue';

// 使用全局store管理视图状态
const chatStore = useChatStore();

// 切换视图模式
const toggleView = () => {
  chatStore.activeView = chatStore.activeView === 'grid' ? 'list' : 'grid';
};


const settingsStore = useSettingsStore();
const appWindow = new Window('main');

// 用户菜单状态
const showUserMenu = ref(false);

// 对话与工具菜单状态
const showConversationMenu = ref(false);

// 工具菜单状态
const showToolMenu = ref(false);

// 命令行窗口状态
const showCommandLine = ref(false);

// 处理窗口控制按钮点击事件
const handleMinimize = () => {
  appWindow.minimize();
};

const handleMaximize = () => {
  appWindow.toggleMaximize();
};

const handleClose = () => {
  appWindow.close();
};

// 处理视图按钮点击事件 - 切换右侧面板
const toggleViewPanel = () => {
  settingsStore.toggleRightPanel();
  // 关闭工具菜单
  showToolMenu.value = false;
};

// 处理系统设置按钮点击事件
const handleSystemSettingsClick = () => {
  settingsStore.setActivePanel('settings');
  
  // 直接更新activeContent状态以显示SettingsContent
  if (window.setActiveContent) {
    window.setActiveContent('settings');
  }
};

// 切换主题
const handleToggleTheme = () => {
  settingsStore.toggleDarkMode();
};

// 处理模型参数按钮点击事件
const handleModelParamsClick = () => {
  settingsStore.setActivePanel('modelParams');
  // 关闭工具菜单
  showToolMenu.value = false;
};

// 处理插件按钮点击事件
const handlePluginClick = () => {
  settingsStore.setActivePanel('plugins');
  // 关闭工具菜单
  showToolMenu.value = false;
};

// 处理命令行窗口点击
const handleCliCommand = () => {
  showCommandLine.value = true;
  // 关闭工具菜单
  showToolMenu.value = false;
};

// 处理MCP服务点击事件
const handleMcpService = () => {
  settingsStore.setActivePanel('mcp');
  // 关闭工具菜单
  showToolMenu.value = false;
};

// 切换用户菜单显示状态
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value;
  // 关闭其他菜单
  showConversationMenu.value = false;
  showToolMenu.value = false;
};

// 切换对话与工具菜单显示状态
const toggleConversationMenu = () => {
  showConversationMenu.value = !showConversationMenu.value;
  // 关闭其他菜单
  showUserMenu.value = false;
  showToolMenu.value = false;
};

// 切换工具菜单显示状态
const toggleToolMenu = () => {
  showToolMenu.value = !showToolMenu.value;
  // 关闭其他菜单
  showUserMenu.value = false;
  showConversationMenu.value = false;
};

// 处理切换账户点击
const handleSwitchAccount = () => {
  showUserMenu.value = false;
  console.log('切换账户');
};

// 处理退出账号点击
const handleLogout = () => {
  showUserMenu.value = false;
  alert('退出账号功能待实现');
};

// 处理返回对话点击
const handleBackToChat = () => {
  showConversationMenu.value = false;
  // 切回左侧面板为历史会话
  settingsStore.setActivePanel('history');
  
  // 主显示区：如果没有聊天消息，显示sendMessage视图，否则显示chat视图
  if (window.setActiveContent) {
    const hasMessages = chatStore.currentChatMessages && chatStore.currentChatMessages.length > 0;
    window.setActiveContent(hasMessages ? 'chat' : 'sendMessage');
  }
};

// 处理RAG工具点击事件
const handleRagTool = () => {
  showConversationMenu.value = false;
  settingsStore.setActivePanel('rag');
};

// 关闭命令行窗口
const closeCommandLine = () => {
  showCommandLine.value = false;
};

// 点击外部区域关闭菜单
const closeMenusOnClickOutside = (event) => {
  const menuElements = document.querySelectorAll('.dropdown-content');
  const menuButtons = document.querySelectorAll('.relative.hover-scale');
  
  let clickedInsideMenu = false;
  menuButtons.forEach(button => {
    if (button.contains(event.target)) {
      clickedInsideMenu = true;
    }
  });
  
  if (!clickedInsideMenu) {
    showUserMenu.value = false;
    showConversationMenu.value = false;
    showToolMenu.value = false;
  }
};

// 添加点击外部事件监听
onMounted(() => {
  document.addEventListener('click', closeMenusOnClickOutside);
});

// 移除事件监听
onUnmounted(() => {
  document.removeEventListener('click', closeMenusOnClickOutside);
});
</script>

<style scoped>

/* 视图切换滑块样式 */
.toggle-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
  background-color: #f0f2f5;
  border-radius: 12px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  user-select: none;
}

.toggle-wrapper:hover {
  background-color: #e4e6eb;
}

.toggle-wrapper.is-active {
  background-color: #f0f2f5;
}

.toggle-slider {
  position: absolute;
  top: 2px;
  left: 2px;
  background-color: #fff;
  border-radius: 50%;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.toggle-slider.is-active {
    transform: translateX(24px);
  }

.toggle-label {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #65676b;
  transition: color 0.3s ease;
}

.toggle-wrapper.is-active .list-label {
  color: #fff;
}

.toggle-wrapper:not(.is-active) .grid-label {
  color: #fff;
}

.toggle-wrapper.is-active .grid-label {
  color: #65676b;
}

.toggle-wrapper:not(.is-active) .list-label {
  color: #65676b;
}

/* 动画效果增强 */
.toggle-wrapper:active .toggle-slider {
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

/* 适配暗色模式 */
  .dark .toggle-wrapper {
    background-color: #3a3b3c;
  }
  
  .dark .toggle-wrapper:hover {
    background-color: #4a4b4c;
  }
  
  .dark .toggle-wrapper.is-active {
    background-color: #3a3b3c;
  }
  
  .dark .toggle-label {
    color: #b0b3b8;
  }
  
  .dark .toggle-wrapper.is-active .list-label,
  .dark .toggle-wrapper:not(.is-active) .grid-label {
    color: #fff;
  }
  
  .dark .toggle-wrapper.is-active .grid-label,
  .dark .toggle-wrapper:not(.is-active) .list-label {
    color: #b0b3b8;
  }

/* 下拉菜单动画 */
.dropdown-content {
  animation: fadeInDown 0.2s ease-out;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translate(-50%, -10px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}

/* 确保圆形按钮中的图标居中 */
.dropdown-content button i {
  display: flex;
  justify-content: center;
}
</style>
