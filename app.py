from flask import Flask, request, jsonify, render_template
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import base64
import requests
from bson import json_util
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from datetime import datetime
import json
import re
import pymongo
import plaid
from bson import ObjectId
from flask_cors import CORS
import io
from PIL import Image
from flask_cors import CORS
import plaid.model
from plaid import ApiClient, Configuration
from plaid.api.plaid_api import PlaidApi
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
import time
from plaid.model.account_base import AccountBase
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from datetime import datetime, timedelta
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from plaid.model.investments_transactions_get_request import InvestmentsTransactionsGetRequest
from plaid.model.investment_transaction_type import InvestmentTransactionType
from plaid.exceptions import ApiException
import joblib
import numpy as np





# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

user_access_tokens = {}




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
collection = db['quiz_questions']
scores_collection = db['user_scores']  # New collection for scores
financial_collection = db['financial']  # New collection for scores


api_key = os.getenv("OPENAI_API_KEY")
"""
@app.route('/get_financial_data', methods=['GET'])
def get_financial_data():
    try:
        # Aggregate data to count accounts by type
        pipeline = [
            {"$group": {"_id": "$type", "count": {"$sum": 1}}}
        ]
        results = list(financial_collection.aggregate(pipeline))
        
        # Transform data for frontend consumption
        data = [{"type": result["_id"], "count": result["count"]} for result in results]
        
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
"""
@app.route('/api/scores/create', methods=['POST'])
def create_score():
    try:
        # Create new score document with initial values
        new_score = {
            "right": 0,
            "wrong": 0
        }
        result = scores_collection.insert_one(new_score)
        
        # Return the created score document with string ID
        score_doc = scores_collection.find_one({"_id": result.inserted_id})
        return jsonify({
            "id": str(score_doc["_id"]),
            "right": score_doc["right"],
            "wrong": score_doc["wrong"]
        })
    except Exception as e:
        print(f"Error creating score: {str(e)}")
        return jsonify({'error': str(e)}), 500
@app.route('/get_stored_accounts', methods=['GET'])
def get_stored_accounts():
    try:
        # Fetch all account data from the 'financial' collection
        accounts = list(financial_collection.find())
        
        # Convert ObjectId to string for JSON serialization
        for account in accounts:
            account["_id"] = str(account["_id"])
        
        return jsonify(accounts), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/scores/<score_id>', methods=['GET'])
