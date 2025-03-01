import os
import json
import requests

DIFY_BASE_URL = os.environ.get('DIFY_BASE_URL', 'https://api.dify.ai/v1')

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
    def __init__(self, dify_config):
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
        inputs = {}
        dify_inputs_str = os.environ.get('DIFY_INPUTS')
        if dify_inputs_str:
            try:
                inputs = json.loads(dify_inputs_str)
            except json.JSONDecodeError:
                print("DIFY_INPUTS 格式错误，请确保是json格式, 可能会影响任务流执行")

        user = "dify-schedule"
        workflow = WorkflowClient(self.dify_config['token'], DIFY_BASE_URL)

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
    tokens_str = os.environ.get('DIFY_TOKENS')
    if not tokens_str:
        send_notify("Dify定时工作流", "【提示】请先填写Dify工作流token")
        return

    tokens_arr = []
    if ";" in tokens_str:
        tokens_arr = tokens_str.split(";")
    elif "\n" in tokens_str:
        tokens_arr = tokens_str.split("\n")
    else:
        tokens_arr = [tokens_str]

    tokens_arr = list(set(filter(None, tokens_arr)))
    print(f"\n====================共{len(tokens_arr)}个Dify工作流=========\n")

    message_list = []
    for token in tokens_arr:
        workflow_task = WorkflowTask({'token': token})
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
