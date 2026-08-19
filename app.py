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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');


@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

html, body, [class*="css"]  {
    font-family: 'Poppins', sans-serif;
}


.block-container {
    animation: fadeIn 0.8s ease-out;
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border-radius: 20px;
    padding: 2rem 3rem !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    margin-top: 50px;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.stTextInput > div > div > input {
    border-radius: 10px;
    border: 1px solid #ddd;
    padding: 10px;
}

div.stButton > button:first-child {
    background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
    color: white;
    border: none;
    border-radius: 25px;
    padding: 10px 24px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    transition: all 0.3s ease;
    width: 100%;
    font-weight: 600;
}

div.stButton > button:first-child:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.4);
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
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
                
                if file_type in ['png', 'jpg', 'jpeg']:
                    st.image(file_path, caption=file_name, use_container_width=True)
                
                elif file_type == 'mp4':
                    st.video(file_path)
                    st.caption(file_name)
                
                else:
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label=f"📄 Download {file_name}",
                            data=f,
                            file_name=file_name,
                            key=f"download_{file_name}_{index}"
                        )
                
                
                if st.button("🗑️ Delete", key=f"delete_{file_name}_{index}"):
                    try:
                        ం
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        
                        
                        del_conn = get_db_connection()
                        del_cursor = del_conn.cursor()
                        del_cursor.execute("DELETE FROM files WHERE filename = %s AND user_id = %s", (file_name, st.session_state['id']))
                        del_conn.commit()
                        
                        st.success("File Deleted 🗑️")
                        st.rerun() 
                    except Exception as e:
                        st.error(f"Not Deleted,Error: {e}")
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




    

        
    
