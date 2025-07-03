import streamlit as st
import pandas as pd
import plotly.express as px
import calendar

@st.cache_data
def load_data():
    df = pd.read_csv("hotel_booking_demand_cleaned.csv")
    df['is_canceled'] = df['is_canceled'].astype('category')
    df['hotel'] = df['hotel'].astype('category')
    return df

def plot_adr_by_month(df):
    adr_month = df.groupby('arrival_month')['adr'].mean().reset_index()
    # Pastikan semua bulan ada, isi yang kosong dengan 0
    all_months = pd.DataFrame({'arrival_month': range(1, 13)})
    adr_month = pd.merge(all_months, adr_month, on='arrival_month', how='left').fillna(0)
    adr_month['arrival_month_name'] = adr_month['arrival_month'].apply(lambda x: calendar.month_abbr[x])
    
    fig = px.line(adr_month, 
                  x='arrival_month_name', 
                  y='adr', 
                  markers=True,
                  labels={'adr': 'Rata-rata ADR ($)', 'arrival_month_name': 'Bulan Kedatangan'},
                  title="Rata-rata Harga Kamar (ADR) per Bulan")
    fig.update_layout(title_x=0.5, xaxis_title=None, yaxis_title="Rata-rata ADR ($)")
    fig.update_traces(hovertemplate='Bulan: %{x}<br>Rata-rata ADR: $%{y:.2f}')
    return fig

def plot_adr_by_day(df):
    """Membuat plot interaktif ADR rata-rata per hari dalam seminggu."""
    adr_day = df.groupby('arrival_day_of_week')['adr'].mean()
    order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    adr_day = adr_day.reindex(order).reset_index()

    fig = px.line(adr_day, 
                  x='arrival_day_of_week', 
                  y='adr', 
                  markers=True,
                  labels={'adr': 'Rata-rata ADR ($)', 'arrival_day_of_week': 'Hari Kedatangan'},
                  title="Rata-rata ADR per Hari dalam Seminggu")
    fig.update_layout(title_x=0.5, xaxis_title=None, yaxis_title="Rata-rata ADR ($)")
    fig.update_traces(hovertemplate='Hari: %{x}<br>Rata-rata ADR: $%{y:.2f}')
    return fig

def plot_adr_by_segment(df):
    """Membuat plot bar interaktif ADR rata-rata per segmen pasar."""
    adr_segment = df.groupby('market_segment')['adr'].mean().sort_values(ascending=False).reset_index()
    
    fig = px.bar(adr_segment, 
                 x='market_segment', 
                 y='adr',
                 text_auto='.2s',
                 labels={'adr': 'Rata-rata ADR ($)', 'market_segment': 'Segmen Pasar'},
                 title="Rata-rata ADR per Segmen Pasar")
    fig.update_layout(title_x=0.5, xaxis_title=None, yaxis_title="Rata-rata ADR ($)")
    fig.update_traces(textposition='outside', hovertemplate='Segmen: %{x}<br>Rata-rata ADR: $%{y:.2f}')
    return fig
    
def plot_cancellation_ratio(df):
    """Membuat plot bar interaktif untuk rasio pembatalan per tipe hotel."""
    cancel_rate = df.groupby('hotel')['is_canceled'].value_counts(normalize=True).mul(100).rename('rate').reset_index()
    cancel_rate['is_canceled'] = cancel_rate['is_canceled'].map({0: 'Tidak Dibatalkan', 1: 'Dibatalkan'})

    fig = px.bar(cancel_rate, 
                 x='hotel', 
                 y='rate', 
                 color='is_canceled',
                 text_auto='.1f',
                 color_discrete_map={'Tidak Dibatalkan': '#86B69A', 'Dibatalkan': '#F29C99'},
                 labels={'rate': 'Persentase (%)', 'hotel': 'Tipe Hotel', 'is_canceled': 'Status Pemesanan'},
                 title="Rasio Pembatalan per Tipe Hotel")
    fig.update_layout(title_x=0.5, yaxis_title="Persentase (%)", xaxis_title=None)
    fig.update_traces(texttemplate='%{y:.1f}%', textposition='inside')
    return fig

