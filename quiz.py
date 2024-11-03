from pymongo import MongoClient
from datetime import datetime
import os

# The quiz data from before
quiz_data = [
    {
        "quiz_category": "Budgeting Basics",
        "financial_literacy_quiz": "What is the 50/30/20 budgeting rule?",
        "option1": "50% needs, 30% wants, 20% savings",
        "option2": "50% savings, 30% needs, 20% wants",
        "option3": "50% wants, 30% savings, 20% needs",
        "answer": "50% needs, 30% wants, 20% savings"
    },
    {
        "quiz_category": "Savings",
        "financial_literacy_quiz": "What is an emergency fund?",
        "option1": "Money set aside for vacation",
        "option2": "Money saved for unexpected expenses",
        "option3": "Money invested in stocks",
        "answer": "Money saved for unexpected expenses"
    },
    {
        "quiz_category": "Investment",
        "financial_literacy_quiz": "What is diversification in investing?",
        "option1": "Putting all money in one stock",
        "option2": "Spreading investments across different assets",
        "option3": "Only investing in bonds",
        "answer": "Spreading investments across different assets"
    },
    {
        "quiz_category": "Credit",
        "financial_literacy_quiz": "What factor has the biggest impact on your credit score?",
        "option1": "Payment history",
        "option2": "Credit utilization",
        "option3": "Length of credit history",
        "answer": "Payment history"
    },
    {
        "quiz_category": "Taxes",
        "financial_literacy_quiz": "What is a tax deduction?",
        "option1": "Money you owe in taxes",
        "option2": "Amount that reduces your taxable income",
        "option3": "Government tax refund",
        "answer": "Amount that reduces your taxable income"
    },
    {
        "quiz_category": "Retirement",
        "financial_literacy_quiz": "What is a 401(k)?",
        "option1": "A government bond",
        "option2": "An employer-sponsored retirement account",
        "option3": "A type of checking account",
        "answer": "An employer-sponsored retirement account"
    },
    {
        "quiz_category": "Banking",
        "financial_literacy_quiz": "What is compound interest?",
        "option1": "Interest earned only on principal amount",
        "option2": "Interest earned on both principal and accumulated interest",
        "option3": "Fixed interest rate for loans",
        "answer": "Interest earned on both principal and accumulated interest"
    },
    {
        "quiz_category": "Insurance",
        "financial_literacy_quiz": "What is a deductible in insurance?",
        "option1": "Monthly premium payment",
        "option2": "Amount you pay before insurance coverage begins",
        "option3": "Total coverage amount",
        "answer": "Amount you pay before insurance coverage begins"
    },
    {
        "quiz_category": "Debt Management",
        "financial_literacy_quiz": "Which debt should typically be paid off first?",
        "option1": "Mortgage",
        "option2": "High-interest credit card debt",
        "option3": "Student loans",
        "answer": "High-interest credit card debt"
    },
    {
        "quiz_category": "Investment",
        "financial_literacy_quiz": "What is a mutual fund?",
        "option1": "Individual stock investment",
        "option2": "Collection of investments managed professionally",
        "option3": "Savings account with high interest",
        "answer": "Collection of investments managed professionally"
    }
]

