import streamlit as st
import pandas as pd
from datetime import date

st.title("💰 খরচ ট্র্যাকার")
st.write("**Produced by REDWAN**")

if "data" not in st.session_state:
    st.session_state.data = []

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
        st.session_state.data.append({
            "তারিখ": str(entry_date),
            "ধরন": entry_type,
            "খাত": category,
            "পরিমাণ": amount,
            "নোট": note
        })
        st.success("এন্ট্রি যোগ হয়েছে!")
    else:
        st.error("পরিমাণ দিন!")

if st.session_state.data:
    st.subheader("📊 সারসংক্ষেপ")
    df = pd.DataFrame(st.session_state.data)

    total_income = df[df["ধরন"] == "আয় 💚"]["পরিমাণ"].sum()
    total_expense = df[df["ধরন"] == "খরচ 🔴"]["পরিমাণ"].sum()
    balance = total_income - total_expense

    col1, col2, col3 = st.columns(3)
    col1.metric("মোট আয়", f"৳{total_income:.0f}")
    col2.metric("মোট খরচ", f"৳{total_expense:.0f}")
    col3.metric("ব্যালেন্স", f"৳{balance:.0f}")

    st.subheader("📋 সব এন্ট্রি")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 CSV ডাউনলোড করুন", csv, "expense.csv", "text/csv")
else:
    st.info("এখনো কোনো এন্ট্রি নেই। উপরে যোগ করুন!")
