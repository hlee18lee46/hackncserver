from flask import Flask, request, jsonify, render_template
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import base64
import requests
import json
import re
import pymongo
import plaid
from bson import ObjectId
from flask_cors import CORS
import io
from PIL import Image

app = Flask(__name__)
CORS(app)






# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Function to create a MongoDB client
def get_mongo_client():
    uri = os.getenv("MONGO_URI")  # Ensure MONGO_URI is correctly set in your environment
    return pymongo.MongoClient(uri)

# Get MongoDB URI and API key from environment variables
uri = os.getenv("MONGO_URI")
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['hackncCluster']  # MongoDB database name
#collection = db['dog_breeds']  # MongoDB collection name
#search_stats_collection = db['search_stats']  # New collection for breed search counts
user_collection = db['users']

api_key = os.getenv("OPENAI_API_KEY")

def get_ngrok_url():
    response = requests.get("http://127.0.0.1:4040/api/tunnels")
    data = response.json()
    public_url = data['tunnels'][0]['public_url']
    return public_url

NGROK_URL = get_ngrok_url()
#NGROK_URL = "https://2e03-152-23-102-253.ngrok-free.app"

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENVIRONMENT = os.getenv("PLAID_ENVIRONMENT", "sandbox")

client = plaid.Client(client_id=os.getenv('PLAID_CLIENT_ID'), 
                      secret=os.getenv('PLAID_SECRET'), 
                      environment='sandbox')

@app.route('/exchange_public_token', methods=['POST'])
def exchange_public_token():
    public_token = request.json.get('public_token')
    if not public_token:
        return jsonify({"error": "public_token is missing"}), 400

    url = "https://sandbox.plaid.com/item/public_token/exchange"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "client_id": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
        "public_token": public_token
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": "Failed to exchange public token"}), 400

    data = response.json()
    access_token = data['access_token']
    return jsonify({"access_token": access_token})

@app.route('/get_accounts', methods=['POST'])
def get_accounts():
    # Retrieve the access token from the request body
    access_token = request.json.get("access_token")

    if not access_token:
        return jsonify({"error": "Access token is required"}), 400

    # Make a request to Plaid's /accounts/get endpoint
    url = "https://sandbox.plaid.com/accounts/get"  # or use https://production.plaid.com/accounts/get for production
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        "client_id": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
        "access_token": access_token
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        accounts_data = response.json().get("accounts", [])
        return jsonify({"accounts": accounts_data})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_balances', methods=['POST'])
def get_balances():
    access_token = request.json.get('access_token')
    if not access_token:
        return jsonify({"error": "access_token is missing"}), 400

    url = "https://sandbox.plaid.com/accounts/balance/get"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "client_id": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
        "access_token": access_token
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": "Failed to retrieve balances"}), 400

    data = response.json()
    return jsonify(data)


@app.route('/get_credit_card_transactions', methods=['POST'])
def get_credit_card_transactions():
    access_token = request.json.get('access_token')
    start_date = '2022-01-01'  # Replace with your preferred start date
    end_date = '2022-12-31'    # Replace with your preferred end date
    try:
        response = client.Transactions.get(access_token, start_date, end_date)
        return jsonify(response)
    except plaid.errors.PlaidError as e:
        return jsonify({"error": str(e)}), 400


@app.route('/create_link_token', methods=['GET'])
def create_link_token():
    url = "https://sandbox.plaid.com/link/token/create"
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        "client_id": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
        "client_name": "1Finance.ai",
        "country_codes": ["US"],
        "language": "en",
        "user": {
            "client_user_id": "unique-user-id"
        },
        "products": ["auth"],
        "redirect_uri": f"{NGROK_URL}/plaid-redirect"
    }
    print("Ngrok URL:", NGROK_URL)

    response = requests.post(url, json=payload, headers=headers)
    link_token = response.json().get("link_token")
    return jsonify({"link_token": link_token})

# Helper function to serialize MongoDB ObjectId
def serialize_mongo_object(data):
    if "_id" in data:
        data["_id"] = str(data["_id"])
    return data

#view user
@app.route('/view_user', methods=['GET'])
def view_user():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username is required"}), 400

    # Fetch user info from MongoDB
    user = user_collection.find_one({"username": username}, {"_id": 0, "password": 0})
    if user:
        return jsonify(user), 200
    else:
        return jsonify({"error": "User not found"}), 404


