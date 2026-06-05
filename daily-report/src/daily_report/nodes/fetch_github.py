from datetime import datetime, timezone

from github import Github
from loguru import logger

from daily_report.state import WorkFlowState


def fetch_github(state: WorkFlowState, github_token: str) -> dict:
    """从GitHub API获取指定日期的commits和PRs。

    Args:
        state: 当前工作流状态。
        github_token: GitHub个人访问令牌。

    Returns:
        状态更新字典。
    """
    date = state["date"]
    repos = state["github_repos"]
    github_data = {}

    try:
        g = Github(github_token)
        target_date = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        for repo_name in repos:
            repo = g.get_repo(repo_name)
            repo_data = {
                'commits': [],
                'pull_requests': [],
                'issues': []
            }
            commits = repo.get_commits(since=target_date)
            for commit in commits:
                repo_data['commits'].append({
                    'sha': commit.sha,
                    'message': commit.commit.message,
                    'author': commit.commit.author.name,
                    'date': commit.commit.author.date.isoformat()
                })

            pulls = repo.get_pulls(state='all', sort='created', direction='desc')
            for pr in pulls:
                if pr.created_at.date() == target_date.date():
                    repo_data['pull_requests'].append({
                        'number': pr.number,
                        'title': pr.title,
                        'state': pr.state,
                        'author': pr.user.login,
                        'url': pr.html_url
                    })

            issues = repo.get_issues(state="all", since=target_date)
            for issue in issues:
                if issue.pull_request is None:
                    repo_data["issues"].append(
                        {
                            "number": issue.number,
                            "title": issue.title,
                            "state": issue.state,
                            "author": issue.user.login,
                            "url": issue.html_url,
                        }
                    )
            github_data[repo_name] = repo_data
            logger.info(f"获取 {repo_name} 的数据成功")
    except Exception as e:
        logger.error(f"获取 GitHub 数据失败: {e}")
        return {
            'github_data': {},
            'error': f'GitHub API 调用失败：{e}'
        }
    return {
        'github_data': github_data
    }