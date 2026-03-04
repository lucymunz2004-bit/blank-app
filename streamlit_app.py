import streamlit as st

email = st.text_input("Gib deine E-Mail-Adresse ein:")

if email:
    with open("Gedankenchaos.pdf", "rb") as file:
        st.download_button(
            label="📥 Download starten",
            data=file,
            file_name="Gedankenchaos.pdf",
            mime="application/pdf"
        )




