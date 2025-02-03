import streamlit as st
import pandas as pd
import plotly.express as px
import openai
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_credentials.json")  # Upload your Firebase credentials
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Authentication Functions
def register_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        db.collection("users").document(user.uid).set({"email": email, "approved": False})
        return "Registration successful. Waiting for admin approval."
    except Exception as e:
        return str(e)

def login_user(email, password):
    try:
        user = auth.get_user_by_email(email)
        doc = db.collection("users").document(user.uid).get()
        if doc.exists and doc.to_dict().get("approved"):
            st.session_state["user_id"] = user.uid
            return True
        else:
            return "Account not approved yet."
    except Exception as e:
        return str(e)

# Authentication UI
st.sidebar.title("Login / Register")
user_email = st.sidebar.text_input("Email")
user_password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    login_status = login_user(user_email, user_password)
    if login_status is True:
        st.sidebar.success("Login successful!")
        st.session_state["authenticated"] = True
    else:
        st.sidebar.error(login_status)

if st.sidebar.button("Register"):
    reg_status = register_user(user_email, user_password)
    st.sidebar.info(reg_status)

# Navigation Based on Authentication
menu = st.sidebar.radio("Select a section", ["Calculators", "Financial Planning", "Expense Dashboard"])

if menu == "Calculators":
    st.subheader("Financial Calculators")
    calc_type = st.selectbox("Select a Calculator", ["Inflation Calculator", "Fixed Deposit Calculator", "SIP Calculator"])

    if calc_type == "Inflation Calculator":
        amount = st.number_input("Initial Amount (₹)", min_value=0.0)
        years = st.number_input("Years", min_value=1, max_value=30, step=1)
        inflation_rate = st.slider("Inflation Rate (%)", min_value=0.0, max_value=30.0, step=0.5)
        future_value = amount * ((1 + inflation_rate / 100) ** years)
        st.write(f"Future Value: ₹{future_value:.2f}")

    elif calc_type == "Fixed Deposit Calculator":
        principal = st.number_input("Principal Amount (₹)", min_value=0.0)
        rate = st.slider("Annual Interest Rate (%)", min_value=0.0, max_value=30.0, step=0.5)
        years = st.number_input("Years", min_value=1, max_value=30, step=1)
        maturity_value = principal * ((1 + rate / 100) ** years)
        st.write(f"Maturity Value: ₹{maturity_value:.2f}")

    elif calc_type == "SIP Calculator":
        monthly_investment = st.number_input("Monthly Investment (₹)", min_value=0.0)
        rate = st.slider("Expected Return Rate (%)", min_value=0.0, max_value=30.0, step=0.5)
        years = st.number_input("Years", min_value=1, max_value=30, step=1)
        months = years * 12
        future_value = monthly_investment * (((1 + (rate / 100) / 12) ** months - 1) / ((rate / 100) / 12)) * (1 + (rate / 100) / 12)
        st.write(f"Future Value: ₹{future_value:.2f}")

elif menu in ["Financial Planning", "Expense Dashboard"] and not st.session_state.get("authenticated"):
    st.warning("Please log in to access this section.")

elif menu == "Financial Planning":
    st.subheader("Financial Planning")
    salary = st.number_input("Enter Monthly Salary (₹)", min_value=0.0, step=1000.0)
    expenses = {}
    expense_categories = ["Rent", "Food", "Transport", "Utilities", "Other"]
    for category in expense_categories:
        expenses[category] = st.number_input(f"{category} Expense (₹)", min_value=0.0, step=500.0)
    
    total_expenses = sum(expenses.values())
    savings = salary - total_expenses
    savings_ratio = (savings / salary * 100) if salary > 0 else 0
    st.write(f"Total Savings: ₹{savings:.2f} ({savings_ratio:.1f}%)")

elif menu == "Expense Dashboard":
    st.subheader("Expense Journaling & Tracking")
    daily_expense = st.number_input("Enter Today's Expense (₹)", min_value=0.0)
    if st.button("Save Expense"):
        st.success("Expense recorded successfully!")

# Footer
st.write("---")
st.write("Made with ❤️")
