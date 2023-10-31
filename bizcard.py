import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
import mysql.connector as mysql
from PIL import Image
import cv2
import os
import matplotlib.pyplot as plt
import re

# Create an EasyOCR reader object
reader = easyocr.Reader(['en'])

red_style = "color: red;"

# CONNECTING WITH MYSQL DATABASE
mydb = mysql.connect(host="localhost",
                   user="root",
                   password="yourpassword",
                   database="yourdatabase"
                   )
mycursor = mydb.cursor(buffered=True)

# TABLE CREATION
mycursor.execute('''CREATE TABLE IF NOT EXISTS bizcard_data
                   (id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    company_name TEXT,
                    card_holder TEXT,
                    designation TEXT,
                    mobile_number VARCHAR(50),
                    email TEXT,
                    website TEXT,
                    area TEXT,
                    city TEXT,
                    state TEXT,
                    pin_code VARCHAR(10)
                    )''')

# Create a Streamlit sidebar with menu options
menu_choice = st.sidebar.radio("Main Menu", ["Home", "Fetch and upload", "Adjust", "Contact"])

# Define the content for the About page
if menu_choice == "Home":
    # Add a custom figure/icon (e.g., using an emoji) before "Home"
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; font-size: 24px;">
            🏠 Home
        </div>
        """,
        unsafe_allow_html=True
    )

    # The rest of your "Home" content goes here

    # Title with purple color and bigger font
    st.markdown("<h1 style='{} font-size: 48px;'> BizCardX: Extracting Business Card Data with OCR </h1>".format(red_style),
                unsafe_allow_html=True)

    # Create two columns for layout
    left_column, right_column = st.columns(2)


    left_column.image("1.jpg")
    left_column.image("image.png")
    # Description in violet color in the right column
    with right_column:
        st.markdown(
            """
            <div style="text-align: left; color: purple; font-size: 18px;">
           BizCardX is an OCR technology specialized in swiftly digitizing and organizing business card data.
           It extracts contact information like names, companies, and job titles from physical cards into digital formats.
           With advanced image processing and intelligent algorithms, it automates manual data entry, enhancing efficiency and accuracy. 
           It often integrates with CRM systems and allows easy data export, making it a valuable tool for professionals managing contacts.
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown("<h1 style='{} font-size: 36px;'>Optical Character Recognition (OCR)</h1>".format(red_style), unsafe_allow_html=True)

    # Add the YouTube video link in the center
    st.markdown(
        """
        <div style="display: flex; justify-content: center; margin-top: 20px;">
            <iframe width="560" height="315" src="https://www.youtube.com/embed/l3BUSEwevs4" 
            frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen>
            </iframe>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Add a description to the right with purple colorhttps://www.youtube.com/watch?v=jO-1rztr4O0
    st.markdown("#     ")
    st.markdown("#     ")
    st.markdown(
        """
        <div style="text-align: left; color: purple;">
        Optical Character Recognition (OCR) is a technology that enables the conversion of different types of documents, 
        such as scanned paper documents, PDF files, or images captured by a digital camera, into editable and searchable data. 
        It works by recognizing text characters within an image, which can then be used for various purposes, including document digitization, 
        data entry automation, and text analysis. OCR systems typically employ techniques such as feature detection, pattern recognition,
         and machine learning algorithms to accurately identify and interpret the characters in the input images. 
         This technology has become increasingly essential in streamlining data processing tasks and enhancing accessibility for various industries, 
         including finance, healthcare, and education.
        </div>
        """,
        unsafe_allow_html=True
    )

# Define the content for the Fetch and upload page
if menu_choice == "Fetch and upload":
    # Add icons using Unicode for "Fetch" and "Upload"
    st.markdown(
        """
         <div style="display: flex; align-items: center; gap: 10px; font-size: 24px;">
            &#128269; Fetch and &#128228; Upload
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader(":blue[Upload a Business Card]")
    uploaded_card = st.file_uploader("upload here", label_visibility="collapsed", type=["png", "jpeg", "jpg"])

    if uploaded_card is not None:

        def save_card(Bizcards):
            Bizcards_dir = os.path.join(os.getcwd(), "Bizcards")
            with open(os.path.join(Bizcards_dir, uploaded_card.name), "wb") as f:
                f.write(uploaded_card.getbuffer())


        save_card(uploaded_card)


        def image_preview(image, res):
            for (bbox, text, prob) in res:
                # unpack the bounding box
                (tl, tr, br, bl) = bbox
                tl = (int(tl[0]), int(tl[1]))
                tr = (int(tr[0]), int(tr[1]))
                br = (int(br[0]), int(br[1]))
                bl = (int(bl[0]), int(bl[1]))
                cv2.rectangle(image, tl, br, (255, 0, 255), 2)
                cv2.putText(image, text, (tl[0], tl[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
            plt.rcParams['figure.figsize'] = (15, 15)
            plt.axis('off')
            plt.imshow(image)


        # DISPLAYING THE UPLOADED IMAGE
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown("Uploaded Image")
            st.image(uploaded_card)
        # DISPLAYING THE CARD WITH HIGHLIGHTS
        with col2:

                st.set_option('deprecation.showPyplotGlobalUse', False)
                saved_img = os.getcwd() + "\\" + "Bizcards" + "\\" + uploaded_card.name
                image = cv2.imread(saved_img)
                res = reader.readtext(saved_img)
                st.markdown("Processed Image")
                st.pyplot(image_preview(image, res))

                # easy OCR
        saved_img = os.getcwd() + "\\" + "Bizcards" + "\\" + uploaded_card.name
        result = reader.readtext(saved_img, detail=0, paragraph=False)


        # CONVERTING IMAGE TO BINARY TO UPLOAD TO SQL DATABASE
        def img_to_binary(file):
            # Convert image data to binary format
            with open(file, 'rb') as file:
                binaryData = file.read()
            return binaryData


        data = {"company_name": [],
                "card_holder": [],
                "designation": [],
                "mobile_number": [],
                "email": [],
                "website": [],
                "area": [],
                "city": [],
                "state": [],
                "pin_code": [],
                }


        def get_data(res):
            for ind, i in enumerate(res):

                # To get WEBSITE_URL
                if "www " in i.lower() or "www." in i.lower():
                    data["website"].append(i)
                elif "WWW" in i:
                    data["website"] = res[4] + "." + res[5]

                # To get EMAIL ID
                elif "@" in i:
                    data["email"].append(i)

                # To get MOBILE NUMBER
                elif "-" in i:
                    data["mobile_number"].append(i)
                    if len(data["mobile_number"]) == 2:
                        data["mobile_number"] = " & ".join(data["mobile_number"])

                # To get COMPANY NAME
                elif ind == len(res) - 1:
                    data["company_name"].append(i)

                # To get CARD HOLDER NAME
                elif ind == 0:
                    data["card_holder"].append(i)

                # To get DESIGNATION
                elif ind == 1:
                    data["designation"].append(i)

                # To get AREA
                if re.findall('^[0-9].+, [a-zA-Z]+', i):
                    data["area"].append(i.split(',')[0])
                elif re.findall('[0-9] [a-zA-Z]+', i):
                    data["area"].append(i)

                # To get CITY NAME
                match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
                match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
                match3 = re.findall('^[E].*', i)
                if match1:
                    data["city"].append(match1[0])
                elif match2:
                    data["city"].append(match2[0])
                elif match3:
                    data["city"].append(match3[0])

                # To get STATE
                state_match = re.findall('[a-zA-Z]{9} +[0-9]', i)
                if state_match:
                    data["state"].append(i[:9])
                elif re.findall('^[0-9].+, ([a-zA-Z]+);', i):
                    data["state"].append(i.split()[-1])
                if len(data["state"]) == 2:
                    data["state"].pop(0)

                # To get PINCODE
                if len(i) >= 6 and i.isdigit():
                    data["pin_code"].append(i)
                elif re.findall('[a-zA-Z]{9} +[0-9]', i):
                    data["pin_code"].append(i[10:])


        get_data(result)


        # FUNCTION TO CREATE DATAFRAME
        def create_df(data):
            df = pd.DataFrame(data)
            return df


        df = create_df(data)
        st.success("Extracted Data")
        st.write(df)

        # Make the extracted data editable
        st.write("#### Edit Extracted Data")
        for i, row in df.iterrows():
            row['company_name'] = st.text_input("Company Name", row['company_name'])
            row['card_holder'] = st.text_input("Card Holder Name", row['card_holder'])
            row['designation'] = st.text_input("Designation", row['designation'])
            row['mobile_number'] = st.text_input("Mobile Number", row['mobile_number'])
            row['email'] = st.text_input("Email", row['email'])
            row['website'] = st.text_input("Website", row['website'])
            row['area'] = st.text_input("Area", row['area'])
            row['city'] = st.text_input("City", row['city'])
            row['state'] = st.text_input("State", row['state'])
            row['pin_code'] = st.text_input("Pin Code", row['pin_code'])

        if st.button("Upload to Database"):
            for i, row in df.iterrows():
                # here %S means string values
                sql = """INSERT INTO bizcard_data(company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                mycursor.execute(sql, tuple(row))
                # the connection is not auto committed by default, so we must commit to save our changes
                mydb.commit()
                st.success("Data saved in SQL successfully")
                uploaded_data = row  # Store the recently uploaded data

        if st.button("Show Updated Data"):
            mycursor.execute(
                "select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from bizcard_data")
            updated_df = pd.DataFrame(mycursor.fetchall(),
                                      columns=["Company_Name", "Card_Holder", "Designation", "Mobile_Number",
                                               "Email",
                                               "Website", "Area", "City", "State", "Pin_Code"])
            st.write(updated_df)


# Define the content for the Adjust page
if menu_choice == "Adjust":
    # Add a custom figure/icon (e.g., using a wrench emoji) before "Adjust"
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; font-size: 24px;">
            &#128295; Adjust
        </div>
        """,
        unsafe_allow_html=True
    )

    # Adding a dropdown for selecting alteration or deletion
    option = st.selectbox("Select Option:", ("Alter Data", "Delete Data"))

    if option == "Alter Data":
        st.write("You selected Alter Data option")
        # Establish connection with the MySQL database
        mydb = mysql.connect(host="localhost",
                             user="root",
                             password="yourpassword",
                             database="yourdatabase")
        mycursor = mydb.cursor(buffered=True)

        # Fetching all the names from the table
        mycursor.execute("SELECT card_holder FROM bizcard_data")
        names = mycursor.fetchall()
        names = [name[0] for name in names]

        # Showing a dropdown of names from the table
        selected_name = st.selectbox("Select Name:", names)

        # Fetching data corresponding to the selected name
        mycursor.execute(f"SELECT * FROM bizcard_data WHERE card_holder='{selected_name}'")
        selected_data = mycursor.fetchone()

        if selected_data:
            st.write("Selected Data:")
            col1, col2 = st.columns(2)
            column_names = [desc[0] for desc in mycursor.description]

            for i, data in enumerate(selected_data):
                col1.write(f"**{column_names[i]}**")
                col2.write(st.text_input("", data, key=f"input_{i}"))

            if st.button("Save Changes"):
                updated_data = [col2.text_input("", value, key=f"input_{i}") for i, value in enumerate(selected_data)]
                update_query = f"UPDATE bizcard_data SET " \
                               f"company_name='{updated_data[1]}', " \
                               f"card_holder='{updated_data[2]}', " \
                               f"designation='{updated_data[3]}', " \
                               f"mobile_number='{updated_data[4]}', " \
                               f"email='{updated_data[5]}', " \
                               f"website='{updated_data[6]}', " \
                               f"area='{updated_data[7]}', " \
                               f"city='{updated_data[8]}', " \
                               f"state='{updated_data[9]}', " \
                               f"pin_code='{updated_data[10]}' " \
                               f"WHERE card_holder='{selected_name}'"

                mycursor.execute(update_query)
                mydb.commit()
                st.success("Data saved in MySQL successfully")

        # Establish connection with MySQL
        mydb = mysql.connect(host="localhost", user="root", password="yourpassword", database="yourdatabase")
        mycursor = mydb.cursor(buffered=True)

        # Add a drop box to display the names
        mycursor.execute("SELECT card_holder FROM bizcard_data")
        names = mycursor.fetchall()
        names = [name[0] for name in names]

    if option == "Delete Data":
        st.write("You selected Delete Data option")
        # Establish connection with the MySQL database
        mydb = mysql.connect(host="localhost",
                             user="root",
                             password="yourpassword",
                             database="yourdatabase")
        mycursor = mydb.cursor(buffered=True)

        # Fetching all the names from the table
        mycursor.execute("SELECT card_holder FROM bizcard_data")
        names = mycursor.fetchall()
        names = [name[0] for name in names]

        # Showing a dropdown of names from the table
        selected_name = st.selectbox("Select Name:", names)

        # Fetching data corresponding to the selected name
        mycursor.execute(f"SELECT * FROM bizcard_data WHERE card_holder='{selected_name}'")
        selected_data = mycursor.fetchone()

        if selected_data:
            st.write("Selected Data:")
            # Display the data
            # ...

            # Add a button to delete the selected data
            if st.button("Delete Data"):
                delete_query = f"DELETE FROM bizcard_data WHERE card_holder='{selected_name}'"
                mycursor.execute(delete_query)
                mydb.commit()
                st.success(f"Data for {selected_name} deleted successfully")

# Define the content for the Contact page
if menu_choice == "Contact":
    # Add a custom figure/icon (e.g., using an educated boy emoji) before "Contact"
    st.markdown(
        """

        <div style="display: flex; align-items: center; gap: 10px; font-size: 24px;">
            🎓 Contact
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("Regards,")
    st.write(
        "I am excited to share the successful completion of the 'BizCardX: Extracting Business Card Data with OCR' project. By leveraging Python, Streamlit, EasyOCR, MySQL, and open-source libraries, I've developed an innovative solution for efficiently managing business card data.")
    st.write(
        "My journey began with creating an OCR-powered system that swiftly extracts information from physical business cards. Storing this data in a robust MySQL database ensures secure storage and easy retrieval.")
    st.write(
        "The highlight of my project is the user-friendly interface, enabling professionals to digitize and organize their contacts efficiently. With Streamlit, I've created a seamless experience for managing business contacts.")
    st.write(
        "With gratitude for the support and guidance from GUVI Geek Networks and the IIT Madras Data Science Programme at IIT Madras Research Park (IITMRP), as well as the collaborative efforts of IITMDSA Zen DataScience, GUVI, I look forward to more exciting ventures ahead.")
    st.write("Best Regards,")
    st.write("🎓Rajashekhara S Gowda")
    st.write("  ")
    st.write("For any inquiries or assistance, please feel free to contact me at:")
    st.write("Email: rajusgowda522000@gmail.com")
    st.write("LinkedIn:https://www.linkedin.com/in/raju-s-gowda-5f2000")
