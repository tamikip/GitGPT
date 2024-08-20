from flask import Flask, request, render_template
import requests
import json
from math import sqrt
import re
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
API_KEY = os.getenv('API_KEY')
BASE_URL = os.getenv('BASE_URL')
token = os.getenv('GITHUB_TOKEN')
if_md = False


def standardized_json(prompt):
    """此函数用于标准化ai生成的json"""
    json_pattern = re.compile(r'\{.*\}', re.DOTALL)
    match = json_pattern.search(prompt)

    json_string = match.group(0) if match else None
    return json_string


def merge_and_remove_duplicates(json1, json2):
    """此函数用于合并中文和英文关键词的仓库并且去重"""
    combined = json1 + json2
    seen_names = set()
    unique_repositories = []

    for repo in combined:
        if repo['name'] not in seen_names:
            unique_repositories.append(repo)
            seen_names.add(repo['name'])

    return unique_repositories


def merge_and_remove_duplicates2(json1, json2, json3):
    """此函数用于合并仓库名，仓库描述，readme关键词的仓库并且去重"""
    combined = json1 + json2 + json3
    seen_names = set()
    unique_repositories = []

    for repo in combined:
        if repo['name'] not in seen_names:
            unique_repositories.append(repo)
            seen_names.add(repo['name'])

    return unique_repositories


def calculate_score(project, keyword):
    """核心，此函数用于计算仓库与用户需求的匹配度，计算公式为仓库名匹配(15)+仓库描述匹配（15）+开根号（star/100）"""
    name_score = 15 if keyword.lower() in project['name'].lower() else 0
    description = project.get('description') or ""
    description_score = 15 if keyword.lower() in description.lower() else 0

    star_score = sqrt(project['stars']) / 100

    total_score = name_score + description_score + star_score
    total_score = round(total_score, 2)
    return total_score


def sort_projects_by_score(projects, keyword):
    """根据匹配度给json排序，由高到低"""
    scored_projects = []

    for project in projects:
        score = calculate_score(project, keyword)
        project_with_score = project.copy()
        project_with_score['score'] = score
        scored_projects.append(project_with_score)

    sorted_projects = sorted(scored_projects, key=lambda x: x['score'], reverse=True)
    return sorted_projects


def gpt(prompt):
    global API_KEY, BASE_URL
    key = API_KEY
    url = BASE_URL
    model = "GLM-4-0520"

    payload = json.dumps({
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "你是一个关键词提取助手，会提取用户的要求里面的关键词，给出该关键词的中文和英文，关键词用逗号隔开。只返回json，不要使用markdown语法,例如 [{cn_keyword:苹果,香蕉}，{en_keyword:apple,banana},{language:None}] ,language为用户指定的编程语言，没指定则返回None，以下内容不属于关键词[开源,软件,应用,app]"
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
    else:
        return None


def search_repositories(keyword, model="name"):
    """根据关键词查找匹配的仓库名和描述"""
    global token
    if not keyword:
        return []

    if model == "name":
        url = f"https://api.github.com/search/repositories?q={keyword}"
    elif model == "describe":
        url = f"https://api.github.com/search/repositories?q={keyword}+in:description"

    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    if token:
        headers["Authorization"] = f"token {token}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        print(f"Error: {response.status_code}")
        return []


def search_repos_by_keyword(keyword):
    """根据关键词查找匹配的readme"""
    search_url = f"https://api.github.com/search/repositories?q={keyword}+in:readme"
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    if token:
        headers["Authorization"] = f"token {token}"

    response = requests.get(search_url, headers=headers)

    if response.status_code == 200:
        search_results = response.json()
        matched_repos = []

        for repo in search_results['items']:
            repo_info = {
                "name": repo['name'],
                "description": repo['description'],
                "stars": repo['stargazers_count'],
                "url": repo['html_url'],
                "language": repo['language']
            }
            matched_repos.append(repo_info)
        matched_repos = json.dumps(matched_repos, indent=4, ensure_ascii=False)
        return matched_repos
    else:
        print(f"Failed to search repositories: {response.status_code}")
        return []


def display_repositories(repositories):
    """处理原始json"""
    if repositories:
        repo_list = []
        for repo in repositories:
            repo_info = {
                "name": repo['name'],
                "description": repo['description'],
                "stars": repo['stargazers_count'],
                "url": repo['html_url'],
                "language": repo['language']
            }
            # 排除垃圾仓库
            if repo['description']:
                if len(repo['description']) < 200:
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
    user_input = request.args.get('q')
    if_md = request.args.get('if_md') == 'off'

    keyword_json = gpt(user_input)
    try:
        keyword_json = standardized_json(keyword_json)
        dict_list = json.loads(keyword_json)
        cn_keyword = dict_list['cn_keyword']
        en_keyword = dict_list['en_keyword']

        name_repositories = json.loads(display_repositories(search_repositories(cn_keyword)))
        describe_repositories = json.loads(display_repositories(search_repositories(cn_keyword, model="describe")))
        try:
            if if_md:
                readme_repositories = json.loads(search_repos_by_keyword(cn_keyword))
                repositories = merge_and_remove_duplicates2(name_repositories, describe_repositories,
                                                            readme_repositories)
            else:

                repositories = merge_and_remove_duplicates(name_repositories, describe_repositories)
            json_output = json.dumps(repositories, ensure_ascii=False, indent=4)
            json_output = json.loads(json_output)
            sorted_projects1 = sort_projects_by_score(json_output, cn_keyword)

            name_repositories = json.loads(display_repositories(search_repositories(en_keyword)))
            describe_repositories = json.loads(display_repositories(search_repositories(en_keyword, model="describe")))
            if if_md:
                readme_repositories = json.loads(search_repos_by_keyword(en_keyword))
                repositories = merge_and_remove_duplicates2(name_repositories, describe_repositories,
                                                            readme_repositories)
            else:
                repositories = merge_and_remove_duplicates(name_repositories, describe_repositories)
            json_output = json.dumps(repositories, ensure_ascii=False, indent=4)
            json_output = json.loads(json_output)
            sorted_projects2 = sort_projects_by_score(json_output, en_keyword)

            final_json = merge_and_remove_duplicates(sorted_projects1, sorted_projects2)
        except Exception as e:
            final_json = [{"name": "没有找到匹配的仓库",
                           'description': '请你尝试换一种说法进行查找',
                           'url': 'index.html', 'score': 0}, ]
    except Exception as e:
        return render_template('index.html', error_message='内容无法识别！请重新输入！')
    return render_template('results.html', results=final_json)


if __name__ == "__main__":
    app.run(debug=True)

