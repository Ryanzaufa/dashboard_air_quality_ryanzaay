import streamlit as st
import pandas as pd
import datetime
import seaborn as sns
import matplotlib.pyplot as plt

# Konfigurasi tampilan
#sns.set_theme(style='ticks')
#plt.style.use('ggplot')
plt.style.use('seaborn-v0_8-darkgrid')  # Untuk Matplotlib terbaru
sns.set_theme(style='darkgrid')  # Untuk Seaborn terbaru

st.title("Dashboard Analisis Kualitas Udara")

# Load dataset dengan caching
@st.cache_data
def load_data(path):
    try:
        df = pd.read_csv(path)
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])
        return df
    except Exception as e:
        st.error(f"Gagal memuat dataset: {e}")
        return None

# Perbaiki jalur file
aotizhongxin_path = "dashboard/aotizhongxin.csv"
changping_path = "dashboard/changping.csv"

df_aotizhongxin = load_data(aotizhongxin_path)
df_changping = load_data(changping_path)

# Sidebar untuk memilih dataset
dataset_choice = st.sidebar.selectbox("Pilih Dataset", ["Aotizhongxin", "Changping"])

# Memilih dataset yang digunakan
df = df_aotizhongxin if dataset_choice == "Aotizhongxin" else df_changping

if df is not None:
    st.subheader(f'Dataset: {dataset_choice}')
    st.write(df.head())

     # Filter data periode 2013-2017
    def filter_data(df):
        return df[(df['datetime'].dt.year >= 2013) & (df['datetime'].dt.year <= 2017)]

    df_filtered = filter_data(df)

    # Pertanyaan 1 : Bagaimana tren kualitas udara di lokasi Aotizhongxin dan Changping selama periode 2013-2017?
    if 'datetime' in df.columns and 'Air_Quality' in df.columns:
        df_grouped = df_filtered.groupby([df_filtered['datetime'].dt.to_period("M"), "Air_Quality"]).size().unstack()

        st.subheader(f"Tren Kualitas Udara Berdasarkan Kualitas Udara di {dataset_choice} (2013-2017)")
        
        fig, ax = plt.subplots(figsize=(15, 6))
        df_grouped.plot(marker='o', linestyle='-', ax=ax)
        
        ax.set_title(f"Tren Jumlah Hari Berdasarkan Kualitas Udara di {dataset_choice} (2013-2017)")
        ax.set_xlabel("Tahun")
        ax.set_ylabel("Jumlah Hari")
        plt.xticks(rotation=45)

        # Meletakkan legend di bawah grafik
        ax.legend(title="Kualitas Udara", bbox_to_anchor=(0.5, -0.2), loc='upper center', ncol=3)

        st.pyplot(fig)
        
        st.write(f"Kualitas udara 'Baik' terlihat paling sering terjadi dibandingkan yang lainnya di **{dataset_choice}**. Namun, terdapat **fluktuasi signifikan** yang menunjukan bahwa ada periode tertentu yang dimana kualitas udara yang lebih buruk. Kualitas udara 'Baik' paling sering terjadi pada periode **2016 awal**.")
    

    # Tren PM2.5 seiring waktu
    if 'datetime' in df.columns and 'PM2.5' in df.columns:
        st.subheader("Tren PM2.5 Seiring Waktu")
        fig, ax = plt.subplots(figsize=(15, 5))
        sns.lineplot(x=df['datetime'], y=df['PM2.5'], ax=ax)
        ax.set_title("Tren PM2.5")
        st.pyplot(fig)
    
    # Pertanyaan 2: Pada tahun berapakah rata-rata tertinggi nilai PM2.5 terjadi pada kedua lokasi?
    if 'datetime' in df.columns and 'PM2.5' in df.columns:
        st.subheader(f"Tren Rata-rata PM2.5 per Tahun di {dataset_choice} (2013-2017)")

        # Menghitung rata-rata PM2.5 per tahun
        df_yearly = df_filtered.groupby(df_filtered['datetime'].dt.year)['PM2.5'].mean()

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df_yearly.index, df_yearly.values, marker='o', linestyle='-', label=f"{dataset_choice}", color='tab:blue')

        # Menentukan tahun dengan PM2.5 tertinggi
        max_year = df_yearly.idxmax()
        ax.axvline(max_year, color='red', linestyle='dashed', label=f'Maks: {max_year}')

        # Label & Legenda
        ax.set_title(f"Tren Rata-rata PM2.5 per Tahun di {dataset_choice} (2013-2017)")
        ax.set_xlabel("Tahun")
        ax.set_ylabel("Rata-rata PM2.5")
        ax.legend(loc='lower right')  # Pindahkan legenda ke bawah kanan
        ax.grid(True)

        st.pyplot(fig)
        
        st.write(f"Di **{dataset_choice}**, tren kenaikan nilai PM2.5 selama periode 2013-2014 dan mengalami penurunan yang signifikan pada tahun 2016. Tetapi pada tahun 2017 nilai PM2.5 mengalami kenaikan yang sangat signifikan hingga menyentuh nilai tertinggi di **{dataset_choice}**")
    
    # Pertanyaan 3: Seberapa besar pengaruh cuaca terhadap nilai PM2.5??
    if 'Weather_Condition' in df.columns and 'PM2.5' in df.columns:
        st.subheader(f"Pengaruh Kondisi Cuaca terhadap PM2.5 di {dataset_choice}")

        # Menghitung rata-rata PM2.5 berdasarkan kondisi cuaca
        df_weather = df.groupby('Weather_Condition')['PM2.5'].mean().sort_values()

        # Membuat grafik
        fig, ax = plt.subplots(figsize=(10, 5))

        # Warna default biru
        colors = ['tab:blue'] * len(df_weather)

        # Menyoroti kondisi cuaca dengan PM2.5 tertinggi dengan warna merah
        max_index = df_weather.idxmax()
        max_value = df_weather.max()
        max_pos = list(df_weather.index).index(max_index)
        colors[max_pos] = 'tab:red'

        # Plot bar chart
        bars = ax.bar(df_weather.index, df_weather.values, color=colors)

        # Menambahkan teks pada nilai tertinggi
        ax.text(max_pos, max_value, f"{max_value:.2f}", ha='center', va='bottom', 
                fontsize=12, fontweight='bold', color='red')

        # Label & Judul
        ax.set_xlabel("Kondisi Cuaca")
        ax.set_ylabel("Rata-rata PM2.5")
        ax.set_title(f"Rata-rata PM2.5 Berdasarkan Kondisi Cuaca ({dataset_choice})")
        plt.xticks(rotation=30, ha='right')

        st.pyplot(fig)

        st.write(f"Di **{dataset_choice}**, **{max_index}** merupakan kondisi cuaca paling berpolusi jika mengacu pada nilai rata-rata PM2.5")

    # Korelasi antara Kecepatan Angin dan PM2.5
    if 'Wind_Speed' in df.columns and 'PM2.5' in df.columns:
        st.subheader(f"Korelasi antara Wind Speed dan PM2.5 di {dataset_choice}")

        # Menghitung korelasi Pearson
        correlation = df[['Wind_Speed', 'PM2.5']].corr(method='pearson').iloc[0, 1]

        # Menampilkan nilai korelasi
        st.write(f"**Korelasi Pearson antara Wind Speed dan PM2.5:** `{correlation:.2f}`")

        # Scatter plot untuk visualisasi
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.scatterplot(x=df['Wind_Speed'], y=df['PM2.5'], alpha=0.6, ax=ax)
        sns.regplot(x=df['Wind_Speed'], y=df['PM2.5'], scatter=False, color='red', ax=ax)

        # Judul & Label
        ax.set_xlabel("Kecepatan Angin (Wind Speed)")
        ax.set_ylabel("Konsentrasi PM2.5")
        ax.set_title(f"Korelasi antara Wind Speed dan PM2.5 ({dataset_choice})\nPearson: {correlation:.2f}")

        st.pyplot(fig)
        st.write(f"Nilai korelasi berada di rentang -0.3 hingga 0, yang menunjukkan korelasi negatif lemah antara PM2.5 dan kecepatan angin. Nilai PM2.5 cenderung menurun saat kecepatan angin meningkat, tetapi hubungan ini tidak terlalu kuat. Diperlukan analisis lebih lanjut untuk memahami hubungan yang lebih kompleks antara PM2.5 dan kecepatan angin.")