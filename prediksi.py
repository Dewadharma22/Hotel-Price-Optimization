import streamlit as st
import joblib
import numpy as np
import pandas as pd
from category_encoders import TargetEncoder
import datetime

# Load model dan file pendukung dengan penanganan error
try:
    model = joblib.load("xgboost_model.joblib")
    model_columns = joblib.load("model_columns.joblib")
    target_encoder = joblib.load("target_encoder.joblib")
except FileNotFoundError:
    st.error("File model atau encoder tidak ditemukan. Pastikan file 'xgboost_model.joblib', 'model_columns.joblib', dan 'target_encoder.joblib' berada di direktori yang sama.")
    st.stop()
except Exception as e:
    st.error(f"Terjadi kesalahan saat memuat model atau encoder: {e}")
    st.stop()

def prediksi_adr(input_df):
    """
    Fungsi ini melakukan pra-pemrosesan pada data input agar sesuai
    dengan format yang digunakan saat training model, lalu melakukan prediksi.
    """
    # 1. Hotel (One-Hot Encoding Manual)
    input_df['hotel_Resort Hotel'] = (input_df['hotel'] == 'Resort Hotel').astype(int)
    input_df = input_df.drop('hotel', axis=1) 

    # 2. Meal (One-Hot Encoding Manual)
    for meal_type_val in ['FB', 'HB', 'SC', 'Undefined']:
        input_df[f'meal_{meal_type_val}'] = (input_df['meal'] == meal_type_val).astype(int)
    input_df = input_df.drop('meal', axis=1) 

    # 3. Distribution Channel (One-Hot Encoding Manual)
    for channel_type_val in ['Direct', 'GDS', 'TA/TO', 'Undefined']:
        input_df[f'distribution_channel_{channel_type_val}'] = (input_df['distribution_channel'] == channel_type_val).astype(int)
    input_df = input_df.drop('distribution_channel', axis=1) 

    # 4. Deposit Type (One-Hot Encoding Manual)
    for deposit_type_val in ['Non Refund', 'Refundable']:
        input_df[f'deposit_type_{deposit_type_val}'] = (input_df['deposit_type'] == deposit_type_val).astype(int)
    input_df = input_df.drop('deposit_type', axis=1) 

    # 5. Customer Type (One-Hot Encoding Manual)
    for customer_type_val in ['Group', 'Transient', 'Transient-Party']:
        input_df[f'customer_type_{customer_type_val}'] = (input_df['customer_type'] == customer_type_val).astype(int)
    input_df = input_df.drop('customer_type', axis=1) 

    # 6. Ordinal Encoding untuk 'arrival_day_of_week'
    ordinal_map = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4,
                   "Friday": 5, "Saturday": 6, "Sunday": 7}
    if "arrival_day_of_week" in input_df.columns:
        input_df["arrival_day_of_week"] = input_df["arrival_day_of_week"].map(ordinal_map)
    
    # 7. Target Encoding untuk kolom kategorikal lainnya
    cols_to_target_encode = ["country", "market_segment", "reserved_room_type", "assigned_room_type"]
    # Memastikan kolom ada sebelum encoding
    cols_to_encode_present = [col for col in cols_to_target_encode if col in input_df.columns]
    if cols_to_encode_present:
        target_encoded_data = target_encoder.transform(input_df[cols_to_encode_present])
        input_df[cols_to_encode_present] = target_encoded_data

    # 8. Reindex agar kolom sesuai dengan model training
    # Ini adalah langkah krusial untuk memastikan konsistensi fitur
    input_df = input_df.reindex(columns=model_columns, fill_value=0)
    
    # Lakukan prediksi dan kembalikan hasil
    log_result = model.predict(input_df)[0]
    hasil = np.expm1(log_result)
    return hasil


