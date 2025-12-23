import { createApp } from 'vue';
import App from './App.vue';
import pinia from './store/pinia.js';
import { useSettingsStore } from './store/settingsStore.js';
import { useModelSettingStore } from './store/modelSettingStore.js';

// 等待DOM完全加载后再初始化Vue应用
document.addEventListener('DOMContentLoaded', async () => {
  try {
    // 创建Vue应用并使用Pinia
    const app = createApp(App);
    app.use(pinia);
    app.mount('#app');

    // 初始化stores
      const settingsStore = useSettingsStore();
      const modelStore = useModelSettingStore();

      // 加载设置
      settingsStore.loadSettings();
      
      // 加载模型设置和模型列表
      modelStore.loadModelSettings();
      await modelStore.loadModels();

      console.log('Vue应用已成功挂载到#app元素，并配置了Pinia状态管理');
      console.log('所有store已初始化');
  } catch (error) {
    console.error('Vue应用挂载失败:', error);
  }
});