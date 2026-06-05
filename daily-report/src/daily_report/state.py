from typing import TypedDict


class WorkFlowState(TypedDict):
    """日报工作流state"""

    #输入
    date: str
    github_repos: list[str]
    manual_input: str

    #中间结果
    github_data: dict
    merged_context: str

    #输出
    report_content: str
    email_sent: bool
    error: str | None

def create_initial_state(
        date: str,
        github_repos: list[str],
        manual_input: str = '',
) -> WorkFlowState:
    return WorkFlowState(
        date=date,
        github_repos=github_repos,
        manual_input=manual_input,
        github_data={},
        merged_context='',
        report_content='',
        email_sent=False,
        error=None
    )