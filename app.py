from flask import Flask, render_template, request, jsonify
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import Cohere
from langchain.chains import RetrievalQA
from langchain.embeddings import CohereEmbeddings
from langchain.vectorstores import Chroma
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load the Cohere API key
api_key = os.getenv("COHERE_API_KEY")
if not api_key:
    raise EnvironmentError("COHERE_API_KEY is missing. Ensure it is set in the environment variables.")

# Load the db
def load_db():
    try:
        embeddings = CohereEmbeddings(cohere_api_key=api_key)
        vectordb = Chroma(persist_directory='db', embedding_function=embeddings)
        qa = RetrievalQA.from_chain_type(
            llm=Cohere(),
            chain_type="refine",
            retriever=vectordb.as_retriever(),
            return_source_documents=True
        )
        return qa
    except Exception as e:
        print(f"Error loading the database: {e}")
        return None

qa = load_db()
# If db doesnt exist
if qa is None:
    raise RuntimeError("Failed to initialize the QA system.")

def answer_from_knowledgebase(message):
    # Handle error if no data was entered
    try:
        if not message or not isinstance(message, str):
            raise ValueError("Invalid input. Please provide a non-empty string.")
        
        res = qa({"query": message})
        return res.get('result', "No answer found.")
    except Exception as e:
        print(f"Error answering from knowledge base: {e}")
        return "An error occurred while retrieving the answer."

def search_knowledgebase(message):
    try:
        if not message or not isinstance(message, str):
            raise ValueError("Invalid input. Please provide a non-empty string.")

        res = qa({"query": message})
        sources = ""
        for count, source in enumerate(res.get('source_documents', []), 1):
            sources += f"Source {count}\n{source.page_content}\n"
        return sources if sources else "No sources found."
    except Exception as e:
        print(f"Error searching the knowledge base: {e}")
        return "An error occurred while searching the knowledge base."

def answer_as_chatbot(message):
    # Handle error if no data was entered
    try:
        if not message or not isinstance(message, str):
            raise ValueError("Invalid input. Please provide a non-empty string.")

        template = """Question: {question}
        Answer as if you are a chatbot helping a human user."""
        prompt = PromptTemplate(template=template, input_variables=["question"])
        llm = Cohere(cohere_api_key=api_key)
        llm_chain = LLMChain(prompt=prompt, llm=llm)
        return llm_chain.run({"question": message})
    except Exception as e:
        print(f"Error answering as chatbot: {e}")
        return "An error occurred while generating the chatbot response."

@app.route('/kbanswer', methods=['POST'])
def kbanswer():
    try:
        message = request.json.get('message')
        if not message:
            return jsonify({'error': 'Message is required.'}), 400
        
        response_message = answer_from_knowledgebase(message)
        return jsonify({'message': response_message}), 200
    except Exception as e:
        print(f"Error in /kbanswer endpoint: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500

@app.route('/search', methods=['POST'])
def search():    
    try:
        message = request.json.get('message')
        if not message:
            return jsonify({'error': 'Message is required.'}), 400
        
        response_message = search_knowledgebase(message)
        return jsonify({'message': response_message}), 200
    except Exception as e:
        print(f"Error in /search endpoint: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500

@app.route('/answer', methods=['POST'])
def answer():
    try:
        message = request.json.get('message')
        if not message:
            return jsonify({'error': 'Message is required.'}), 400
        
        response_message = answer_as_chatbot(message)
        return jsonify({'message': response_message}), 200
    except Exception as e:
        print(f"Error in /answer endpoint: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500

@app.route("/")
def index():
    return render_template("index.html", title="")

if __name__ == "__main__":
    app.run()
