# 🚀 AI-Offer-Hunter (Offer 收割机)

基于 DeepSeek 大语言模型打造的全链路 AI 求职工作台。从简历诊断到模拟面试，一站式解决求职痛点。

## ✨ 核心功能
- **📄 简历深度诊断**：上传 PDF 简历与目标 JD，AI 自动分析匹配度、缺失项，并用 STAR 法则重写项目经历。
- **💬 HR 高情商回复**：粘贴 HR 消息，AI 结合 JD 自动生成高情商应对策略（支持校招/社招双模式）。
- **🎤 AI 模拟面试**：集成浏览器摄像头与语音输入（Web Speech API），AI 面试官实时提问并生成终期评估报告。
- **✨ 网页简历生成与多语言导出**：一键生成带高级排版的 HTML 简历，支持中文、英文、韩语多语种切换，支持原生打印导出 PDF 与下载 Word 版本。

## 🛠️ 技术栈
- **前端**：HTML5, Tailwind CSS, 原生 JavaScript, `html-docx-js` (Word 导出)
- **后端**：Python, FastAPI, `PyPDF2` (PDF 解析)
- **AI 核心**：DeepSeek API (利用 OpenAI 兼容 SDK)

## 🚀 本地运行指南
1. 克隆仓库并进入目录
2. 安装依赖：`pip install fastapi uvicorn openai httpx PyPDF2`
3. 设置环境变量（勿将 Key 硬编码）：
   - Windows PowerShell: `$env:DEEPSEEK_API_KEY="sk-你的真实API_KEY"`
   - Mac/Linux: `export DEEPSEEK_API_KEY="sk-你的真实API_KEY"`
4. 启动服务：`python -m uvicorn main:app --reload`
5. 浏览器访问 `http://127.0.0.1:8000`

## 💡 开发踩坑记录（Technical Highlights）
在开发过程中，遇到了 **Python 3.13 环境下 `httpx` 库与 `openai` 库底层版本冲突（TypeError: 'process()' takes no keyword arguments）** 的致命问题。
**解决方案**：通过查阅源码，确认是新版本底层网络组件不兼容，最终通过在后端**手动注入自定义 `httpx.Client(timeout=90.0)` 实例**，绕过默认配置，成功解决请求异常，保证了 AI 接口的稳定调用。

## 👨‍💻 作者
- **Yangjiaxin-ai** (GitHub: [@Yangjiaxin-ai](https://github.com/Yangjiaxin-ai))
- 本项目为个人独立开发的全栈 AI 产品原型。
