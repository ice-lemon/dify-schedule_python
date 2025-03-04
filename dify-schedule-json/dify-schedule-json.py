import os
import json
import requests

DIFY_BASE_URL = os.environ.get('DIFY_BASE_URL', 'https://api.dify.ai/v1')
DIFY_WORKFLOW_CONFIG_FILE = os.environ.get('DIFY_WORKFLOW_CONFIG', 'dify_workflows.json') # 新增配置文件环境变量

class WorkflowClient:
    def __init__(self, token, base_url):
        self.token = token
        self.base_url = base_url
        self.headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

    def info(self, user):
        url = f'{self.base_url}/info'
        params = {'user': user}
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching workflow info: {e}")
            return {'data': {}}

    def getWorkflowResult(self, inputs, user, is_scheduled=True):
        url = f'{self.base_url}/workflows/run'
        data = {
            'inputs': inputs,
            'user': user,
            'is_scheduled': is_scheduled
        }
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error executing workflow: {e}")
            return {'text': 'Workflow execution failed.'}

class Task:
    def __init__(self, dify_config): # dify_config 包含 token 和 inputs
        self.dify_config = dify_config
        self.taskName = ""
        self.result = None

    async def run(self):
        pass

    def __str__(self):
        return f'[{self.taskName}] Result: {self.result}' if self.result else f'[{self.taskName}] No result'

class WorkflowTask(Task):
    def __init__(self, dify_config):
        super().__init__(dify_config)
        self.taskName = "Dify工作流任务"
        self.workfolwName = ""

    async def run(self):
        if not DIFY_BASE_URL:
            raise Exception("没有配置Dify api地址，请检查后执行!")

        inputs = self.dify_config.get('inputs', {}) # 从配置中获取 inputs
        user = "dify-schedule"
        workflow = WorkflowClient(self.dify_config['token'], DIFY_BASE_URL) # 从配置中获取 token

        print("正在获取Dify工作流基础信息...")
        info_response = workflow.info(user)
        self.workfolwName = info_response.get('name', 'Unknown Workflow')
        print(f"Dify工作流【{self.workfolwName}】开始执行...")

        result_response = workflow.getWorkflowResult(inputs, user, True)
        self.result = result_response.get('text', 'No response text.')

    def __str__(self):
        return f"Workflow: {self.workfolwName}\nResult: {self.result}"


def send_notify(title, message):
    print(f"\n==============📣系统通知📣==============\n")
    print(f"Title: {title}")
    print(f"Message: {message}")
    print(f"\n========================================\n")

async def main():
    config_file = DIFY_WORKFLOW_CONFIG_FILE
    if not os.path.exists(config_file):
        send_notify("Dify定时工作流", f"【提示】找不到Dify工作流配置文件: {config_file}")
        return

    try:
        with open(config_file, 'r') as f:
            workflow_configs = json.load(f)
    except json.JSONDecodeError as e:
        send_notify("Dify定时工作流", f"【错误】Dify工作流配置文件 {config_file} JSON 格式错误: {e}")
        return
    except FileNotFoundError: # 再次检查文件是否存在，以防万一
        send_notify("Dify定时工作流", f"【提示】找不到Dify工作流配置文件: {config_file}")
        return


    print(f"\n====================共{len(workflow_configs)}个Dify工作流配置=========\n")

    message_list = []
    for config in workflow_configs: # 遍历工作流配置列表
        if 'token' not in config:
            print("⚠️  工作流配置缺少 token，跳过")
            continue
        workflow_task = WorkflowTask(config) # 将整个配置传递给 WorkflowTask
        await workflow_task.run()
        content = str(workflow_task)
        print(content)
        message_list.append(content)
        print("-" * 15)

    message = "\n".join(message_list)
    send_notify("Dify定时工作流", message)

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except Exception as e:
        error_message = f"Dify定时工作流, 失败! 原因: {e}"
        print(f"❌ {error_message}!")
        send_notify("Dify定时工作流-失败", error_message)
    finally:
        print("Done.")