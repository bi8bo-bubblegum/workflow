"""邮件发送节点"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from loguru import logger

from ..state import WorkFlowState


def send_email(
        state: WorkFlowState,
        smtp_host: str,
        smtp_port: int,
        sender: str,
        password: str,
        recipients: list[str]
) -> dict:
    """通过SMTP发送日报邮件

    发送失败时将日报保存到本地文件作为备份。

    Args：
        state: 当前工作流状态
        smtp_host: SMTP服务器地址
        smtp_port: SMTP服务器端口
        sender: 发件人邮箱
        password: 发件人授权码
        recipients: 收件人邮箱列表

    Returns:
        状态更新字典。
    """

    date = state["date"]
    subject = f'工作日报 - {date}'
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    html_content = _markdown_to_html(state['report_content'])
    msg.attach(MIMEText(state['report_content'], 'plain', 'utf-8'))
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                server.login(sender, password)
                server.sendmail(sender, recipients, msg.as_string())
            logger.info(f'日报邮件已发送到 {recipients}')
            return {'email_sent': True, 'error': None}
        except Exception as e:
            logger.warning(f"发送邮件第{attempt}次失败: {e}")
            if attempt == max_retries:
                _save_backup(date, state["report_content"])
                return {
                    "email_sent": False,
                    "error": f"邮件发送失败（已重试 {max_retries} 次）: {e}",
                }
    return {'email_sent': False, 'error': f'邮件发送失败'}

def _markdown_to_html(markdown_text: str) -> str:
    """将 Markdown 文本简单转换为 HTML。"""
    lines = markdown_text.split("\n")
    html_lines = []
    for line in lines:
        if line.startswith("# "):
            html_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("- "):
            html_lines.append(f"<li>{line[2:]}</li>")
        else:
            html_lines.append(f"<p>{line}</p>")
    return f"<html><body>{''.join(html_lines)}</body></html>"

def _save_backup(date: str, content: str) -> None:
    """将日报保存到本地文件作为备份。"""
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    backup_path = backup_dir / f"daily-report-{date}.md"
    backup_path.write_text(content, encoding="utf-8")
    logger.info(f"日报已备份到 {backup_path}")