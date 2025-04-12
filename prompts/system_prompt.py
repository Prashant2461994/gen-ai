from dotenv import load_dotenv;
from openai import OpenAI;


client=OpenAI();

client.chat.completions.create