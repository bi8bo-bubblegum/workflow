from functools import partial

from langgraph.constants import START, END
from langgraph.graph import StateGraph

from .config import AppConfig
from .nodes.fetch_github import fetch_github
from .nodes.generate import generate_report
from .nodes.merge_input import merge_manual_input
from .nodes.send_email import send_email
from .state import WorkFlowState


def build_graph(config: AppConfig):
    """构建日报工作流图。

    Args:
        config: 应用配置。

    Returns:
        编译后的 LangGraph 工作流。
    """
    graph = StateGraph(WorkFlowState)

    graph.add_node(
        'fetch_github',
        partial(fetch_github, github_token=config.github.token)
    )
    graph.add_node(
        'merge_manual_input',merge_manual_input
    )
    graph.add_node(
        'generate_report',
        partial(
            generate_report,
            model=config.llm.model,
            base_url=config.llm.base_url,
            api_key=config.llm.api_key,
            temperature=config.llm.temperature
        )
    )
    graph.add_node(
        'send_email',
        partial(
            send_email,
            smtp_host=config.email.smtp_host,
            smtp_port=config.email.smtp_port,
            sender=config.email.sender,
            password=config.email.password,
            recipients=config.email.recipients
        )
    )

    graph.add_edge(START, 'fetch_github')
    graph.add_edge('fetch_github', 'merge_manual_input')
    graph.add_edge('merge_manual_input', 'generate_report')
    graph.add_edge('generate_report', 'send_email')
    graph.add_edge('send_email', END)

    return graph.compile()