"""定时调度"""
from datetime import date

from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger

from daily_report.config import AppConfig
from daily_report.graph import build_graph
from daily_report.state import create_initial_state


class DailyReportScheduler:
    """定时任务调度器"""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.scheduler = BackgroundScheduler()
        self.graph = build_graph(config)

    def _run_report(self) -> None:
        """执行日报生成任务"""
        today = date.today().isoformat()
        logger.info(f"开始生成{today}的日报")
        manual_input_parts = []
        if self.config.manual_input.problems:
            manual_input_parts.append(f'遇到的问题：{self.config.manual_input.problems}')
        if self.config.manual_input.tomorrow_plan:
            manual_input_parts.append(f'明日计划：{self.config.manual_input.tomorrow_plan}')
        initial_state = create_initial_state(
            date=today,
            github_repos=self.config.github.repos,
            manual_input='\n'.join(manual_input_parts)
        )
        result = self.graph.invoke(initial_state)

        if result.get('error'):
            logger.error(f'日报生成出错：{result["error"]}')
        elif result.get('email_sent'):
            logger.info(f'{today}日报生成成功，已发送邮件')
        else:
            logger.warning(f"{today} 日报邮件发送失败，请检查备份文件")

    def start(self) -> None:
        """启动定时任务"""
        self.scheduler.add_job(
            self._run_report,
            'cron',
            **self._parse_cron(self.config.schedule.cron),
            timezone=self.config.schedule.timezone
        )
        self.scheduler.start()
        logger.info(
            f"调度器已启动，cron: {self.config.schedule.cron}，"
            f"时区: {self.config.schedule.timezone}"
        )

    def stop(self) -> None:
        """停止定时调度。"""
        self.scheduler.shutdown()
        logger.info("调度器已停止")

    @staticmethod
    def _parse_cron(cron_expr: str) -> dict:
        """将 5 字段 cron 表达式解析为 APScheduler 参数。

        格式: minute hour day month day_of_week
        """
        parts = cron_expr.strip().split()
        if len(parts) != 5:
            raise ValueError(f"无效的 cron 表达式: {cron_expr}")

        return {
            "minute": parts[0],
            "hour": parts[1],
            "day": parts[2],
            "month": parts[3],
            "day_of_week": parts[4],
        }