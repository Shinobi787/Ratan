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

