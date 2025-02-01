<<<<<<< HEAD
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from pathlib import Path
import json

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

def authenticate(email, password):
    """Basic authentication"""
    if email == "demo@example.com" and password == "password":
        st.session_state.authenticated = True
        return True
    return False

def generate_financial_advice(financial_data):
    """Generate financial advice based on basic financial rules"""
    income = financial_data['income']
    expenses = financial_data['expenses']
    monthly_savings = financial_data['monthly_savings']
    savings_ratio = financial_data['savings_ratio']
    savings_goal = financial_data['savings_goal']
    
    advice = []
    
    # Basic 50/30/20 rule check
    total_expenses = sum(expenses.values())
    needs_ratio = sum(v for k, v in expenses.items() if k in ['Housing', 'Food', 'Utilities']) / income * 100
    wants_ratio = sum(v for k, v in expenses.items() if k not in ['Housing', 'Food', 'Utilities']) / income * 100
    savings_ratio = (monthly_savings / income) * 100
    
    # Generate personalized advice
    if needs_ratio > 50:
        advice.append("🏠 Your essential expenses (housing, food, utilities) are above 50% of income. "
                     "Consider finding ways to reduce these costs or increase income.")
    
    if wants_ratio > 30:
        advice.append("🎯 Your discretionary spending is above 30% of income. "
                     "Try tracking these expenses more closely to find potential savings.")
    
    if savings_ratio < 20:
        advice.append("💰 Your savings rate is below the recommended 20%. "
                     f"Try to increase monthly savings by ${(0.2 * income) - monthly_savings:.2f} to reach this goal.")
    
    # Housing cost check
    if expenses.get('Housing', 0) > 0.3 * income:
        advice.append("🏘️ Your housing costs exceed 30% of your income. "
                     "This might strain your budget - consider ways to reduce housing costs.")
    
    # Emergency fund check
    months_to_emergency_fund = (income * 6 - savings_goal) / monthly_savings if monthly_savings > 0 else float('inf')
    if months_to_emergency_fund > 0:
        advice.append(f"🏦 At current savings rate, it will take {months_to_emergency_fund:.1f} months "
                     "to build a 6-month emergency fund.")
    
    # Generate savings plan
    monthly_target = savings_goal / 12
    if monthly_savings < monthly_target:
        deficit = monthly_target - monthly_savings
        potential_savings = {
            "Reduce dining out": min(expenses.get('Food', 0) * 0.3, deficit),
            "Optimize utilities": min(expenses.get('Utilities', 0) * 0.2, deficit),
            "Transportation savings": min(expenses.get('Transportation', 0) * 0.25, deficit),
        }
        
        advice.append("\n💡 To reach your savings goal, consider these monthly savings opportunities:")
        for category, amount in potential_savings.items():
            if amount > 0:
                advice.append(f"- {category}: ${amount:.2f}")
    
    return "\n\n".join(advice)

def create_savings_plan(financial_data):
    """Create a monthly savings plan to reach the goal"""
    income = financial_data['income']
    monthly_savings = financial_data['monthly_savings']
    savings_goal = financial_data['savings_goal']
    
    # Calculate months needed at current rate
    months_to_goal = savings_goal / monthly_savings if monthly_savings > 0 else float('inf')
    
    # Create a 12-month plan
    plan_data = []
    cumulative_savings = 0
    monthly_target = savings_goal / 12  # Ideal monthly savings to reach goal in 1 year
    
    for month in range(1, 13):
        cumulative_savings += monthly_savings
        target_cumulative = monthly_target * month
        
        plan_data.append({
            'Month': f'Month {month}',
            'Target Savings': target_cumulative,
            'Projected Savings': cumulative_savings,
            'Monthly Target': monthly_target,
            'Current Rate': monthly_savings,
            'Difference': monthly_savings - monthly_target
        })
    
    return pd.DataFrame(plan_data)

def render_login():
    """Render login form"""
    st.title("Welcome to Ratan - Your Financial Planner")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if authenticate(email, password):
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

