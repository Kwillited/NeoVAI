<template>
  <div class="state-display text-center py-6">
    <!-- 加载状态 -->
    <div v-if="type === 'loading'" class="flex flex-col items-center justify-center">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary mb-3"></div>
      <p class="text-neutral text-sm">{{ message || '加载中...' }}</p>
    </div>
    
    <!-- 空状态 -->
    <div v-else-if="type === 'empty'" class="flex flex-col items-center justify-center">
      <i :class="['fa-solid', icon || 'fa-inbox', 'text-4xl text-gray-300 mb-3']"></i>
      <h3 class="text-lg font-medium mb-1">{{ title || '暂无数据' }}</h3>
      <p class="text-neutral text-sm mb-4">{{ message || '这里还没有任何内容' }}</p>
      <slot name="actions"></slot>
    </div>
    
    <!-- 错误状态 -->
    <div v-else-if="type === 'error'" class="flex flex-col items-center justify-center">
      <i :class="['fa-solid', icon || 'fa-exclamation-circle', 'text-4xl text-red-400 mb-3']"></i>
      <h3 class="text-lg font-medium mb-1">{{ title || '操作失败' }}</h3>
      <p class="text-neutral text-sm mb-4">{{ message || '发生了一些错误' }}</p>
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  type: {
    type: String,
    required: true,
    validator: (value) => ['loading', 'empty', 'error'].includes(value)
  },
  title: {
    type: String,
    default: ''
  },
  message: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: ''
  }
});
</script>

<style scoped>
.state-display {
  transition: all 0.3s ease;
}
</style>