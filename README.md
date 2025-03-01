# Dify 定时工作流执行脚本

## 简介

本 Python 脚本旨在帮助用户定时执行 [Dify](https://dify.ai/) 工作流，并收集和通知工作流的执行结果。 你可以通过设置环境变量 `DIFY_TOKENS` 来配置一个或多个 Dify API Token，脚本将循环执行这些 Token 对应的工作流。 这对于需要定期运行 Dify 工作流，例如数据同步、报表生成等场景非常有用。

## 主要特性

*   **批量执行工作流**: 支持配置多个 Dify API Token，脚本将顺序执行每个 Token 对应的工作流。
*   **灵活的 Token 配置**:  支持通过环境变量 `DIFY_TOKENS` 配置多个 Token，可以使用分号 `;` 或换行符 `\n` 分隔，方便从不同来源复制粘贴 Token 列表。
*   **可配置 Dify API 地址**:  允许用户通过环境变量 `DIFY_BASE_URL` 自定义 Dify API 的根地址，默认为官方地址 `https://api.dify.ai/v1`，方便连接到私有部署的 Dify 服务。
*   **自定义工作流输入**:  支持通过环境变量 `DIFY_INPUTS` 以 JSON 格式传递工作流的输入参数，实现更灵活的工作流控制。
*   **详细的执行日志**:  脚本运行时会输出详细的日志信息，包括工作流名称、执行结果等，方便用户了解工作流的执行状态和排查问题。
*   **执行结果通知**:  脚本执行完成后，会发送系统通知，告知用户所有工作流的执行结果，包括成功和失败的情况，方便用户及时掌握工作流运行状态。

## 前提条件

*   **Python 3.6 或更高版本**：确保你的运行环境中安装了 Python 3.6 或更高版本。
*   **requests 库**:  用于发送 HTTP 请求与 Dify API 交互。 如果没有安装，可以使用 pip 安装：
    ```bash
    pip install requests
    ```

## 环境变量

你需要配置以下环境变量来运行脚本：

*   **`DIFY_TOKENS` (必需)**:  Dify API Token。 这是访问 Dify API 的凭证。
    *   如果你只有一个 Token，直接将 Token 值填入即可。
    *   如果有多个 Token，请使用分号 `;` 或换行符 `\n` 分隔每个 Token。
    *   **示例 (单个 Token):**
        ```
        DIFY_TOKENS=dify_api_token_xxxxxxxxxxxxx
        ```
    *   **示例 (多个 Token):**
        ```
        DIFY_TOKENS=dify_api_token_11111111111;dify_api_token_22222222222;dify_api_token_33333333333
        ```
        或者 (使用换行符):
        ```
        DIFY_TOKENS=dify_api_token_11111111111
        dify_api_token_22222222222
        dify_api_token_33333333333
        ```

*   **`DIFY_BASE_URL` (可选)**:  Dify API 的根地址。
    *   **默认值**: `https://api.dify.ai/v1` (官方 Dify API 地址)
    *   如果你使用的是私有部署的 Dify 服务，请将此变量设置为你的 Dify API 地址。
    *   **示例 (私有部署):**
        ```
        DIFY_BASE_URL=http://your_dify_domain:port/v1
        ```

*   **`DIFY_INPUTS` (可选)**:  传递给 Dify 工作流的输入参数，JSON 格式的字符串。
    *   **默认值**:  空 JSON 对象 `{}` (表示不传递任何输入参数)
    *   如果你的 Dify 工作流需要输入参数，请将参数以 JSON 格式设置在此变量中。
    *   **示例 (传递输入参数):**
        ```
        DIFY_INPUTS='{"input1": "value1", "input2": 123}'
        ```
        **注意**:  请确保 JSON 字符串的格式正确，特别是键值对需要使用双引号 `"`，字符串值也需要使用双引号 `"`。

## 使用方法

1.  **安装 `requests` 库** (如果尚未安装):
    ```bash
    pip install requests
    ```

2.  **配置环境变量**:
    *   根据你的需求，设置 `DIFY_TOKENS` (必需), `DIFY_BASE_URL` (可选), 和 `DIFY_INPUTS` (可选) 环境变量。
    *   你可以通过多种方式设置环境变量，例如：
        *   在终端中直接使用 `export` 命令 (Linux/macOS) 或 `set` 命令 (Windows) 临时设置。
        *   将环境变量写入 `.env` 文件，并使用 `python-dotenv` 等库加载 (更推荐，方便管理)。
        *   在操作系统或容器平台的配置中设置环境变量 (例如 Docker, Kubernetes)。

3.  **运行脚本**:
    ```bash
    python your_script_name.py
    ```
    将 `your_script_name.py` 替换为你的脚本文件名。

4.  **查看执行结果**:
    *   脚本会在终端输出详细的执行日志，包括每个工作流的名称和执行结果。
    *   脚本执行完成后，会发送系统通知，汇总所有工作流的执行结果。

## 通知

脚本在执行完成后，会发送系统通知，通知标题为 "Dify定时工作流"，通知内容包含所有已执行的工作流的执行结果，格式如下：

```
==============📣系统通知📣==============

Title: Dify定时工作流
Message: Workflow: 工作流名称1
Result: 工作流1的执行结果

Workflow: 工作流名称2
Result: 工作流2的执行结果

...

========================================
```

如果任何工作流执行失败，或者脚本运行过程中出现错误，通知标题会变为 "Dify定时工作流-失败"，并在通知内容中包含错误原因。

## 错误处理

*   **Dify API 连接错误**:  如果无法连接到 Dify API 或 API 请求失败 (例如网络错误、Token 无效等)，脚本会输出错误日志，并在通知中提示 "Workflow execution failed."。
*   **JSON 解析错误**:  如果 `DIFY_INPUTS` 环境变量配置的 JSON 格式不正确，脚本会输出错误提示，并可能影响工作流的执行。请确保 `DIFY_INPUTS` 的 JSON 格式正确。
*   **未配置 Dify API 地址**: 如果环境变量 `DIFY_BASE_URL` 为空，脚本会抛出异常并停止执行，请确保配置了 `DIFY_BASE_URL` 环境变量或使用默认值。
*   **未配置 Dify Token**: 如果环境变量 `DIFY_TOKENS` 为空，脚本会发送通知提示 "请先填写Dify工作流token" 并停止执行，请确保配置了 `DIFY_TOKENS` 环境变量。
*   **其他异常**:  如果在脚本运行过程中发生其他未预期的异常，脚本会捕获异常，输出错误日志，并在通知中提示 "Dify定时工作流, 失败! 原因: [错误信息]"。

请根据你的实际使用情况配置环境变量，并确保网络连接正常，Dify API 服务可用。

---

希望这个 README 文件能够帮助你理解和使用这个 Dify 定时工作流执行脚本。 如有任何问题或建议，欢迎提出。
```

请问这个 README 文本是否满足你的需求？ 如果有任何需要修改或补充的地方，请随时告诉我。
