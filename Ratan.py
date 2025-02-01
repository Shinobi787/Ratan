import streamlit as st
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'api_key_submitted' not in st.session_state:
    st.session_state.api_key_submitted = False

def get_ai_recommendations(financial_data, api_key):
    """Generate AI recommendations using OpenAI"""
    try:
        import openai
        openai.api_key = api_key
        
        prompt = f"""
        Based on the following financial data:
        Monthly Income: ${financial_data['income']}
        Monthly Expenses: ${sum(financial_data['expenses'].values())}
        Current Savings Ratio: {financial_data['savings_ratio']:.1f}%
        Savings Goal: ${financial_data['savings_goal']}
        
        Provide 3 specific financial recommendations to help reach the savings goal.
        Consider:
        1. Expense optimization
        2. Savings strategies
        3. Investment suggestions
        Be specific and practical.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating AI recommendations: {str(e)}"

def authenticate(email, password):
    """Basic authentication"""
    if email == "demo@example.com" and password == "password":
        st.session_state.authenticated = True
        return True
    return False

def render_login():
    """Render login form"""
    st.title("Welcome to Ratan - AI Financial Planner")
    
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
                
    st.markdown("Use demo@example.com / password to login")

def render_financial_input():
    """Render financial data input form"""
    st.title("Set Your Financial Goals")
    
    # API Key Input Section
    if not st.session_state.api_key_submitted:
        st.info("🔑 To get AI-powered recommendations, please enter your OpenAI API key.")
        with st.form("api_key_form"):
            api_key = st.text_input("OpenAI API Key", type="password")
            submit_key = st.form_submit_button("Submit API Key")
            
            if submit_key and api_key:
                st.session_state.api_key = api_key
                st.session_state.api_key_submitted = True
                st.success("API Key saved! You can now get AI recommendations.")
                st.rerun()
    
    # Financial Data Input Form
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
            fig2 = px.bar(
                expenses_df,
                x='Category',
                y='Amount',
                title='Monthly Spending by Category'
            )
            st.plotly_chart(fig2)
        
        # AI Recommendations
        st.subheader("🤖 AI-Powered Financial Recommendations")
        if hasattr(st.session_state, 'api_key') and st.session_state.api_key_submitted:
            recommendations = get_ai_recommendations(st.session_state.user_data, st.session_state.api_key)
            st.write(recommendations)
        else:
            st.warning("Please submit your OpenAI API key in the Financial Goals section to get AI-powered recommendations.")

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
    
    # API Key Status in Sidebar
    if hasattr(st.session_state, 'api_key_submitted') and st.session_state.api_key_submitted:
        st.sidebar.success("AI Features: Enabled ✅")
    else:
        st.sidebar.warning("AI Features: Disabled ❌")
    
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.api_key_submitted = False
        if hasattr(st.session_state, 'api_key'):
            del st.session_state.api_key
        st.rerun()
    
    # Page routing
    if page == "Financial Goals":
        render_financial_input()
    elif page == "Dashboard":
        render_dashboard()

if __name__ == "__main__":
    main()