quiz_data_extended = [
    {
        "quiz_category": "Banking",
        "financial_literacy_quiz": "What is overdraft protection?",
        "option1": "Service that prevents account from going negative",
        "option2": "Insurance for stolen credit cards",
        "option3": "Protection against fraud",
        "answer": "Service that prevents account from going negative"
    },
    {
        "quiz_category": "Investment",
        "financial_literacy_quiz": "What is a bear market?",
        "option1": "Market where prices are rising",
        "option2": "Market where prices are falling",
        "option3": "Market with high trading volume",
        "answer": "Market where prices are falling"
    },
    {
        "quiz_category": "Credit",
        "financial_literacy_quiz": "What is a good credit utilization ratio?",
        "option1": "Below 30%",
        "option2": "Below 50%",
        "option3": "Below 80%",
        "answer": "Below 30%"
    },
    {
        "quiz_category": "Taxes",
        "financial_literacy_quiz": "What is the standard tax deduction?",
        "option1": "Amount everyone must pay in taxes",
        "option2": "Reduction in taxable income without itemizing",
        "option3": "Tax credit for dependents",
        "answer": "Reduction in taxable income without itemizing"
    },
    {
        "quiz_category": "Retirement",
        "financial_literacy_quiz": "What is a Roth IRA?",
        "option1": "Pre-tax retirement account",
        "option2": "After-tax retirement account",
        "option3": "Employer-sponsored retirement plan",
        "answer": "After-tax retirement account"
    },
    {
        "quiz_category": "Savings",
        "financial_literacy_quiz": "What is APY?",
        "option1": "Annual Percentage Yield",
        "option2": "Average Payment Yearly",
        "option3": "Account Payment Yield",
        "answer": "Annual Percentage Yield"
    },
    {
        "quiz_category": "Insurance",
        "financial_literacy_quiz": "What is a premium?",
        "option1": "Regular payment for insurance coverage",
        "option2": "Amount paid when filing a claim",
        "option3": "Coverage limit",
        "answer": "Regular payment for insurance coverage"
    },
    {
        "quiz_category": "Debt",
        "financial_literacy_quiz": "What is debt consolidation?",
        "option1": "Combining multiple debts into one payment",
        "option2": "Declaring bankruptcy",
        "option3": "Paying minimum payments",
        "answer": "Combining multiple debts into one payment"
    },
    {
        "quiz_category": "Investment",
        "financial_literacy_quiz": "What is an ETF?",
        "option1": "Exchange-Traded Fund",
        "option2": "Electronic Transfer Fee",
        "option3": "Extended Term Financing",
        "answer": "Exchange-Traded Fund"
    },
    {
        "quiz_category": "Credit",
        "financial_literacy_quiz": "What is a secured credit card?",
        "option1": "Card backed by a cash deposit",
        "option2": "Card with fraud protection",
        "option3": "Card with no annual fee",
        "answer": "Card backed by a cash deposit"
    },
    {
        "quiz_category": "Banking",
        "financial_literacy_quiz": "What is direct deposit?",
        "option1": "Electronic transfer of payments",
        "option2": "Cash deposit at ATM",
        "option3": "Check deposit by phone",
        "answer": "Electronic transfer of payments"
    },
    {
        "quiz_category": "Investment",
        "financial_literacy_quiz": "What is dollar-cost averaging?",
        "option1": "Investing fixed amounts regularly",
        "option2": "Buying when prices are low",
        "option3": "Converting currencies",
        "answer": "Investing fixed amounts regularly"
    },
    {
        "quiz_category": "Taxes",
        "financial_literacy_quiz": "What is a W-2 form?",
        "option1": "Wage and tax statement",
        "option2": "Business expense form",
        "option3": "Investment income report",
        "answer": "Wage and tax statement"
    },
    {
        "quiz_category": "Insurance",
        "financial_literacy_quiz": "What is a deductible?",
        "option1": "Amount you pay before insurance covers",
        "option2": "Monthly premium payment",
        "option3": "Coverage limit",
        "answer": "Amount you pay before insurance covers"
    },
    {
        "quiz_category": "Credit",
        "financial_literacy_quiz": "What is a credit freeze?",
        "option1": "Restricts access to credit reports",
        "option2": "Cancels credit cards",
        "option3": "Stops credit card charges",
        "answer": "Restricts access to credit reports"
    },
    {
        "quiz_category": "Retirement",
        "financial_literacy_quiz": "What is a pension?",
        "option1": "Regular retirement payments from employer",
        "option2": "Personal savings account",
        "option3": "Social security benefit",
        "answer": "Regular retirement payments from employer"
    },
    {
        "quiz_category": "Investment",
        "financial_literacy_quiz": "What is asset allocation?",
        "option1": "Distribution of investments",
        "option2": "Selling investments",
        "option3": "Buying real estate",
        "answer": "Distribution of investments"
    },
    {
        "quiz_category": "Banking",
        "financial_literacy_quiz": "What is a CD (Certificate of Deposit)?",
        "option1": "Time-restricted savings account",
        "option2": "Checking account",
        "option3": "Investment account",
        "answer": "Time-restricted savings account"
    },
    {
        "quiz_category": "Credit",
        "financial_literacy_quiz": "What is a balance transfer?",
        "option1": "Moving debt between cards",
        "option2": "Paying off credit card",
        "option3": "Checking account balance",
        "answer": "Moving debt between cards"
    },
    {
        "quiz_category": "Taxes",
        "financial_literacy_quiz": "What is tax withholding?",
        "option1": "Money employer takes out for taxes",
        "option2": "Tax refund amount",
        "option3": "Tax deadline extension",
        "answer": "Money employer takes out for taxes"
    }
    # Note: This is just the first 20 questions. Continue with similar format for remaining 80...
]


