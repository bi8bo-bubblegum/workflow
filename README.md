# 1. 克隆代码

git clone https://github.com/bi8bo-bubblegum/workflow.git

cd daily-report/daily-report

# 2. 创建虚拟环境（推荐）

python -m venv venv

venv\Scripts\activate      # Windows

source venv/bin/activate  # Linux/Mac

# 3. 安装依赖

pip install -e .

# 4. 创建自己的 .env 文件，修改配置

# 5. 运行

python -m daily_report --help
