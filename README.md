# 1. 克隆代码

git clone https://github.com/bi8bo-bubblegum/workflow.git

cd daily-report/daily-report

# 2. 创建虚拟环境（推荐）

python -m venv venv

venv\Scripts\activate      # Windows

source venv/bin/activate  # Linux/Mac

# 3. 安装依赖

pip install -e .

# 4. 创建自己的 .env 文件

GITHUB_TOKEN=ghp_xxxxxxxxxxxx

DEEPSEEK_API_KEY=sk_xxxxxxxxxxxx

EMAIL_PASSWORD=xxxxxxxxxxxx

# 5. 运行

python -m daily_report --help
