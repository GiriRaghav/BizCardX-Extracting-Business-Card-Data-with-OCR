
# BizCardX: Extracting Business Card Data with OCR

BizCardX is an Optical Character Recognition (OCR) application that allows users to extract information from business cards. It provides a user-friendly interface for uploading business card images, extracting relevant details, and storing the extracted data in a MySQL database.

## Features

#### User authentication: 
Users need to login with a username and password to access the application's features.

#### Business card image upload: 
Users can upload business card images (JPG, JPEG, or PNG) to extract information.

#### Information extraction: 
The application uses the EasyOCR library to extract information from the uploaded images.

#### Data parsing: 
Extracted text is parsed to identify company name, cardholder name, designation, mobile number, email address, website URL, area, city, state, pin code, and image path.

#### Database integration: 
Extracted information can be saved to a MySQL database for future reference.

#### View database entries: 
Users can view the stored entries in the database.

#### Update and delete data: 
Users can update or delete specific entries in the database.

## Prerequisite

* Python 3.6 or higher
* Streamlit
* EasyOCR
* NumPy
* PIL (Python Imaging Library)
* MySQL server

## Usage

* Run the application using the following command:

```
   streamlit run app.py

```
* Access the application by opening the provided URL in your web browser.

* Login with the predefined username and password or modify the login credentials in the code.

* Choose from the available options in the menu:
    #### Home: 
    Upload a business card image and extract information from it.
    #### View Database: 
    View the entries stored in the database.
    #### Update Data: 
    Update information for a specific entry in the database.
    #### Delete Data: 
    Delete a specific entry from the database.

