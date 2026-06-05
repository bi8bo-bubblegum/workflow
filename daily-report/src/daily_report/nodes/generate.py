"""LLM 生产日报节点"""
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from loguru import logger

from daily_report.prompts import USER_PROMPT_TEMPLATE, SYSTEM_PROMPT
from daily_report.state import WorkFlowState


def generate_report(
        state: WorkFlowState,
        model: str,
        base_url: str,
        api_key: str,
        temperature: float= 0.3
) -> dict:
    """调用 LLM 生成结构化日报。

    Args:
        state: 当前工作流状态。
        model: LLM 模型名称。
        base_url: API 基础 URL。
        api_key: API 密钥。
        temperature: 生成温度。

    Returns:
        状态更新字典。
    """
    try:
        llm = ChatOpenAI(
            model=model,
            base_url=base_url,
            api_key=api_key,
            temperature=temperature
        )

        user_prompt = USER_PROMPT_TEMPLATE.format(
            date = state["date"],
            context = state["merged_context"]
        )

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ]

        response = llm.invoke(messages)
        report_content = response.content
        logger.info(f"LLM 生成日报成功")

        return {'report_content': report_content, 'error': None}

    except Exception as e:
        logger.error(f"LLM 生成日报失败: {e}")
        return {'report_content': '', 'error': f'LLM 生成日报失败：{e}'}