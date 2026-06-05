"""项目配置文件。

所有配置项均从 .env 文件读取，不包含任何真实数据。
支持 `.env` 和 `.env.local` 两个文件，后者优先级更高。
"""

from dotenv import dotenv_values, load_dotenv

from daily_report.config import AppConfig, EmailConfig, GitHubConfig, LLMConfig

load_dotenv()
env = {**dotenv_values(".env"), **dotenv_values(".env.local")}

# GitHub 配置
github = GitHubConfig(
    token=env["GITHUB_TOKEN"],
    repos=env["GITHUB_REPOS"].split(","),
)

# LLM 配置
llm = LLMConfig(
    model=env.get("LLM_MODEL"),
    base_url=env.get("LLM_BASE_URL"),
    api_key=env["LLM_API_KEY"],
    temperature=float(env.get("LLM_TEMPERATURE", "0.3")),
)

# 邮件配置
email = EmailConfig(
    smtp_host=env["EMAIL_SMTP_HOST"],
    smtp_port=int(env.get("EMAIL_SMTP_PORT", "465")),
    sender=env["EMAIL_SENDER"],
    password=env["EMAIL_PASSWORD"],
    recipients=env["EMAIL_RECIPIENTS"].split(","),
)

config = AppConfig(
    github=github,
    llm=llm,
    email=email,
)
