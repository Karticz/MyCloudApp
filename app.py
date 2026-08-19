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

glass_css = """
<style>
.stApp {
    background: linear-gradient(-45deg, #1e3c72, #2a5298, #ff6a00, #ee0979);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
h1, h2, h3, p, label {
    color: #ffffff !important;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
div[data-testid="stTextInput"] > div > div > input {
    background: rgba(255, 255, 255, 0.15) !important;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 12px;
    color: white !important;
}
div[data-testid="stButton"] > button {
    background: rgba(255, 255, 255, 0.2) !important;
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.4) !important;
    border-radius: 12px;
    color: white !important;
    font-weight: bold;
    font-size: 16px;
    transition: all 0.3s ease;
}
div[data-testid="stButton"] > button:hover {
    background: rgba(255, 255, 255, 0.4) !important;
    transform: scale(1.05);
}
</style>
"""
st.markdown(glass_css, unsafe_allow_html=True)

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
    # Screen visible after successful login
    st.subheader(f"Welcome to your Cloud, {st.session_state['username']}! ☁️")
    
    # --- FIX: We define save_folder here so BOTH Upload and Gallery can access it ---
    save_folder = "MyCloudStorage"
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    
    # 1. Streamlit widget for file upload
    uploaded_file = st.file_uploader("Upload your file here (Photos/Videos/Docs)", type=['png', 'jpg', 'jpeg', 'mp4', 'txt', 'pdf'])
    
    if uploaded_file is not None:
        if st.button("Upload to Cloud ⏏"):
            file_path = os.path.join(save_folder, uploaded_file.name)
            
            # Writing the uploaded file to the local storage
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            # Saving file details into the MySQL database
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
    
    # --- GALLERY SECTION START ---
    st.subheader("📁 Your Cloud Gallery")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Fetching only the logged-in user's files from the database
        cursor.execute("SELECT filename, file_type FROM files WHERE user_id = %s", (st.session_state['id'],))
        user_files = cursor.fetchall()
        
        if user_files:
            # Creating a 3-column grid layout for the gallery
            cols = st.columns(3)
            
            for index, file_record in enumerate(user_files):
                file_name = file_record[0]
                file_type = file_record[1].lower()
                file_path = os.path.join(save_folder, file_name)
                
                # Check if the file actually exists in the D Drive
                if os.path.exists(file_path):
                    col = cols[index % 3] # Cycle through the 3 columns
                    
                    with col:
                        # If it's an image, display it
                        if file_type in ['png', 'jpg', 'jpeg']:
                            st.image(file_path, caption=file_name, use_container_width=True)
                        # If it's a video, play it
                        elif file_type == 'mp4':
                            st.video(file_path)
                            st.caption(file_name)
                        # For documents or other files, provide a download button
                        else:
                            with open(file_path, "rb") as f:
                                st.download_button(
                                    label=f"📄 Download {file_name}",
                                    data=f,
                                    file_name=file_name,
                                    key=f"download_{file_name}_{index}" # Added key to prevent errors
                                )
                else:
                    st.warning(f"File missing on disk: {file_name}")
        else:
            st.info("No files uploaded yet. Start uploading to see your gallery!")
            
    except Exception as e:
         st.error(f"Failed to load gallery: {e}")
    # --- GALLERY SECTION END ---

    st.write("---") # Divider before logout
    
    if st.button("Logout ❮❮requirements.txt"):
        st.session_state['logged_in'] = False
        st.rerun()




    

        
    
