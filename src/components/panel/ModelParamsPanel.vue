<template>
  <div id="modelParamsPanel" class="h-full flex flex-col">
    <PanelHeader title="模型参数设置" backButtonId="backToChatBtnFromParams" />

    <div class="overflow-y-auto h-[calc(100%-57px)] scrollbar-thin p-4">
      <div class="space-y-6">
        <!-- 温度参数设置 -->
        <div class="mb-6 border-b border-gray-200 pb-4">
          <div class="flex justify-between items-center mb-1">
            <div class="flex items-center gap-1">
              <label class="text-sm font-medium text-gray-700">温度 (0-2)</label>
              <button
                class="text-xs text-neutral cursor-help p-1 relative"
                @mouseover="showTooltip('temperature', $event)"
                @mouseleave="hideTooltip('temperature')"
              >
                <i class="fa-solid fa-circle-question"></i>
              </button>
              <!-- 悬停提示弹窗 -->
              <div
                v-if="activeTooltip === 'temperature'"
                class="click-tooltip absolute z-50 bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-sm max-w-xs animate-fade-in"
                :style="tooltipStyle"
              >
                <div class="font-medium mb-1">温度参数说明</div>
                <p class="text-gray-700">控制生成结果的随机性，较低的值产生更确定的结果，较高的值产生更多样的结果。</p>
                <div class="mt-2 text-xs text-gray-500">范围: 0-2</div>
              </div>
            </div>
            <span
              class="text-sm font-medium text-primary px-2 py-0.5 bg-primary/10 rounded-full"
              id="temperatureValue"
              >{{ modelParams.temperature }}</span
            >
          </div>
          <input
            type="range"
            min="0"
            max="2"
            step="0.1"
            :value="modelParams.temperature"
            class="slider w-full"
            id="temperatureSlider"
            @input="handleTemperatureChange"
          />
          <div class="flex justify-between text-xs text-neutral mt-1">
            <span>精确</span>
            <span>随机</span>
          </div>
        </div>

        <!-- Top-p参数设置 -->
        <div class="mb-6 border-b border-gray-200 pb-4">
          <div class="flex justify-between items-center mb-1">
            <div class="flex items-center gap-1">
              <label class="text-sm font-medium text-gray-700">Top-p (0-1)</label>
              <button
                class="text-xs text-neutral cursor-help p-1 relative"
                @mouseover="showTooltip('topP', $event)"
                @mouseleave="hideTooltip('topP')"
              >
                <i class="fa-solid fa-circle-question"></i>
              </button>
              <!-- 悬停提示弹窗 -->
              <div
                v-if="activeTooltip === 'topP'"
                class="click-tooltip absolute z-50 bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-sm max-w-xs animate-fade-in"
                :style="tooltipStyle"
              >
                <div class="font-medium mb-1">Top-p参数说明</div>
                <p class="text-gray-700">控制词汇多样性，只有累积概率超过此阈值的词才会被考虑。</p>
                <div class="mt-2 text-xs text-gray-500">范围: 0-1</div>
              </div>
            </div>
            <span class="text-sm font-medium text-primary px-2 py-0.5 bg-primary/10 rounded-full" id="topPValue">{{
              modelParams.top_p
            }}</span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            :value="modelParams.top_p"
            class="slider w-full"
            id="topPSlider"
            @input="handleTopPChange"
          />
          <div class="flex justify-between text-xs text-neutral mt-1">
            <span>严格</span>
            <span>宽松</span>
          </div>
        </div>

        <!-- Top-k参数设置 -->
        <div class="mb-6 border-b border-gray-200 pb-4">
          <div class="flex justify-between items-center mb-1">
            <div class="flex items-center gap-1">
              <label class="text-sm font-medium text-gray-700">Top-k (0-100)</label>
              <button
                class="text-xs text-neutral cursor-help p-1 relative"
                @mouseover="showTooltip('topK', $event)"
                @mouseleave="hideTooltip('topK')"
              >
                <i class="fa-solid fa-circle-question"></i>
              </button>
              <!-- 悬停提示弹窗 -->
              <div
                v-if="activeTooltip === 'topK'"
                class="click-tooltip absolute z-50 bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-sm max-w-xs animate-fade-in"
                :style="tooltipStyle"
              >
                <div class="font-medium mb-1">Top-k参数说明</div>
                <p class="text-gray-700">限制每一步考虑的最高概率词汇数量，较小的值会产生更连贯的结果。</p>
                <div class="mt-2 text-xs text-gray-500">范围: 0-100</div>
              </div>
            </div>
            <span class="text-sm font-medium text-primary px-2 py-0.5 bg-primary/10 rounded-full" id="frequencyPenaltyValue">{{
              modelParams.frequency_penalty
            }}</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
              step="1"
              :value="modelParams.frequency_penalty"
              class="slider w-full"
              id="frequencyPenaltySlider"
            @input="handleFrequencyPenaltyChange"
          />
          <div class="flex justify-between text-xs text-neutral mt-1">
            <span>少样</span>
            <span>多样</span>
          </div>
        </div>

        <!-- 最大长度参数设置 -->
        <div class="mb-6 pb-4">
          <div class="flex justify-between items-center mb-1">
            <div class="flex items-center gap-1">
              <label class="text-sm font-medium text-gray-700">最大长度</label>
              <button
                class="text-xs text-neutral cursor-help p-1 relative"
                @mouseover="showTooltip('maxLength', $event)"
                @mouseleave="hideTooltip('maxLength')"
              >
                <i class="fa-solid fa-circle-question"></i>
              </button>
              <!-- 悬停提示弹窗 -->
              <div
                v-if="activeTooltip === 'maxLength'"
                class="click-tooltip absolute z-50 bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-sm max-w-xs animate-fade-in"
                :style="tooltipStyle"
              >
                <div class="font-medium mb-1">最大长度参数说明</div>
                <p class="text-gray-700">控制生成内容的最大长度，较大的值可以生成更长的回复，但可能会导致生成时间延长。</p>
                <div class="mt-2 text-xs text-gray-500">范围: 512-8192</div>
              </div>
            </div>
            <span class="text-sm font-medium text-primary px-2 py-0.5 bg-primary/10 rounded-full" id="maxLengthValue">{{
              modelParams.max_tokens
            }}</span>
          </div>
          <input
            type="range"
            min="512"
            max="8192"
            step="512"
            :value="modelParams.max_tokens"
            class="slider w-full"
            id="maxLengthSlider"
            @input="handleMaxLengthChange"
          />
          <div class="flex justify-between text-xs text-neutral mt-1">
            <span>较短</span>
            <span>较长</span>
          </div>
        </div>


      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useModelSettingStore } from '../../store/modelSettingStore.js';
