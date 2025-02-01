import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
import openai

# Title and App Description
st.title("Ratan - AI Financial Planner")
st.write("Track your finances and get AI-powered recommendations.")

# Sidebar for Input Options
st.sidebar.header("Input Your Financial Details")

# User Inputs
salary = st.sidebar.number_input("Monthly Salary (in ₹)", min_value=0.0, step=1000.0)
expenses = {}
expense_categories = ["Rent", "Food", "Transport", "Utilities", "Other"]

for category in expense_categories:
    expenses[category] = st.sidebar.number_input(f"{category} Expense (in ₹)", min_value=0.0, step=500.0)

total_expenses = sum(expenses.values())
savings = salary - total_expenses
savings_ratio = (savings / salary * 100) if salary > 0 else 0

st.sidebar.subheader("Set Your Financial Goals")
financial_goal = st.sidebar.text_input("Your Goal (e.g., Buy a Car, Save for House)")
goal_amount = st.sidebar.number_input("Goal Amount (in ₹)", min_value=0.0, step=5000.0)
goal_age = st.sidebar.number_input("Target Age to Achieve Goal", min_value=18, step=1)
current_age = st.sidebar.number_input("Your Current Age", min_value=18, step=1)

time_left = max(goal_age - current_age, 0)
monthly_savings_needed = (goal_amount / (time_left * 12)) if time_left > 0 else 0

if st.sidebar.button("Save Details"):
    st.session_state.financial_data = {
        "salary": salary,
        "expenses": expenses,
        "savings": savings,
        "savings_ratio": savings_ratio,
        "financial_goal": financial_goal,
        "goal_amount": goal_amount,
        "goal_age": goal_age,
        "current_age": current_age,
        "monthly_savings_needed": monthly_savings_needed
    }
    st.sidebar.success("Financial details saved!")

# Display Financial Summary
if "financial_data" in st.session_state:
    st.subheader("Financial Summary")
    data = st.session_state.financial_data
    st.write(f"**Salary:** ₹{data['salary']:.2f}")
    st.write(f"**Total Expenses:** ₹{total_expenses:.2f}")
    st.write(f"**Savings:** ₹{data['savings']:.2f} ({data['savings_ratio']:.1f}%)")
    st.write(f"**Goal:** {data['financial_goal']} (₹{data['goal_amount']:.2f}) by age {data['goal_age']}")
    st.write(f"**Monthly Savings Needed:** ₹{data['monthly_savings_needed']:.2f}")

    # Visualization
    st.subheader("Expense Distribution")
    df = pd.DataFrame(list(data['expenses'].items()), columns=["Category", "Amount"])
    if not df.empty:
        fig = px.pie(df, values="Amount", names="Category", title="Expenses Breakdown (₹)")
        st.plotly_chart(fig)
    else:
        st.write("No expenses recorded yet.")

    # AI Financial Recommendations
    st.subheader("🤖 AI Financial Recommendations")
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    if st.button("Get AI Insights") and api_key:
        openai.api_key = api_key
        prompt = f"""
        I earn ₹{data['salary']} per month and my expenses are ₹{total_expenses}. 
        My savings are ₹{data['savings']} ({data['savings_ratio']:.1f}%). 
        My goal is to save ₹{data['goal_amount']} for {data['financial_goal']} by age {data['goal_age']}. 
        Suggest practical ways to optimize expenses and achieve my goal."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            st.write(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Error generating AI recommendations: {str(e)}")

# Footer
st.write("---")
st.write("Made with ❤️ using Streamlit")
