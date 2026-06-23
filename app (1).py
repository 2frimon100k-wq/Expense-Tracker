import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import date
import pandas as pd

st.title("💰 খরচ ট্র্যাকার")
st.write("**Produced by REDWAN**")

SHEET_ID = "1MX31AC44gXwWBNU9h57Epb8E-hpZJeNoYGVYBXyf14U"

def get_sheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1
    return sheet

def init_sheet(sheet):
    if sheet.row_count == 0 or sheet.cell(1, 1).value is None:
        sheet.append_row(["তারিখ", "ধরন", "খাত", "পরিমাণ", "নোট"])

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
            sheet = get_sheet()
            init_sheet(sheet)
            sheet.append_row([str(entry_date), entry_type, category, amount, note])
            st.success("✅ এন্ট্রি Google Sheets এ সেভ হয়েছে!")
        except Exception as e:
            st.error(f"সমস্যা হয়েছে: {e}")
    else:
        st.error("পরিমাণ দিন!")

st.subheader("📊 সব এন্ট্রি দেখুন")

if st.button("🔄 ডেটা লোড করুন"):
    try:
        sheet = get_sheet()
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            total_income = df[df["ধরন"] == "আয় 💚"]["পরিমাণ"].sum()
            total_expense = df[df["ধরন"] == "খরচ 🔴"]["পরিমাণ"].sum()
            balance = total_income - total_expense

            col1, col2, col3 = st.columns(3)
            col1.metric("মোট আয়", f"৳{total_income:.0f}")
            col2.metric("মোট খরচ", f"৳{total_expense:.0f}")
            col3.metric("ব্যালেন্স", f"৳{balance:.0f}")

            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 CSV ডাউনলোড", csv, "expense.csv", "text/csv")
        else:
            st.info("এখনো কোনো এন্ট্রি নেই!")
    except Exception as e:
        st.error(f"সমস্যা হয়েছে: {e}")
