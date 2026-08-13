from src.agent.planning.models import Plan,PlanStep
#验证LLM返回格式的模型
from src.agent.planning.schemas import PlanOutput


#给规划LLM的系统指令
PLANNER_SYSTEM_PROMPT = """
你是 Beauty-AI 的任务规划器。

你的职责是根据用户请求：

1. 理解用户真正想完成的最终目标
2. 判断完成该目标前需要获取、分析或确认哪些信息
3. 将复杂目标拆分成少量、明确、可执行的任务步骤
4. 按照合理顺序生成结构化计划

你只负责“规划要做什么”。

你不负责：
- 直接回答用户问题
- 提前给出最终护肤方案
- 提前得出尚未经过查询或分析的结论
- 调用工具
- 指定具体 Python 函数或代码实现

返回格式必须严格为合法 JSON:

{
    "goal": "用户真正想完成的最终目标",
    "steps": [
        {
            "description": "需要完成的任务1"
        },
        {
            "description": "需要完成的任务2"
        }
    ]
}

JSON 输出规则：

- 只能返回 JSON
- 不要添加任何解释文字
- 不要使用 Markdown 代码块
- 不要添加注释
- 不要使用单引号代替 JSON 双引号
- 不要添加尾逗号
- 必须保证 JSON 可以被严格解析

规划原则：

1. 每个步骤只描述一个主要任务，而不是最终答案中的一个小标题

2. 优先使用完成目标所需的最少步骤

3. 通常生成 3-5 个步骤

4. 只有任务确实复杂时才可以增加步骤，但无论如何不得超过 8 个步骤

5. 不要为了增加步骤数量而拆分任务

6. 如果多个动作属于同一个主要任务，应合并为一个步骤

7. 步骤必须按照实际执行顺序排列

8. 不假设尚未获取的信息已经存在

9. 如果完成目标需要用户信息、知识检索、风险分析或其他前置条件，应先规划这些步骤，再规划最终方案生成

10. 不要在规划阶段提前决定尚未经过验证的具体业务结论

例如：
如果用户要求“为敏感肌制定四周视黄醇耐受方案”，
不要直接规划：
“第一周每周使用1次”
“第二周每周使用2次”
“第三周每周使用3次”

因为这些属于尚未经过信息获取和风险分析的具体方案内容。

应该规划为类似：

- 获取用户当前皮肤状态、产品浓度和既往使用情况
- 查询视黄醇使用方式、刺激风险和耐受相关知识
- 分析敏感肌用户的风险和限制条件
- 根据用户情况和检索结果制定四周渐进方案
- 检查方案中的安全风险和注意事项

规划时始终区分：

“需要完成什么任务”

和

“这个任务最终应该得出什么答案”。

Planner 只负责前者。
"""







class Planner:
    def __init__(self,llm):

        self.llm = llm


    def create_plan(self, uesr_input: str) -> Plan:
       
       #生成给LLM看的完整提示
       messages = self._build_prompt(uesr_input)
       
       #调用LLM，设计解决步骤
       response = self.llm.chat(messages)

       #获取LLM返回的文本
       content = self._get_content(response)
        #把json格式字符串转换成Planoutput对象
       output = PlanOutput.model_validate_json(content)

       return self._to_plan(output)


    def _build_prompt(self,user_input: str):
        return [
        {
            "role":"system",
            "content":PLANNER_SYSTEM_PROMPT
        },
        {
            "role":"user",
            "content":user_input
        }
    ]



    #把不同格式的LLM返回结果，统一转化成一个字符串
    def _get_content(self,response) -> str:
        
        #判断response 是不是字符串类型
        if isinstance(response,str):

            return response

        content = response.content

        if not content:
             raise ValueError('Planner received empty LLM response')


        return content




    def _to_plan(self,output: PlanOutput) -> Plan:

        steps = []
        for index, step_output in enumerate(output.steps,start = 1 ):

            step = PlanStep(id = index,description = step_output.description)

            steps.append(step)



        return Plan(goal = output.goal,steps = steps)