<template>
  <div class="space-y-6 max-w-2xl mx-auto">
    <div class="card p-4 depth-1 hover:depth-2 transition-all duration-300">
      <h4 class="font-medium mb-4">通知偏好</h4>

      <div class="space-y-4">
        <div class="setting-item p-3 rounded-lg">
          <div class="flex justify-between items-center">
            <div>
              <div class="font-medium text-sm">新消息通知</div>
              <div class="text-xs text-neutral mt-0.5">当收到AI回复时通知</div>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" :checked="settingsStore.notificationsConfig.newMessage" @change="updateNotificationSetting('newMessage', $event)" />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>

        <div class="setting-item p-3 rounded-lg">
          <div class="flex justify-between items-center">
            <div>
              <div class="font-medium text-sm">声音提示</div>
              <div class="text-xs text-neutral mt-0.5">新消息通知时播放提示音</div>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" :checked="settingsStore.notificationsConfig.sound" @change="updateNotificationSetting('sound', $event)" />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>

        <div class="setting-item p-3 rounded-lg">
          <div class="flex justify-between items-center">
            <div>
              <div class="font-medium text-sm">系统通知</div>
              <div class="text-xs text-neutral mt-0.5">显示应用更新等系统通知</div>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" :checked="settingsStore.notificationsConfig.system" @change="updateNotificationSetting('system', $event)" />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>

        <div class="setting-item p-3 rounded-lg">
          <div>
            <div class="font-medium text-sm">通知显示时间</div>
            <div class="text-xs text-neutral mt-0.5">控制通知在屏幕上停留的时间</div>

            <select
              v-model="settingsStore.notificationsConfig.displayTime"
              class="input-field w-full text-sm px-2 py-1.5 mt-2 focus:outline-none focus:ring-1 focus:ring-primary"
              @change="updateNotificationsConfig"
            >
              <option>2秒</option>
              <option>5秒</option>
              <option>10秒</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useSettingsStore } from '../../store/settingsStore.js';

const settingsStore = useSettingsStore();

// 更新单个通知设置
function updateNotificationSetting(key, event) {
  settingsStore.notificationsConfig[key] = event.target.checked;
  settingsStore.saveSettings();
}

// 更新整个通知配置
function updateNotificationsConfig() {
  // 由于使用了v-model，直接保存整个配置对象
  settingsStore.saveSettings();
}
</script>