import PanelHeader from '../common/PanelHeader.vue';

const modelStore = useModelSettingStore();
const activeTooltip = ref('');
const tooltipStyle = ref({});

// 从store获取模型参数
const modelParams = computed(() => modelStore.currentModelParams);

// 处理温度参数变化
const handleTemperatureChange = (event) => {
  modelStore.updateModelParams({ temperature: parseFloat(event.target.value) });
};

// 处理Top-p参数变化
const handleTopPChange = (event) => {
  modelStore.updateModelParams({ top_p: parseFloat(event.target.value) });
};

// 处理频率惩罚参数变化
  const handleFrequencyPenaltyChange = (event) => {
    modelStore.updateModelParams({ frequency_penalty: parseInt(event.target.value) });
  };

// 处理最大长度参数变化
const handleMaxLengthChange = (event) => {
  modelStore.updateModelParams({ max_tokens: parseInt(event.target.value) });
};

// 使用PanelHeader组件的默认返回行为

// 显示提示信息
const showTooltip = (tooltipId, event) => {
  activeTooltip.value = tooltipId;
  
  // 计算弹窗位置
  if (event) {
    const rect = event.target.getBoundingClientRect();
    // 获取触发元素的中心点垂直位置
    const triggerCenterY = rect.top + rect.height / 2;
    
    tooltipStyle.value = {
      // 让tooltip顶部对齐触发元素中心点，实现垂直居中
      top: `${triggerCenterY}px`,
      left: `${rect.left}px`,
      // 添加transform使tooltip自身垂直居中
      transform: 'translateY(-50%)'
    };
  }
};

// 隐藏提示信息
const hideTooltip = (tooltipId) => {
  // 如果传入了tooltipId，只隐藏特定的提示
  if (tooltipId) {
    if (activeTooltip.value === tooltipId) {
      activeTooltip.value = '';
    }
  } else {
    // 否则隐藏所有提示
    activeTooltip.value = '';
  }
};

// 组件挂载时加载参数
onMounted(() => {
  // 参数从store中获取，不需要额外加载
  console.log('模型参数面板已加载');
});
</script>

<style scoped>
/* 组件特定样式 */

.slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: #e5e7eb;
  outline: none;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.slider:hover {
  opacity: 1;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  transition: all 0.2s ease;
}

.slider::-webkit-slider-thumb:hover {
  transform: scale(1.2);
  box-shadow: 0 0 0 6px rgba(59, 130, 246, 0.1);
}

.slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.slider::-moz-range-thumb:hover {
  transform: scale(1.2);
  box-shadow: 0 0 0 6px rgba(59, 130, 246, 0.1);
}

/* 悬停提示样式 */
.tooltip {
  position: absolute;
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  z-index: 1000;
  white-space: nowrap;
}

/* 点击提示弹窗样式 */
.click-tooltip {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  animation: fadeIn 0.2s ease-in-out;
}

.animate-fade-in {
  animation: fadeIn 0.2s ease-in-out;
}
</style>
