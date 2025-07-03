import streamlit as st
st.set_page_config(layout="wide")
st.image("Hotel-Room-Banner.jpg", use_container_width=True)
st.title("Hotel Pricing Optimization App")

st.markdown("""
Selamat datang di aplikasi prediksi harga kamar hotel!  
Aplikasi ini menggunakan model machine learning untuk memprediksi **Average Daily Rate (ADR)** berdasarkan input data pemesanan hotel.
""")

# Tab Navigasi di Atas
tab1, tab2, tab3 = st.tabs(["🏷️ Prediksi Harga", "📊 EDA", "🧑 Tentang Saya"])

# Prediksi Harga
with tab1:
    import prediksi
    prediksi.tampilkan_prediksi()

# EDA
with tab2:
    import eda
    eda.tampilkan_eda()

# Tentang Saya
with tab3:
    import about
    about.tampilkan_tentang_saya()