def tampilkan_prediksi():
    """
    Fungsi untuk menampilkan antarmuka pengguna Streamlit dan menangani input.
    """
    st.title("🏨 Prediksi Harga Kamar Hotel (ADR)")
    st.markdown("""
        Selamat datang di aplikasi **Prediksi Harga Kamar Hotel (ADR)**!
        Aplikasi ini membantu Anda memperkirakan *Average Daily Rate* (ADR) untuk pemesanan hotel
        berdasarkan berbagai detail pemesanan. Masukkan informasi di bawah ini untuk mendapatkan prediksi.
    """)

    with st.form("Input Data Pemesanan Hotel", clear_on_submit=False):
        
        # Section 1: Detail Umum Pemesanan & Tamu
        st.header("📝 Detail Pemesanan Umum")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Hotel & Status")
            hotel = st.selectbox("Tipe Hotel", ["City Hotel", "Resort Hotel"], key="hotel_type_v2")
            is_canceled = st.toggle("Pemesanan Dibatalkan?", value=False, help="Aktifkan jika pemesanan ini dibatalkan.", key="is_canceled_toggle")
            lead_time = st.slider("Lead Time (hari sebelum check-in)", min_value=0, max_value=709, value=30, help="Jumlah hari antara tanggal pemesanan dan tanggal kedatangan.", key="lead_time_input_v2")

        with col2:
            st.subheader("Detail Tamu")
            adults = st.number_input("Jumlah Dewasa", min_value=1, value=2, max_value=10, key="adults_input_v2")
            children = st.number_input("Jumlah Anak-anak", min_value=0, value=0, max_value=3, key="children_input_v2")
            babies = st.number_input("Jumlah Bayi", min_value=0, value=0, max_value=2, key="babies_input_v2")
            is_repeated_guest = st.toggle("Tamu Berulang?", value=False, help="Aktifkan jika ini adalah tamu yang pernah menginap sebelumnya.", key="repeated_guest_toggle")

        with col3:
            st.subheader("Riwayat & Negara")
            previous_bookings_not_canceled = st.number_input("Jumlah Pemesanan Sebelumnya (tidak dibatalkan)", min_value=0, value=0, max_value=50, key="prev_bookings_input_v2")
            previous_cancellations = st.number_input("Jumlah Pembatalan Sebelumnya", min_value=0, value=0, max_value=26, key="prev_cancellations_input_v2")
            country = st.text_input("Negara Tamu (Kode 3 huruf, misal: IDN)", "IDN", max_chars=3, help="Gunakan kode negara ISO 3 huruf.", key="country_input_v2").upper()

        st.markdown("---") 

        # Section 2: Kedatangan, Menginap & Permintaan Khusus
        st.header("📅 Detail Kedatangan & Menginap")
        col4, col5 = st.columns(2)
        with col4:
            st.subheader("Tanggal Kedatangan")
            arrival_date_month = st.selectbox("Bulan Kedatangan", list(range(1, 13)), key="arrival_month_select")
            arrival_date_day_of_month = st.slider("Tanggal Kedatangan", 1, 31, 15, key="arrival_day_slider")
            arrival_day_of_week = st.selectbox("Hari Dalam Minggu Kedatangan", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], key="day_of_week_select_v2")

        with col5:
            st.subheader("Durasi Menginap & Permintaan")
            stays_in_weekend_nights = st.slider("Jumlah Malam di Akhir Pekan", min_value=0, max_value=7, value=1, help="Jumlah malam menginap pada hari Sabtu atau Minggu.", key="weekend_nights_slider_v2")
            stays_in_week_nights = st.slider("Jumlah Malam di Hari Kerja", min_value=0, max_value=14, value=2, help="Jumlah malam menginap dari Senin hingga Jumat.", key="weekday_nights_slider_v2")
            total_of_special_requests = st.slider("Jumlah Permintaan Khusus", min_value=0, max_value=5, value=0, help="Misalnya, kamar dengan pemandangan tertentu, ranjang bayi.", key="special_requests_slider_v2")
            required_car_parking_spaces = st.toggle("Butuh Tempat Parkir?", value=False, key="parking_toggle")
            
        st.markdown("---") # Separator

        # Section 3: Kamar, Layanan & Pembayaran
        st.header("🔑 Detail Kamar, Layanan & Pembayaran")
        col6, col7 = st.columns(2)
        with col6:
            st.subheader("Detail Kamar & Lain-lain")
            meal = st.selectbox("Tipe Makanan (Meal Type)", ['BB', 'SC', 'HB', 'Undefined', 'FB'], help="BB: Bed & Breakfast, HB: Half Board, FB: Full Board, SC: Self-catering.", key="meal_type_select_v2")
            reserved_room_type = st.selectbox("Tipe Kamar yang Dipesan", ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'L'], key="reserved_room_select_v2")
            assigned_room_type = st.selectbox("Tipe Kamar yang Diberikan", ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L'], help="Tipe kamar yang benar-benar diberikan kepada tamu.", key="assigned_room_select_v2")
            booking_changes = st.number_input("Jumlah Perubahan Booking", min_value=0, value=0, max_value=20, help="Berapa kali pemesanan diubah.", key="booking_changes_input_v2")

        with col7:
            st.subheader("Distribusi & Keuangan")
            market_segment = st.selectbox("Segmen Pasar", ['Online TA', 'Offline TA/TO', 'Direct', 'Groups', 'Corporate', 'Complementary', 'Aviation', 'Undefined'], help="Bagian pasar dari mana pemesanan berasal.", key="market_segment_select_v2")
            distribution_channel = st.selectbox("Saluran Distribusi", ['TA/TO', 'Direct', 'Corporate', 'GDS', 'Undefined'], help="Saluran distribusi pemesanan.", key="distribution_channel_select_v2")
            deposit_type = st.selectbox("Tipe Deposit", ["No Deposit", "Non Refund", "Refundable"], key="deposit_type_select_v2")
            customer_type = st.selectbox("Tipe Customer", ["Transient", "Transient-Party", "Contract", "Group"], key="customer_type_select_v2")
            agent = st.number_input("ID Agen (0 jika tidak ada)", min_value=0, value=0, max_value=535, help="Identifikasi agen perjalanan yang membuat atau mengelola pemesanan.", key="agent_id_input_v2")
            days_in_waiting_list = st.number_input("Hari dalam Daftar Tunggu", min_value=0, value=0, max_value=391, help="Jumlah hari pemesanan berada dalam daftar tunggu sebelum dikonfirmasi.", key="waiting_list_input_v2")

        st.markdown("---") # Separator
        
        # Tombol Submit Form di bagian bawah
        col_submit = st.columns(3)
        with col_submit[1]: # Center the button
            submitted = st.form_submit_button("🚀 Prediksi Harga Kamar Sekarang!")

        if submitted:
            # Validasi input sebelum prediksi
            if len(country) != 3 or not country.isalpha():
                st.error("❌ Kode negara harus terdiri dari 3 huruf (misal: IDN untuk Indonesia).")
                st.stop()
            
            if adults == 0 and children == 0 and babies == 0:
                st.warning("⚠️ Jumlah tamu (dewasa/anak/bayi) minimal harus 1.")
                st.stop()

            # Buat dictionary dari semua input
            input_dict = {
                "hotel": hotel,
                "is_canceled": 1 if is_canceled else 0,
                "lead_time": lead_time,
                "arrival_date_month": arrival_date_month,
                "arrival_date_day_of_month": arrival_date_day_of_month,
                "stays_in_weekend_nights": stays_in_weekend_nights,
                "stays_in_week_nights": stays_in_week_nights,
                "adults": adults,
                "children": children,
                "babies": babies,
                "country": country,
                "market_segment": market_segment,
                "is_repeated_guest": 1 if is_repeated_guest else 0,
                "previous_cancellations": previous_cancellations,
                "previous_bookings_not_canceled": previous_bookings_not_canceled,
                "reserved_room_type": reserved_room_type,
                "assigned_room_type": assigned_room_type,
                "booking_changes": booking_changes,
                "agent": agent,
                "days_in_waiting_list": days_in_waiting_list,
                "distribution_channel": distribution_channel,
                "deposit_type": deposit_type,
                "customer_type": customer_type,
                "arrival_day_of_week": arrival_day_of_week,
                "meal": meal,
                "required_car_parking_spaces": 1 if required_car_parking_spaces else 0,
                "total_of_special_requests": total_of_special_requests,
                "arrival_month": arrival_date_month
            }
            
            # Buat DataFrame dari dictionary
            input_df = pd.DataFrame([input_dict])

            # Panggil fungsi prediksi
            with st.spinner('Sedang memprediksi harga kamar...'):
                try:
                    hasil = prediksi_adr(input_df)
                    # Tampilkan hasil
                    st.success(f"🎉 **Harga Kamar yang Diprediksi (ADR): $ {hasil:,.2f}**")
                    st.info("💡 Catatan: Hasil ini hanyalah perkiraan berdasarkan model yang telah dilatih. Harga sebenarnya dapat bervariasi tergantung faktor lain seperti dinamika pasar, promosi khusus, dan kebijakan hotel.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat melakukan prediksi: {e}")