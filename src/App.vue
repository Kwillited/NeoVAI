<template>
  <div 
    class="app-container h-screen flex flex-col overflow-hidden bg-light text-dark dark:bg-dark-primary dark:text-light"
    :class="{ 'transition-all duration-300': !isInitialLoading }"
  >
    <!-- 1. 顶部导航栏 -->
    <TopNav data-tauri-drag-region/>

    <!-- 主内容区域：包含左侧导航和显示区域 -->
    <div class="flex flex-1 overflow-hidden">
      <!-- 2. 左侧导航栏 -->
      <LeftNav v-if="settingsStore.leftNavVisible" />

      <!-- 3. 显示区域容器 -->
      <DisplayArea 
        :active-content="settingsStore.activeContent" 
        :saved-right-panel-width="savedRightPanelWidth" 
        :is-initial-loading="isInitialLoading"
      />
    </div>

    <!-- 模型版本表单（支持添加和编辑） -->
    <ModelVersionForm />

    <!-- 模型配置抽屉 -->
    <ModelSettingsDrawer />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import LeftNav from './components/layout/LeftNav.vue';
import TopNav from './components/layout/TopNav.vue';
import ModelVersionForm from './components/models/ModelVersionForm.vue';
import ModelSettingsDrawer from './components/models/ModelSettingsDrawer.vue';
import DisplayArea from './components/layout/DisplayArea.vue';
import { useChatStore } from './store/chatStore.js';
import { useSettingsStore } from './store/settingsStore.js';
import { useModelSettingStore } from './store/modelSettingStore.js';

// 初始化stores
const chatStore = useChatStore();
const settingsStore = useSettingsStore();
const modelSettingStore = useModelSettingStore();

// 内容区域状态现在由settingsStore管理

// 添加右侧面板显示状态，并根据settingsStore初始化
const isRightPanelVisible = ref(settingsStore.rightPanelVisible);
// 使用store中的宽度作为初始值，确保状态集中管理
const savedPanelWidth = ref(settingsStore.leftNavWidth); // 使用store中的左侧面板宽度
const savedRightPanelWidth = ref(settingsStore.rightPanelWidth); // 使用store中的右侧面板宽度
// 初始加载状态，用于控制首次加载时的动画
const isInitialLoading = ref(true);

// 监听settingsStore中的rightPanelVisible变化，保持同步
watch(() => settingsStore.rightPanelVisible, (newValue) => {
  isRightPanelVisible.value = newValue;
  
  // 控制右侧调整器的禁用状态
  const rightResizer = document.getElementById('RightResizer');
  if (rightResizer) {
    if (newValue) {
      // 面板显示时，启用调整器
      rightResizer.classList.remove('resizer-disabled');
    } else {
      // 面板隐藏时，禁用调整器
      rightResizer.classList.add('resizer-disabled');
    }
  }
  
  // 当面板从隐藏变为显示时，确保应用保存的宽度
  if (newValue) {
    setTimeout(() => {
      const rightPanelElement = document.querySelector('#rightPanel');
      if (rightPanelElement) {
        rightPanelElement.style.width = savedRightPanelWidth.value;
      }
    }, 50); // 小延迟确保DOM已更新
  }
});

// 监听左侧导航栏可见性变化，确保DOM元素与状态同步
watch(() => settingsStore.leftNavVisible, () => {
  togglePanelVisibility();
});

// 保存resizer相关函数的引用
let startResizeFunction = null;
// 添加右侧resizer相关函数的引用
let startRightResizeFunction = null;



