import streamlit as st
import joblib
import numpy as np
import pandas as pd
from category_encoders import TargetEncoder
import datetime

# Load model dan kolom
try:
    model = joblib.load("xgboost_model.joblib")
    model_columns = joblib.load("model_columns.joblib")
    target_encoder = joblib.load("target_encoder.joblib")
except FileNotFoundError:
    st.error("File model atau encoder tidak ditemukan. Pastikan file 'xgboost_model.joblib', 'model_columns.joblib', dan 'target_encoder.joblib' berada di direktori yang sama.")
    st.stop()

def prediksi_adr(input_df):
    # 1. Hotel
    input_df['hotel_Resort Hotel'] = (input_df['hotel'] == 'Resort Hotel').astype(int)
    input_df = input_df.drop('hotel', axis=1) 

    # 2. Meal
    for meal_type_val in ['FB', 'HB', 'SC', 'Undefined']:
        input_df[f'meal_{meal_type_val}'] = (input_df['meal'] == meal_type_val).astype(int)
    input_df = input_df.drop('meal', axis=1) 

    # 3. Distribution Channel
    for channel_type_val in ['Direct', 'GDS', 'TA/TO', 'Undefined']:
        input_df[f'distribution_channel_{channel_type_val}'] = (input_df['distribution_channel'] == channel_type_val).astype(int)
    input_df = input_df.drop('distribution_channel', axis=1) 

    # 4. Deposit Type
    for deposit_type_val in ['Non Refund', 'Refundable']:
        input_df[f'deposit_type_{deposit_type_val}'] = (input_df['deposit_type'] == deposit_type_val).astype(int)
    input_df = input_df.drop('deposit_type', axis=1) 

    # 5. Customer Type
    for customer_type_val in ['Group', 'Transient', 'Transient-Party']:
        input_df[f'customer_type_{customer_type_val}'] = (input_df['customer_type'] == customer_type_val).astype(int)
    input_df = input_df.drop('customer_type', axis=1) 

    # Ordinal Encoding untuk 'arrival_day_of_week'
    ordinal_map = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4,
                   "Friday": 5, "Saturday": 6, "Sunday": 7}
    if "arrival_day_of_week" in input_df.columns:
        input_df["arrival_day_of_week"] = input_df["arrival_day_of_week"].map(ordinal_map)
    
    # Target Encoding
    cols_to_target_encode = ["country", "market_segment", "reserved_room_type", "assigned_room_type"]
    df_to_encode = input_df[cols_to_target_encode]
    target_encoded_data = target_encoder.transform(df_to_encode)
    input_df[cols_to_target_encode] = target_encoded_data

    # Reindex agar sama dengan saat training
    input_df = input_df.reindex(columns=model_columns, fill_value=0)
    
    log_result = model.predict(input_df)[0]
    hasil = np.expm1(log_result)
    return hasil


