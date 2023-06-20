import streamlit as st
import easyocr
from PIL import Image
import mysql.connector
import numpy as np
from streamlit_option_menu import option_menu
import re

# Create MySQL database and table
db = mysql.connector.connect(
    host="localhost",
    user="your_username",
    password="your_password",
    database="business_cards",
    auth_plugin='mysql_native_password'
)

cursor = db.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS business_cards (
        id INT AUTO_INCREMENT PRIMARY KEY,
        company_name VARCHAR(255),
        cardholder_name VARCHAR(255),
        designation VARCHAR(255),
        mobile_number VARCHAR(255),
        email_address VARCHAR(255),
        website_url VARCHAR(255),
        area VARCHAR(255),
        city VARCHAR(255),
        state VARCHAR(255),
        pin_code VARCHAR(255),
        image_path VARCHAR(255)
    )
""")
db.commit()

# Create EasyOCR reader
reader = easyocr.Reader(['en'])

# Streamlit Application
def main():
    st.set_page_config(page_title='BizCardX OCR App', page_icon=":credit_card:", layout='wide')
    st.title("&emsp;:blue[BizCardX: Extracting Business Card Data with OCR] :credit_card:")

    # User authentication
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        login()
    
    else:
        menu = option_menu("MENU", ["Home","View Database","Update Data","Delete Data"],
                            icons=["house-fill",'cloud-fill','plus-slash-minus','trash-fill'],
                            menu_icon= "menu-button-wide",
                            default_index=0,
                            orientation="horizontal",
                            )
       
        if menu == "Home":
            st.header("Upload Business Card")
            upload_image()

        elif menu == "View Database":
            st.header("View Database")
            view_database()

        elif menu == "Update Data":
            st.header("Update Data")
            update_data()

        elif menu == "Delete Data":
            st.header("Delete Data")
            delete_data()

# User login
def login():
    st.subheader('Login')

    # Define hardcoded username and password 
    username = 'admin'
    password = 'password'

    # Username and password input fields
    input_username = st.text_input('Username')
    input_password = st.text_input('Password', type='password')

    if st.button('Login'):
        if input_username == username and input_password == password:
            st.session_state.authenticated = True
        else:
            st.error('Invalid username or password')

# Upload image and Extract information
def upload_image():
    uploaded_file = st.file_uploader(label="Upload Business Card Image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Business Card', use_column_width=True)

        if st.button("Extract Information"):
            # Convert image to numpy array
            image_np = np.array(image)
            extracted_info = extract_information(image_np)
            display_information(extracted_info, uploaded_file.name)
            save_to_database(extracted_info, uploaded_file.name)

# Extract information from the image using EasyOCR
def extract_information(image):
    with st.spinner("Extracting information..."):
        # Use EasyOCR to extract text from the image
        result = reader.readtext(image, detail=0, paragraph=False)

        extracted_info = {}
        extracted_info['Cardholder Name'] = result[0]
        extracted_info['Company Name'] = ''
        extracted_info['Designation'] = result[1]
        extracted_info['Mobile Number'] = ''
        extracted_info['Email Address'] = ''
        extracted_info['Website URL'] = ''
        extracted_info['Area'] = ''
        extracted_info['City'] = ''
        extracted_info['State'] = ''
        extracted_info['Pin Code'] = ''

        # Parse the text to extract the relevant information
        for text in result:
            if re.findall(r"\+?[0-9]{2,3}-?[0-9]{3}-?[0-9]{4}", text):
                extracted_info['Mobile Number'] = text
            elif re.findall(r"[^A-Z0-9.-_+~!@#$ %&*()]+@+[a-zA-Z0-9]+.[a-z]+", text):
                extracted_info['Email Address'] = text
            elif re.findall(r"[^,0-9!@#$%&*()_+]+[A-Za-z]+.com", text):
                extracted_info['Website URL'] = text
            elif re.findall(r"\d+\s[a-zA-Z\s]+\b", text):
                extracted_info['Area'] = text.split(',')[0].strip()
            
            company_names = ['selva digitals', 'GLOBAL INSURANCE', 'BORCELLE AIRLINES', 'Family Restaurant', 'Sun Electricals']
            for name in company_names:
                words = name.split()  # Split the company name into individual words
                for word in words:
                    if any(re.search(r"\b" + re.escape(word) + r"\b", text, flags=re.IGNORECASE) for text in result):
                        extracted_info['Company Name'] = name
                        break
                if extracted_info['Company Name']:
                    break
                    
            city_match = re.search(r",\s*([A-Za-z\s]+)\b(?![^,]*,\s*\d{6,7}\b)", text)
            if city_match:
                city = city_match.group(1).strip()
                extracted_info['City'] = city

            state_matches = re.findall(r"[A-Za-z\s]+(?=\s*\d{6})", text)
            if state_matches:
                extracted_info['State'] = state_matches[0].strip()
                
            pincode_matches = re.findall(r"\b(\d{6,7})\b", text)
            if pincode_matches:
                extracted_info['Pin Code'] = pincode_matches[0]

        return extracted_info
    
# Display the extracted information in a table
def display_information(extracted_info, image_path):
    st.subheader("Extracted Information")

    extracted_table = {
        'Cardholder Name': extracted_info['Cardholder Name'],
        'Company Name': extracted_info['Company Name'],
        'Designation': extracted_info['Designation'],
        'Mobile Number': extracted_info['Mobile Number'],
        'Email Address': extracted_info['Email Address'],
        'Website URL': extracted_info['Website URL'],
        'Area': extracted_info['Area'],
        'City': extracted_info['City'],
        'State': extracted_info['State'],
        'Pin Code': extracted_info['Pin Code'],
        'Image Path': image_path,
    }

    st.table(extracted_table)

# Save the extracted information to the database
def save_to_database(extracted_info, image_path):
    query = """
        INSERT INTO business_cards (cardholder_name,company_name,
        designation, mobile_number, email_address,
        website_url, area, city, state, pin_code, image_path
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        extracted_info['Cardholder Name'], extracted_info['Company Name'],
        extracted_info['Designation'], extracted_info['Mobile Number'],
        extracted_info['Email Address'], extracted_info['Website URL'],
        extracted_info['Area'], extracted_info['City'],
        extracted_info['State'], extracted_info['Pin Code'],
        image_path
    )

    cursor.execute(query, values)
    db.commit()

    st.success("Data saved to the Database!")