def render_financial_input():
    """Render financial data input form"""
    st.title("Set Your Financial Goals")
    
    with st.form("financial_form"):
        monthly_income = st.number_input("Monthly Income ($)", min_value=0.0, step=100.0)
        
        st.subheader("Monthly Expenses")
        housing = st.number_input("Housing ($)", min_value=0.0, step=100.0)
        transportation = st.number_input("Transportation ($)", min_value=0.0, step=50.0)
        food = st.number_input("Food ($)", min_value=0.0, step=50.0)
        utilities = st.number_input("Utilities ($)", min_value=0.0, step=50.0)
        
        savings_goal = st.number_input("Annual Savings Goal ($)", min_value=0.0, step=1000.0)
        
        submit = st.form_submit_button("Generate Financial Plan")
        
        if submit:
            expenses = {
                'Housing': housing,
                'Transportation': transportation,
                'Food': food,
                'Utilities': utilities
            }
            
            monthly_savings = monthly_income - sum(expenses.values())
            savings_ratio = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0
            
            financial_data = {
                'income': monthly_income,
                'expenses': expenses,
                'monthly_savings': monthly_savings,
                'savings_ratio': savings_ratio,
                'savings_goal': savings_goal
            }
            
            st.session_state.user_data = financial_data
            save_user_data(financial_data)
            
            st.success("Financial plan generated!")
            st.rerun()

def render_dashboard():
    """Render financial dashboard"""
    if st.session_state.user_data:
        st.title("Your Financial Dashboard")
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Monthly Income", f"${st.session_state.user_data['income']:.2f}")
        with col2:
            st.metric("Monthly Savings", f"${st.session_state.user_data['monthly_savings']:.2f}")
        with col3:
            st.metric("Savings Ratio", f"{st.session_state.user_data['savings_ratio']:.1f}%")
        
        # Expenses breakdown chart
        expenses_df = pd.DataFrame(
            list(st.session_state.user_data['expenses'].items()),
            columns=['Category', 'Amount']
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                expenses_df,
                values='Amount',
                names='Category',
                title='Expenses Breakdown'
            )
            st.plotly_chart(fig)
        
        with col2:
            # Monthly spending bar chart
            fig2 = px.bar(
                expenses_df,
                x='Category',
                y='Amount',
                title='Monthly Spending by Category'
            )
            st.plotly_chart(fig2)
        
        # Financial Advice
        st.subheader("📊 Financial Analysis & Recommendations")
        advice = generate_financial_advice(st.session_state.user_data)
        st.write(advice)
        
        # Savings Plan
        st.subheader("💰 12-Month Savings Plan")
        savings_plan = create_savings_plan(st.session_state.user_data)
        
        # Savings progress chart
        fig3 = px.line(
            savings_plan,
            x='Month',
            y=['Target Savings', 'Projected Savings'],
            title='Savings Progress Projection'
        )
        st.plotly_chart(fig3)
        
        # Detailed plan table
        st.dataframe(
            savings_plan.style.format({
                'Target Savings': '${:,.2f}',
                'Projected Savings': '${:,.2f}',
                'Monthly Target': '${:,.2f}',
                'Current Rate': '${:,.2f}',
                'Difference': '${:,.2f}'
            })
        )

def save_user_data(data):
    """Save user data to JSON file"""
    Path("data").mkdir(exist_ok=True)
    with open('data/user_data.json', 'w') as f:
        json.dump(data, f)

def load_user_data():
    """Load user data from JSON file"""
    try:
        with open('data/user_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def main():
    # Authentication check
    if not st.session_state.authenticated:
        render_login()
        return
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Financial Goals", "Dashboard"]
    )
    
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
    
    # Page routing
    if page == "Financial Goals":
        render_financial_input()
    elif page == "Dashboard":
        render_dashboard()

if __name__ == "__main__":
    main()
=======
# Ratan.py
import streamlit as st
import pandas as pd
from datetime import datetime
import openai
import plotly.express as px
import yaml
from pathlib import Path
import json

# Config and Security
def load_config():
    """Load configuration from config.yaml"""
    with open('config.yaml') as file:
        config = yaml.safe_load(file)
    return config

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

# Authentication
def authenticate(email, password):
    """Basic authentication - replace with Firebase in production"""
    # Demo credentials - replace with actual authentication
    if email == "demo@example.com" and password == "password":
        st.session_state.authenticated = True
        return True
    return False