def get_score(score_id):
    try:
        score = scores_collection.find_one({"_id": ObjectId(score_id)})
        if score:
            return jsonify({
                "id": str(score["_id"]),
                "right": score["right"],
                "wrong": score["wrong"]
            })
        return jsonify({'error': 'Score not found'}), 404
    except Exception as e:
        print(f"Error getting score: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scores/<score_id>/update', methods=['POST'])
def update_score(score_id):
    try:
        data = request.get_json()
        is_correct = data.get('correct', False)
        
        # Increment the appropriate counter
        update_field = "right" if is_correct else "wrong"
        result = scores_collection.update_one(
            {"_id": ObjectId(score_id)},
            {"$inc": {update_field: 1}}
        )
        
        if result.modified_count > 0:
            # Get and return updated score
            updated_score = scores_collection.find_one({"_id": ObjectId(score_id)})
            return jsonify({
                "id": str(updated_score["_id"]),
                "right": updated_score["right"],
                "wrong": updated_score["wrong"]
            })
        return jsonify({'error': 'Score not found'}), 404
    except Exception as e:
        print(f"Error updating score: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/questions', methods=['GET'])
def get_all_questions():
    try:
        questions = list(collection.find({}, {'_id': 0}))
        return jsonify(questions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
"""
@app.route('/api/question/<int:index>', methods=['GET'])
def get_question(index):
    try:
        question = collection.find({}).skip(index).limit(1)
        question_list = list(question)
        if question_list:
            # Convert ObjectId to string for JSON serialization
            return json.loads(json_util.dumps(question_list[0]))
        return jsonify({'error': 'Question not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify/<int:index>/<selected_answer>', methods=['GET'])
def verify_answer(index, selected_answer):
    try:
        question = collection.find({}).skip(index).limit(1)
        question_list = list(question)
        if question_list:
            correct_answer = question_list[0]['answer']
            is_correct = selected_answer == correct_answer
            return jsonify({
                'correct': is_correct,
                'correct_answer': correct_answer
            })
        return jsonify({'error': 'Question not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
"""

@app.route('/api/question/<int:index>', methods=['GET'])
def get_question(index):
    try:
        questions = list(collection.find())
        print(f"Total questions found: {len(questions)}")
        
        if 0 <= index < len(questions):
            question = questions[index]
            question_dict = {
                "quiz_category": question["quiz_category"],
                "financial_literacy_quiz": question["financial_literacy_quiz"],
                "option1": question["option1"],
                "option2": question["option2"],
                "option3": question["option3"],
                "answer": question["answer"]
            }
            print(f"Sending question: {json.dumps(question_dict, indent=2)}")
            return jsonify(question_dict)
        else:
            print(f"Index {index} out of range")
            return jsonify({'error': 'Question index out of range'}), 404
            
    except Exception as e:
        print(f"Error in get_question: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify/<int:index>/<path:selected_answer>', methods=['GET'])
def verify_answer(index, selected_answer):
    try:
        questions = list(collection.find())
        print(f"Verifying answer for question {index}: {selected_answer}")
        
        if 0 <= index < len(questions):
            correct_answer = questions[index]['answer']
            is_correct = selected_answer == correct_answer
            
            # Structure the response to match the Swift model exactly
            response = {
                "correct": is_correct,
                "correctAnswer": correct_answer  # Make sure this matches the Swift model
            }
            print(f"Sending verification response: {json.dumps(response, indent=2)}")
            return jsonify(response)
        else:
            return jsonify({'error': 'Question index out of range'}), 404
            
    except Exception as e:
        print(f"Error in verify_answer: {str(e)}")
        return jsonify({'error': str(e)}), 500


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

if PLAID_ENVIRONMENT == 'sandbox':
    host = plaid.Environment.Sandbox
elif PLAID_ENVIRONMENT == 'development':
    host = plaid.Environment.Development
elif PLAID_ENVIRONMENT == 'production':
    host = plaid.Environment.Production
else:
    host = plaid.Environment.Sandbox

configuration = plaid.Configuration(
    host=host,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

# Load the loan approval model
model = joblib.load("loan_approval_model.joblib")

@app.route("/predict_loan_approval", methods=["POST"])
def predict_loan_approval():
    data = request.json
    income = data.get("income")
    loan_amount = data.get("loan_amount")
    duration = data.get("duration")

    # Make sure all values are provided
    if income is None or loan_amount is None or duration is None:
        return jsonify({"error": "Missing input values"}), 400
    
    # Format the input for the model
    input_features = np.array([[income, loan_amount, duration]])
    prediction = model.predict_proba(input_features)
    
    # Get the probability of approval (assume '1' is the approval label)
    approval_probability = prediction[0][1] * 100  # Convert to percentage

    return jsonify({"approval_probability": round(approval_probability, 2)})

@app.route('/create_link_token', methods=['GET'])
def create_link_token():
    print("Create link token route hit")
    try:
        request = LinkTokenCreateRequest(
            products=[
                Products('auth'),
                Products('transactions'),
                Products('assets'),
                Products('investments'),
                Products('liabilities'),
                Products('identity')
            ],
            client_name="Plaid Test App",
            country_codes=[CountryCode('US')],
            language='en',
            user=LinkTokenCreateRequestUser(
                client_user_id=str(time.time())
            ),

            redirect_uri=f"{NGROK_URL}/plaid-redirect" # Add your registered redirect URI here

        )
        
        print("Sending request to Plaid API:", request.to_dict())
        response = client.link_token_create(request)
        print("Link token created successfully:", response.to_dict())
        return jsonify(response.to_dict())
    except plaid.ApiException as e:
        print(f"Plaid API error: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/exchange_public_token', methods=['POST'])
def exchange_public_token():
    public_token = request.json.get("public_token")
    if not public_token:
        return jsonify({"error": "public_token is required"}), 400
    try:
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        exchange_response = client.item_public_token_exchange(exchange_request)
        access_token = exchange_response.access_token

        # Store the access token for future use (e.g., in a database or in memory)
        user_id = "unique_user_id"  # Replace with actual user ID
        user_access_tokens[user_id] = access_token

        return jsonify({"access_token": access_token, "message": "Access token saved"}), 200
    except plaid.ApiException as e:
        error_response = e.body if hasattr(e, 'body') else str(e)
        return jsonify({"error": error_response}), 500

"""
@app.route('/exchange_public_token', methods=['POST'])
def exchange_public_token():
    print("Exchange public token route hit")
    public_token = request.json.get('public_token')
    if not public_token:
        return jsonify({'error': 'public_token is required'}), 400
    try:
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        exchange_response = client.item_public_token_exchange(exchange_request)
        access_token = exchange_response.access_token

        # Store the access token associated with the user
        user_id = 'unique_user_id'  # In a real app, use the authenticated user's ID
        user_access_tokens[user_id] = access_token

        return jsonify({'access_token': access_token, 'message': 'Access token saved'})
    except plaid.ApiException as e:
        error_response = e.body if hasattr(e, 'body') else str(e)
        return jsonify({"error": error_response}), 500
"""
@app.route('/get_accounts', methods=['GET'])
def get_accounts():
    print("Get accounts route hit")
    user_id = 'unique_user_id'  # In a real app, use the authenticated user's ID
    access_token = user_access_tokens.get(user_id)
    if not access_token:
        return jsonify({'error': 'Access token not found'}), 400
    try:
        balance_request = AccountsBalanceGetRequest(access_token=access_token)
        balance_response = client.accounts_balance_get(balance_request)
        accounts = balance_response.accounts
        accounts_data = []
        for account in accounts:
            account_info = {
                'account_id': account.account_id,
                'name': account.name,
                'type': account.type.value if account.type else None,
                'subtype': account.subtype.value if account.subtype else None,
                'mask': account.mask,
                'balances': {
                    'available': float(account.balances.available) if account.balances.available is not None else None,
                    'current': float(account.balances.current) if account.balances.current is not None else None,
                    'limit': float(account.balances.limit) if account.balances.limit is not None else None,
                }
            }
            accounts_data.append(account_info)
        return jsonify({'accounts': accounts_data})
    except plaid.ApiException as e:
        error_response = e.body if hasattr(e, 'body') else str(e)
        return jsonify({"error": error_response}), 500

    
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/get_financial_data_chart', methods=['GET'])
def get_financial_data():
    try:
        # Aggregate data by type and sum the balances.current for each type
        pipeline = [
            {"$group": {"_id": "$type", "total_balance": {"$sum": "$balances.current"}}}
        ]
        results = list(financial_collection.aggregate(pipeline))
        
        # Transform data for frontend consumption
        data = [{"type": result["_id"], "balance": result["total_balance"]} for result in results]
        
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get_financial_data', methods=['GET'])
def get_financial_data():
    print("Get financial data route hit")
    user_id = 'unique_user_id'  # In a real app, use the authenticated user's ID
    access_token = user_access_tokens.get(user_id)
    if not access_token:
        return jsonify({'error': 'Access token not found'}), 400

    try:
        # Get accounts
        accounts_request = AccountsGetRequest(access_token=access_token)
        accounts_response = client.accounts_get(accounts_request)
        accounts = accounts_response['accounts']

        # Get transactions for the last 30 days
        start_date = (datetime.now() - timedelta(days=30)).date()
        end_date = datetime.now().date()
        transactions_request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options=TransactionsGetRequestOptions(count=500, offset=0)
        )
        transactions_response = client.transactions_get(transactions_request)
        transactions = transactions_response['transactions']

        # Get investments holdings
        investments_request = InvestmentsHoldingsGetRequest(access_token=access_token)
        investments_response = client.investments_holdings_get(investments_request)
        holdings = investments_response['holdings']
        securities = investments_response['securities']

        # Get investment transactions
        inv_transactions_request = InvestmentsTransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date
        )
        inv_transactions_response = client.investments_transactions_get(inv_transactions_request)
        investment_transactions = inv_transactions_response['investment_transactions']

        # Process the financial data and ensure serialization compatibility
        financial_data = {
            'accounts': [
                {
                    'account_id': account['account_id'],
                    'name': account['name'],
                    'type': str(account['type']),
                    'subtype': str(account['subtype']),
                    'balances': {
                        'available': float(account['balances']['available']) if account['balances']['available'] is not None else None,
                        'current': float(account['balances']['current']) if account['balances']['current'] is not None else None,
                        'limit': float(account['balances']['limit']) if account['balances']['limit'] is not None else None,
                    }
                } for account in accounts
            ],
            'transactions': [
                {
                    'transaction_id': transaction['transaction_id'],
                    'amount': float(transaction['amount']),
                    'date': str(transaction['date']),
                    'name': transaction['name'],
                    'category': transaction['category']
                } for transaction in transactions
            ],
            'investments': {
                'holdings': [
                    {
                        'account_id': holding['account_id'],
                        'security_id': holding['security_id'],
                        'quantity': float(holding['quantity']),
                        'institution_value': float(holding['institution_value']) if holding['institution_value'] is not None else None,
                        'cost_basis': float(holding['cost_basis']) if holding['cost_basis'] is not None else None,
                    } for holding in holdings
                ],
                'securities': [
                    {
                        'security_id': security['security_id'],
                        'name': security['name'],
                        'ticker_symbol': security.get('ticker_symbol'),
                        'type': str(security['type']),
                        'close_price': float(security['close_price']) if security['close_price'] is not None else None,
                    } for security in securities
                ],
                'transactions': [
                    {
                        'investment_transaction_id': tx['investment_transaction_id'],
                        'account_id': tx['account_id'],
                        'security_id': tx['security_id'],
                        'date': str(tx['date']),
                        'name': tx['name'],
                        'quantity': float(tx['quantity']),
                        'amount': float(tx['amount']),
                        'type': str(tx['type']),
                    } for tx in investment_transactions
                ]
            },
        }

        return jsonify(financial_data)
    except ApiException as e:
        print(f"Plaid API error: {e}")
        error_response = e.body if hasattr(e, 'body') else str(e)
        return jsonify(error_response), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
"""
@app.route('/get_accounts', methods=['POST'])
def get_accounts():
    access_token = request.json.get("access_token")
    try:
        request = AccountsGetRequest(access_token=access_token)
        response = client.accounts_get(request)
        accounts = response['accounts']
        return jsonify(accounts)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
"""
"""
# Exchange public token for access token
@app.route('/exchange_public_token', methods=['POST'])
def exchange_public_token():
    public_token = request.json.get("public_token")
    request_data = ItemPublicTokenExchangeRequest(public_token=public_token)
    try:
        response = client.item_public_token_exchange(request_data)
        access_token = response['access_token']
        return jsonify({"access_token": access_token})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
"""

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
    start_date = request.json.get('start_date', '2022-01-01')
    end_date = request.json.get('end_date', datetime.now().strftime('%Y-%m-%d'))

    try:
        # Create the Plaid request object
        request_data = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options=TransactionsGetRequestOptions(count=500, offset=0)
        )

        # Make the API call
        response = client.transactions_get(request_data)
        transactions = response.to_dict().get('transactions', [])

        # Filter for transactions with subtype 'credit card'
        credit_card_transactions = [
            txn for txn in transactions if txn.get('account_subtype') == 'credit card'
        ]

        print("Credit Card Transactions Retrieved:", credit_card_transactions)  # Debugging line

        return jsonify(credit_card_transactions)
    except plaid.errors.PlaidError as e:
        print(f"Plaid API error: {e}")  # Log the error for debugging
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

"""
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
"""
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
            "Can you provide a JSON object of object name (as \"name\"), median price (as \"price\"), about the object in the image?"
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
                    "error": "No commodity detected in the image. Please upload an image with a clear view."
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
                "Can you provide a JSON object of object name (as \"name\"), median price (as \"price\"), about the object in the image?"
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
