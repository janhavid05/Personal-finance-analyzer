# Personal Finance Analyzer

## 📊 Project Description
Personal Finance Analyzer is a comprehensive web-based application designed to help individuals track their income, expenses, and manage budgets efficiently. The platform provides a clear overview of financial health through an intuitive dashboard, categorical breakdowns, and month-by-month comparisons, empowering users to make informed financial decisions.

## 💻 Tech Stack
* **Frontend:** HTML5, CSS3, Vanilla JavaScript
* **Backend:** Python, Flask, Flask-CORS
* **Database:** MySQL
* **Environment Management:** python-dotenv

## ✨ Key Features
* **User Authentication:** Secure registration and login system.
* **Interactive Dashboard:** Real-time summary of total expenses, target budget, net worth, and total transactions.
* **Expense Tracking:** Log and categorize daily expenses easily.
* **Budget Management:** Set monthly budget targets and monitor spending against them.
* **Category Breakdown:** Analyze spending across various categories (e.g., Food, Travel, Utilities) to identify high-expense areas.
* **Historical Data Comparison:** Compare financial statistics across different months.

## 📁 Directory Structure
```text
Personal-finance-analyzer/
│
├── backend/                  # Flask application and server logic
│   ├── venv/                 # Python virtual environment
│   ├── .env                  # Environment variables for DB connections
│   ├── app.py                # Main backend application file (API routes)
│   └── requirements.txt      # Python dependencies
│
├── frontend/                 # User interface
│   ├── css/                  # Stylesheets for UI
│   ├── js/                   # Client-side logic and API integrations
│   ├── index.html            # Landing / Login page
│   ├── register.html         # User registration page
│   └── dashboard.html        # Main dashboard interface
│
├── sql queries.sql           # Database schema and initial setup queries
├── .gitignore                # Git ignore rules
└── README.md                 # Project documentation
```

## 🚀 Setup and Installation

### Prerequisites
* Python 3.x
* MySQL Server
* Web Browser (Chrome, Firefox, Safari, Edge)

### 1. Database Setup
1. Create a MySQL database (e.g., `finance_analyzer`).
2. Run the SQL commands found in `sql queries.sql` to set up the necessary tables (`users`, `expenses`, `categories`, `budgets`, etc.).

### 2. Backend Configuration
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows: venv\Scripts\activate
   # On Mac/Linux: source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Verify or update the environment variables in `backend/.env` file:
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=finance_analyzer
   ```
5. Start the backend server:
   ```bash
   python app.py
   ```
   The backend should now be running (typically on port 5000).

### 3. Frontend Setup
1. Open the `frontend` folder.
2. Since the frontend uses standard HTML/JS, you can simply open `index.html` in your browser. Alternatively, you can run a local server (like the Live Server extension in VS Code) for a better development experience.