quiz_data_extended_2 = [
    {
        "quiz_category": "Investment",
        "financial_literacy_quiz": "What is compound interest?",
        "option1": "Interest earned on interest",
        "option2": "Fixed interest rate",
        "option3": "Simple interest calculation",
        "answer": "Interest earned on interest"
    },
    {
        "quiz_category": "Banking",
        "financial_literacy_quiz": "What is mobile banking?",
        "option1": "Managing accounts via smartphone",
        "option2": "ATM withdrawals",
        "option3": "Branch banking",
        "answer": "Managing accounts via smartphone"
    },
    {
        "quiz_category": "Credit",
        "financial_literacy_quiz": "What is a credit report?",
        "option1": "Record of credit history",
        "option2": "Monthly credit card statement",
        "option3": "Loan application",
        "answer": "Record of credit history"
    },
    {
        "quiz_category": "Retirement",
        "financial_literacy_quiz": "What is a 403(b)?",
        "option1": "Retirement plan for non-profits",
        "option2": "Personal savings account",
        "option3": "Government pension plan",
        "answer": "Retirement plan for non-profits"
    },
    {
        "quiz_category": "Taxes",
        "financial_literacy_quiz": "What is AGI?",
        "option1": "Adjusted Gross Income",
        "option2": "Annual Growth Index",
        "option3": "Average Gain Interest",
        "answer": "Adjusted Gross Income"
    },
    {
        "quiz_category": "Investment",
        "financial_literacy_quiz": "What is diversification?",
        "option1": "Spreading investment risk",
        "option2": "Buying single stock",
        "option3": "Selling all investments",
        "answer": "Spreading investment risk"
    },
    {
        "quiz_category": "Insurance",
        "financial_literacy_quiz": "What is term life insurance?",
        "option1": "Coverage for specific period",
        "option2": "Permanent life insurance",
        "option3": "Health insurance plan",
        "answer": "Coverage for specific period"
    },
    {
        "quiz_category": "Banking",
        "financial_literacy_quiz": "What is ACH transfer?",
        "option1": "Electronic bank-to-bank transfer",
        "option2": "Wire transfer",
        "option3": "Cash withdrawal",
        "answer": "Electronic bank-to-bank transfer"
    },
    {
        "quiz_category": "Credit",
        "financial_literacy_quiz": "What is a good credit score?",
        "option1": "Above 700",
        "option2": "Above 500",
        "option3": "Above 300",
        "answer": "Above 700"
    },
    {
        "quiz_category": "Investment",
        "financial_literacy_quiz": "What is a dividend?",
        "option1": "Company profit distribution",
        "option2": "Stock price",
        "option3": "Trading fee",
        "answer": "Company profit distribution"
    }
    # Continuing with similar format...
]

