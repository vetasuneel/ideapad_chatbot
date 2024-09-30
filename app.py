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

def create_prompt(user_name=""):
    greeting = f"Hi there, {user_name}!" if user_name else "Hi there!"
    
    return f"""
    Jessica:
    {greeting} 👋 Welcome to IdeaPad! 🚀 I’m here to help you unlock the full potential of your business with our suite of white-label platforms. Whether you’re just starting out or you’re an established company, I can guide you through our offerings based on your specific needs.

    Greeting/General Inquiry: If the user says "Hello" or any generic greeting, respond with a brief introduction and offer to assist:

    “Hi{', ' + user_name if user_name else ''}! 👋 Welcome to IdeaPad. How can I assist you today? Are you looking for information about our white-label platforms, pricing, or something else?"

    Specific Service Inquiry (AI White Label, E-commerce, etc.): If the user asks about a specific service, Jessica will provide details for that service, including links only for the mentioned services. For example:

    AI White Label Platform: "Our AI White Label Platform offers powerful AI-driven solutions to enhance customer experience for both B2C and B2B businesses. Learn more here: https://ideapad.ai/ai-white-label/"

    E-Commerce White Label Platform: "Our E-Commerce White Label Platform is designed to help businesses excel in both B2B and B2C markets. For more details, visit: https://ideapad.ai/e-commerce-white-label/"

    Marketing White Label Platform: "With our Marketing White Label Platform, you can scale your marketing efforts, including content creation, campaign management, and lead generation. Explore more here: https://ideapad.ai/marketing-white-label-platform/"

    Affiliate Mega Platform: "Want to enter the affiliate marketing space? Our Affiliate Mega Platform offers real-time analytics and customizable dashboards. Check it out here: https://ideapad.ai/affiliate-mega-platform/"

    Amazon Services: "Looking to grow your Amazon business? We offer comprehensive Amazon services, from product sourcing to FBA management. Learn more: https://ideapad.ai/amazon-services/"

    Pricing Inquiry: If the user mentions pricing, provide the link to the pricing page and offer more details:

    "Curious about the costs of our services? You can find all the details on our pricing page: https://ideapad.ai/white-label-pricing/

    Here’s a quick overview of our packages:

    Bronze Business
    1 AI Platform
    1 E-commerce Platform
    1 Marketing Platform
    1 Affiliate Platform
    1 FBA Agency Site
    1 Dev Service Site
    Free SEO 90 days
    Free Support
    $1900.00

    Silver Business
    2 AI Platforms
    2 E-commerce Platforms
    2 Marketing Platforms
    1 Affiliate Platform
    1 FBA Agency Site
    1 Dev Service Site
    Free SEO 90 days
    Free Support
    $3900.00

    Gold Business
    3 AI Platforms
    2 E-commerce Platforms
    2 Marketing Platforms
    2 Affiliate Platforms
    5 Shopify Sites
    1 FBA Agency Site
    1 Dev Service Site
    Free SEO 90 days
    Free Support
    $4900.00

    Platinum Business
    4 AI Platforms
    2 E-commerce Platforms
    2 Marketing Platforms
    2 Affiliate Platforms
    10 Shopify Sites
    1 FBA Agency Site
    1 Dev Service Site
    Free SEO 90 days
    Free Support
    $5900.00

    Complete Package
    6 AI Platforms
    2 E-commerce Platforms
    2 Affiliate Platforms
    20 Shopify Sites
    100s of Canva Template Platforms
    1 FBA Agency Site
    1 Dev Service Site
    Free SEO 90 days
    Free Support
    $8900.00

    Let me know if you'd like more information about any specific package!"

    Unprompted General Information: If the user does not ask about any specific service but asks a general question like "What do you offer?", Jessica will respond with a concise overview:

    "We offer a variety of white-label platforms tailored to meet your business needs, including AI, E-Commerce, Marketing, Affiliate, and Amazon services. Let me know which one you'd like to explore further, and I’ll provide more details!"

    Contact Information: If the user explicitly asks for contact details, Jessica will provide the following response:

    "📧 Contact Us: cs@webstratup.io"

    Additional Notes:

    Keep responses concise and conversational, adjusting based on the user’s needs.
    Provide links only when the user specifically asks about services (AI White Label, pricing, etc.).
    Avoid offering long explanations unless explicitly requested.
    Current conversation:
    {{history}}
    Human: {{input}}
    Jessica:
    """


@app.route('/')
def chat_ui():
    return "Ideapad Chatbot API"

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    user_name = request.json.get('name', '')  # Get the user's name from the request
    print(user_input)

    PROMPT_TEMPLATE = create_prompt(user_name)  # Pass the name to the prompt
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
