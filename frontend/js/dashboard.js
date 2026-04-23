const API_URL = 'http://localhost:5000/api';
let currentUser = null;
let currentMonth = 'All Time';
let pieChartInstance = null;
let barChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    // Check authentication
    const userStr = localStorage.getItem('user');
    if (!userStr) {
        window.location.href = 'index.html';
        return;
    }
    currentUser = JSON.parse(userStr);

    // Setup UI
    setupNavigation();
    setupDashboard();
    loadCategories();
    
    // Event listeners
    document.getElementById('logoutBtn').addEventListener('click', () => {
        localStorage.removeItem('user');
        window.location.href = 'index.html';
    });

    document.getElementById('monthFilter').addEventListener('change', (e) => {
        currentMonth = e.target.value;
        loadDashboardData();
    });

    document.getElementById('exportBtn').addEventListener('click', exportToPDF);
    document.getElementById('addExpenseForm').addEventListener('submit', handleAddExpense);
    document.getElementById('budgetForm').addEventListener('submit', handleUpdateBudget);
});

function setupNavigation() {
    const navLinks = {
        'nav-dashboard': 'view-dashboard',
        'nav-add-expense': 'view-add-expense',
        'nav-expenses': 'view-expenses',
        'nav-budget': 'view-budget'
    };

    const exportBtn = document.getElementById('exportBtn');

    for (const [navId, viewId] of Object.entries(navLinks)) {
        document.getElementById(navId).addEventListener('click', (e) => {
            e.preventDefault();
            
            // Update active state in nav
            document.querySelectorAll('.nav-links li').forEach(li => li.classList.remove('active'));
            e.target.parentElement.classList.add('active');

            // Show corresponding view
            document.querySelectorAll('.view').forEach(view => view.style.display = 'none');
            document.getElementById(viewId).style.display = 'block';

            // Change title
            document.getElementById('page-title').innerText = e.target.innerText;

            // Specific view actions and export button visibility
            if (viewId === 'view-dashboard') {
                exportBtn.style.display = 'inline-block';
                loadDashboardData();
            } else {
                exportBtn.style.display = 'none';
            }
            
            if (viewId === 'view-expenses') {
                loadExpenses();
            }
        });
    }
}

async function setupDashboard() {
    await loadDashboardData();
}

async function loadDashboardData() {
    try {
        const response = await fetch(`${API_URL}/dashboard?user_id=${currentUser.id}&month=${currentMonth}`);
        if (!response.ok) throw new Error('Failed to load dashboard data');
        const data = await response.json();
        
        // Update Stats
        document.getElementById('netWorth').innerText = `₹${data.net_worth.toFixed(2)}`;
        document.getElementById('totalExpenses').innerText = `₹${data.total_expenses.toFixed(2)}`;
        document.getElementById('targetBudget').innerText = data.target_budget ? `₹${data.target_budget.toFixed(2)}` : 'Not Set';
        document.getElementById('totalTransactions').innerText = data.total_transactions;
        document.getElementById('highestExpense').innerText = data.highest_expense;

        // Render Charts
        renderPieChart(data.category_breakdown);
        renderBarChart(data.category_breakdown);

    } catch (error) {
        console.error('Error fetching dashboard data:', error);
    }
}

async function loadCategories() {
    try {
        const response = await fetch(`${API_URL}/categories`);
        if (response.ok) {
            const categories = await response.json();
            const select = document.getElementById('expCategory');
            select.innerHTML = '';
            categories.forEach(c => {
                const option = document.createElement('option');
                option.value = c.id;
                option.textContent = c.name;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

async function handleAddExpense(e) {
    e.preventDefault();
    const payload = {
        user_id: currentUser.id,
        amount: document.getElementById('expAmount').value,
        category_id: document.getElementById('expCategory').value,
        billing_month: document.getElementById('expMonth').value,
        transaction_date: document.getElementById('expDate').value,
        description: document.getElementById('expDesc').value
    };

    try {
        const response = await fetch(`${API_URL}/expenses`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (response.ok) {
            alert('Expense added successfully!');
            document.getElementById('addExpenseForm').reset();
            loadDashboardData();
        }
    } catch (error) {
        console.error('Error saving expense:', error);
    }
}

async function loadExpenses() {
    try {
        const response = await fetch(`${API_URL}/expenses?user_id=${currentUser.id}&month=${currentMonth}`);
        if (response.ok) {
            const expenses = await response.json();
            const tbody = document.getElementById('expensesTableBody');
            tbody.innerHTML = '';
            expenses.forEach(e => {
                tbody.innerHTML += `
                    <tr>
                        <td>${e.date}</td>
                        <td>${e.billing_month}</td>
                        <td><span class="badge">${e.category_name}</span></td>
                        <td>${e.description}</td>
                        <td>₹${e.amount}</td>
                    </tr>
                `;
            });
        }
    } catch (error) {
        console.error('Error loading expenses:', error);
    }
}

async function handleUpdateBudget(e) {
    e.preventDefault();
    const payload = {
        user_id: currentUser.id,
        month: document.getElementById('budgetMonth').value,
        amount: document.getElementById('budgetAmount').value
    };

    try {
        const response = await fetch(`${API_URL}/budget`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (response.ok) {
            alert('Budget updated successfully!');
            document.getElementById('budgetForm').reset();
            loadDashboardData();
        }
    } catch (error) {
        console.error('Error updating budget:', error);
    }
}

function renderPieChart(data) {
    const ctx = document.getElementById('pieChart').getContext('2d');
    const labels = data.map(d => d.name);
    const values = data.map(d => parseFloat(d.total));

    if (pieChartInstance) pieChartInstance.destroy();

    pieChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: ['#4f46e5', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

function renderBarChart(data) {
    const ctx = document.getElementById('barChart').getContext('2d');
    const labels = data.map(d => d.name);
    const values = data.map(d => parseFloat(d.total));

    if (barChartInstance) barChartInstance.destroy();

    barChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Expenses by Category (₹)',
                data: values,
                backgroundColor: '#3b82f6',
                borderRadius: 4
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

function exportToPDF() {
    const element = document.getElementById('content-area');
    const opt = {
        margin: 10,
        filename: 'Finance_Report.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'landscape' }
    };
    html2pdf().set(opt).from(element).save();
}