# Check MongoDB connection
@app.route('/ping_db', methods=['GET'])
def ping_db():
    try:
        client.admin.command('ping')
        return jsonify({"message": "Pinged your deployment. Successfully connected to MongoDB!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users', methods=['GET'])
def get_all_users():
    users = user_collection.find({}, {"password": 0})  # Exclude the password field
    user_list = [{"username": user["username"]} for user in users]
    return jsonify(user_list), 200

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    # Check if the username already exists
    if user_collection.find_one({"username": username}):
        return jsonify({"error": "Username already exists"}), 409

    # Hash the password and store it
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    user_collection.insert_one({
        "username": username,
        "password": hashed_password
    })

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    # Retrieve user data from the database
    user = user_collection.find_one({"username": username})

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    # Authentication successful, return success message or token if needed
    return jsonify({"message": "Login successful"}), 200


# Route to display the upload form
@app.route("/upload", methods=["GET"])
def upload_form():
    return render_template("upload.html")

# Process the uploaded image and analyze it
@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file:
        # Encode the image in base64
        base64_image = base64.b64encode(file.read()).decode("utf-8")

        # Define the prompt
        prompt = (
            "Can you provide a JSON object with details such as height (as the field name \"height\"), weight (as the field name \"weight\"), "
            "lifespan (as the field name \"lifespan\"), breed (as the field name \"breed\"), breed group (only group name, not including \"Group\", as the field name \"breed_group\"), shed level (as the field name \"shed_level\"), temperament (in a list, as the field name \"temperament\"), energy level (as the field name \"energy_level\"), and "
            "common health concerns (in the list, as the field name \"common_health_concerns\") about the dog in the image? Format the response in JSON."
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        # Build the payload for the API call
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            "max_tokens": 900
        }

        # Make the request to OpenAI API
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )
        response_data = response.json()

        # Print response data for debugging
        print("Response Data:", response_data)

        if response_data and "choices" in response_data and len(response_data["choices"]) > 0:
            content_text = response_data["choices"][0]["message"]["content"]
            
            # Use regular expressions to check for JSON structure inside content_text
            json_match = re.search(r'\{.*\}', content_text, re.DOTALL)
            
            if json_match:
                dog_info_json = json_match.group(0)

                try:
                    # Parse the JSON string into a Python dictionary
                    dog_data = json.loads(dog_info_json)
                    
                    # Display the full JSON data to the user
                    display_data = dog_data

                    # Extract breed and breed_group for search stats
                    breed = dog_data.get("breed")
                    breed_group = dog_data.get("breed_group")

                    # Update or insert search count in `breed_stats` 
                    if breed and breed_group:
                        db.breed_stats.update_one(
                            {"breed": breed, "breed_group": breed_group},
                            {"$inc": {"count": 1}},  # Increment count by 1 if it exists
                            upsert=True  # Insert a new document if it doesn't exist
                        )

                    # Return the full JSON to the user
                    return jsonify(display_data), 200
                except Exception as e:
                    print("Error parsing JSON:", e)
                    return jsonify({"error": "Error parsing JSON response"}), 500
            else:
                # No JSON detected; return a friendly message
                return jsonify({
                    "error": "No dog detected in the image. Please upload an image with a clear view of a dog."
                }), 200

    return jsonify({"error": "Unknown error"}), 500

@app.route("/upload_and_analyze", methods=["POST"])
def upload_and_analyze_image():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file:
        try:
            # Load the image in memory for processing
            image = Image.open(io.BytesIO(file.read()))

            # Convert the image to base64 for sending to any image analysis API if needed
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # Define your prompt or payload for the API
            prompt = (
                "Can you provide a JSON object with details such as height (as height), weight (as weight), "
                "lifespan (as lifespan), breed (as breed), breed group (as breed_group), shed level (as shed_level), "
                "temperament (in a list, as temperament), energy level (as energy_level), "
                "and common health concerns (in the list, as common_health_concerns) about the dog in the image?"
            )

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }

            # Make the request to the analysis API
            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }
                ],
                "max_tokens": 900
            }
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            response_data = response.json()

            # Extracting the JSON response for SwiftUI
            if response_data and "choices" in response_data and len(response_data["choices"]) > 0:
                content_text = response_data["choices"][0]["message"]["content"]
                
                # Use regular expressions to check for JSON structure inside content_text
                json_match = re.search(r'\{.*\}', content_text, re.DOTALL)
                
                if json_match:
                    dog_info_json = json_match.group(0)
                    dog_data = json.loads(dog_info_json)  # Parse into a Python dictionary
                    return jsonify(dog_data), 200  # Send JSON back to Swift

            return jsonify({"error": "Failed to analyze image content"}), 500

        except Exception as e:
            print("Error processing image:", e)
            return jsonify({"error": "Failed to process image"}), 500

    return jsonify({"error": "Unknown error"}), 500
@app.route("/upload_multipart", methods=["POST"])
def upload_multipart():
    # Ensure a file was provided
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    # Retrieve the file
    file = request.files["file"]
    
    # Optionally, you can save or process this file
    file.save("uploaded_image.jpg")  # Save temporarily to disk for processing
    
    # For demonstration, return a success message
    return jsonify({"message": "File received successfully"}), 200

@app.route('/convert_to_base64', methods=['GET', 'POST'])
def convert_to_base64():
    if request.method == 'POST':
        if 'image' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Convert the uploaded image to a base64 string
        base64_image = base64.b64encode(file.read()).decode('utf-8')
        print("Base64 Encoded Image:", base64_image)  # Debugging: Print to console

        # Return the base64-encoded string as JSON
        return jsonify({"base64_string": base64_image}), 200

    # Render the HTML form on GET request
    return render_template('upload_image.html')



@app.route('/')
def home():
    return "Welcome to 1Finance.ai Back-end Server"

# app.py
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
