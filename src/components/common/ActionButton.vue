<template>
  <button
    :class="['btn-secondary w-8 h-8 p-1.5 flex items-center justify-center hover:bg-gray-100 dark:hover:bg-dark-700 rounded-full text-neutral dark:text-gray-300 transition-all duration-300', $attrs.class]"
    :title="title"
    @click="handleClick"
  >
    <i :class="['fa-solid', icon.startsWith('fa-') ? icon : 'fa-' + icon]"></i>
  </button>
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
  }
});

// 定义组件事件
const emit = defineEmits(['click']);

// 处理点击事件并传递事件对象
const handleClick = (event) => {
  emit('click', event);
};

defineComponent({
  name: 'ActionButton',
  props,
  emits: ['click']
});
</script>

<style scoped>
/* 样式已内联在模板中 */
</style>