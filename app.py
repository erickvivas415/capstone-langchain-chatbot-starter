# Import necessary modules
from flask import Flask, render_template, request, jsonify
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import Cohere
from langchain.chains import RetrievalQA
from langchain.embeddings import CohereEmbeddings
from langchain.vectorstores import Chroma
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Fetch the Cohere API key from the environment variables
api_key = os.getenv("COHERE_API_KEY")
if not api_key:
    # Raise an error if the API key is not set
    raise EnvironmentError("COHERE_API_KEY is missing. Ensure it is set in the environment variables.")

# Function to load the database and initialize the QA system
def load_db():
    try:
        # Initialize Cohere embeddings for vectorizing documents
        embeddings = CohereEmbeddings(cohere_api_key=api_key)
        # Load the vector database from the specified directory
vectordb = Chroma(persist_directory='db', embedding_function=embeddings)

# Set up a RetrievalQA system using Cohere LLM and the vector database retriever
qa = RetrievalQA.from_chain_type(
    llm=Cohere(),  # Use Cohere's LLM for processing
    chain_type="refine",  # Specify the chain type for refining answers
    retriever=vectordb.as_retriever(),  # Use the vector database as the retriever
    return_source_documents=True  # Include source documents in responses
)
return qa  # Return the initialized QA system
except Exception as e:
    # Log and return None if there's an error
    print(f"Error loading the database: {e}")
    return None

# Initialize the QA system
qa = load_db()
if qa is None:
    # Stop the application if the QA system failed to initialize
    raise RuntimeError("Failed to initialize the QA system.")

# Function to query the knowledge base for an answer
def answer_from_knowledgebase(message):
    try:
        # Validate input
        if not message or not isinstance(message, str):
            raise ValueError("Invalid input. Please provide a non-empty string.")
        
        # Query the QA system
        res = qa({"query": message})
        return res.get('result', "No answer found.")  # Return the answer or a fallback message
    except Exception as e:
        # Log the error and return a fallback message
        print(f"Error answering from knowledge base: {e}")
        return "An error occurred while retrieving the answer."

# Function to search the knowledge base and retrieve source documents
def search_knowledgebase(message):
    try:
        # Validate input
        if not message or not isinstance(message, str):
            raise ValueError("Invalid input. Please provide a non-empty string.")

        # Query the QA system
        res = qa({"query": message})
        sources = ""  # Initialize an empty string for sources
        for count, source in enumerate(res.get('source_documents', []), 1):
            # Append each source document with its index
            sources += f"Source {count}\n{source.page_content}\n"
        return sources if sources else "No sources found."  # Return the sources or a fallback message
    except Exception as e:
        # Log the error and return a fallback message
        print(f"Error searching the knowledge base: {e}")
        return "An error occurred while searching the knowledge base."

# Function to respond as a chatbot
def answer_as_chatbot(message):
    try:
        # Validate input
        if not message or not isinstance(message, str):
            raise ValueError("Invalid input. Please provide a non-empty string.")

        # Define a prompt template for the chatbot
        template = """Question: {question}
        Answer as if you are a chatbot helping a human user."""
        prompt = PromptTemplate(template=template, input_variables=["question"])
        
        # Initialize the Cohere LLM and set up a chain with the prompt
        llm = Cohere(cohere_api_key=api_key)
        llm_chain = LLMChain(prompt=prompt, llm=llm)
        
        # Generate a response using the chain
        return llm_chain.run({"question": message})
    except Exception as e:
        # Log the error and return a fallback message
        print(f"Error answering as chatbot: {e}")
        return "An error occurred while generating the chatbot response."

# Flask route for knowledge base queries
@app.route('/kbanswer', methods=['POST'])
def kbanswer():
    try:
        # Extract the user's message from the request payload
        message = request.json.get('message')
        if not message:
            return jsonify({'error': 'Message is required.'}), 400  # Bad Request

        # Generate a response from the knowledge base
        response_message = answer_from_knowledgebase(message)
        return jsonify({'message': response_message}), 200  # OK
    except Exception as e:
        # Log the error and return an internal server error
        print(f"Error in /kbanswer endpoint: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500

# Flask route for searching the knowledge base
@app.route('/search', methods=['POST'])
def search():
    try:
        # Extract the user's message from the request payload
        message = request.json.get('message')
        if not message:
            return jsonify({'error': 'Message is required.'}), 400  # Bad Request

        # Search the knowledge base for relevant documents
        response_message = search_knowledgebase(message)
        return jsonify({'message': response_message}), 200  # OK
    except Exception as e:
        # Log the error and return an internal server error
        print(f"Error in /search endpoint: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500

# Flask route for chatbot-style answers
@app.route('/answer', methods=['POST'])
def answer():
    try:
        # Extract the user's message from the request payload
        message = request.json.get('message')
        if not message:
            return jsonify({'error': 'Message is required.'}), 400  # Bad Request

        # Generate a chatbot-style response
        response_message = answer_as_chatbot(message)
        return jsonify({'message': response_message}), 200  # OK
    except Exception as e:
        # Log the error and return an internal server error
        print(f"Error in /answer endpoint: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500

# Flask route for the home page
@app.route("/")
def index():
    # Render an HTML template for the index page
    return render_template("index.html", title="")

# Run the Flask application if the script is executed directly
if __name__ == "__main__":
    app.run()
