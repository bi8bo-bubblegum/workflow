"""项目配置文件。

敏感信息优先从 .env 文件读取，也支持环境变量。
支持 `.env` 和 `.env.local` 两个文件，后者优先级更高。
"""

from dotenv import dotenv_values, load_dotenv

from daily_report.config import AppConfig, EmailConfig, GitHubConfig, LLMConfig

load_dotenv()
env = {**dotenv_values(".env"), **dotenv_values(".env.local")}

# GitHub 配置
github = GitHubConfig(
    token=env["GITHUB_TOKEN"],
    repos=[
        "bi8bo-bubblegum/chat-demo",
        "bi8bo-bubblegum/chat",
        "bi8bo-bubblegum/workflow"
    ],
)

# LLM 配置
llm = LLMConfig(
    model="deepseek-v4-flash",
    base_url="https://api.deepseek.com",
    api_key=env["DEEPSEEK_API_KEY"],
    temperature=0.3,
)

# 邮件配置
email = EmailConfig(
    smtp_host="smtp.163.com",
    smtp_port=465,
    sender="18381863687@163.com",
    password=env["EMAIL_PASSWORD"],
    recipients=[
        "1035081050@qq.com",
    ],
)

config = AppConfig(
    github=github,
    llm=llm,
    email=email,
)