import streamlit as st

st.title("Hello from Streamlit!")

name = st.text_input("Enter your name")
if name:
    st.write(f"Welcome, {name}!")
