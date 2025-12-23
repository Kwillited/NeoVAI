<template>
  <!-- 信息面板 - 调整为绝对定位，放置在canvas上方 -->
  <div ref="infoPanel" class="absolute bottom-6 left-6 right-6 md:left-auto md:right-6 md:w-80 bg-dark/70 backdrop-blur-md rounded-xl border border-primary/20 p-6 z-20 transform transition-all duration-500 hover:translate-y-0 hover:shadow-lg hover:shadow-primary/10">
    <h2 class="text-xl font-bold mb-4 flex items-center">
      <i class="fa-solid fa-circle-info text-primary mr-2"></i>知识宇宙探索
    </h2>
    <p class="text-gray-300 mb-4">这是一个交互式3D知识图谱，展示了概念之间的关联。通过旋转、缩放和点击节点来探索知识的连接。</p>
    <div class="flex justify-between items-center text-sm text-gray-400">
      <div>
        <i class="fa-solid fa-hand-pointer mr-1"></i> 点击节点查看详情
      </div>
      <div>
        <i class="fa-solid fa-arrows mr-1"></i> 拖动旋转视图
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

// 面板引用，保持与原代码一致
const infoPanel = ref(null);

// 组件挂载时初始化
onMounted(() => {
  // 0.6秒后自动隐藏信息面板
  if (infoPanel.value) {
    setTimeout(() => {
      if (infoPanel.value) {
        infoPanel.value.style.opacity = '0';
        setTimeout(() => {
          if (infoPanel.value) {
            infoPanel.value.style.display = 'none';
          }
        }, 500); // 等待过渡动画完成
      }
    }, 600);
  }
});

// 可以通过 props 传递自定义内容，增加组件的灵活性
// 这里暂时保持与原代码一致的静态内容
</script>

<style scoped>
/* 保持原有的样式，确保视觉一致性 */
/* 自定义滚动条样式 */
:deep(.custom-scrollbar::-webkit-scrollbar) {
  width: 6px;
}

:deep(.custom-scrollbar::-webkit-scrollbar-track) {
  background: transparent;
}

:deep(.custom-scrollbar::-webkit-scrollbar-thumb) {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

:deep(.custom-scrollbar::-webkit-scrollbar-thumb:hover) {
  background: rgba(255, 255, 255, 0.3);
}
</style>