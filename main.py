from flask import Flask, render_template, request
import pandas as pd
import os
import hashlib
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_company', methods=['GET', 'POST'])
def add_company():
    if request.method == 'POST':
        company_name = request.form['company_name']
        shares = int(request.form['shares'])
        bitcoins = int(request.form['bitcoins'])
        filename = f"{company_name}.csv"
        
        # Check if file already exists
        if os.path.exists(filename):
            return render_template('result.html', message=f"Company {company_name} already exists.")
        
        df = pd.DataFrame({
            'Company': [company_name],
            'Shares': [shares],
            'Bitcoins': [bitcoins]
        })
        df.to_csv(filename, index=False)
        return render_template('result.html', message=f"Company {company_name} added successfully!")
    return render_template('add_company.html')

@app.route('/make_transaction', methods=['GET', 'POST'])
def make_transaction():
    if request.method == 'POST':
        seller = request.form['seller']
        buyer = request.form['buyer']
        shares = int(request.form['shares'])
        
        # File paths
        seller_filename = f"{seller}.csv"
        buyer_filename = f"{buyer}.csv"
        
        # Check if both seller and buyer are registered
        if not os.path.exists(seller_filename):
            return render_template('result.html', message=f"Seller {seller} is not registered. <a href='/add_company'>Register here</a>.")
        if not os.path.exists(buyer_filename):
            return render_template('result.html', message=f"Buyer {buyer} is not registered. <a href='/add_company'>Register here</a>.")
        
        # Load the seller and buyer CSV files
        seller_df = pd.read_csv(seller_filename)
        buyer_df = pd.read_csv(buyer_filename)

        # Ensure the Shares column is numeric
        seller_df['Shares'] = pd.to_numeric(seller_df['Shares'], errors='coerce')
        buyer_df['Shares'] = pd.to_numeric(buyer_df['Shares'], errors='coerce')

        # Check if the required columns exist
        if 'Shares' not in seller_df.columns or 'Shares' not in buyer_df.columns:
            return render_template('result.html', message="Transaction failed: Missing 'Shares' column in one of the company's data.")
        
        # Perform transaction logic
        if seller_df.loc[0, 'Shares'] >= shares:
            seller_df.loc[0, 'Shares'] -= shares
            buyer_df.loc[0, 'Shares'] += shares
            
            # Create a transaction hash
            transaction_details = f"{seller} -> {buyer}: {shares} shares"
            transaction_hash = hashlib.sha256(transaction_details.encode()).hexdigest()
            date_time = datetime.now()
            date = date_time.strftime("%Y-%m-%d")
            time = date_time.strftime("%H:%M:%S")
            
            # Append transaction details to both CSV files
            transaction_data_seller = {
                'Company': seller,
                'Shares': seller_df.loc[0, 'Shares'],
                'Bitcoins': seller_df.loc[0, 'Bitcoins'],
                'Transaction Hash': transaction_hash,
                'Date': date,
                'Time': time
            }
            transaction_data_buyer = {
                'Company': buyer,
                'Shares': buyer_df.loc[0, 'Shares'],
                'Bitcoins': buyer_df.loc[0, 'Bitcoins'],
                'Transaction Hash': transaction_hash,
                'Date': date,
                'Time': time
            }
            
            # Append transaction data to CSV files
            seller_df = pd.concat([seller_df, pd.DataFrame(transaction_data_seller, index=[0])], ignore_index=True)
            buyer_df = pd.concat([buyer_df, pd.DataFrame(transaction_data_buyer, index=[0])], ignore_index=True)
            
            # Save updated CSV files
            seller_df.to_csv(seller_filename, index=False)
            buyer_df.to_csv(buyer_filename, index=False)
            
            return render_template('result.html', message="Transaction successful!")
        else:
            return render_template('result.html', message="Transaction failed: Not enough shares.")
    return render_template('make_transaction.html')

if __name__ == '__main__':
    app.run(debug=True)
