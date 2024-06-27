import streamlit as st
from st_on_hover_tabs import on_hover_tabs
import base64
import sqlite3 as sq
import pandas as pd
import matplotlib.pyplot as plt
import os
from streamlit import components
import json
from pathlib import Path

with open('data rumah sakit_0920.json') as f:
    data = json.load(f)
def database():
    conn = sq.connect('tesss.db')
    return conn

def membuat_table():
    conn = database()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS dokter (
                    ID_Dokter INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT NOT NULL,
                    spesialisasi TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS pasien (
                    ID_Pasien INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT NOT NULL,
                    umur INTEGER NOT NULL,
                    tanggal_masuk DATE,
                    alamat TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS penyakit (
                    ID_Penyakit INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT NOT NULL,
                    pasien_id INTEGER,
                    tanggal_masuk DATE,
                    FOREIGN KEY (pasien_id) REFERENCES pasien (ID_Pasien))''')
    conn.commit()
    conn.close()

def muat_data():
    conn = database()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM dokter')
    dokter_count = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM pasien')
    pasien_count = c.fetchone()[0]
    if dokter_count == 0 and pasien_count == 0:
        for dokter in data['dokter']:
            c.execute('INSERT INTO dokter (nama, spesialisasi) VALUES (?,?)', (dokter['nama'], dokter['spesialisasi']))
        for pasien in data['pasien']:
            c.execute('INSERT INTO pasien (nama, umur, alamat, tanggal_masuk) VALUES (?,?,?,?)', 
                      (pasien['nama'], pasien['umur'], pasien['alamat'], pasien['tanggal_masuk']))
            pasien_id = c.lastrowid
            c.execute('INSERT INTO penyakit (nama, pasien_id, tanggal_masuk) VALUES (?,?,?)', 
                      (pasien['penyakit'], pasien_id, pasien['tanggal_masuk']))
    conn.commit()
    conn.close()
    
def initialize_database():
    membuat_table()
    muat_data()

initialize_database()

membuat_table()

ADMIN_0920 = {
    "admin": "Ut0mo.27"
}

def login_admin(username, password):
    return ADMIN_0920.get(username) == password

def login_pasien(nama):
    conn = database()
    c = conn.cursor()
    c.execute('SELECT * FROM pasien WHERE nama = ?', (nama,))
    result = c.fetchone()
    conn.close()
    return result

def get_role(username):
    if username in ADMIN_0920:
        return "admin"
    else:
        return "pasien"

def masukan_dokter(nama_dokter_0920, spesialisasi_dokter_0920):
    conn = database()
    c = conn.cursor()
    c.execute('INSERT INTO dokter (nama, spesialisasi) VALUES (?, ?)', (nama_dokter_0920, spesialisasi_dokter_0920))
    conn.commit()
    conn.close()

def melihat_data_dokter():
    conn = database()
    c = conn.cursor()
    c.execute('SELECT * FROM dokter')
    dokter_0920 = pd.DataFrame(c.fetchall(), columns=[desc[0] for desc in c.description])
    conn.close()
    return dokter_0920

def melihat_data_pasien():
    conn = database()
    query = '''
    SELECT pa.ID_Pasien, pa.nama AS Nama_Pasien, pa.umur, pa.alamat, py.nama AS Nama_Penyakit, py.tanggal_masuk
    FROM pasien pa
    LEFT JOIN penyakit py ON pa.ID_Pasien = py.pasien_id
    '''
    c = conn.cursor()
    c.execute(query)
    pasien_0920 = pd.DataFrame(c.fetchall(), columns=[desc[0] for desc in c.description])
    conn.close()
    return pasien_0920

def cari_dokter(nama_dokter_0920):
    conn = database()
    c = conn.cursor()
    c.execute('SELECT * FROM dokter WHERE nama LIKE ?', (nama_dokter_0920,))
    dokter_0920 = pd.DataFrame(c.fetchall(), columns=[desc[0] for desc in c.description])
    conn.close()
    return dokter_0920

def cari_pasien(nama_pasien_0920):
    conn = database()
    c = conn.cursor()
    c.execute('SELECT * FROM pasien WHERE nama LIKE ?', (nama_pasien_0920,))
    pasien_0920 = pd.DataFrame(c.fetchall(), columns=[desc[0] for desc in c.description])
    conn.close()
    return pasien_0920

def melihat_data_diri(username_0920):
    conn = database()
    c = conn.cursor()
    c.execute('SELECT * FROM pasien WHERE nama = ?', (username_0920,))
    data_diri_0920 = pd.DataFrame(c.fetchall(), columns=[desc[0] for desc in c.description])
    conn.close()
    return data_diri_0920

def melihat_penyakit_diri(username_0920):
    conn = database()
    query = '''
    SELECT p.nama as Penyakit, p.tanggal_masuk as Tanggal_Masuk
    FROM penyakit p
    JOIN pasien pa ON p.pasien_id = pa.ID_Pasien
    WHERE pa.nama = ?
    '''
    c = conn.cursor()
    c.execute(query, (username_0920,))
    penyakit_diri_0920 = pd.DataFrame(c.fetchall(), columns=[desc[0] for desc in c.description])
    conn.close()
    return penyakit_diri_0920

def memilih_dokter(username_0920, dokter_id):
    conn = database()
    c = conn.cursor()
    c.execute('UPDATE pasien SET rumah_sakit_id = ? WHERE nama = ?', (dokter_id, username_0920))
    conn.commit()
    conn.close()

def masukan_pasien_dan_penyakit(nama_pasien_0920, umur_pasien_0920, alamat_pasien_0920, nama_penyakit_0920, tanggal_masuk_0920):
    conn = database()
    c = conn.cursor()
    c.execute('INSERT INTO pasien (nama, umur, alamat) VALUES (?, ?, ?)', (nama_pasien_0920, umur_pasien_0920, alamat_pasien_0920))
    pasien_id = c.lastrowid
    c.execute('INSERT INTO penyakit (nama, pasien_id, tanggal_masuk) VALUES (?, ?, ?)', (nama_penyakit_0920, pasien_id, tanggal_masuk_0920))
    conn.commit()
    conn.close()

def visualisasi_jumlah_penyakit(nama_penyakit):
    conn = database()
    query = '''
    SELECT tanggal_masuk, COUNT(ID_Penyakit) as jumlah_kasus
    FROM penyakit
    WHERE nama = ?
    GROUP BY tanggal_masuk
    ORDER BY tanggal_masuk
    '''
    c = conn.cursor()
    c.execute(query, (nama_penyakit,))
    data_0920 = pd.DataFrame(c.fetchall(), columns=[desc[0] for desc in c.description])
    conn.close()
    return data_0920

def membandingkan_data_penyakit():
    conn = database()
    query = '''
    SELECT p.nama as Penyakit, COUNT(p.ID_Penyakit) as Jumlah_Kasus
    FROM penyakit p
    GROUP BY p.nama
    '''
    c = conn.cursor()
    c.execute(query)
    perbandingan_0920 = pd.DataFrame(c.fetchall(), columns=[desc[0] for desc in c.description])
    conn.close()
    return perbandingan_0920

def memfilter_jenis_penyakit(pilih_penyakit_0920):
    conn = database()
    query = '''
    SELECT p.nama as Penyakit, COUNT(p.ID_Penyakit) as Jumlah_Kasus
    FROM penyakit p
    WHERE p.nama = ?
    GROUP BY p.nama
    '''
    c = conn.cursor()
    c.execute(query, (pilih_penyakit_0920,))
    hasil_filter_0920 = pd.DataFrame(c.fetchall(), columns=[desc[0] for desc in c.description])
    conn.close()
    return hasil_filter_0920

def hapus_dokter(dokter_id_0920):
    conn = database()
    c = conn.cursor()
    c.execute('DELETE FROM dokter WHERE ID_Dokter = ?', (dokter_id_0920,))
    conn.commit()
    conn.close()

def hapus_pasien(pasien_id_0920):
    conn = database()
    c = conn.cursor()
    c.execute('DELETE FROM pasien WHERE ID_Pasien = ?', (pasien_id_0920,))
    conn.commit()
    conn.close()

def get_image_path(image_name):
    script_dir = os.path.dirname(__file__) 
    return os.path.join(script_dir, image_name) 

@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

img = get_img_as_base64(get_image_path("hd hospital.jpg"))

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
background-image: url("data:image/png;base64,{img}");
background-size: cover;
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

st.markdown(
    """
    <style>
    .stButton>button {
        width: 200px; /* Lebar tombol */
        height: 50px; /* Tinggi tombol */
        font-size: 18px; /* Ukuran font */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    [data-testid="stHeader"] {
        background: transparent;
    }
    .main > div:first-child {
        background: transparent;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    [data-testid="stAppViewBlockContainer"] {
        width: 35%;
        padding: 15rem 1rem 10rem;
        max-width: 46rem;
        box-sizing: border-box;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    [data-testid="stMarkdownContainer"] h1 {
        color: white; 
        font-family: sans-serif; 
        font-size: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if 'logged_in_0920' not in st.session_state:
    st.session_state['logged_in_0920'] = False
    st.session_state['role_0920'] = None
    st.session_state['username_0920'] = None

if not st.session_state['logged_in_0920']:
    st.header("Login")
    login_type_0920 = st.selectbox("Login sebagai", ["Admin", "Pasien"])

    if login_type_0920 == "Admin":
        username_0920 = st.text_input("Username")
        password_0920 = st.text_input("Password", type="password")
        login_button_0920 = st.button("Login sebagai Admin")
        
        if login_button_0920:
            if login_admin(username_0920, password_0920):
                st.session_state['logged_in_0920'] = True
                st.session_state['role_0920'] = "admin"
                st.session_state['username_0920'] = username_0920
                st.success("Login berhasil!")
            else:
                st.error("Username atau password salah")
    else:
        username_0920 = st.text_input("Nama Pasien")
        login_button_0920 = st.button("Login sebagai Pasien")
        
        if login_button_0920:
            if login_pasien(username_0920):
                st.session_state['logged_in_0920'] = True
                st.session_state['role_0920'] = "pasien"
                st.session_state['username_0920'] = username_0920
                st.success("Login berhasil!")
            else:
                st.error("Nama pasien tidak ditemukan")
                
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(BASE_DIR, 'style.css')) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    with st.sidebar:
        st.sidebar.title("MENU")
        if st.session_state['role_0920'] == "admin":
            tabs = on_hover_tabs(tabName=['Dashboard', 'Lihat Dokter', 'Lihat Pasien', 'Cari Dokter', 'Cari Pasien', 'Tambahkan Dokter', 'Tambahkan Data Pasien', 'Hapus Dokter', 'Hapus Pasien', 'Filter Penyakit', 'Bandingkan Penyakit', 'Visualisasi Jumlah Penyakit', 'Logout'], 
                            iconName=['dashboard', 'search', 'search', 'search', 'search', 'add', 'add', 'delete', 'delete', 'filter', 'filter', 'filter', 'logout'], default_choice=0)
        else:
            tabs = on_hover_tabs(tabName=['Dashboard', 'Lihat Data Diri', 'Lihat Penyakit Diri', 'Lihat Dokter', 'Logout'], 
                            iconName=['dashboard', 'search', 'search', 'search', 'logout'], default_choice=0)

    if tabs == "Logout":
        st.session_state['logged_in_0920'] = False
        st.session_state['role_0920'] = None
        st.session_state['username_0920'] = None
        st.success("Anda telah logout")

    elif tabs =='Dashboard':
        def apply_style(style):
            st.markdown(f'<style>{style}</style>', unsafe_allow_html=True)

        apply_style(
            """
            body, /* or your parent container */
            [data-testid="stAppViewBlockContainer"] {
                display: flex; 
                flex-direction: column; 
                min-height: 100vh;
            }
            [data-testid="stAppViewBlockContainer"] {
                flex: 1;
                width: 100%;
                padding: 0rem 3rem 10rem;
                max-width: 46rem;
                box-sizing: border-box;
                background: white !important; 
            }
            """
        )
    
        import streamlit.components.v1 as components
        components.html(
            """
        <!DOCTYPE html>
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
        * {box-sizing: border-box;}
        body {font-family: Verdana, sans-serif;}
        .mySlides {display: none;}
        img {vertical-align: middle;}

        /* Slideshow container */
        .slideshow-container {
            max-width: 2000px;
            position: relative;
            margin: auto;
        }

        /* The dots/bullets/indicators */
        .dot {
            height: 15px;
            width: 15px;
            margin: 0 2px;
            background-color: #bbb;
            border-radius: 50%;
            display: inline-block;
            transition: background-color 0.6s ease;
        }

        .active {
            background-color: #717171;
        }

        /* Fading animation */
        .fade {
            animation-name: fade;
            animation-duration: 1.5s;
        }

        @keyframes fade {
            from {opacity: .4} 
            to {opacity: 1}
        }

        /* On smaller screens, decrease text size */
        @media only screen and (max-width: 300px) {
        .text {font-size: 11px}
        }
        </style>
        </head>
        <body>
            <div class="main">
                <StaffViewBlockContainer class="stapp-staff-block-white">
                    <h2>HomePage</h2>
                </StaffViewBlockContainer>
                </div>
        
        <div class="slideshow-container">

        <div class="mySlides fade">
            <img src="https://images.unsplash.com/photo-1598256989800-fe5f95da9787?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&dl=atikah-akhtar-XJptUS8nbhs-unsplash.jpg" style="width:100%">
        </div>

        <div class="mySlides fade">
            <img src="https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&dl=martha-dominguez-de-gouveia-nMyM7fxpokE-unsplash.jpg" style="width:100%">
        </div>

        <div class="mySlides fade">
            <img src="https://images.unsplash.com/photo-1606811841689-23dfddce3e95?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&dl=caroline-lm--m-4tYmtLlI-unsplash.jpg" style="width:100%">
        </div>

        </div>
        <br>

        <div style="text-align:center">
            <span class="dot"></span> 
            <span class="dot"></span> 
            <span class="dot"></span> 
        </div>

        <script>
        let slideIndex = 0;
        showSlides();

        function showSlides() {
        let i;
        let slides = document.getElementsByClassName("mySlides");
        let dots = document.getElementsByClassName("dot");
        for (i = 0; i < slides.length; i++) {
            slides[i].style.display = "none";  
        }
        slideIndex++;
        if (slideIndex > slides.length) {slideIndex = 1}    
        for (i = 0; i < dots.length; i++) {
            dots[i].className = dots[i].className.replace(" active", "");
        }
        slides[slideIndex-1].style.display = "block";  
        dots[slideIndex-1].className += " active";
        setTimeout(showSlides, 4000); // Change image every 2 seconds
        }
        </script>

        </body>
        </html> 

            """,
            height=600,
        )

    elif tabs == "Lihat Dokter":
        dokter_0920 = melihat_data_dokter()
        st.dataframe(dokter_0920)

    elif tabs == "Lihat Pasien":
        if st.session_state['role_0920'] == "admin":
            pasien_0920 = melihat_data_pasien()
            st.dataframe(pasien_0920)
        else:
            st.error("Anda tidak memiliki akses untuk fitur ini.")
            
    elif tabs == "Cari Dokter":
        nama_dokter_0920 = st.text_input("Masukkan nama dokter yang ingin dicari:")
        if nama_dokter_0920:
            hasil_cari_dokter_0920 = cari_dokter(nama_dokter_0920)
            st.dataframe(hasil_cari_dokter_0920)

    elif tabs == "Cari Pasien":
        nama_pasien_0920 = st.text_input("Masukkan nama pasien yang ingin dicari:")
        if nama_pasien_0920:
            hasil_cari_pasien_0920 = cari_pasien(nama_pasien_0920)
            st.dataframe(hasil_cari_pasien_0920)
        
    elif tabs == "Tambahkan Dokter":
        if st.session_state['role_0920'] == "admin":
            with st.form("dokter_form_0920", clear_on_submit=True):
                nama_dokter_0920 = st.text_input("Nama Dokter")
                spesialisasi_dokter_0920 = st.text_input("Spesialisasi Dokter")
                tambahkan_0920 = st.form_submit_button("Tambahkan")

                if tambahkan_0920:
                    masukan_dokter(nama_dokter_0920, spesialisasi_dokter_0920)
                    st.success("Dokter berhasil ditambahkan!")
                    st.dataframe(melihat_data_dokter())
        
    elif tabs == "Tambahkan Data Pasien":
        if st.session_state['role_0920'] == "admin":
            with st.form("pasien_penyakit_form_0920", clear_on_submit=True):
                nama_pasien_0920 = st.text_input("Nama Pasien")
                umur_pasien_0920 = st.number_input("Umur Pasien", min_value=0)
                alamat_pasien_0920 = st.text_input("Alamat Pasien")
                nama_penyakit_0920 = st.text_input("Nama Penyakit")
                deskripsi_penyakit_0920 = st.text_area("Deskripsi Penyakit")
                tanggal_masuk_0920 = st.date_input("Tanggal Masuk")
                tambahkan_0920 = st.form_submit_button("Tambahkan")

                if tambahkan_0920:
                    masukan_pasien_dan_penyakit(nama_pasien_0920, umur_pasien_0920, alamat_pasien_0920, nama_penyakit_0920, tanggal_masuk_0920)
                    st.success("Pasien dan Penyakit berhasil ditambahkan!")
                    st.dataframe(melihat_data_pasien())
        
    elif tabs == "Hapus Dokter":
        if st.session_state['role_0920'] == "admin":
            dokter_id_0920 = st.number_input("Masukkan ID Dokter yang Ingin Dihapus", min_value=1)
            hapus_button_0920 = st.button("Hapus Dokter")
            
            if hapus_button_0920:
                hapus_dokter(dokter_id_0920)
                st.success("Dokter berhasil dihapus!")
                st.dataframe(melihat_data_dokter())
        
    elif tabs == "Hapus Pasien":
        if st.session_state['role_0920'] == "admin":
            pasien_id_0920 = st.number_input("Masukkan ID Pasien yang Ingin Dihapus", min_value=1)
            hapus_button_0920 = st.button("Hapus Pasien")
            
            if hapus_button_0920:
                hapus_pasien(pasien_id_0920)
                st.success("Pasien berhasil dihapus!")
                st.dataframe(melihat_data_pasien())
        
    elif tabs == "Filter Penyakit":
        pilih_penyakit_0920 = st.text_input("Masukkan nama penyakit yang ingin difilter:")
        hasil_filter_0920 = memfilter_jenis_penyakit(pilih_penyakit_0920)
        st.dataframe(hasil_filter_0920)
        
    elif tabs == "Bandingkan Penyakit":
        perbandingan_0920 = membandingkan_data_penyakit()
        st.dataframe(perbandingan_0920)
        plt.figure(figsize=(10, 5))
        plt.bar(perbandingan_0920['Penyakit'], perbandingan_0920['Jumlah_Kasus'])
        plt.xlabel('Nama Penyakit')
        plt.ylabel('Jumlah Kasus')
        plt.title('Perbandingan Jumlah Kasus Penyakit')
        st.pyplot(plt)
        
    elif tabs == "Visualisasi Jumlah Penyakit":
        penyakit_0920 = st.text_input("Masukkan Nama Penyakit untuk Visualisasi")
        if penyakit_0920:
            data_0920 = visualisasi_jumlah_penyakit(penyakit_0920)
            if not data_0920.empty:
                plt.figure(figsize=(10, 5))
                plt.plot(data_0920['tanggal_masuk'], data_0920['jumlah_kasus'], marker='o')
                plt.xlabel('Tanggal Masuk')
                plt.ylabel('Jumlah Kasus')
                plt.title(f'Jumlah Kasus {penyakit_0920} per Tanggal')
                st.pyplot(plt)
            else:
                st.warning("Tidak ada data untuk penyakit tersebut.")
        
    elif tabs == "Lihat Data Diri":
        if st.session_state['role_0920'] == "pasien":
            username_0920 = st.session_state['username_0920']
            data_diri_0920 = melihat_data_diri(username_0920)
            st.dataframe(data_diri_0920)
                
    elif tabs == "Lihat Penyakit Diri":
        if st.session_state['role_0920'] == "pasien":
            username_0920 = st.session_state['username_0920']
            penyakit_diri_0920 = melihat_penyakit_diri(username_0920)
            st.dataframe(penyakit_diri_0920)
