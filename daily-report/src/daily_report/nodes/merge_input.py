from daily_report.state import WorkFlowState


def _format_github_data(github_data: dict) -> str:
    """将github数据格式化为文本"""
    if not github_data:
        return 'GitHub数据获取失败'
    sections = []
    for repo_name, data in github_data.items():
        sections.append(f'## 仓库：{repo_name}')

        if data.get('commits'):
            sections.append('### Commits')
            for commit in data['commits']:
                sections.append(
                    f'- [{commit['sha']}] {commit['message']} ({commit['author']})'
                )

        if data.get('pul_requests'):
            sections.append('### Pull Requests')
            for pr in data['pul_requests']:
                sections.append(
                    f'- #{pr['number']} {pr['title']} [{pr['state']}] ({pr['author']})'
                )

        if data.get('issues'):
            sections.append('### Issues')
            for issue in data['issues']:
                sections.append(
                    f'- #{issue['number']} {issue['title']} [{issue['state']}] ({issue['author']})'
                )

    return '\n'.join(sections)

def merge_manual_input(state: WorkFlowState) -> dict:
    """将GitHub数据和手动输入合并为上下文文本

    Args:
        state: 当前工作流状态

    Returns:
        状态更新字典：包含 merged_context
    """
    github_text = _format_github_data(state['github_data'])

    parts = [
        f'# 日期： {state['date']}',
        '',
        github_text
    ]

    if state['manual_input']:
        parts.extend(
            [
                '',
                '## 手动输入',
                state['manual_input']
            ]
        )

    merged = '\n'.join(parts)
    return {
        'merged_context': merged
    }