quiz_data_extended_3 = [
    {
        "quiz_category": "Mortgages",
        "financial_literacy_quiz": "What is PMI?",
        "option1": "Private Mortgage Insurance",
        "option2": "Personal Money Investment",
        "option3": "Property Management Insurance",
        "answer": "Private Mortgage Insurance"
    },
    {
        "quiz_category": "Budgeting",
        "financial_literacy_quiz": "What is a zero-based budget?",
        "option1": "Every dollar has a purpose",
        "option2": "Spending no money",
        "option3": "Having zero debt",
        "answer": "Every dollar has a purpose"
    },
    {
        "quiz_category": "Cryptocurrency",
        "financial_literacy_quiz": "What is blockchain?",
        "option1": "Decentralized transaction ledger",
        "option2": "Digital wallet",
        "option3": "Trading platform",
        "answer": "Decentralized transaction ledger"
    },
    {
        "quiz_category": "Real Estate",
        "financial_literacy_quiz": "What is escrow?",
        "option1": "Third party holding funds",
        "option2": "Down payment",
        "option3": "Property tax",
        "answer": "Third party holding funds"
    },
    {
        "quiz_category": "Personal Finance",
        "financial_literacy_quiz": "What is net worth?",
        "option1": "Assets minus liabilities",
        "option2": "Total income",
        "option3": "Total savings",
        "answer": "Assets minus liabilities"
    },
    {
        "quiz_category": "Banking",
        "financial_literacy_quiz": "What is FDIC insurance?",
        "option1": "Bank deposit protection",
        "option2": "Credit card insurance",
        "option3": "Investment protection",
        "answer": "Bank deposit protection"
    },
    {
        "quiz_category": "Credit Cards",
        "financial_literacy_quiz": "What is a cash advance?",
        "option1": "Borrowing cash from credit card",
        "option2": "ATM withdrawal",
        "option3": "Debit card purchase",
        "answer": "Borrowing cash from credit card"
    },
    {
        "quiz_category": "Investing",
        "financial_literacy_quiz": "What is a market cap?",
        "option1": "Total value of company shares",
        "option2": "Stock price limit",
        "option3": "Trading volume",
        "answer": "Total value of company shares"
    },
    {
        "quiz_category": "Retirement",
        "financial_literacy_quiz": "What is a required minimum distribution (RMD)?",
        "option1": "Mandatory retirement account withdrawal",
        "option2": "Minimum investment amount",
        "option3": "Regular monthly deposit",
        "answer": "Mandatory retirement account withdrawal"
    },
    {
        "quiz_category": "Insurance",
        "financial_literacy_quiz": "What is an HSA?",
        "option1": "Health Savings Account",
        "option2": "Home Security Allowance",
        "option3": "High-Stakes Account",
        "answer": "Health Savings Account"
    }
    # Continuing with similar format...
]


def insert_quiz_data(connection_string):
    try:
        # Create MongoDB client
        #quiz_data = quiz_data_extended_3
        client = MongoClient(connection_string)

        # Access database and collection
        db = client['hackncCluster']  # MongoDB database name
        collection = db['quiz_questions']  # collection name
        
        # Add metadata to each document
        for quiz in quiz_data:
            quiz['created_at'] = datetime.utcnow()
            quiz['last_updated'] = datetime.utcnow()
        
        # Insert the data
        result = collection.insert_many(quiz_data)
        
        print(f"Successfully inserted {len(result.inserted_ids)} documents")
        
        # Create indexes for better query performance
        collection.create_index("quiz_category")
        collection.create_index("created_at")
        
        return True
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
        
    finally:
        client.close()

# Example usage:
if __name__ == "__main__":
    # Replace with your MongoDB Atlas connection string
    MONGODB_URI = uri = os.getenv("MONGO_URI")
    
    insert_quiz_data(MONGODB_URI)