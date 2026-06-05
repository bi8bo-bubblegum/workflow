"""配置加载与验证。"""

import importlib.util
from pathlib import Path

from pydantic import BaseModel, field_validator


class GitHubConfig(BaseModel):
    token: str
    repos: list[str]

    @field_validator("repos")
    @classmethod
    def repos_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("至少需要配置一个 GitHub 仓库")
        return v


class LLMConfig(BaseModel):
    model: str
    base_url: str
    api_key: str
    temperature: float = 0.3

    @field_validator("temperature")
    @classmethod
    def temperature_range(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("temperature 必须在 0.0 到 1.0 之间")
        return v


class EmailConfig(BaseModel):
    smtp_host: str
    smtp_port: int
    sender: str
    password: str
    recipients: list[str]

    @field_validator("recipients")
    @classmethod
    def recipients_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("至少需要一个邮件收件人")
        return v


class ScheduleConfig(BaseModel):
    cron: str = "0 18 * * 1-5"
    timezone: str = "Asia/Shanghai"


class ManualInputConfig(BaseModel):
    problems: str = ""
    tomorrow_plan: str = ""


class AppConfig(BaseModel):
    github: GitHubConfig
    llm: LLMConfig
    email: EmailConfig
    schedule: ScheduleConfig = ScheduleConfig()
    manual_input: ManualInputConfig = ManualInputConfig()


def load_config(data: dict) -> AppConfig:
    """从字典加载配置。"""
    return AppConfig(**data)


def load_config_from_module(path: str | Path) -> AppConfig:
    """从 Python 配置文件加载配置。

    配置文件需导出名为 `config` 的 AppConfig 实例。

    Args:
        path: 配置文件路径，如 "config.py"。

    Returns:
        AppConfig 实例。
    """
    path = Path(path).resolve()
    module_name = path.stem

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"无法加载配置文件: {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "config"):
        raise ValueError(f"配置文件 {path} 中未找到 `config` 变量")

    cfg = module.config
    # if not isinstance(cfg, AppConfig):
    #     raise ValueError(f"配置文件 {path} 中的 `config` 必须是 AppConfig 实例")

    return cfg