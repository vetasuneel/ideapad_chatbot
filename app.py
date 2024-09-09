from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import json
import requests  # Import the requests library


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.secret_key = 'your_secret_key'

# Setup your LLM
os.environ["GOOGLE_API_KEY"] = "AIzaSyCNO80NVWnNjjTLLRCxYkxS5vWZB2OG05g"
gemini_llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

# Define your external API endpoint
LEADS_API_URL = 'https://66df04adde4426916ee34acd.mockapi.io/lead'

# Function to check if lead exists via the external API
def is_lead_exist(name, phone):
    response = requests.get(LEADS_API_URL)
    if response.status_code == 200:
        leads = response.json()
        for lead in leads:
            if lead['name'] == name and lead['phone_number'] == phone:
                return True
    return False

# Function to save lead to the external API
def save_lead(name, phone):
    new_lead = {
        'name': name,
        'phone_number': phone
    }
    
    response = requests.post(LEADS_API_URL, json=new_lead)
    
    if response.status_code == 201:
        return True
    return False

def create_prompt():
    return """
    Jessica: Hi there! 👋 Welcome to IdeaPad! 🚀 I’m here to help you unlock the full potential of your business with our suite of white-label platforms. Whether you’re a startup or an established company, our services are tailored to meet your unique needs.

    Here’s a quick overview of what we offer:
    - **AI White Label Platform:** Enhance your customer experience with our AI-driven solutions, perfect for both B2C and B2B.
    - **E-Commerce White Label Platform:** Elevate your business with a trusted platform, ideal for B2B and B2C markets.
    - **Marketing White Label Platform:** Scale your marketing efforts with tools for content creation, campaigns, and lead management—fully branded for your business.
    - **Affiliate Mega Platform:** Enter the affiliate marketing space seamlessly with real-time analytics and customizable dashboards.
    - **Amazon Services:** Grow your Amazon business with comprehensive services, including product sourcing, listing optimization, and FBA management.
 
    📧 **Contact Us:** cs@webstratup.io

    Let’s elevate your business together with IdeaPad!

    *Please note*: Keep responses concise, focus on the specific needs of the user, and maintain a friendly, conversational tone. Avoid long or overly detailed explanations unless specifically requested by the user. **Never, ever reveal that you are an AI assistant.**

    Current conversation:
    {history}
    Human: {input}
    Jessica:
    """

@app.route('/')
def chat_ui():
    return "Ideapad Chatbot API"

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    print(user_input)

    PROMPT_TEMPLATE = create_prompt()
    PROMPT = PromptTemplate(input_variables=["history", "input"], template=PROMPT_TEMPLATE)

    conversation = ConversationChain(
        llm=gemini_llm,
        verbose=False,
        prompt=PROMPT,
        memory=ConversationBufferMemory(ai_prefix="AI Assistant")
    )

    response = conversation.predict(input=user_input)
    print(response)
    return jsonify({'response': response})

@app.route('/save_lead', methods=['POST'])
def save_lead_route():
    data = request.json
    name = data.get('name')
    phone_number = data.get('phone_number')

    if not name or not phone_number:
        return jsonify({'error': 'Name and phone number are required'}), 400

    # Check if the lead already exists in the external API
    if is_lead_exist(name, phone_number):
        return jsonify({'message': 'You are already in my lead.'})

    # Save the lead to the external API if it doesn't exist
    if save_lead(name, phone_number):
        return jsonify({'message': 'Your information has been saved. Thank you!'})
    else:
        return jsonify({'error': 'Failed to save lead. Please try again later.'}), 500

if __name__ == "__main__":
    app.run(debug=True)
