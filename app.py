from flask import Flask, render_template
from flask import request, jsonify, abort
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

from langchain.llms import Cohere

import os
from dotenv import load_dotenv

from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)



load_dotenv()

api_key = os.getenv("COHERE_API_KEY")

app = Flask(__name__)

def answer_from_knowledgebase(message):
    # TODO: Write your code here
    return ""

def search_knowledgebase(message):
    # TODO: Write your code here
    sources = ""
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
    # TODO: Write your code here
    
    # call answer_from_knowledebase(message)
        
    # Return the response as JSON
    return 

@app.route('/search', methods=['POST'])
def search():    
    # Search the knowledgebase and generate a response
    # (call search_knowledgebase())
    
    # Return the response as JSON
    return

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