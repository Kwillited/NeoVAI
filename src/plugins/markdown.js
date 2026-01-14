import { marked } from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css';

// 配置 marked 选项
const renderer = new marked.Renderer();

// 自定义代码块渲染
renderer.code = function(code, language) {
  // 如果没有语言或语言为'text'，则显示为'plaintext'
  const displayLanguage = language && language !== 'text' ? language : 'plaintext';
  
  // 创建唯一ID用于复制功能
  const codeBlockId = `code-block-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  
  // 返回带头部的代码块HTML
  return `
    <div class="code-container">
      <div class="code-header">
        <span class="code-language">${displayLanguage}</span>
        <button 
          class="copy-code-btn"
          data-code-block-id="${codeBlockId}"
          title="复制代码"
        >
          <i class="fa-solid fa-copy"></i>
        </button>
      </div>
      <pre><code id="${codeBlockId}">${code}</code></pre>
    </div>
  `;
};

// 设置 marked 配置
marked.setOptions({
  renderer: renderer,
  breaks: true,
  gfm: true
});

// 导出配置好的 marked 和 highlight.js
export { marked, hljs };