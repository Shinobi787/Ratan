import streamlit as st
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import plotly.express as px

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

        # Updated prompt for INR
        prompt = f"""
        Based on the following financial data:
        Monthly Income: ₹{financial_data['income']}
        Monthly Expenses: ₹{sum(financial_data['expenses'].values())}
        Current Savings Ratio: {financial_data['savings_ratio']:.1f}%
        Savings Goal: ₹{financial_data['savings_goal']}

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
            else:
                st.error("Invalid email or password")

def render_dashboard():
    """Render financial dashboard"""
    st.title("Financial Dashboard")

    if st.session_state.user_data:
        user_data = st.session_state.user_data

        # Convert income and expenses to INR
        income_inr = user_data['income'] * 82  # Assuming 1 USD = 82 INR
        expenses_inr = {k: v * 82 for k, v in user_data['expenses'].items()}
        savings_goal_inr = user_data['savings_goal'] * 82

        # Pie chart
        labels = list(expenses_inr.keys()) + ["Savings"]
        values = list(expenses_inr.values()) + [income_inr - sum(expenses_inr.values())]

        try:
            fig = px.pie(
                names=labels,
                values=values,
                title="Expense Distribution (INR)",
                hole=0.4
            )
            st.plotly_chart(fig)
        except Exception as e:
            st.error(f"Error rendering pie chart: {str(e)}")

        # Display recommendations
        if st.session_state.api_key_submitted:
            api_key = st.text_input("Enter OpenAI API Key", type="password")
            if api_key:
                recommendations = get_ai_recommendations(user_data, api_key)
                st.subheader("AI Recommendations")
                st.write(recommendations)
        else:
            st.warning("Submit your API key to see recommendations.")
    else:
        st.warning("No user data available. Please log in and enter your details.")

def render_user_input():
    """Capture user input for financial data"""
    st.title("Enter Your Financial Details")

    with st.form("user_input_form"):
        income = st.number_input("Monthly Income (INR)", min_value=0)
        expenses = {}
        for category in ["Rent", "Food", "Transport", "Others"]:
            expenses[category] = st.number_input(f"{category} Expenses (INR)", min_value=0)
        savings_goal = st.number_input("Savings Goal (INR)", min_value=0)
        submit = st.form_submit_button("Submit")

        if submit:
            st.session_state.user_data = {
                "income": income,
                "expenses": expenses,
                "savings_ratio": ((income - sum(expenses.values())) / income) * 100 if income > 0 else 0,
                "savings_goal": savings_goal
            }
            st.success("Financial data saved!")

def main():
    """Main application entry point"""
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Login", "Dashboard", "User Input"])

    if page == "Login":
        render_login()
    elif page == "Dashboard":
        if st.session_state.authenticated:
            render_dashboard()
        else:
            st.warning("Please log in to access the dashboard.")
    elif page == "User Input":
        if st.session_state.authenticated:
            render_user_input()
        else:
            st.warning("Please log in to enter your financial details.")

if __name__ == "__main__":
    main()
