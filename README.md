# GitGPT

GitGPT 是一个基于 Flask 构建的 Web 应用程序，旨在通过 GPT 模型和 GitHub API 帮助用户根据关键词查找和筛选 GitHub 仓库。它可以根据用户输入的关键词，提取出中文和英文的关键词，并根据这些关键词在 GitHub 上搜索相关的仓库，最终根据匹配度对结果进行排序和展示。

## 功能

- **关键词提取**：通过 GPT 模型从用户输入中提取出中英文关键词。
- **仓库搜索**：根据关键词在 GitHub 上搜索仓库，支持根据仓库名、描述和 README 文件进行搜索。
- **去重合并**：将多个来源的搜索结果去重并合并。
- **匹配度计算**：根据仓库名、描述与关键词的匹配度以及仓库的星标数，计算仓库的匹配度得分。
- **结果展示**：将排序后的仓库结果以友好的方式展示给用户。

## 环境要求

- Python 3.x
- Flask
- requests

## 安装

1. 克隆本仓库到本地：

    ```bash
    git clone https://github.com/yourusername/GitGPT.git
    cd GitGPT
    ```

2. 创建并激活虚拟环境（可选）：

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate  # Windows
    ```

3. 安装依赖：

    ```bash
    pip install -r requirements.txt
    ```

4. 配置环境变量：

    在项目根目录下创建一个 `.env` 文件，添加以下内容：

    ```bash
    API_KEY=your_gpt_api_key
    BASE_URL=your_gpt_api_base_url
    GITHUB_TOKEN=your_github_token  # 可选
    ```

    请将 `your_gpt_api_key`、`your_gpt_api_base_url` 和 `your_github_token` 替换为你的实际 API 密钥和 GitHub Token。

## 使用

1. 启动 Flask 应用：

    ```bash
    python app.py
    ```

2. 在浏览器中打开 `http://127.0.0.1:5000/`，进入应用主页。

3. 在搜索框中输入你想要查找的关键词，点击搜索按钮，应用将显示与关键词匹配的 GitHub 仓库列表。

## API 说明

- `GET /search?q=<keyword>&if_md=<off/on>`：根据关键词搜索 GitHub 仓库。
  - `q`：用户输入的关键词。
  - `if_md`：是否启用 README 文件搜索，`off` 表示不启用，`on` 表示启用。

## 贡献

欢迎对本项目进行贡献！你可以通过以下方式参与：

1. 提交问题（Issues）和功能请求。
2. 提交 Pull Request 以修复问题或添加新功能。
3. 改进文档。

## 许可证

本项目采用 [MIT 许可证](LICENSE)。
