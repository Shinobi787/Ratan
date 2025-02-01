# app.py
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
    
    return "\n\n".join(advice)

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
        
        # Financial Advice
        st.subheader("📊 Financial Analysis & Recommendations")
        advice = generate_financial_advice(st.session_state.user_data)
        st.write(advice)

def main():
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Financial Goals", "Dashboard"]
    )
    
    # Page routing
    if page == "Financial Goals":
        render_financial_input()
    elif page == "Dashboard":
        render_dashboard()

if __name__ == "__main__":
    main()