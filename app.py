import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import date
import pandas as pd
import hashlib

st.title("💰 খরচ ট্র্যাকার")
st.write("**Produced by REDWAN**")

SHEET_ID = "1MX31AC44gXwWBNU9h57Epb8E-hpZJeNoYGVYBXyf14U"

def get_client():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"]
    )
    return gspread.authorize(creds)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_users_sheet():
    client = get_client()
    spreadsheet = client.open_by_key(SHEET_ID)
    try:
        return spreadsheet.worksheet("Users")
    except:
        sheet = spreadsheet.add_worksheet(title="Users", rows=100, cols=3)
        sheet.append_row(["username", "password", "created"])
        return sheet

def get_data_sheet():
    client = get_client()
    spreadsheet = client.open_by_key(SHEET_ID)
    try:
        return spreadsheet.worksheet("Data")
    except:
        sheet = spreadsheet.add_worksheet(title="Data", rows=1000, cols=6)
        sheet.append_row(["username", "তারিখ", "ধরন", "খাত", "পরিমাণ", "নোট"])
        return sheet

def register_user(username, password):
    sheet = get_users_sheet()
    users = sheet.get_all_records()
    for user in users:
        if user["username"] == username:
            return False, "এই নাম আগেই নেওয়া হয়েছে!"
    sheet.append_row([username, hash_password(password), str(date.today())])
    return True, "Registration সফল হয়েছে!"

def login_user(username, password):
    sheet = get_users_sheet()
    users = sheet.get_all_records()
    for user in users:
        if user["username"] == username and user["password"] == hash_password(password):
            return True
    return False

def add_entry(username, entry_type, amount, category, entry_date, note):
    sheet = get_data_sheet()
    sheet.append_row([username, str(entry_date), entry_type, category, amount, note])

def get_user_data(username):
    sheet = get_data_sheet()
    all_data = sheet.get_all_records()
    return [d for d in all_data if d["username"] == username]

def delete_entry(username, row_index):
    sheet = get_data_sheet()
    all_data = sheet.get_all_values()
    actual_row = None
    count = 0
    for i, row in enumerate(all_data[1:], start=2):
        if row[0] == username:
            count += 1
            if count == row_index:
                actual_row = i
                break
    if actual_row:
        sheet.delete_rows(actual_row)
        return True
    return False

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Login / Register
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

    with tab1:
        st.subheader("Login করুন")
        username = st.text_input("Username:", key="login_user")
        password = st.text_input("Password:", type="password", key="login_pass")
        if st.button("Login ✅"):
            if username and password:
                try:
                    if login_user(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.error("Username বা Password ভুল!")
                except Exception as e:
                    st.error(f"সমস্যা: {e}")
            else:
                st.error("সব তথ্য দিন!")

    with tab2:
        st.subheader("নতুন Account বানান")
        new_username = st.text_input("Username:", key="reg_user")
        new_password = st.text_input("Password:", type="password", key="reg_pass")
        confirm_password = st.text_input("Password আবার দিন:", type="password", key="reg_confirm")
        if st.button("Register 📝"):
            if new_username and new_password and confirm_password:
                if new_password != confirm_password:
                    st.error("Password মিলছে না!")
                else:
                    try:
                        success, msg = register_user(new_username, new_password)
                        if success:
                            st.success(msg + " এখন Login করুন!")
                        else:
                            st.error(msg)
                    except Exception as e:
                        st.error(f"সমস্যা: {e}")
            else:
                st.error("সব তথ্য দিন!")

else:
    st.write(f"👋 স্বাগতম, **{st.session_state.username}**!")
    if st.button("Logout 🚪"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.subheader("➕ নতুন এন্ট্রি যোগ করুন")
    col1, col2 = st.columns(2)
    with col1:
        entry_type = st.selectbox("ধরন:", ["আয় 💚", "খরচ 🔴"])
        amount = st.number_input("পরিমাণ (টাকা):", min_value=0.0)
    with col2:
        category = st.selectbox("খাত:", ["খাবার", "যাতায়াত", "ব্যবসা", "শিক্ষা", "বিনোদন", "অন্যান্য"])
        entry_date = st.date_input("তারিখ:", value=date.today())

    note = st.text_input("নোট (ঐচ্ছিক):")

    if st.button("যোগ করুন ✅"):
        if amount > 0:
            try:
                add_entry(st.session_state.username, entry_type, amount, category, entry_date, note)
                st.success("✅ এন্ট্রি সেভ হয়েছে!")
            except Exception as e:
                st.error(f"সমস্যা: {e}")
        else:
            st.error("পরিমাণ দিন!")

    st.subheader("📊 আমার সব এন্ট্রি")
    if st.button("🔄 ডেটা লোড করুন"):
        try:
            data = get_user_data(st.session_state.username)
            if data:
                df = pd.DataFrame(data).drop(columns=["username"])
                total_income = df[df["ধরন"] == "আয় 💚"]["পরিমাণ"].sum()
                total_expense = df[df["ধরন"] == "খরচ 🔴"]["পরিমাণ"].sum()
                balance = total_income - total_expense

                col1, col2, col3 = st.columns(3)
                col1.metric("মোট আয়", f"৳{total_income:.0f}")
                col2.metric("মোট খরচ", f"৳{total_expense:.0f}")
                col3.metric("ব্যালেন্স", f"৳{balance:.0f}")

                st.dataframe(df, use_container_width=True)

                st.subheader("🗑️ এন্ট্রি Delete করুন")
                delete_index = st.number_input("কত নম্বর এন্ট্রি delete করবে?", min_value=1, max_value=len(df), step=1)
                if st.button("Delete 🗑️"):
                    try:
                        if delete_entry(st.session_state.username, delete_index):
                            st.success("✅ Delete হয়েছে! আবার লোড করুন।")
                        else:
                            st.error("Delete হয়নি!")
                    except Exception as e:
                        st.error(f"সমস্যা: {e}")

                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 CSV ডাউনলোড", csv, "expense.csv", "text/csv")
            else:
                st.info("এখনো কোনো এন্ট্রি নেই!")
        except Exception as e:
            st.error(f"সমস্যা: {e}")
