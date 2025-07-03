import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import calendar

@st.cache_data
def load_data():
    """Memuat data dari CSV dan mengembalikan DataFrame."""
    df = pd.read_csv("hotel_booking_demand_cleaned.csv")
    return df

def tampilkan_eda():
    st.title("📊 Exploratory Data Analysis (EDA)")
    st.markdown("Visualisasi data untuk memahami tren dan pola dalam pemesanan hotel.")

    # Load Data
    df = load_data()
    
    st.sidebar.header("Filter Data")
    
    # Tipe Hotel
    hotel_options = ["All"] + list(df['hotel'].unique())
    selected_hotel = st.sidebar.multiselect("Tipe Hotel", hotel_options, default=["All"])
    hotel_filter = df['hotel'].unique() if "All" in selected_hotel else selected_hotel

    # Status Pembatalan
    cancel_map = {0: "Tidak Dibatalkan", 1: "Dibatalkan"}
    cancel_options_display = ["All"] + list(cancel_map.values())
    selected_cancel_display = st.sidebar.multiselect("Status Pembatalan", cancel_options_display, default=["All"])
    # Mengkonversi kembali label yang dipilih ke nilai numerik 0/1 untuk filtering
    cancel_filter_raw = [k for k, v in cancel_map.items() if v in selected_cancel_display]
    cancel_filter = df['is_canceled'].unique() if "All" in selected_cancel_display else cancel_filter_raw

    # Segment Pasar
    segment_options = ["All"] + list(df['market_segment'].unique())
    selected_segment = st.sidebar.multiselect("Segment Pasar", segment_options, default=["All"])
    segment_filter = df['market_segment'].unique() if "All" in selected_segment else selected_segment

    # Tipe Customer
    customer_options = ["All"] + list(df['customer_type'].unique())
    selected_customer = st.sidebar.multiselect("Tipe Customer", customer_options, default=["All"])
    customer_filter = df['customer_type'].unique() if "All" in selected_customer else selected_customer

    # Hari Kedatangan
    day_options = ["All"] + list(df['arrival_day_of_week'].unique())
    selected_day = st.sidebar.multiselect("Hari Kedatangan", day_options, default=["All"])
    day_filter = df['arrival_day_of_week'].unique() if "All" in selected_day else selected_day

    # Bulan Kedatangan
    month_options_numeric = sorted(df['arrival_month'].unique())
    # Membuat daftar nama bulan untuk tampilan
    month_names = ["All"] + [calendar.month_name[m] for m in month_options_numeric]
    selected_month_name = st.sidebar.multiselect("Bulan Kedatangan", month_names, default=["All"])
    
    # Mengkonversi kembali nama bulan yang dipilih ke angka bulan
    if "All" in selected_month_name:
        month_filter = month_options_numeric
    else:
        month_filter = [list(calendar.month_name).index(name) for name in selected_month_name]


    # Apply Filters
    filtered_df = df[
        (df['hotel'].isin(hotel_filter)) &
        (df['is_canceled'].isin(cancel_filter)) &
        (df['market_segment'].isin(segment_filter)) &
        (df['customer_type'].isin(customer_filter)) &
        (df['arrival_day_of_week'].isin(day_filter)) &
        (df['arrival_month'].isin(month_filter))
    ]

    col1, col2 = st.columns(2)
    with col1:
        # Visualisasi 1: ADR per Bulan
        st.subheader("📅 Rata-rata Harga Kamar (ADR) per Bulan")
        adr_month = filtered_df.groupby('arrival_month')['adr'].mean().reset_index()
        all_months = pd.DataFrame({'arrival_month': range(1, 13)})
        adr_month = pd.merge(all_months, adr_month, on='arrival_month', how='left').fillna(0) 

        # Mapping angka bulan ke nama bulan
        adr_month['arrival_month_name'] = adr_month['arrival_month'].apply(lambda x: calendar.month_abbr[x] if x != 0 else '')

        fig1, ax1 = plt.subplots(figsize=(10, 5))
        ax1.plot(adr_month['arrival_month_name'], adr_month['adr'], marker='o')
        ax1.set_title("Rata-rata ADR per Bulan")
        ax1.set_xlabel("Bulan Kedatangan") 
        ax1.set_ylabel("Rata-rata ADR") 
        ax1.tick_params(axis='x', rotation=45) 

        for i, v in enumerate(adr_month['adr'].values):
            if v > 0: 
                ax1.text(i, v + 1, str(round(v)), ha='center')
        st.pyplot(fig1)
        plt.close(fig1) 

        # tambahkan insight
        with st.expander("Insight"):
            st.markdown("""
            - **Puncak ADR**: Terjadi pada bulan-bulan tertentu, kemungkinan karena musim liburan atau acara khusus. (Cek grafik Anda, misalnya 'Agustus')
            - **Penurunan ADR**: Terlihat pada bulan-bulan tertentu penurunan yang signifikan, mungkin karena penurunan permintaan. (Cek grafik Anda)
            """)

        # Visualisasi 3: ADR per Segment
        st.subheader("📊 Rata-rata ADR per Segmen Pasar")
        fig3, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(x='market_segment', y='adr', data=filtered_df, ax=ax, ci=None, estimator='mean', palette='Set2')

        for p in ax.patches:
            height = p.get_height()
            if height > 0:
                ax.annotate(f'{height:.0f}', 
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom', fontsize=11)

        ax.set_title("Rata-rata ADR per Segmen Pasar")
        ax.set_xlabel("Segmen Pasar") 
        ax.set_ylabel("Rata-rata ADR") 
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right') 
        st.pyplot(fig3)
        plt.close(fig3)
        
        # tambahkan insight
        with st.expander("Insight"):
            st.markdown("""
            - **Segmentasi Terbaik**: Online TA (Tour Agent) dan Direct memiliki rata-rata harga kamar (adr) tertinggi.
            - **Segmentasi Terendah**: Complementary memiliki rata-rata harga kamar (adr) terendah kemungkinan karena biasanya diskon '100%' dari pihak hotel.
            """)

    with col2:
        # Visualisasi 2: ADR per Hari
        st.subheader("🗓️ Rata-rata ADR per Hari dalam Seminggu")
        adr_day = filtered_df.groupby('arrival_day_of_week')['adr'].mean()
        order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        adr_day = adr_day.reindex(order)
        
        fig2, ax2 = plt.subplots(figsize=(10, 5)) 
        ax2.plot(adr_day.values, marker='o')
        ax2.set_xticks(range(7))
        ax2.set_xticklabels(order, rotation=45)
        ax2.set_title("Rata-rata ADR per Hari dalam Seminggu")
        ax2.set_xlabel("Hari Kedatangan") 
        ax2.set_ylabel("Rata-rata ADR") 

        for i, v in enumerate(adr_day.values):
            if pd.notna(v):
                ax2.text(i, v + 1, str(round(v)), ha='center')

        st.pyplot(fig2)
        plt.close(fig2) # Tutup plot

        # tambahkan insight
        with st.expander("Insight"):
            st.markdown("""
            - **Hari dengan ADR Tertinggi**: Harga cenderung naik tinggi saat akhir pekan (Friday, Saturday dan Sunday).
            - **Hari Terendah**: Hari kerja (Tuesday, Wednesday dan Thursday) cenderung lebih rendah.
            """)
        
        # Visualisasi 4: Rasio Pembatalan
        st.subheader("🚫 Rasio Pembatalan per Tipe Hotel")

        # hitung cancel rate dan booking total
        cancel_rate = filtered_df.groupby(['hotel', 'is_canceled']).size().reset_index(name='count')
        total_booking = filtered_df.groupby('hotel').size().reset_index(name='total_booking')

        # merge dan hitung proporsi
        cancel_rate = cancel_rate.merge(total_booking, on='hotel')
        cancel_rate['rate'] = cancel_rate['count'] / cancel_rate['total_booking']

        # Map 0/1 ke label deskriptif untuk legenda
        cancel_rate['is_canceled_label'] = cancel_rate['is_canceled'].map({0: 'Tidak Dibatalkan', 1: 'Dibatalkan'})

        # visualisasi
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=cancel_rate, x='hotel', y='rate', hue='is_canceled_label', palette=['#C7D6CE', '#F4A8B6'], ax=ax)

        # label persentase
        for p in ax.patches:
            height = p.get_height()
            if height > 0:
                ax.text(
                    x=p.get_x() + p.get_width() / 2,
                    y=height + 0.01,
                    s=f'{height:.1%}',
                    ha='center', va='bottom', fontsize=9
                )

        # format & label
        ax.set_ylim(0, 1)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
        ax.set_title('Rasio Pembatalan per Tipe Hotel')
        ax.set_xlabel('Hotel')
        ax.set_ylabel('Proporsi')
        ax.legend(title='Status Pembatalan')

        st.pyplot(fig)
        plt.close(fig)

        # tambahkan insight
        with st.expander("Insight"):
            st.markdown("""
            - City Hotel memiliki tingkat pembatalan lebih tinggi dibandingkan Resort Hotel.
            - Sedangkan, Resort hotel lebih stabil dalam hal kedatangan customer.
            """)