from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import datetime

app = Flask(__name__)
CORS(app)

# Database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '@rupa123',
    'database': 'finance_analyzer'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'message': 'Missing required fields'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        # Check if email exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({'message': 'Email already registered'}), 400

        # Insert new user
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        conn.commit()
        return jsonify({'message': 'Registration successful'}), 201
    except Error as e:
        return jsonify({'message': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing email or password'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        # Using raw password matching (for simplicity as requested)
        cursor.execute("SELECT id, name, email FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        
        if user:
            return jsonify({'message': 'Login successful', 'user': user}), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    except Error as e:
        return jsonify({'message': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    user_id = request.args.get('user_id')
    month = request.args.get('month') # e.g., 'January', 'All Time'
    
    if not user_id:
        return jsonify({'message': 'User ID required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        
        # 1. Total Income (Dummy 0 for now as we don't have income table yet, but let's send 0)
        total_income = 0
        
        # 2. Total Expenses
        expense_query = "SELECT SUM(amount) as total FROM expenses WHERE user_id = %s"
        expense_params = [user_id]
        if month and month != 'All Time':
            expense_query += " AND billing_month = %s"
            expense_params.append(month)
        
        cursor.execute(expense_query, tuple(expense_params))
        total_expenses = cursor.fetchone()['total'] or 0
        
        # 3. Target Budget
        budget_query = "SELECT SUM(amount) as total FROM budgets WHERE user_id = %s"
        budget_params = [user_id]
        if month and month != 'All Time':
            budget_query += " AND month = %s"
            budget_params.append(month)
            
        cursor.execute(budget_query, tuple(budget_params))
        target_budget = cursor.fetchone()['total'] or 0
        
        # 4. Total Transactions count
        cursor.execute("SELECT COUNT(id) as count FROM expenses WHERE user_id = %s", (user_id,))
        total_transactions = cursor.fetchone()['count'] or 0
        
        # 5. Category Breakdown (Pie Chart data)
        # Demonstrating JOIN query here
        cursor.execute("""
            SELECT c.name, SUM(e.amount) as total 
            FROM expenses e 
            JOIN categories c ON e.category_id = c.id 
            WHERE e.user_id = %s 
            GROUP BY c.name
        """, (user_id,))
        category_breakdown = cursor.fetchall()
        
        # Highest expense category
        highest_expense = 'None'
        if category_breakdown:
            highest_expense = max(category_breakdown, key=lambda x:x['total'])['name']
        
        # Net Worth
        net_worth = float(target_budget) - float(total_expenses)
        
        return jsonify({
            'total_income': total_income,
            'total_expenses': float(total_expenses),
            'target_budget': float(target_budget),
            'net_worth': net_worth,
            'total_transactions': total_transactions,
            'highest_expense': highest_expense,
            'category_breakdown': category_breakdown
        }), 200
        
    except Error as e:
        return jsonify({'message': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/expenses', methods=['GET', 'POST'])
def manage_expenses():
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            data = request.json
            user_id = data.get('user_id')
            amount = data.get('amount')
            category_id = data.get('category_id')
            billing_month = data.get('billing_month')
            transaction_date = data.get('transaction_date')
            description = data.get('description', '')
            
            if not user_id or not amount or not category_id or not billing_month or not transaction_date:
                return jsonify({'message': 'Missing required fields'}), 400
                
            cursor.execute("""
                INSERT INTO expenses (user_id, category_id, amount, description, transaction_date, billing_month)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, category_id, amount, description, transaction_date, billing_month))
            conn.commit()
            return jsonify({'message': 'Expense added successfully'}), 201
            
        elif request.method == 'GET':
            user_id = request.args.get('user_id')
            month = request.args.get('month')
            
            if not user_id:
                return jsonify({'message': 'User ID required'}), 400
                
            query = """
                SELECT e.id, e.amount, e.description, DATE_FORMAT(e.transaction_date, '%d-%m-%Y') as date, 
                       e.billing_month, c.name as category_name
                FROM expenses e
                JOIN categories c ON e.category_id = c.id
                WHERE e.user_id = %s
            """
            params = [user_id]
            if month and month != 'All Time':
                query += " AND e.billing_month = %s"
                params.append(month)
                
            query += " ORDER BY e.transaction_date DESC"
            
            cursor.execute(query, tuple(params))
            expenses = cursor.fetchall()
            return jsonify(expenses), 200

    except Error as e:
        return jsonify({'message': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/categories', methods=['GET'])
def get_categories():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categories")
        categories = cursor.fetchall()
        return jsonify(categories), 200
    except Error as e:
        return jsonify({'message': str(e)}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/budget', methods=['POST'])
def update_budget():
    data = request.json
    user_id = data.get('user_id')
    month = data.get('month')
    amount = data.get('amount')
    
    if not user_id or not month or not amount:
        return jsonify({'message': 'Missing required fields'}), 400
        
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        # Use INSERT ... ON DUPLICATE KEY UPDATE to either create or update the budget
        cursor.execute("""
            INSERT INTO budgets (user_id, month, amount) 
            VALUES (%s, %s, %s) 
            ON DUPLICATE KEY UPDATE amount = %s
        """, (user_id, month, amount, amount))
        conn.commit()
        return jsonify({'message': 'Budget updated successfully'}), 200
    except Error as e:
        return jsonify({'message': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
