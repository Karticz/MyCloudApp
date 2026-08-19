import streamlit as st
import mysql.connector
import os

def get_db_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        port=4000,
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"]
    )

st.set_page_config(page_title="My Cloud App", page_icon="☁️", layout="centered")

# --- EPIC CSS & ANIMATIONS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

html, body, [class*="css"]  {
    font-family: 'Poppins', sans-serif;
}

/* 1. Animated Moving Background */
.stApp {
    background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #1a2a6c);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* 2. Page Transition Animation */
@keyframes pageTransition {
    0% { opacity: 0; transform: translateX(-40px) scale(0.95); }
    100% { opacity: 1; transform: translateX(0px) scale(1); }
}

.block-container {
    animation: pageTransition 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(25px);
    -webkit-backdrop-filter: blur(25px);
    border-radius: 20px;
    padding: 3rem !important;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
    margin-top: 40px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white; 
}

/* Make text elements white */
p, h1, h2, h3, label, .stRadio label {
    color: #ffffff !important;
}

/* 3. Floating Title Animation */
h1 {
    animation: float 3s ease-in-out infinite;
    text-shadow: 0 4px 15px rgba(255, 255, 255, 0.3);
}
@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
    100% { transform: translateY(0px); }
}

/* 4. Beautiful Glass Input Boxes */
.stTextInput > div > div > input {
    border-radius: 15px;
    background: rgba(255,255,255,0.1);
    border: 2px solid rgba(255,255,255,0.2);
    color: white;
    padding: 12px;
    transition: all 0.3s ease;
}
.stTextInput > div > div > input:focus {
    background: rgba(255,255,255,0.2);
    border: 2px solid #00f2fe;
    box-shadow: 0 0 15px rgba(0, 242, 254, 0.5);
}

/* 5. EPIC Glow Effect Buttons */
div.stButton > button:first-child {
    background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
    color: #000 !important;
    border: none;
    border-radius: 30px;
    padding: 12px 24px;
    font-weight: bold;
    letter-spacing: 1px;
    transition: all 0.4s ease;
    box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3);
    width: 100%;
}
div.stButton > button:first-child:hover {
    transform: translateY(-5px) scale(1.05);
    box-shadow: 0 0 25px 10px rgba(0, 242, 254, 0.7); 
}

/* 6. FIXED SIDEBAR & HEADER BACKGROUND (No more white!) */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2027, #2c5364) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.1);
}
[data-testid="stSidebar"] * {
    color: white !important;
}
[data-testid="stHeader"] {
    background-color: transparent !important;
}

/* Hide default streamlit elements safely */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("☁️ My Own Cloud Storage")
st.write("🔒︎ Keep your photos and videos completely safe.")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.sidebar.title("Menu 𓃌")
    menu = ["Login", "Sign Up"]
    choice = st.sidebar.radio("Select an option:", menu)

    if choice == "Login":
        st.subheader(" ♡ Welcome Back!")
        login_user = st.text_input("Username")
        login_pass = st.text_input("Password", type="password")
        
        if st.button("Login "):
            if login_user and login_pass:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id, username FROM users WHERE username = %s AND password = %s", (login_user, login_pass))
                user_record = cursor.fetchone()
                
                if user_record:
                    st.success("Login Successful!")
                    st.session_state['logged_in'] = True
                    st.session_state['id'] = user_record[0]
                    st.session_state['username'] = user_record[1]
                    st.rerun() 
                else:
                    st.error("Invalid Username or Password! Please try again.")
            else:
                 st.warning("Please fill in both fields.")

    elif choice == "Sign Up":
        st.subheader("➜] Create a New Account")
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")
        confirm_pass = st.text_input("Confirm Password", type="password")
        
        if st.button("Register ➤"):
            if new_pass != confirm_pass:
                st.error("Passwords do not match!")
            elif new_user and new_pass:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (new_user, new_pass))
                    conn.commit()
                    st.success("Account created successfully! Please go to Login menu.")
                except mysql.connector.IntegrityError:
                    st.error("Username already exists. Please choose a different one.")
            else:
                st.warning("Please fill in all fields.")
else:
    st.subheader(f"Welcome to your Cloud, {st.session_state['username']}! ☁️")
    
    save_folder = "MyCloudStorage"
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    
    uploaded_file = st.file_uploader("Upload your file here (Photos/Videos/Docs)", type=['png', 'jpg', 'jpeg', 'mp4', 'txt', 'pdf'])
    
    if uploaded_file is not None:
        if st.button("Upload to Cloud ⏏"):
            file_path = os.path.join(save_folder, uploaded_file.name)
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                file_ext = uploaded_file.name.split('.')[-1]
                
                sql_query = "INSERT INTO files (filename, file_type, user_id) VALUES (%s, %s, %s)"
                values = (uploaded_file.name, file_ext, st.session_state['id'])
                
                cursor.execute(sql_query, values)
                conn.commit()
                
                st.success(f"Success! '{uploaded_file.name}' has been safely saved to your cloud. 🥳")
            except Exception as e:
                st.error(f"An error occurred: {e}")

    st.write("---")
    
    st.subheader("📁 Your Cloud Gallery")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT filename, file_type FROM files WHERE user_id = %s", (st.session_state['id'],))
        user_files = cursor.fetchall()
        
        if user_files:
            cols = st.columns(3)
            
            for index, file_record in enumerate(user_files):
                file_name = file_record[0]
                file_type = file_record[1].lower()
                file_path = os.path.join(save_folder, file_name)
                
                if os.path.exists(file_path):
                    col = cols[index % 3]
                    
                    with col:
                        # Display Image
                        if file_type in ['png', 'jpg', 'jpeg']:
                            st.image(file_path, caption=file_name, use_container_width=True)
                        # Display Video
                        elif file_type == 'mp4':
                            st.video(file_path)
                            st.caption(file_name)
                        # Display Download Button for other files
                        else:
                            with open(file_path, "rb") as f:
                                st.download_button(
                                    label=f"📄 Download {file_name}",
                                    data=f,
                                    file_name=file_name,
                                    key=f"download_{file_name}_{index}"
                                )
                        
                        # Delete Button Functionality
                        if st.button("🗑️ Delete", key=f"delete_{file_name}_{index}"):
                            try:
                                if os.path.exists(file_path):
                                    os.remove(file_path)
                                
                                del_conn = get_db_connection()
                                del_cursor = del_conn.cursor()
                                del_cursor.execute("DELETE FROM files WHERE filename = %s AND user_id = %s", (file_name, st.session_state['id']))
                                del_conn.commit()
                                
                                st.success("File deleted successfully! 🗑️")
                                st.rerun() 
                            except Exception as e:
                                st.error(f"Failed to delete, error: {e}")
                else:
                    st.warning(f"File missing on disk: {file_name}")
        else:
            st.info("No files uploaded yet. Start uploading to see your gallery!")
            
    except Exception as e:
         st.error(f"Failed to load gallery: {e}")
    
    st.write("---") 
    
    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()
