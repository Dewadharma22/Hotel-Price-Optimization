import streamlit as st

def tampilkan_tentang_saya():
    # --- Header Section ---
    st.title("👨‍💻 Tentang Saya")
    st.markdown("""
        <div style="text-align: center;">
            <p style="font-size: 24px;">👋 Halo, saya <b>I Dewa Nyoman Dharma Santika</b></p>
            <p style="font-size: 18px; color: #888;">
                Dari dunia <b>caregiving</b> dan <b>carpenter</b> di Jepang, kini saya bertransformasi ke dunia <b>Data Science</b>!
            </p>
            <p style="font-size: 18px; color: #888;">
                Saat ini saya fokus belajar intensif di bootcamp <b>Dibimbing.id</b>, dan telah menyelesaikan beberapa proyek analisis data & machine learning yang menarik.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- Skills Section ---
    st.header("💡 Keahlian & Tools")
    st.markdown("""
    Saya memiliki pengalaman dan keahlian dalam berbagai tools dan teknik yang relevan dengan Data Science:
    * 📊 **Pemrograman & Analisis Data:**
        * **Python:** Pandas, NumPy, Scikit-learn
    * 📈 **Visualisasi Data:**
        * Matplotlib, Seaborn, Tableau
    * 🧠 **Machine Learning:**
        * Regresi (Ridge, Lasso), Klasifikasi (Logistic Regression, Decision Trees, Random Forests), 
          Clustering (K-Means, Hierarchical Clustering)
    * 💾 **Manajemen & Transformasi Data:**
        * Database & ETL (Extract, Transform, Load) dengan **SQL**
    """)
    
    st.markdown("---")

    # --- Projects Section ---
    st.header("🚀 Proyek Pilihan")
    st.markdown("""
    Berikut adalah beberapa proyek yang telah saya kerjakan:
    * **Prediksi Harga Sewa Rumah:** Menggunakan model **Ridge Regression** untuk memprediksi harga properti.
    * **Segmentasi Pelanggan Hotel:** Menganalisis data pelanggan hotel menggunakan teknik **RFM (Recency, Frequency, Monetary)** dan algoritma **K-Means Clustering** untuk segmentasi yang lebih baik.
    * **Web Scraping Villa Mewah Bali:** Mengumpulkan data villa mewah di Bali menggunakan **Selenium** untuk *web scraping* dan menganalisisnya dengan **Tableau** untuk insight bisnis.
    """)

    st.markdown("---") 

    # --- Contact Section ---
    st.header("🌐 Hubungi Saya")
    st.markdown("""
    Jangan ragu untuk terhubung dengan saya!
    * 💼 **LinkedIn:** [I Dewa Nyoman Dharma Santika](https://www.linkedin.com/in/dewanyomandharma)
    * 📧 **Email:** [dewadharma@gmail.com](mailto:dewadharma@gmail.com)
    * 🌐 **GitHub:** [dewadharma](https://github.com/Dewadharma22)
    """)
    
    st.markdown("---") 
    
    st.info("✨ Terima kasih telah berkunjung ke halaman portofolio saya! Saya menantikan kesempatan untuk berkolaborasi. 🙏")