# Financial Data Processing
def process_financial_data(income, expenses, savings_goal):
    """Process user financial data and return recommendations"""
    monthly_savings = income - sum(expenses.values())
    savings_ratio = (monthly_savings / income) * 100
    
    data = {
        'income': income,
        'expenses': expenses,
        'monthly_savings': monthly_savings,
        'savings_ratio': savings_ratio,
        'savings_goal': savings_goal
    }
    
    return data

def get_ai_recommendations(financial_data):
    """Generate AI recommendations using OpenAI"""
    prompt = f"""
    Based on the following financial data:
    Monthly Income: ${financial_data['income']}
    Monthly Expenses: ${sum(financial_data['expenses'].values())}
    Current Savings Ratio: {financial_data['savings_ratio']:.1f}%
    Savings Goal: ${financial_data['savings_goal']}

    Provide 3 specific financial recommendations to help reach the savings goal.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Unable to generate AI recommendations at the moment."

# UI Components
def render_login():
    """Render login form"""
    st.title("Welcome to Ratan - Your AI Financial Planner")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if authenticate(email, password):
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

def render_financial_input():
    """Render financial data input form"""
    st.title("Set Your Financial Goals")
    
    with st.form("financial_form"):
        monthly_income = st.number_input("Monthly Income ($)", min_value=0.0, step=100.0)
        
        st.subheader("Monthly Expenses")
        housing = st.number_input("Housing ($)", min_value=0.0, step=100.0)
        transportation = st.number_input("Transportation ($)", min_value=0.0, step=50.0)
        food = st.number_input("Food ($)", min_value=0.0, step=50.0)
        utilities = st.number_input("Utilities ($)", min_value=0.0, step=50.0)
        
        savings_goal = st.number_input("Savings Goal ($)", min_value=0.0, step=1000.0)
        
        submit = st.form_submit_button("Generate Financial Plan")
        
        if submit:
            expenses = {
                'Housing': housing,
                'Transportation': transportation,
                'Food': food,
                'Utilities': utilities
            }
            
            financial_data = process_financial_data(monthly_income, expenses, savings_goal)
            st.session_state.user_data = financial_data
            
            # Store data (replace with proper database in production)
            save_user_data(financial_data)
            
            st.success("Financial plan generated!")
            st.rerun()

def render_dashboard():
    """Render financial dashboard"""
    if st.session_state.user_data:
        st.title("Your Financial Dashboard")
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Monthly Income", f"${st.session_state.user_data['income']:.2f}")
        with col2:
            st.metric("Monthly Savings", f"${st.session_state.user_data['monthly_savings']:.2f}")
        with col3:
            st.metric("Savings Ratio", f"{st.session_state.user_data['savings_ratio']:.1f}%")
        
        # Expenses breakdown chart
        expenses_df = pd.DataFrame(
            list(st.session_state.user_data['expenses'].items()),
            columns=['Category', 'Amount']
        )
        
        fig = px.pie(
            expenses_df,
            values='Amount',
            names='Category',
            title='Expenses Breakdown'
        )
        st.plotly_chart(fig)
        
        # AI Recommendations
        st.subheader("AI-Powered Recommendations")
        recommendations = get_ai_recommendations(st.session_state.user_data)
        st.write(recommendations)

# Data Storage
def save_user_data(data):
    """Save user data to JSON file (replace with database in production)"""
    Path("data").mkdir(exist_ok=True)
    with open('data/user_data.json', 'w') as f:
        json.dump(data, f)

def load_user_data():
    """Load user data from JSON file"""
    try:
        with open('data/user_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

# Main App
def main():
    # Load configuration
    config = load_config()
    
    # Set OpenAI API key
    openai.api_key = config['openai_api_key']
    
    # Authentication check
    if not st.session_state.authenticated:
        render_login()
        return
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Financial Goals", "Dashboard"]
    )
    
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
    
    # Page routing
    if page == "Financial Goals":
        render_financial_input()
    elif page == "Dashboard":
        render_dashboard()

if __name__ == "__main__":
    main()

>>>>>>> 0ae0e7df40e4b7c79f88a6b3dd3618fe188d1184