def tampilkan_prediksi():
    st.title("🏷️ Prediksi Harga Kamar Hotel")

    st.header("Input Data Pemesanan Hotel")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("> Detail Umum Pemesanan")
        hotel = st.selectbox("Tipe Hotel", ["City Hotel", "Resort Hotel"], key="hotel_type")
        is_canceled = st.radio("Status Pembatalan", ["Tidak Dibatalkan", "Dibatalkan"], key="is_canceled_radio")
        lead_time = st.number_input("Lead Time (hari sebelum check-in)", min_value=0, value=30, max_value=709, key="lead_time_input")
        
        st.subheader("> Detail Tamu")
        adults = st.number_input("Jumlah Dewasa", min_value=1, value=2, key="adults_input")
        children = st.number_input("Jumlah Anak-anak", min_value=0, value=0, key="children_input")
        babies = st.number_input("Jumlah Bayi", min_value=0, value=0, key="babies_input")
        is_repeated_guest = st.radio("Tamu yang Sama?", ["Ya", "Bukan"], key="repeated_guest_radio")
        previous_bookings_not_canceled = st.number_input("Booking Lalu (tidak dibatalkan)", 0, 50, 0, key="prev_bookings_input")
        previous_cancellations = st.number_input("Jumlah Pembatalan Sebelumnya", min_value=0, value=0, max_value=26, key="prev_cancellations_input")
        country = st.text_input("Negara (Kode 3 huruf)", "IDN", max_chars=3).upper()

        st.subheader("> Informasi Tambahan")
        required_car_parking_spaces = st.radio("Butuh Tempat Parkir?", ["Ya", "Tidak"], key="parking_radio")
        total_of_special_requests = st.slider("Jumlah Permintaan Khusus", 0, 5, 0, key="special_requests_slider")

    with col2:
        st.subheader("> Detail Kedatangan & Menginap")
        arrival_date_month = st.selectbox("Bulan Kedatangan", list(range(1, 13)), key="arrival_month_select")
        arrival_date_day_of_month = st.slider("Tanggal Kedatangan", 1, 31, 15, key="arrival_day_slider")
        arrival_day_of_week = st.selectbox("Hari Kedatangan", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], key="day_of_week_select")
        stays_in_weekend_nights = st.slider("Jumlah Malam di Akhir Pekan", 0, 7, 1, key="weekend_nights_slider")
        stays_in_week_nights = st.slider("Jumlah Malam di Hari Kerja", 0, 14, 2, key="weekday_nights_slider")
        
        st.subheader("> Detail Kamar & Layanan")
        meal = st.selectbox("Meal Type", ['BB', 'SC', 'HB', 'Undefined', 'FB'], key="meal_type_select")
        reserved_room_type = st.selectbox("Tipe Kamar yang Dipesan", ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'L'], key="reserved_room_select")  
        assigned_room_type = st.selectbox("Tipe Kamar yang Diberikan", ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L'], key="assigned_room_select")
        booking_changes = st.number_input("Jumlah Perubahan Booking", 0, 20, 0, key="booking_changes_input")
        
        st.subheader("> Detail Pembayaran & Distribusi")
        market_segment = st.selectbox("Jenis Customer", ['Online TA', 'Offline TA/TO', 'Direct', 'Groups', 'Corporate', 'Complementary', 'Aviation', 'Undefined'], key="market_segment_select_2") 
        distribution_channel = st.selectbox("Distribution Channel", ['TA/TO', 'Direct', 'Corporate', 'GDS', 'Undefined'], key="distribution_channel_select")
        deposit_type = st.selectbox("Tipe Deposit", ["No Deposit", "Non Refund", "Refundable"], key="deposit_type_select")
        customer_type = st.selectbox("Tipe Customer", ["Transient", "Transient-Party", "Contract", "Group"], key="customer_type_select")
        
        agent = st.number_input("ID Agen (0 jika tidak ada)", min_value=0, value=0, max_value=535, key="agent_id_input")
        days_in_waiting_list = st.number_input("Hari dalam Daftar Tunggu", min_value=0, value=0, max_value=391, key="waiting_list_input")


    input_dict = {
        "hotel": hotel,
        "is_canceled": 1 if is_canceled == "Dibatalkan" else 0,
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
        "is_repeated_guest": 1 if is_repeated_guest == "Ya" else 0,
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
        "required_car_parking_spaces": 1 if required_car_parking_spaces == "Ya" else 0,
        "total_of_special_requests": total_of_special_requests,
        "arrival_month": arrival_date_month, 
    }

    if st.button("Prediksi Harga Kamar", key="predict_button"):
        if len(country) != 3 or not country.isalpha():
            st.error("Kode negara harus 3 huruf (misal: IDN untuk Indonesia).")
            st.stop()

        try:
            arrival_date_obj = datetime.date(2023, arrival_date_month, arrival_date_day_of_month)
            input_dict["arrival_week"] = arrival_date_obj.isocalendar()[1]
        except ValueError:
            st.error(f"Tanggal kedatangan tidak valid untuk bulan {arrival_date_month} dan tanggal {arrival_date_day_of_month}. Mohon periksa kembali tanggal dan bulan.")
            st.stop()
            
        input_df = pd.DataFrame([input_dict])

        hasil = prediksi_adr(input_df)
        st.success(f"💰 Harga Kamar yang Diprediksi (ADR): ${hasil:.2f}")
        st.info("Catatan: Hasil ini hanya perkiraan berdasarkan model yang telah dilatih. Harga sebenarnya dapat bervariasi tergantung faktor lain.")

# Panggil fungsi utama Streamlit
tampilkan_prediksi()