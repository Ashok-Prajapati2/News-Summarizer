import os
import random
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# GROQ_API_KEY = os.getenv('GROQ_API_KEY')


# client = Groq(
#     api_key=os.environ.get(GROQ_API_KEY))

API_KEYS = [
    os.getenv('GROQ_API_KEY'),
    os.getenv('GROQ_API_KEY1'),
    os.getenv('GROQ_API_KEY2'),
    os.getenv('GROQ_API_KEY2'),
    os.getenv('GROQ_API_KEY3'),
    os.getenv('GROQ_API_KEY4'),
    os.getenv('GROQ_API_KEY5'),


]

def initialize_groq_client():
    api_key = random.choice(API_KEYS)
    return Groq(api_key=api_key)

def model_responce(query):
    client = initialize_groq_client()
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"{query}",
            }
        ],
        model="llama-3.1-8b-instant",
    )
    return chat_completion.choices[0].message.content

# import os
# from groq import Groq
# from dotenv import load_dotenv
# load_dotenv()
# GROQ_API_KEY5 = os.getenv('GROQ_API_KEY5')

# client = Groq(
#     api_key=os.environ.get(GROQ_API_KEY5))
# def model_responce(query):
#         chat_completion = client.chat.completions.create(
#             messages=[
#                 {
#                     "role": "user",
#                     "content": f"{query}",
#                 }
#             ],
#             model="llama-3.2-11b-text-preview",
#         )
#         return chat_completion.choices[0].message.content
