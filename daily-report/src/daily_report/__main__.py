"""CLI 入口点。"""
import argparse
import signal
import sys
import time

from loguru import logger

from daily_report.config import load_config_from_module
from daily_report.graph import build_graph
from daily_report.scheduler import DailyReportScheduler
from daily_report.state import create_initial_state


def _run_once(config_path: str, date: str | None, problems: str, plan: str) -> None:
    """立即执行一次日报生成。"""
    config = load_config_from_module(config_path)

    from datetime import date as date_type

    report_date = date or date_type.today().isoformat()

    manual_input_parts = []
    if config.manual_input.problems:
        manual_input_parts.append(f"遇到的问题: {config.manual_input.problems}")
    if config.manual_input.tomorrow_plan:
        manual_input_parts.append(f"明日计划: {config.manual_input.tomorrow_plan}")
    if problems:
        manual_input_parts.append(f"遇到的问题: {problems}")
    if plan:
        manual_input_parts.append(f"明日计划: {plan}")

    initial_state = create_initial_state(
        date=report_date,
        github_repos=config.github.repos,
        manual_input="\n".join(manual_input_parts),
    )

    graph = build_graph(config)
    result = graph.invoke(initial_state)

    if result.get("error"):
        logger.error(f"日报生成出错: {result['error']}")
        sys.exit(1)
    else:
        logger.info("日报生成完成")
        if result.get("email_sent"):
            logger.info("邮件已发送")
        else:
            logger.warning("邮件发送失败，请检查备份文件")


def _serve(config_path: str) -> None:
    """启动定时调度服务。"""
    config = load_config_from_module(config_path)
    scheduler = DailyReportScheduler(config)

    def signal_handler(sig, frame):
        logger.info("收到停止信号，正在关闭...")
        scheduler.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    scheduler.start()
    logger.info("日报调度服务已启动，按 Ctrl+C 停止")

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.stop()


def __main__() -> None:
    """CLI 主入口。"""
    parser = argparse.ArgumentParser(description="LangGraph 驱动的自动化工作日报系统")
    parser.add_argument("--config", default="config.py", help="配置文件路径")
    parser.add_argument("--date", default=None, help="日报日期 (YYYY-MM-DD)，默认今天")
    parser.add_argument("--problems", default="", help="遇到的问题")
    parser.add_argument("--plan", default="", help="明日计划")
    parser.add_argument("--serve", action="store_true", help="启动定时调度服务")

    args = parser.parse_args()

    if args.serve:
        _serve(args.config)
    else:
        _run_once(args.config, args.date, args.problems, args.plan)


if __name__ == "__main__":
    __main__()