import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# MongoDB connection setup
MONGO_URI = os.getenv("MONGO_URI")  # Make sure MONGO_URI is set in your .env file
client = MongoClient(MONGO_URI)
db = client['hackncCluster']  # Replace with your database name
financial_collection = db['financial']

# Define hardcoded account data
accounts_data = [
    {
        "account_id": "pQNARmLB4NuPja4Km9aJiwQQDaWjNpuplWW6Z",
        "name": "Plaid Checking",
        "type": "depository",
        "subtype": "checking",
        "balances": {
            "available": 100,
            "current": 110,
            "iso_currency_code": "USD"
        },
        "mask": "0000",
        "official_name": "Plaid Gold Standard 0% Interest Checking"
    },
    {
        "account_id": "oe4ymoXza4iReW4q7JW5iQ44wxEKnXIoQzzB3",
        "name": "Plaid Saving",
        "type": "depository",
        "subtype": "savings",
        "balances": {
            "available": 200,
            "current": 210,
            "iso_currency_code": "USD"
        },
        "mask": "1111",
        "official_name": "Plaid Silver Standard 0.1% Interest Saving"
    },
    {
        "account_id": "gxK7a6AgqKcRZJd561JqiXllg7pwkAiENwwZm",
        "name": "Plaid CD",
        "type": "depository",
        "subtype": "cd",
        "balances": {
            "available": None,
            "current": 1000,
            "iso_currency_code": "USD"
        },
        "mask": "2222",
        "official_name": "Plaid Bronze Standard 0.2% Interest CD"
    },
    {
        "account_id": "8beZjPwrXeCWqzMK5QzVHoRR4VBaDrfW7GGQA",
        "name": "Plaid Credit Card",
        "type": "credit",
        "subtype": "credit card",
        "balances": {
            "available": None,
            "current": 410,
            "iso_currency_code": "USD",
            "limit": 2000
        },
        "mask": "3333",
        "official_name": "Plaid Diamond 12.5% APR Interest Credit Card"
    },
    {
        "account_id": "EdG3BWNQXGCq9rLDMZrgIzKK8ANXdJt4811Ay",
        "name": "Plaid Money Market",
        "type": "depository",
        "subtype": "money market",
        "balances": {
            "available": 43200,
            "current": 43200,
            "iso_currency_code": "USD"
        },
        "mask": "4444",
        "official_name": "Plaid Platinum Standard 1.85% Interest Money Market"
    },
    {
        "account_id": "WWvkyA8xnvf1NwbomewzhqppkjZRaEs63DDNb",
        "name": "Plaid IRA",
        "type": "investment",
        "subtype": "ira",
        "balances": {
            "available": None,
            "current": 320.76,
            "iso_currency_code": "USD"
        },
        "mask": "5555",
        "official_name": None
    },
    {
        "account_id": "Az8KkWQPX8uz9jmNMgjwFp11vPmMzBi9LddVj",
        "name": "Plaid 401k",
        "type": "investment",
        "subtype": "401k",
        "balances": {
            "available": None,
            "current": 23631.9805,
            "iso_currency_code": "USD"
        },
        "mask": "6666",
        "official_name": None
    },
    {
        "account_id": "G4vdx63MXvfrq38Lpk36upNNb6d9jgi6KQQN9",
        "name": "Plaid Student Loan",
        "type": "loan",
        "subtype": "student",
        "balances": {
            "available": None,
            "current": 65262,
            "iso_currency_code": "USD"
        },
        "mask": "7777",
        "official_name": None
    },
    {
        "account_id": "n7aAQ9prdaT5ZwQl7Bw1HnaaxvwVNmtA9nn7R",
        "name": "Plaid Mortgage",
        "type": "loan",
        "subtype": "mortgage",
        "balances": {
            "available": None,
            "current": 56302.06,
            "iso_currency_code": "USD"
        },
        "mask": "8888",
        "official_name": None
    },
    {
        "account_id": "bKvyzo3MnvH5pDrKJMDoHwqqr6pEAnumndd9e",
        "name": "Plaid HSA",
        "type": "depository",
        "subtype": "hsa",
        "balances": {
            "available": 6009,
            "current": 6009,
            "iso_currency_code": "USD"
        },
        "mask": "9001",
        "official_name": "Plaid Cares Health Savings Account"
    },
    {
        "account_id": "mjdAXwLKxdCr8g4Rw5gLuPddvRepn9ugeWWKl",
        "name": "Plaid Cash Management",
        "type": "depository",
        "subtype": "cash management",
        "balances": {
            "available": 12060,
            "current": 12060,
            "iso_currency_code": "USD"
        },
        "mask": "9002",
        "official_name": "Plaid Growth Cash Management"
    },
    {
        "account_id": "yELrWR371Lc8doDNAZo6ILyyDa1NAlt4Pll11",
        "name": "Plaid Business Credit Card",
        "type": "credit",
        "subtype": "credit card",
        "balances": {
            "available": 4980,
            "current": 5020,
            "iso_currency_code": "USD",
            "limit": 10000
        },
        "mask": "9999",
        "official_name": "Plaid Platinum Small Business Credit Card"
    }
]


# Insert data into MongoDB
try:
    result = financial_collection.insert_many(accounts_data)
    print(f"Successfully inserted {len(result.inserted_ids)} documents into the 'financial' collection.")
except Exception as e:
    print(f"Error inserting data: {e}")
