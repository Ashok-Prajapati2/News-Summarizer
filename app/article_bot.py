import os
import random
import logging
from groq import Groq
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnableSequence, RunnableLambda


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


load_dotenv()
API_KEYS = [
    os.getenv('GROQ_API_KEY'),
    os.getenv('GROQ_API_KEY1'),
    os.getenv('GROQ_API_KEY2'),
    os.getenv('GROQ_API_KEY2'),
    os.getenv('GROQ_API_KEY3'),
    os.getenv('GROQ_API_KEY4'),
    os.getenv('GROQ_API_KEY5'),
    
    
]
GROQ_API_KEY = random.choice(API_KEYS)
# GROQ_API_KEY = os.getenv('GROQ_API_KEY')

client = Groq(api_key=GROQ_API_KEY)

def groq_response(query):
    try:
        logger.info("Sending query to Groq: %s", query)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": str(query),  
                }
            ],
            model="llama-3.1-70b-versatile",
        )
        logger.info("Received response from Groq.")
        return chat_completion.choices[0].message.content
    except Exception as e:
        logger.error("Error in groq_response: %s", str(e))
        raise

class ArticleChatbot:
    def __init__(self, article_content):
        self.article_content = article_content
        self.memory = ConversationBufferMemory()
        logger.info("ArticleChatbot initialized with article content.")

    def ask_question(self, question):
        logger.info("User asked a question: %s", question)

        prompt_template = PromptTemplate(
            input_variables=["article", "question"],
            template="The following is the article content:\n\n{article}\n\nAnswer the question: {question}",
        )

        llm = RunnableLambda(groq_response)

        chain = RunnableSequence(
            prompt_template | llm
        )

        try:
            response = chain.invoke({
                "article": self.article_content,
                "question": question
            })
            logger.info("Generated response for the question.")
            return response
        except Exception as e:
            logger.error("Error in ask_question: %s", str(e))
            raise
