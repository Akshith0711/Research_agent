import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

print("KEY:", os.getenv("GROQ_API_KEY"))

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

response = llm.invoke("Hello")
print(response)