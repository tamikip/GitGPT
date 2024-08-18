import requests

# GitHub API 访问令牌
token = "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"
headers = {"Authorization": f"token {token}"}

# 搜索 README.md 文件中包含 "machine learning" 关键字的仓库
search_term = "machine learning"
search_url = f"https://api.github.com/search/code?q={search_term}+in:file+filename:README.md"
search_response = requests.get(search_url, headers=headers)
results = search_response.json().get('items', [])
