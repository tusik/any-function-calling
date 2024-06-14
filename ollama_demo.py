'''
Author: Image image@by.cx
Date: 2024-05-22 10:12:44
LastEditors: Image image@by.cx
LastEditTime: 2024-06-13 11:43:07
filePathColon: /
Description: 

Copyright (c) 2024 by Image, All Rights Reserved. 
'''

import requests
import json
# 描述工具的json格式
tools = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": [
                        "celsius",
                        "fahrenheit"
                    ]
                }
            },
            "required": [
                "location"
            ]
        }
    },
    {
        "name": "light_switch",
        "description": "控制设备内部照明的开关",
        "parameters": {
            "type": "object",
            "properties": {
                "on": {
                    "type": "bool",
                    "description": "true打开,false关闭"
                }
            },
            "required": [
                "on"
            ]
        }
    }
]
# 工具函数
def get_current_weather(obj):
    print("get_current_weather",obj)

def light_switch(obj):
    print("light_switch",obj)
    
# 工具函数映射
functions = {
    "get_current_weather":get_current_weather,
    "light_switch":light_switch,
}

# 中文系统提示
system_zh = f"""你能在系统上调用以下工具:
{json.dumps(tools)}
可以选择以上工具的其中一个来操作系统, 或者不使用工具直接回应用户, 且只能使用以下json格式回应用户:
{{
    "tool": <工具名，未选择工具可以留空>,  
    "tool_input": <工具输入参数，根据工具提供的json格式输入，未选择工具可以留空>, 
    "message":<其他回复用户的内容>
}}
"""
# 英文系统提示
system_en = f"""You have access to the following tools:
{json.dumps(tools)}
You can select one of the above tools or just response user's content and respond with only a JSON object matching the following schema:
{{
  "tool": <name of the selected tool>,
  "tool_input": <parameters for the selected tool, matching the tool's JSON schema>,
  "message": <direct response users content>
}}"""

# 默认message格式
messages = [
    {
        "role":"system",
        "content":system_en
    }
]

def extract_json(s):
    if '{' not in s or '}' not in s:
        return None
    i = s.index('{')
    count = 1 #当前所在嵌套深度，即还没闭合的'{'个数
    for j,c in enumerate(s[i+1:], start=i+1):
        if c == '}':
            count -= 1
        elif c == '{':
            count += 1
        if count == 0:
            break
    assert(count == 0) #检查是否找到最后一个'}'
    return s[i:j+1]

# 解析LLM返回的结果，如果有json则去解析json
def process_result(res):
    
    json_str = extract_json(res["message"]["content"])
    if json_str is not None:
        obj = json.loads(json_str)
        if "tool" in obj:
            if obj["tool"] in functions:
                fun = functions[obj["tool"]]
                fun(obj["tool_input"])
        return obj["message"]
    
def main():
        
    url = "http://127.0.0.1:11434/v1/chat/completions" 
    model = "qwen2:7b"
    while True:
        
        user_input = input('Enter a string: ')
        messages.append({
            "role":"user",
            "content":user_input
        })
        payload = {
            "model": model,
            "messages":messages,
        }
        payload = json.dumps(payload)
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.request("POST", url, headers=headers, data=payload)
        
        print(response.text)
        resp = json.loads(response.text)
        
        ai_msg = process_result(resp["choices"][0])
        messages.append({
            "role":"assistant",
            "content":json.dumps(resp["choices"][0])
        })
        print("ai_msg",ai_msg)

if __name__ == '__main__':
    main()