# View the database entries
def view_database():
    query = "SELECT * FROM business_cards"
    cursor.execute(query)
    entries = cursor.fetchall()

    for entry in entries:
        st.subheader(f"Entry ID: {entry[0]}")

        entry_info = {
            'Company Name': entry[1],
            'Cardholder Name': entry[2],
            'Designation': entry[3],
            'Mobile Number': entry[4],
            'Email Address': entry[5],
            'Website URL': entry[6],
            'Area': entry[7],
            'City': entry[8],
            'State': entry[9],
            'Pin Code': entry[10],
            'Image Path': entry[11],
        }

        st.table(entry_info)

# Update data in the database
def update_data():
    entry_id = st.number_input("Enter the ID of the entry you want to update", min_value=1, value=1)
    query = "SELECT * FROM business_cards WHERE id = %s"
    cursor.execute(query, (entry_id,))
    entry = cursor.fetchone()

    if entry:
        st.subheader(f"Updating Entry ID: {entry[0]}")

        updated_info = {
            'Company Name': entry[1],
            'Cardholder Name': entry[2],
            'Designation': entry[3],
            'Mobile Number': entry[4],
            'Email Address': entry[5],
            'Website URL': entry[6],
            'Area': entry[7],
            'City': entry[8],
            'State': entry[9],
            'Pin Code': entry[10],
            'Image Path': entry[11],
        }

        for key, value in updated_info.items():
            new_value = st.text_input(key, value)
            updated_info[key] = new_value

        query = """
            UPDATE business_cards
            SET
                company_name = %s,
                cardholder_name = %s,
                designation = %s,
                mobile_number = %s,
                email_address = %s,
                website_url = %s,
                area = %s,
                city = %s,
                state = %s,
                pin_code = %s,
                image_path = %s
            WHERE id = %s
        """

        values = (
            updated_info['Company Name'], updated_info['Cardholder Name'],
            updated_info['Designation'], updated_info['Mobile Number'],
            updated_info['Email Address'], updated_info['Website URL'],
            updated_info['Area'], updated_info['City'],
            updated_info['State'], updated_info['Pin Code'],
            updated_info['Image Path'], entry_id
        )

        cursor.execute(query, values)
        db.commit()

        st.success("Data updated!")
    else:
        st.warning("Entry not found!")

# Delete data from the database
def delete_data():
    entry_id = st.number_input("Enter the ID of the entry you want to delete", min_value=1, value=1)
    query = "SELECT * FROM business_cards WHERE id = %s"
    cursor.execute(query, (entry_id,))
    entry = cursor.fetchone()

    if entry:
        st.subheader(f"Deleting Entry ID: {entry[0]}")
        st.write("Extracted Information:")

        # To preview the extracted information
        preview_info(entry) 

        confirm_delete = st.button("Confirm delete")

        if confirm_delete:
            query = "DELETE FROM business_cards WHERE id = %s"
            cursor.execute(query, (entry_id,))
            db.commit()

            st.success("Entry deleted!")
    else:
        st.warning("Entry not found!")

# To preview the extracted information
def preview_info(entry):
    extracted_info = {
        'Company Name': entry[1],
        'Cardholder Name': entry[2],
        'Designation': entry[3],
        'Mobile Number': entry[4],
        'Email Address': entry[5],
        'Website URL': entry[6],
        'Area': entry[7],
        'City': entry[8],
        'State': entry[9],
        'Pin Code': entry[10],
        'Image Path': entry[11],
    }

    st.table(extracted_info)

if __name__ == '__main__':
    main()
    cursor.close()
    db.close()
