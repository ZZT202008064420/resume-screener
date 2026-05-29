# 简历智能筛选系统

基于大语言模型的简历自动解析与岗位匹配评分系统。上传 PDF 简历并输入招聘 JD，系统自动完成信息提取、关键词分析与多维度评分，输出结构化匹配报告。

**在线体验：[zzt202008064420.github.io/resume-screener](https://zzt202008064420.github.io/resume-screener/)**

---

## 项目背景

招聘场景下，HR 需要人工逐份阅读简历并与 JD 比对，效率低且主观性强。本项目通过 LLM + 关键词双层评分机制，将简历筛选流程自动化，输出可量化的匹配分数与推荐意见，辅助招聘决策。

---

## 核心功能

- **PDF 简历解析**：基于 pdfplumber 提取文本，结合 jieba 中文分词做预处理
- **AI 结构化提取**：通过 Prompt Engineering 调用通义千问，将非结构化简历文本解析为姓名、学历、技能、经历等结构化 JSON
- **双层评分引擎**：第一层 jieba 关键词匹配计算技能命中率，第二层调用 LLM 进行语义层面的综合评估
- **多维度评分报告**：技能匹配（40分）/ 经验匹配（30分）/ 学历匹配（15分）/ 综合契合（15分），雷达图可视化
- **关键词对比**：高亮命中关键词与缺失关键词，定位候选人短板
- **Redis 缓存**：以文件 MD5 Hash 为 Key 缓存解析结果，避免重复调用 LLM 接口

---

## 技术架构

```
前端（Vue3）
    ↓ HTTP / CORS
后端 API（Flask / FastAPI）
    ├── PDF 解析层      pdfplumber + jieba
    ├── AI 提取层       DashScope API（qwen-plus）
    ├── 评分引擎层      双层评分：关键词匹配 + LLM 语义评分
    └── 缓存层          Redis（MD5 Hash Key）
```

**技术选型：**

| 模块 | 技术 |
|------|------|
| 前端框架 | Vue 3 Composition API + Vite |
| UI / 样式 | Tailwind CSS |
| 数据可视化 | ECharts 雷达图 |
| 后端框架 | Flask / FastAPI |
| AI 接口 | 阿里云百炼 DashScope（通义千问 qwen-plus） |
| PDF 解析 | pdfplumber + pdfminer.six |
| 中文分词 | jieba |
| 缓存 | Redis |
| 前端部署 | GitHub Pages + GitHub Actions CI/CD |
| 后端部署 | 阿里云函数计算 FC（Serverless） |

---

## 项目结构

```
resume-screener/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── StepUpload.vue   # 步骤一：拖拽上传 PDF
│   │   │   ├── StepInfo.vue     # 步骤二：简历信息展示 + JD 输入
│   │   │   ├── StepResult.vue   # 步骤三：评分报告（雷达图 + 关键词）
│   │   │   ├── ScoreBar.vue     # 分维度进度条组件
│   │   │   └── InfoRow.vue      # 信息行展示组件
│   │   ├── api/
│   │   │   └── index.js         # 后端接口封装
│   │   └── App.vue
│   └── vite.config.js
│
├── backend/
│   ├── modules/
│   │   ├── parser.py        # PDF 文本提取与预处理
│   │   ├── extractor.py     # LLM 结构化信息提取
│   │   ├── scorer.py        # 双层评分引擎
│   │   └── cache.py         # Redis 缓存（MD5 Key）
│   ├── utils/
│   │   ├── response.py      # 统一响应格式
│   │   └── validator.py     # 入参校验
│   ├── app_local.py         # 本地开发入口
│   ├── handler.py           # 阿里云 FC 函数入口
│   └── requirements.txt
│
└── .github/workflows/
    └── deploy.yml           # 前端自动部署到 GitHub Pages
```

---

## 评分算法

```
总分（100分）
├── 技能匹配  40分   jieba 分词关键词提取，计算 JD 技能命中率
├── 经验匹配  30分   LLM 评估工作年限、项目经验与 JD 要求的契合度
├── 学历匹配  15分   规则匹配（学历层次映射）
└── 综合契合  15分   LLM 对候选人整体背景与岗位的语义评估
```

双层设计的意义：关键词匹配保证评分的客观性与可解释性，LLM 语义评分弥补关键词无法覆盖的上下文理解能力。

---

## 本地运行

**环境要求：** Python 3.10+，Node 18+，Docker

```bash
# 1. 启动 Redis
docker run -d --name redis-local -p 6379:6379 redis:7-alpine

# 2. 后端
cd backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt

# 配置 .env
DASHSCOPE_API_KEY=你的百炼APIKey
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
ENV=local

python app_local.py      # 本地开发，监听 :5000

# 3. 前端
cd frontend
npm install && npm run dev   # 监听 :5173
```

---

## 部署

### 前端 — GitHub Pages

推送到 `main` 分支，GitHub Actions 自动构建部署。在仓库 Settings → Secrets 中配置 `VITE_API_URL` 为后端地址。

### 后端 — 阿里云函数计算 FC

函数配置：Python 3.10 运行时，入口 `handler.handler`，HTTP 触发器（无需认证）。

> **打包说明**：由于 FC Linux 运行环境的 GLIBC 版本限制，推荐在 FC 在线终端中直接安装依赖，避免 Windows 本地打包的平台兼容问题：
> ```bash
> pip install -r /code/requirements.txt -t /code/
> ```

FC 环境变量：`DASHSCOPE_API_KEY`、`ENV=production`

---

## 可扩展方向

- 批量简历上传，多候选人横向评分排名
- 历史记录持久化（localStorage / 数据库）
- Prompt 优化，支持更细粒度的岗位类型适配
- 导出 Excel 评分报告

---

## License

MIT
