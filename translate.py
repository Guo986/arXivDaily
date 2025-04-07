# -*- coding: utf-8 -*-

# This code shows an example of text translation from English to Simplified-Chinese.
# This code runs on Python 2.7.x and Python 3.x.
# You may install `requests` to run this code: pip install requests
# Please refer to `https://api.fanyi.baidu.com/doc/21` for complete api document

import requests
import random
import json
from hashlib import md5
from myTranslateConfig import baidu_appid,baidu_appkey,deepseek_apikey

def baiduTranslate(query):
    # Set your own appid/appkey.
    appid = baidu_appid
    appkey = baidu_appkey

    # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
    from_lang = 'en'
    to_lang =  'zh'

    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path

    # Generate salt and sign
    def make_md5(s, encoding='utf-8'):
        return md5(s.encode(encoding)).hexdigest()

    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)

    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

    # Send request
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()

    # Show response
    # print(json.dumps(result, indent=4, ensure_ascii=False))
    resultAll = ''
    for item in result['trans_result']:
        resultAll += item['dst']
    return resultAll

'''
https://api-docs.deepseek.com/zh-cn/
https://platform.deepseek.com/usage

words = 269
openai_token = 378
deepseek_token = 421
CompletionUsage(completion_tokens=200, prompt_tokens=221, total_tokens=421, completion_tokens_details=None, prompt_tokens_details=PromptTokensDetails(audio_tokens=None, cached_tokens=0), prompt_cache_hit_tokens=0, prompt_cache_miss_tokens=221)
'''
def deepseekV3Translate(query, outputTokens=False):
    # Please install OpenAI SDK first: `pip3 install openai`
    from openai import OpenAI

    client = OpenAI(api_key=deepseek_apikey, base_url="https://api.deepseek.com")

    # 14.7s
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "Translate it from English to Chinese. Output the translation, only."},
            {"role": "user", "content": query},
        ],
        stream=False
    )
    if outputTokens:
        return response.choices[0].message.content, response.usage.total_tokens
    else:
        return response.choices[0].message.content

def test(query, outputTokens):
    if outputTokens:
        return "test", 0
    else:
        return "test"

def translate(query, outputTokens=False):
    # return test(query, outputTokens)
    return deepseekV3Translate(query, outputTokens)
# q = "  The emergence of LLM-based agents represents a paradigm shift in AI, enabling\nautonomous systems to plan, reason, use tools, and maintain memory while\ninteracting with dynamic environments. This paper provides the first\ncomprehensive survey of evaluation methodologies for these increasingly capable\nagents. We systematically analyze evaluation benchmarks and frameworks across\nfour critical dimensions: (1) fundamental agent capabilities, including\nplanning, tool use, self-reflection, and memory; (2) application-specific\nbenchmarks for web, software engineering, scientific, and conversational\nagents; (3) benchmarks for generalist agents; and (4) frameworks for evaluating\nagents. Our analysis reveals emerging trends, including a shift toward more\nrealistic, challenging evaluations with continuously updated benchmarks. We\nalso identify critical gaps that future research must address-particularly in\nassessing cost-efficiency, safety, and robustness, and in developing\nfine-grained, and scalable evaluation methods. This survey maps the rapidly\nevolving landscape of agent evaluation, reveals the emerging trends in the\nfield, identifies current limitations, and proposes directions for future\nresearch.\n"
# q = q.replace('\n', ' ').strip()
# result = translate(q, outputTokens=True)
# print(f"{result=}")