from flask import Flask, render_template
from flask import request, jsonify, abort
from langchain.prompts import PromptTemplate

from langchain.chains import LLMChain

from langchain.llms import Cohere

from langchain.chains import RetrievalQA
from langchain.embeddings import CohereEmbeddings
from langchain.vectorstores import Chroma

import os
from dotenv import load_dotenv

from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)



load_dotenv()

api_key = os.getenv("COHERE_API_KEY")

def load_db():
    try:
        embeddings = CohereEmbeddings(cohere_api_key=os.environ["COHERE_API_KEY"])
        vectordb = Chroma(persist_directory='db', embedding_function=embeddings)
        qa = RetrievalQA.from_chain_type(
            llm=Cohere(),
            chain_type="refine",
            retriever=vectordb.as_retriever(),
            return_source_documents=True
        )
        return qa
    except Exception as e:
        print("Error:", e)

qa = load_db()

app = Flask(__name__)

def answer_from_knowledgebase(message):
    res = qa({"query": message})
    return res['result']

def search_knowledgebase(message):
    res = qa({"query": message})
    sources = ""
    for count, source in enumerate(res['source_documents'],1):
        sources += "Source " + str(count) + "\n"
        sources += source.page_content + "\n"
    return sources

def answer_as_chatbot(message):
    # Define the template
    template = """Question: {question}
    Answer as if you are a chatbot helping a human user."""
    
    # Ensure the template matches input_variables
    prompt = PromptTemplate(template=template, input_variables=["question"])
    
    # Instantiate the LLM (Ensure the API key is correctly configured)
    llm = Cohere(cohere_api_key=os.getenv("COHERE_API_KEY"))
    
    # Create the LLMChain
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    
    # Run the chain with the correct variable name
    response = llm_chain.run({"question": message})  # Map 'message' to 'question'
    return response

@app.route('/kbanswer', methods=['POST'])
def kbanswer():
    message = request.json['message']
    
    # Generate a response
    response_message = answer_from_knowledgebase(message)
    
    # Return the response as JSON
    return jsonify({'message': response_message}), 200
    return 

@app.route('/search', methods=['POST'])
def search():    
    message = request.json['message']
    
    # Generate a response
    response_message = search_knowledgebase(message)
    
    # Return the response as JSON
    return jsonify({'message': response_message}), 200

@app.route('/answer', methods=['POST'])
def answer():
    message = request.json['message']
    
    # Generate a response
    response_message = answer_as_chatbot(message)
    
    # Return the response as JSON
    return jsonify({'message': response_message}), 200

@app.route("/")
def index():
    return render_template("index.html", title="")

if __name__ == "__main__":
    app.run()