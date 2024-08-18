from flask import Flask, request, render_template, redirect, url_for
import requests
import json
from math import sqrt

app = Flask(__name__)

API_KEY = "YOUR_API_KEY"
BASE_URL = "BASE_URL"
GITHUB_TOKEN = "GITHUB_TOKEN"

def merge_and_remove_duplicates(json1, json2):
    combined = json1 + json2
    seen_names = set()
    unique_repositories = []

    for repo in combined:
        if repo['name'] not in seen_names:
            unique_repositories.append(repo)
            seen_names.add(repo['name'])

    return unique_repositories


def calculate_score(project, keyword):
    name_score = 15 if keyword.lower() in project['name'].lower() else 0
    description_score = 15 if keyword.lower() in project['description'].lower() else 0
    star_score = sqrt(project['stars']) / 100

    total_score = name_score + description_score + star_score
    total_score = round(total_score, 2)
    return total_score


def sort_projects_by_score(projects, keyword):
    scored_projects = []

    for project in projects:
        score = calculate_score(project, keyword)
        project_with_score = project.copy()  # 创建项目的副本
        project_with_score['score'] = score
        scored_projects.append(project_with_score)

    sorted_projects = sorted(scored_projects, key=lambda x: x['score'], reverse=True)
    return sorted_projects


def gpt(prompt):
    key = "API_KEY"
    url = "BASE_URL"
    model = "gpt-4o-mini"

    payload = json.dumps({
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "你是一个关键词提取助手，会提取我的要求里面的关键词，给出该关键词的中文和英文，关键词用逗号隔开。只返回关键词"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    })

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {key}',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        content = json.loads(response.text)['choices'][0]['message']['content']
        return content


def search_repositories(keyword, token=None, model="name"):
    if model == "name":
        url = f"https://api.github.com/search/repositories?q={keyword}"
    elif model == "describe":
        url = f"https://api.github.com/search/repositories?q={keyword}+in:description"
    else:
        url = f"https://api.github.com/search/code?q={keyword}+in:file+filename:README.md"

    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    if token:
        headers["Authorization"] = f"token {token}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()["items"]
    else:
        print(f"Error: {response.status_code}")
        return None


def display_repositories(repositories):
    if repositories:
        repo_list = []
        for repo in repositories:
            repo_info = {
                "name": repo['name'],
                "description": repo['description'],
                "stars": repo['stargazers_count'],
                "url": repo['html_url']
            }
            repo_list.append(repo_info)

        json_output = json.dumps(repo_list, indent=4, ensure_ascii=False)
        return json_output
    else:
        return json.dumps({"message": "No repositories found."}, indent=4)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('q')
    keyword = gpt(keyword)
    name_repositories = search_repositories(keyword)
    describe_repositories = search_repositories(keyword, model="describe")
    repositories = merge_and_remove_duplicates(name_repositories, describe_repositories)
    json_output = json.loads(display_repositories(repositories))
    sorted_projects = sort_projects_by_score(json_output, keyword)
    return render_template('results.html', results=sorted_projects)


if __name__ == "__main__":
    app.run(debug=True)
