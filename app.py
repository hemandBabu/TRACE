import streamlit as st
import sqlite3


# ==============================
# DATABASE
# ==============================

conn = sqlite3.connect(
    "missing_system.db",
    check_same_thread=False
)

cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS reports(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT,

    type TEXT,

    name TEXT,

    age INTEGER,

    gender TEXT,

    location TEXT,

    clothing TEXT,

    description TEXT,

    status TEXT

)
""")


conn.commit()



# ==============================
# USER FUNCTIONS
# ==============================

def register(username,password):

    try:

        cursor.execute(
            """
            INSERT INTO users(username,password)
            VALUES(?,?)
            """,
            (username,password)
        )

        conn.commit()
        return True

    except:
        return False



def login(username,password):

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE username=?
        AND password=?
        """,
        (username,password)
    )

    return cursor.fetchone()



# ==============================
# REPORT FUNCTIONS
# ==============================

def add_report(data):

    cursor.execute(
        """
        INSERT INTO reports
        (
        username,
        type,
        name,
        age,
        gender,
        location,
        clothing,
        description,
        status
        )

        VALUES(?,?,?,?,?,?,?,?,?)

        """,
        data
    )

    conn.commit()



def get_user_reports(username):

    cursor.execute(
        """
        SELECT *
        FROM reports
        WHERE username=?
        """,
        (username,)
    )

    return cursor.fetchall()



def get_found_reports():

    cursor.execute(
        """
        SELECT *
        FROM reports
        WHERE type='Found'
        """
    )

    return cursor.fetchall()



# ==============================
# MATCHING
# ==============================

def find_match(missing):

    matches=[]

    found_people=get_found_reports()


    for found in found_people:

        score=0


        # age
        if missing[4]==found[4]:
            score+=1


        # gender
        if missing[5]==found[5]:
            score+=1


        # clothing
        if (
            missing[7]
            and
            found[7]
            and
            missing[7].lower()
            in
            found[7].lower()
        ):
            score+=1


        if score>=2:

            matches.append(found)


    return matches



# ==============================
# STREAMLIT CONFIG
# ==============================

st.set_page_config(
    page_title="Missing Finder",
    page_icon="🔎",
    layout="wide"
)


st.title("🔎 Missing & Found System")



# ==============================
# SESSION
# ==============================

if "user" not in st.session_state:

    st.session_state.user=None



# ==============================
# LOGIN
# ==============================

if st.session_state.user is None:


    option=st.sidebar.selectbox(
        "Account",
        [
            "Login",
            "Register"
        ]
    )


    if option=="Register":


        st.header("Create Account")


        username=st.text_input("Username")

        password=st.text_input(
            "Password",
            type="password"
        )


        if st.button("Register"):

            if register(username,password):

                st.success(
                    "Account created"
                )

            else:

                st.error(
                    "Username exists"
                )



    else:


        st.header("Login")


        username=st.text_input("Username")

        password=st.text_input(
            "Password",
            type="password"
        )


        if st.button("Login"):


            result=login(
                username,
                password
            )


            if result:

                st.session_state.user=username

                st.rerun()

            else:

                st.error(
                    "Invalid login"
                )


    st.stop()



# ==============================
# USER AREA
# ==============================

user=st.session_state.user


st.sidebar.success(
    f"User : {user}"
)



if st.sidebar.button("Logout"):

    st.session_state.clear()

    st.rerun()



page=st.sidebar.selectbox(

    "Menu",

    [
        "Report Missing",
        "Report Found",
        "My Status"
    ]

)



# ==============================
# MISSING
# ==============================

if page=="Report Missing":


    st.header("Report Missing Person")


    name=st.text_input("Name")

    age=st.number_input(
        "Age",
        0,
        100
    )


    gender=st.selectbox(
        "Gender",
        [
            "Male",
            "Female"
        ]
    )


    location=st.text_input(
        "Last Seen Location"
    )


    clothing=st.text_input(
        "Clothing"
    )


    description=st.text_area(
        "Description"
    )


    if st.button(
        "Submit Missing Report"
    ):


        add_report(

        (
        user,
        "Missing",
        name,
        age,
        gender,
        location,
        clothing,
        description,
        "Searching"
        )

        )


        st.success(
            "Missing report submitted"
        )



# ==============================
# FOUND
# ==============================

elif page=="Report Found":


    st.header("Report Found Person")


    name=st.text_input(
        "Name (if known)"
    )


    age=st.number_input(
        "Approximate Age",
        0,
        100
    )


    gender=st.selectbox(
        "Gender",
        [
            "Male",
            "Female"
        ]
    )


    location=st.text_input(
        "Found Location"
    )


    clothing=st.text_input(
        "Clothing"
    )


    description=st.text_area(
        "Description"
    )



    if st.button(
        "Submit Found Report"
    ):


        add_report(

        (
        user,
        "Found",
        name,
        age,
        gender,
        location,
        clothing,
        description,
        "Available"
        )

        )


        st.success(
            "Found report submitted"
        )



# ==============================
# STATUS
# ==============================

else:


    st.header(
        "My Missing Reports"
    )


    reports=get_user_reports(user)


    missing=[

        r for r in reports

        if r[2]=="Missing"

    ]



    if not missing:

        st.info(
            "No reports"
        )


    for report in missing:


        st.divider()


        st.subheader(
            report[3]
        )


        st.write(
        f"""
Age : {report[4]}

Gender : {report[5]}

Location : {report[6]}

Status : {report[9]}
"""
        )


        matches=find_match(report)



        if matches:


            st.success(
                "Possible match found!"
            )


            for m in matches:


                st.warning(
                f"""
Found Person

Name : {m[3]}

Age : {m[4]}

Gender : {m[5]}

Location : {m[6]}

Clothing : {m[7]}

Description : {m[8]}
"""
                )


        else:

            st.info(
                "Searching..."
            )
