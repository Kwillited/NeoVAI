<template>
  <div class="bg-white dark:bg-dark-700 p-4 rounded-xl shadow-card hover:shadow-card-hover transition-all duration-300 ease-in-out flex flex-col items-center p-5">
    <div class="w-12 h-12 bg-primary/10 dark:bg-primary/20 rounded-full flex items-center justify-center mb-3 transition-colors duration-300">
      <i :class="['fa', 'fa-' + icon, 'text-primary', 'text-xl', 'transition-colors', 'duration-300']"></i>
    </div>
    <h4 class="font-medium text-dark dark:text-white mb-1 transition-colors duration-300">{{ title }}</h4>
    <p class="text-sm text-neutral dark:text-gray-300 transition-colors duration-300">{{ description }}</p>
  </div>
</template>

<script setup>
import { defineComponent } from 'vue';

// 定义组件属性
const props = defineProps({
  icon: {
    type: String,
    required: true,
    validator: (value) => {
      // 基本的Font Awesome图标验证
      return typeof value === 'string' && value.length > 0;
    }
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  }
});

defineComponent({
  name: 'FeatureCard',
  props
});
</script>

<style scoped>
/* 卡片样式已内联在模板中 */
</style>