// 初始化应用
  onMounted(async () => {
    // 加载用户设置和数据
    settingsStore.loadSettings();
    
    // 初始化右侧调整器状态
    setTimeout(() => {
      const rightResizer = document.getElementById('RightResizer');
      if (rightResizer) {
        // 根据rightPanelVisible的初始值设置调整器状态
        if (!settingsStore.rightPanelVisible) {
          rightResizer.classList.add('resizer-disabled');
        }
      }
    }, 100); // 小延迟确保DOM已加载
    
    // 加载模型数据
    try {
      await modelSettingStore.loadModels();
    } catch (error) {
      console.error('初始化加载模型数据失败:', error);
    }

    // 异步加载对话历史（非阻塞方式）
    chatStore.loadChatHistory().catch(error => {
      console.error('初始化加载对话历史失败，但应用继续运行:', error);
    });

    // 初始化默认面板
    if (!settingsStore.activePanel) {
      settingsStore.setActivePanel('history');
    }

    console.log('AIClient应用已初始化，使用Pinia状态管理');

    // 添加全局函数用于设置活动内容（向后兼容）
    window.setActiveContent = (content) => {
      settingsStore.setActiveContent(content);
    };
    
    // 添加全局函数用于切换侧边面板显示状态
    window.toggleSidePanel = () => {
      // 先切换store状态
      settingsStore.toggleLeftNav();
      // DOM更新会通过watch监听器自动触发
    };

    // 为隐藏菜单按钮添加点击事件
    const menuButton = document.querySelector('button[title="隐藏左侧面板"]');
    if (menuButton) {
      menuButton.addEventListener('click', togglePanelVisibility);
    }

    // 保存初始宽度
    setTimeout(() => {
      const panelContainer = document.getElementById('panelContainer');
      if (panelContainer) {
        savedPanelWidth.value = `${panelContainer.offsetWidth}px`;
      }
      // 添加右侧面板初始宽度保存
      const rightPanelElement = document.querySelector('#rightPanel');
      if (rightPanelElement) {
        // 只有在面板可见时才保存宽度
        if (settingsStore.rightPanelVisible) {
          savedRightPanelWidth.value = `${rightPanelElement.offsetWidth}px`;
        }
      }
    }, 100);

  // 监听activePanel变化，同步更新activeContent
  watch(
    () => settingsStore.activePanel,
    (newPanel) => {
      // 当切换到任何面板时，自动展开左侧面板
      settingsStore.leftNavVisible = true;
      
      // 只有当前视图不是sendMessage时，才根据activePanel更新视图
      if (settingsStore.activeContent !== 'sendMessage') {
        if (newPanel === 'settings') {
          settingsStore.setActiveContent('settings');
        } else {
          // 当面板不是settings时，切换回chat内容
          settingsStore.setActiveContent('chat');
        }
      }
    }
  );

  // 实现面板大小调整功能 - 抽象为通用函数
  const initPanelResizer = (resizerId, panelElementId, contentElementId, isRightPanel = false, savedWidthRef, visibilityStore = null) => {
    const resizer = document.getElementById(resizerId);
    const panelElement = panelElementId ? document.getElementById(panelElementId) : (resizer ? resizer.nextElementSibling : null);
    const contentElement = document.getElementById(contentElementId);
    const displayArea = document.getElementById('displayArea');
    
    if (resizer && panelElement && contentElement && displayArea) {
      // 为面板容器添加宽度变化的过渡效果
      panelElement.style.transition = 'width 0.05s ease-out';
      
      let isResizing = false;
      let startX, startWidth;
      let resizeRequestId = null;
      
      const startResize = (e) => {
        // 如果面板不可见，不允许调整大小
        if ((isRightPanel && visibilityStore && !visibilityStore.rightPanelVisible) || 
            (!isRightPanel && visibilityStore && !visibilityStore.leftNavVisible)) {
          return;
        }
        
        isResizing = true;
        startX = e.clientX;
        
        // 获取当前宽度作为初始值
        startWidth = panelElement.offsetWidth;
        
        // 禁用过渡效果以便在拖动时立即响应
        panelElement.style.transition = 'none';
        
        // 添加调整大小的临时样式
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        contentElement.style.pointerEvents = 'none';
        resizer.classList.add('resizing');
        
        // 添加事件监听器
        document.addEventListener('mousemove', resizePanel);
        document.addEventListener('mouseup', stopResize);
        // 阻止默认行为和事件冒泡
        e.preventDefault();
        e.stopPropagation();
      };
      
      const resizePanel = (e) => {
        if (!isResizing) return;
        
        // 取消上一个动画帧请求
        if (resizeRequestId) {
          cancelAnimationFrame(resizeRequestId);
        }
        
        // 使用requestAnimationFrame优化动画性能
        resizeRequestId = requestAnimationFrame(() => {
          // 计算宽度变化，右侧面板调整方向相反
          const widthChange = isRightPanel ? (startX - e.clientX) : (e.clientX - startX);
          let newWidth = startWidth + widthChange;
          
          // 设置最小和最大宽度限制
          const minWidth = 200; // 最小宽度为200px
          const panelMaxWidth = 370; // 所有面板的最大宽度为370px
          const mainContentMinWidth = 300; // 主内容区最小宽度
          
          // 获取当前所有面板的宽度
          const leftPanel = document.getElementById('panelContainer');
          const leftPanelWidth = leftPanel ? leftPanel.offsetWidth : 0;
          
          const rightPanel = document.getElementById('rightPanel');
          const rightPanelWidth = rightPanel && settingsStore.rightPanelVisible ? rightPanel.offsetWidth : 0;
          
          // 计算可用总宽度
          const availableWidth = displayArea.offsetWidth;
          
          // 计算最大宽度：可用总宽度 - 主内容区最小宽度 - 另一侧面板宽度
          let maxWidth;
          if (!isRightPanel) {
            // 左侧面板最大宽度：取计算值和固定最大值中的较小值
            const calculatedMaxWidth = availableWidth - mainContentMinWidth - rightPanelWidth;
            maxWidth = Math.min(panelMaxWidth, calculatedMaxWidth);
          } else {
            // 右侧面板最大宽度：取计算值和固定最大值中的较小值
            const calculatedMaxWidth = availableWidth - mainContentMinWidth - leftPanelWidth;
            maxWidth = Math.min(panelMaxWidth, calculatedMaxWidth);
          }
          
          // 确保最大宽度不小于最小宽度
          maxWidth = Math.max(minWidth, maxWidth);
          
          // 限制新宽度在合理范围内
          newWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));
          
          panelElement.style.width = `${newWidth}px`;
          // 保存调整后的宽度
          savedWidthRef.value = `${newWidth}px`;
        });
      };
      
      const stopResize = () => {
        isResizing = false;
        
        // 重新启用过渡效果
        panelElement.style.transition = 'width 0.2s ease-out';
        
        // 移除临时样式
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        contentElement.style.pointerEvents = '';
        resizer.classList.remove('resizing');
        
        // 移除事件监听器
        document.removeEventListener('mousemove', resizePanel);
        document.removeEventListener('mouseup', stopResize);
        
        // 取消最后一个动画帧请求
        if (resizeRequestId) {
          cancelAnimationFrame(resizeRequestId);
          resizeRequestId = null;
        }
        
        // 更新store中的面板宽度，实现状态集中管理
        if (isRightPanel && visibilityStore) {
          visibilityStore.setRightNavWidth(savedWidthRef.value);
        } else {
          visibilityStore.setLeftNavWidth(savedWidthRef.value);
        }
      };
      
      // 添加鼠标按下事件监听器
      resizer.addEventListener('mousedown', startResize);
      
      // 添加鼠标离开窗口的事件监听，确保在任何情况下都能停止调整
      window.addEventListener('mouseleave', stopResize);
      
      // 返回startResize函数引用，用于后续管理
      return startResize;
    }
    return null;
  };
  
  // 初始化左侧面板调整器
  startResizeFunction = initPanelResizer(
    'LeftResizer',
    'panelContainer',
    'mainContent', // 统一使用mainContent作为内容区域ID
    false,
    savedPanelWidth,
    settingsStore // 为左侧面板也传递settingsStore，用于状态管理
  );
  
  // 初始化右侧面板调整器
  startRightResizeFunction = initPanelResizer(
    'RightResizer',
    null, // 右侧面板是resizer的下一个兄弟元素
    'mainContent',
    true,
    savedRightPanelWidth,
    settingsStore
  );
  
  // 初始化完成，启用动画
  isInitialLoading.value = false;
  
  // 移除了面板内容透明度初始化，面板内容透明度由CSS控制
});

// 切换面板显示/隐藏状态
function togglePanelVisibility() {
  // 面板可见性状态由store管理，这里只负责保存宽度
  
  if (!settingsStore.leftNavVisible) {
    // 当面板隐藏时，保存当前宽度
    const panelContainer = document.getElementById('panelContainer');
    if (panelContainer) {
      savedPanelWidth.value = `${panelContainer.offsetWidth}px`;
      // 更新store中的宽度
      settingsStore.setLeftNavWidth(savedPanelWidth.value);
    }
  }
}


</script>

<style>
.resizer.resizing {
  background-color: #94a3b8;
}

/* 添加面板过渡动画 */
#panelContainer, #RightResizer + .v-enter-from, #RightResizer + .v-enter-to, #RightResizer + .v-leave-from, #RightResizer + .v-leave-to {
  transition: width 0.3s ease;
  min-width: 0;
}

/* 隐藏状态样式 */
.hidden {
  display: none !important;
}

/* 不可用状态的调整器样式 */
.resizer-disabled {
  cursor: not-allowed !important;
  opacity: 0.5;
  pointer-events: none;
}
</style>