# --- UI STREAMLIT ---
def tampilkan_eda():
    st.title("📊 Dashboard Analisis Eksplorasi Data (EDA) Hotel")
    st.markdown("Gunakan filter di samping untuk menjelajahi tren dan pola dalam data pemesanan hotel.")

    # Load Data
    df = load_data()

    # --- SIDEBAR UNTUK FILTER ---
    st.sidebar.header("⚙️ Filter Data")

    hotel_options = ["Semua"] + list(df['hotel'].unique())
    selected_hotel = st.sidebar.multiselect("Tipe Hotel", hotel_options, default=["Semua"])

    cancel_map = {0: "Tidak Dibatalkan", 1: "Dibatalkan"}
    cancel_options_display = ["Semua"] + list(cancel_map.values())
    selected_cancel_display = st.sidebar.multiselect("Status Pembatalan", cancel_options_display, default=["Semua"])
    
    segment_options = ["Semua"] + list(df['market_segment'].unique())
    selected_segment = st.sidebar.multiselect("Segmen Pasar", segment_options, default=["Semua"])

    customer_options = ["Semua"] + list(df['customer_type'].unique())
    selected_customer = st.sidebar.multiselect("Tipe Customer", customer_options, default=["Semua"])

    month_options_numeric = sorted(df['arrival_month'].unique())
    month_names = ["Semua"] + [calendar.month_name[m] for m in month_options_numeric]
    selected_month_name = st.sidebar.multiselect("Bulan Kedatangan", month_names, default=["Semua"])

    # --- LOGIKA FILTER ---
    filtered_df = df.copy()
    if "Semua" not in selected_hotel:
        filtered_df = filtered_df[filtered_df['hotel'].isin(selected_hotel)]
    if "Semua" not in selected_cancel_display:
        cancel_filter_raw = [k for k, v in cancel_map.items() if v in selected_cancel_display]
        filtered_df = filtered_df[filtered_df['is_canceled'].isin(cancel_filter_raw)]
    if "Semua" not in selected_segment:
        filtered_df = filtered_df[filtered_df['market_segment'].isin(selected_segment)]
    if "Semua" not in selected_customer:
        filtered_df = filtered_df[filtered_df['customer_type'].isin(selected_customer)]
    if "Semua" not in selected_month_name:
        month_filter = [list(calendar.month_name).index(name) for name in selected_month_name]
        filtered_df = filtered_df[filtered_df['arrival_month'].isin(month_filter)]
    
    # --- HALAMAN UTAMA ---
    
    # Metrik Utama (KPI)
    st.markdown("### Ringkasan Data")
    if filtered_df.empty:
        st.warning("Tidak ada data yang cocok dengan filter yang dipilih. Harap ubah pilihan Anda.")
    else:
        kpi1, kpi2, kpi3 = st.columns(3)
        total_bookings = len(filtered_df)
        avg_adr = filtered_df['adr'].mean()
        cancellation_rate = filtered_df[filtered_df['is_canceled'] == 1].shape[0] / total_bookings * 100 if total_bookings > 0 else 0

        kpi1.metric(label="Total Booking", value=f"{total_bookings:,}")
        kpi2.metric(label="Rata-rata ADR", value=f"${avg_adr:.2f}")
        kpi3.metric(label="Cancellation Rate", value=f"{cancellation_rate:.1f}%")

        st.markdown("<hr>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(plot_adr_by_month(filtered_df), use_container_width=True)
            with st.expander("Lihat Insight"):
                st.markdown("""
                - **Puncak ADR**: Harga cenderung naik signifikan pada bulan-bulan musim liburan seperti Juli dan Agustus.
                - **Penurunan ADR**: Bulan dengan permintaan rendah seperti November dan Januari menunjukkan ADR yang lebih rendah.
                """)
            
            st.plotly_chart(plot_adr_by_segment(filtered_df), use_container_width=True)
            with st.expander("Lihat Insight"):
                st.markdown("""
                - **Segmen Paling Menguntungkan**: Pemesanan 'Direct' dan 'Online TA' cenderung memiliki ADR tertinggi.
                - **Segmen Peluang**: 'Complementary' memiliki ADR sangat rendah, sering kali karena bagian dari promosi atau kompensasi.
                """)

        with col2:
            st.plotly_chart(plot_adr_by_day(filtered_df), use_container_width=True)
            with st.expander("Lihat Insight"):
                st.markdown("""
                - **Akhir Pekan Lebih Mahal**: Harga kamar jelas lebih tinggi pada akhir pekan (Jumat & Sabtu) dibandingkan hari kerja.
                - **Hari Kerja Lebih Murah**: Pelancong bisnis atau mereka yang fleksibel bisa mendapatkan harga lebih baik di hari kerja.
                """)

            st.plotly_chart(plot_cancellation_ratio(filtered_df), use_container_width=True)
            with st.expander("Lihat Insight"):
                st.markdown("""
                - **Risiko Pembatalan**: 'City Hotel' menunjukkan tingkat pembatalan yang lebih tinggi secara konsisten. Ini mungkin karena perubahan rencana perjalanan yang lebih sering untuk tamu kota.
                - **Stabilitas**: 'Resort Hotel' memiliki tingkat pembatalan yang lebih rendah, mungkin karena pemesanan lebih direncanakan untuk liburan.
                """)