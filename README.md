# daily-report — LangGraph 自动化工作日报系统

基于 LangGraph 构建的自动化开发工作日报系统。每天定时从 GitHub 采集开发活动数据，通过 DeepSeek LLM 生成结构化日报，并通过邮件推送。

## 功能

- 自动从 GitHub 获取当天的 commits、Pull Requests、Issues
- 支持手动补充遇到的问题、明日计划等内容
- 通过 LLM 自动生成结构化中文日报
- 支持 SMTP 邮件推送
- 支持定时调度（工作日定时执行）和手动即时执行

## 技术栈

- **语言**：Python 3.11+
- **框架**：LangGraph（工作流编排）
- **LLM**：DeepSeek（OpenAI 兼容接口）
- **GitHub**：PyGithub
- **调度**：APScheduler
- **配置**：python-dotenv

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/bi8bo-bubblegum/workflow.git
cd daily-report/
```

### 2. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv venv_name
venv_name\Scripts\activate

# Linux / macOS
python -m venv venv_name
source venv_name/bin/activate
```

### 3. 安装依赖

```bash
pip install -e .
```

### 4. 配置 .env 文件

复制 `.env.example` 为 `.env`，填写你的配置：

```bash
copy .env.example .env        # Windows
# cp .env.example .env        # Linux / macOS
```

编辑 `.env` 文件，填入真实信息：

```ini
# GitHub 配置
GITHUB_TOKEN=ghp_你的GitHub个人访问令牌
GITHUB_REPOS=你的用户名/仓库1,你的用户名/仓库2

# LLM 配置
LLM_MODEL=llm-model-name
LLM_BASE_URL=llm-base-url
LLM_API_KEY=llm-api-key

# 邮箱配置
EMAIL_SMTP_HOST=smtp.example.com           # SMTP 服务器地址
EMAIL_SENDER=你的邮箱@example.com           # 发件人邮箱
EMAIL_PASSWORD=你的SMTP授权码            # 不是邮箱密码，是授权码
EMAIL_RECIPIENTS=收件人1@qq.com,收件人2@163.com   # 收件人，多个用逗号分隔
```

> 各字段含义参见 [配置详解](#配置详解) 章节。

### 5. 运行

```bash
# 运行时出现错误请查看常见问题（往下翻）

# 查看帮助
python -m daily_report --help

# 立即生成今日日报
python -m daily_report

# 指定日期
python -m daily_report --date 2026-06-04

# 带手动输入
python -m daily_report --problems "今天遇到的困难" --plan "明天的计划"

# 启动定时调度服务（每天 18:00 自动生成）
python -m daily_report --serve
```

---

## 配置详解

### 获取各平台密钥

<details>
<summary><b>GitHub Token</b></summary>

1. 登录 GitHub → 右上角头像 → **Settings**
2. 左侧导航 → **Developer settings** → **Personal access tokens** → **Fine-grained tokens**
3. 点击 **Generate new token**
4. Token name填写
5. Repository access 选择 **All repositories** 或指定的仓库
6. Permissions → Repository permissions → **Contents: Read-only**
7. 点击 **Generate token**，复制生成的 token

</details>

<details>
<summary><b>邮箱 SMTP 授权码</b></summary>

| 邮箱 | SMTP 服务器 | 端口 | 获取方式 |
|------|------------|------|---------|
| QQ 邮箱 | `smtp.qq.com` | 465 | 设置 → 账户 → 开启 POP3/SMTP，获取授权码 |
| 163 邮箱 | `smtp.163.com` | 465 | 设置 → POP3/SMTP → 开启，设置客户端授权密码 |
| Gmail | `smtp.gmail.com` | 465 | Google 账户 → 安全 → 应用专用密码 |
| 企业微信 | `smtp.exmail.qq.com` | 465 | 邮箱密码本身 |

> 授权码不是邮箱登录密码，需要在邮箱设置中单独开启 SMTP 服务后获取。
</details>

### 环境变量说明

| 变量 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `GITHUB_TOKEN` | 是 | GitHub 个人访问令牌 | `ghp_xxxx` |
| `GITHUB_REPOS` | 是 | 要采集的仓库，多个用逗号分隔 | `owner/repo1,owner/repo2` |
| `LLM_API_KEY` | 是 | LLM API 密钥 | `sk_xxxx` |
| `LLM_MODEL` | 否 | 模型名称 |
| `LLM_BASE_URL` | 否 | API 地址 |
| `LLM_TEMPERATURE` | 否 | 生成温度，默认 `0.3` | `0.3` |
| `EMAIL_SMTP_HOST` | 是 | SMTP 服务器地址 | `smtp.163.com` |
| `EMAIL_SMTP_PORT` | 否 | SMTP 端口，默认 `465` | `465` |
| `EMAIL_SENDER` | 是 | 发件人邮箱 | `your@example.com` |
| `EMAIL_PASSWORD` | 是 | SMTP 授权码（非登录密码） | `xxxx` |
| `EMAIL_RECIPIENTS` | 是 | 收件人邮箱，多个用逗号分隔 | `a@qq.com,b@163.com` |

---

## 项目结构

```
daily-report/
├── .env.example             # 环境变量模板
├── pyproject.toml            # 项目配置与依赖
├── config.py                 # 配置加载（从 .env 读取）
├── src/
│   └── daily_report/
│       ├── __init__.py
│       ├── __main__.py       # CLI 入口
│       ├── config.py         # 配置模型与验证
│       ├── state.py          # 工作流状态定义
│       ├── prompts.py        # LLM 提示词模板
│       ├── graph.py          # LangGraph 工作流编排
│       ├── scheduler.py      # APScheduler 定时调度
│       └── nodes/
│           ├── fetch_github.py   # 节点：GitHub 数据采集
│           ├── merge_input.py    # 节点：合并手动输入
│           ├── generate.py       # 节点：LLM 生成日报
│           └── send_email.py     # 节点：邮件发送
└── tests/                   # 测试目录（可选）
```

### 工作流

```
fetch_github (采集 GitHub 数据)
    ↓
merge_manual_input (合并手动输入)
    ↓
generate_report (LLM 生成日报)
    ↓
send_email (邮件推送)
```

---

## 常见问题

<details>
<summary><b>SSL 证书验证失败（GitHub数据获取失败）</b></summary>

```bash
# 临时跳过 SSL 验证（不推荐生产环境使用）
$env:PYTHONHTTPSVERIFY = "0"    # Windows
# export PYTHONHTTPSVERIFY=0    # Linux/macOS
```

或更新证书：

```bash
# 安装 certifi 证书包
pip install --upgrade certifi

# 查看 Python 当前使用的证书路径
python -c "import certifi; print(certifi.where())"

如果上面命令返回了一个路径，再执行：

# 将新的证书合并到 Python 的证书存储
pip install python-certifi-win32
```
</details>

<details>
<summary><b>ModuleNotFoundError: No module named 'daily_report'</b></summary>

没有安装包，执行：

```bash
pip install -e .
```
</details>

<details>
<summary><b>邮件发送失败</b></summary>

- 确认 `.env` 中的 `EMAIL_PASSWORD` 是**授权码**而不是登录密码
- 确认邮箱已开启 SMTP 服务
- 默认端口是 465（SSL），如果使用 587（TLS）需修改 `EMAIL_SMTP_PORT=587`
- 发送失败时日报会自动备份到 `backups/` 目录
</details>

<details>
<summary><b>GitHub API 限流</b></summary>

GitHub 未认证请求每小时 60 次，配置 Token 后提升到 5000 次。如果遇到限流，确认 `GITHUB_TOKEN` 配置正确。
</details>

---

## 许可证

MIT
