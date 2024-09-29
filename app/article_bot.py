import os
import logging
from groq import Groq
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnableSequence, RunnableLambda


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

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
            model="llava-v1.5-7b-4096-preview",
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
