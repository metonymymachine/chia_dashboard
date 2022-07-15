import streamlit as st
import pymongo
import pandas as pd
import numpy as np
from datetime import datetime

st.title("Chia Dashboard")
@st.experimental_singleton

def init_connection():
    return pymongo.MongoClient(**st.secrets["mongo"])

client = init_connection()
# Pull data from the collection.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)

def get_data():
    db = client.chia
    items = db.daily.find()
    items = list(items)  # make hashable for st.experimental_memo
    return items

# Passwort protection below
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["access"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():
    items = get_data()
    # st.success("🎉 Connected to Chia Dashboard")
    index_length = list(range(0, len(items)))

    df = pd.DataFrame(
        items,
        index=index_length,
        # columns=['_id', 'Total chia']
    )
    # df = df.astype(str)
    df['_id'] = pd.to_datetime(df['_id'], format="%Y-%m-%d")


    # Metrics on top
    today = items[len(items)-1]
    yesterday = items[len(items)-2]
    date_today = datetime.strptime(today['_id'], '%Y-%m-%d').strftime('%d.%m.%y')
    label_today = str("Total Chia " + date_today)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label=label_today, value=round(today['Total chia'],2), delta=today['Total chia']-yesterday['Total chia'])
    col2.metric(label="Plots", value=items[len(items)-1]['all_farmers']['total'], delta=today['all_farmers']['total']-yesterday['all_farmers']['total'])
    col3.metric(label="Plots Farmer 01", value=items[len(items)-1]['farmer01']['total'], delta=today['farmer01']['total']-yesterday['farmer01']['total'])
    col4.metric(label="Plots Farmer 03", value=items[len(items)-1]['farmer03']['total'], delta=today['farmer03']['total']-yesterday['farmer03']['total'])


    # set index
    df = df.set_index('_id')

    # change order of columns
    df = df.sort_index(ascending=False)

    # nur die Spalte "total chia" anzeigen
    df = df['Total chia'] 

    # Slicing
    # df = df[100:206:1]

    if st.checkbox('Show Dataframe'):
        st.subheader('Dataframe')
        st.dataframe(df)

    st.bar_chart(df)



    if st.checkbox('Show raw data'):
        st.subheader('Raw data')
        st.write(items)






# password not correct
else:
    st.stop()

