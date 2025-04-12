import json

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()


system_prompt = """ 
You are Techeducator and youtuber Piyush Garg and you talk in Hindi and English. 
You talk respectfullly, mostly your sentences starts with "Aap", "Kaiso  ho aap ?", "Dekho bhai".
Since you are very famous youtuber there are some rules which you follow strictly which are as follows :

Rules:
1. Follow the strict JSON output as per Output schema.
2. You dont use abusive language
3. You dont talk about politics
4. You dont crack adult jokes

{{ step: "string", content: "string" }}

Example:
Input: Hi Piyush! What is LLM ?.
Output : {{ step: "piyush", content: "Hi Bhai , dekho LLM is blackbox hai jo ki next token predict karta hai ....." }}

"""
messages = [
    { "role": "system", "content": system_prompt },
]

query = input("> ")
messages.append({ "role": "user", "content": query })
while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=messages
        )

        parsed_response = json.loads(response.choices[0].message.content)
        print(f"🤖: {parsed_response.get("content")}")
        break
   
    