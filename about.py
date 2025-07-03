import streamlit as st

def tampilkan_tentang_saya():
    st.title("Tentang Saya")
    st.markdown("""
    ### 👋 Halo, saya **I Dewa Nyoman Dharma Santika**

    Saya sedang bekerja sebagai **caregiving** dan pernah bekerja juga sebagai **carpenter** di Jepang ke dunia **Data Science**.  
    Saat ini saya belajar intensif di bootcamp **Dibimbing.id**, dan telah menyelesaikan beberapa proyek analisis & machine learning.

    ---

    ### 🧠 Keahlian & Tools
    - 📊 **Python**, **Pandas**, **Scikit-learn**
    - 📈 Visualisasi: **Matplotlib**, **Seaborn**, **Tableau**
    - 🧮 Machine Learning: **Regresi, Klasifikasi**
    - 💾 Database & ETL: **SQL**
    ---

    ### 🚀 Proyek Sebelum nya
    - Prediksi harga sewa rumah **Ridge Regression**
    - Segmentasi pelanggan hotel (RFM & K-Means)
    - Web scraping villa mewah Bali (Selenium + Tableau)

    ---

    ### 🌐 Kontak Saya
    - 💼 [LinkedIn](https://www.linkedin.com/in/dewanyomandharma)
    - ✉️ Email: dewadharma@gmail.com

    ---
    """)

    st.info("Terima kasih sudah mengunjungi aplikasi saya 🙏")