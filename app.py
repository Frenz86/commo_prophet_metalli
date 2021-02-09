import streamlit as st
import investpy
import pandas as pd
import plotly.express as px
import datetime
from matplotlib import pyplot as plt
from fbprophet import Prophet
from fbprophet.plot import plot_plotly
from pag1 import main as pag1

#to monitor logging
import csv
from datetime import datetime as dt
import base64
import gspread

st.set_option('deprecation.showPyplotGlobalUse', False)

# Security##
#passlib,hashlib,bcrypt,scrypt
import hashlib
def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False
# DB Management
import sqlite3 
conn = sqlite3.connect('data.db')
c = conn.cursor()
# DB  Functions
def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username,password):
	c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
	conn.commit()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data


def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data

### to monitor the logging
def get_time():
    d = dt.now().strftime("%Y-%m-%d-%H:%M:%S")
    return d

def write_data_on_csv(filename, listdata):
    with open(filename, mode='a') as f:
        fw = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        fw.writerow(listdata)

name = 'COMMODITY-METALS'

def main():
	# ################ css background #########################
	page_bg_img = '''
	<style>
	body {
	background-image: url("https://i.pinimg.com/originals/85/6f/31/856f31d9f475501c7552c97dbe727319.jpg");
	background-size: cover;
	}
	</style>
	'''
	st.markdown(page_bg_img, unsafe_allow_html=True)
############################################################
	################ load logo from web #########################
	from PIL import Image
	import requests
	from io import BytesIO
	url='https://frenzy86.s3.eu-west-2.amazonaws.com/fav/logo.png'
	response = requests.get(url)
	image = Image.open(BytesIO(response.content))
	st.image(image, caption='',use_column_width=True)
	##############################################################
	st.title("Predictive Analytics")

	#menu = ["Login","SignUp"] # per creare password
	menu = ["Login"]
	choice = st.sidebar.selectbox("Menu",menu)

	if choice == "Login":
		st.subheader("")

		username = st.sidebar.text_input("User Name")
		password = st.sidebar.text_input("Password",type='password')
		if st.sidebar.checkbox("Login"):
			# if password == '12345':
			create_usertable()
			hashed_pswd = make_hashes(password)

			result = login_user(username,check_hashes(password,hashed_pswd))
			if result:
                ########    WRITE CSV AS LOGGED TIMESTAMP ###########
				#st.success("Logged In as {}".format(username))
				log = ("{}".format(username))
				time_print = get_time()
				#write_data_on_csv(filename="login.csv",listdata=[time_print,name,log]) # to wite csv in local
				print("Logged In as {}".format(username))
				gc = gspread.service_account(filename='credentials.json')
				sh = gc.open("Login_webapp")
				worksheet = sh.sheet1
				#print(len(res))
				listdata=[time_print,name,log]
				worksheet.append_row(listdata)# no specify the row
				### retrieve data ###
				res = worksheet.get_all_records() # list of dictionaries
				res = worksheet.get_all_values() # list of lists
				print(res)

################################################
				pag1()

#################################################

################################################

			else:
				st.warning("Incorrect Username/Password")
	else:
		st.subheader("Create New Account")
		new_user = st.text_input("Username")
		new_password = st.text_input("Password",type='password')

		if st.button("Signup"):
			create_usertable()
			add_userdata(new_user,make_hashes(new_password))
			st.success("You have successfully created a valid Account")
			st.info("Go to Login Menu to login")

if __name__ == '__main__':
	main()


