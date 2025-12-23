# 事件总线服务使用指南

## 概述

事件总线服务是一个用于Vue 3应用中组件间通信的工具，它替代了原有的全局`window`事件机制，提供了更安全、更高效的事件管理方式。

## 为什么需要事件总线

1. **避免全局污染**：使用专用的事件总线而不是全局`window`对象，避免了全局命名空间污染
2. **更好的类型支持**：统一的事件类型常量定义，减少拼写错误
3. **更完善的API**：提供了一次性事件、上下文绑定等高级功能
4. **更好的性能**：相比`window`事件，专用事件总线更轻量级，性能更好
5. **便于调试**：可以跟踪事件注册和触发情况

## 如何使用

### 1. 导入事件总线

在需要使用事件总线的组件中导入：

```javascript
import { eventBus, EVENT_TYPES } from '../services/eventBus.js';
```

### 2. 注册事件监听

```javascript
// 在组件中注册事件监听
// 方法1：使用函数引用
const handleChatSelect = (data) => {
  const { chatId } = data;
  console.log('选择了对话:', chatId);
  // 处理逻辑
};

// 在组件挂载时注册
onMounted(() => {
  eventBus.on(EVENT_TYPES.CHAT_SELECT, handleChatSelect);
});

// 在组件卸载时清理
onUnmounted(() => {
  eventBus.off(EVENT_TYPES.CHAT_SELECT, handleChatSelect);
});

// 方法2：在选项式API中使用
mounted() {
  this.chatSelectHandler = this.handleChatSelect.bind(this);
  eventBus.on(EVENT_TYPES.CHAT_SELECT, this.chatSelectHandler);
},

beforeUnmount() {
  eventBus.off(EVENT_TYPES.CHAT_SELECT, this.chatSelectHandler);
}
```

### 3. 发送事件

```javascript
// 发送简单事件
const handleButtonClick = () => {
  eventBus.emit(EVENT_TYPES.SYSTEM_SETTINGS_CLICK);
};

// 发送带数据的事件
const handleChatSelect = (chatId) => {
  eventBus.emit(EVENT_TYPES.CHAT_SELECT, { chatId });
};
```

### 4. 一次性事件

```javascript
// 注册只执行一次的事件监听
const handleFirstLoad = () => {
  console.log('组件首次加载');
};

eventBus.once(EVENT_TYPES.APP_LOADED, handleFirstLoad);
```

## 已定义的事件类型

目前系统中已定义的事件类型如下：

### 对话相关事件

- `CHAT_SELECT`: 选择对话时触发
- `NEW_CHAT_CLICKED`: 点击新对话按钮时触发
- `SEND_MESSAGE`: 发送消息时触发
- `FILE_UPLOAD`: 上传文件时触发

### 导航相关事件

- `BACK_TO_CHAT`: 返回聊天界面时触发
- `SYSTEM_SETTINGS_CLICK`: 点击系统设置时触发
- `RAG_TOOL_CLICKED`: 点击RAG工具时触发
- `MCP_SERVICE_CLICKED`: 点击MCP服务时触发

### 设置相关事件

- `SETTINGS_SECTION_CHANGE`: 设置项变更时触发
- `MODEL_PARAMS_SAVE`: 模型参数保存时触发
- `MODEL_PARAM_CHANGE`: 模型参数变更时触发
- `BACK_TO_CHAT_FROM_PARAMS`: 从模型参数面板返回聊天时触发
- `MODEL_SELECT`: 模型选择时触发

## 最佳实践

1. **统一使用常量**：始终使用`EVENT_TYPES`中定义的常量来引用事件类型，而不是硬编码字符串
2. **清理监听器**：在组件卸载时务必清理所有注册的事件监听器，防止内存泄漏
3. **合理命名**：添加新事件时，使用清晰、描述性的名称
4. **数据结构**：发送事件时，数据结构应保持一致和可预测
5. **避免过度使用**：事件总线适合于不直接关联的组件间通信，对于父子组件，优先使用props和emit

## 事件总线API参考

### `on(event, callback, context = null)`

注册事件监听器

- `event`: 事件名称
- `callback`: 回调函数
- `context`: 回调函数的上下文（可选）
- 返回值: 取消监听的函数

### `off(event, callback)`

移除事件监听器

- `event`: 事件名称
- `callback`: 要移除的回调函数

### `emit(event, data = null)`

触发事件

- `event`: 事件名称
- `data`: 事件数据（可选）

### `once(event, callback, context = null)`

注册一次性事件监听器

- 参数同`on`方法

### `clear(event = null)`

清除所有事件监听器或指定事件的监听器

- `event`: 可选的事件名称

### `listenerCount(event)`

获取指定事件的监听器数量

- `event`: 事件名称
- 返回值: 监听器数量

### `getEvents()`

获取所有已注册的事件名称

- 返回值: 事件名称数组

## 常见问题与解决方案

### Q: 为什么我的事件监听器没有被调用？

A: 请检查以下几点：

1. 确认事件类型名称拼写正确，最好使用`EVENT_TYPES`常量
2. 确认监听器在事件触发前已经注册
3. 确认在组件卸载时没有提前移除了监听器

### Q: 如何处理事件监听器中的错误？

A: 事件总线内置了错误捕获机制，单个监听器的错误不会影响其他监听器的执行。建议在复杂的监听器中添加自己的错误处理逻辑。

### Q: 如何添加新的事件类型？

A: 在`eventBus.js`文件的`EVENT_TYPES`对象中添加新的事件类型常量，然后在需要的地方使用它。
