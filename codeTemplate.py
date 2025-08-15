from langchain_ollama import ChatOllama

llm = ChatOllama(model="deepseek-r1:latest")
result = llm.invoke("What is the capital of India?")
print(result.content)
