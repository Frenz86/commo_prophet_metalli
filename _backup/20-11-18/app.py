import streamlit as st
import investpy
import pandas as pd
import plotly.express as px
import datetime
from matplotlib import pyplot as plt
from fbprophet import Prophet
from fbprophet.plot import plot_plotly

# Security
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



def main():
	"""Simple Login App"""

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
				#st.success("Logged In as {}".format(username))
				commodity_transl = ['Oro','Rame','Argento','Palladio','Platino','Alluminio','Zinco','Piombo','Nichel','Stagno',
				'Rame',"Xetra-Oro","MCX Aluminio Mini",'MCX Aluminio',"MCX Rame","MCX Rame Mini","MCX Oro 1 Kg","MCX Oro Guinea",
				"MCX Oro Mini","MCX oro Petal","MCX Oro Petal Del","MCX Piombo","MCX Piombo Mini","MCX Nickel",
				"MCX Nickel Mini","MCX Argento","MCX Argento Micro","MCX Argento Mini","MCX Zinco","MCX Zinco Mini",
				"US Caffè C","US Cotone # 2","US Zucchero # 11","Succo d'arancia","US Cacao","London Caffè",
				"London Cacao","London Zucchero","Legname","MCX Cardamomo","Cotone MCX","MCX Olio di Palma Crudo","MCX Cotone",
				"Olio di menta MCX","Seme di ricino MCX",'Bovini vivi','Maiali magri','Feeder Cattle',"Olio Brent","Olio Crudo WTI",
				"London Gas Oil",'Gas naturale','Olio bollente','Emissioni di carbonio',"Benzina RBOB","Olio Brent MCX","MCX Olio Crudo WTI",
				"MCX Gas Naturale","London Grano",'Riso grezzo',"Olio di semi di soia USA","Farina di soia americana",
				"Fagioli di soia americani","US Grano","Mais USA",'Avena']

				############### change in realtime  ##############
				import requests
				class CurrencyConverter():
					def __init__(self,url):
						self.data= requests.get(url).json()
						self.currencies = self.data['rates']
					
					def convert(self, from_currency, to_currency, amount): 
						initial_amount = amount 
						#first convert it into USD if it is not in USD.
						# because our base currency is USD
						if from_currency != 'USD' : 
							amount = amount / self.currencies[from_currency] 

						# limiting the precision to 4 decimal places 
						amount = round(amount * self.currencies[to_currency], 4) 
						return amount

				curr = ['USD','AUD','EUR','GBP']

				#currency selected for conversion
				in_curr = 'USD'
				out_curr = 'EUR'
				url = 'https://api.exchangerate-api.com/v4/latest/USD'
				converter = CurrencyConverter(url)
				tasso_camb = converter.convert(in_curr,out_curr,1)
				####################################################
				##########DIZIONARIO COMMODITY TRANSLATE ###########
				st.write("### Selezionare la commodity di interesse: ")
				commodity_ = investpy.commodities.get_commodities_list(group=None)
				zipbObj = zip(commodity_,commodity_transl)
				# Create a dictionary from zip object
				COMMODITY = dict(zipbObj)

				option0 = st.selectbox( '',('Metalli', 'Beni Alimentari', 'Energia'))
				#st.write('You selected:', option0)

				keys_to_extract_comm1 = ['Gold','Copper','Silver','Palladium','Platinum','Aluminum','Zinc','Lead','Nickel','Tin','Copper','Xetra-Gold',
				'MCX Aluminum Mini','MCX Aluminum','MCX Copper','MCX Copper Mini','MCX Gold 1 Kg','MCX Gold Guinea','MCX Gold Mini',
				'MCX Gold Petal','MCX Gold Petal Del','MCX Lead','MCX Lead Mini','MCX Nickel','MCX Nickel Mini','MCX Silver',
				'MCX Silver Micro','MCX Silver Mini','MCX Zinc','MCX Zinc Mini',]

				keys_to_extract_comm2 = ['US Coffee C','US Cotton #2','US Sugar #11','Orange Juice','US Cocoa','London Coffee','London Cocoa','London Sugar','Lumber',
				'MCX Cardamom','MCX Cotton','MCX Crude Palm Oil','MCX Kapas','MCX Mentha Oil','MCX Castor Seed','Live Cattle','Lean Hogs','Feeder Cattle',
				'US Soybean Meal','US Soybeans','US Wheat','US Corn','Oats','London Wheat','Rough Rice','US Soybean Oil']

				keys_to_extract_comm3 = ['Brent Oil','Crude Oil WTI','London Gas Oil','Natural Gas','Heating Oil','Carbon Emissions','Gasoline RBOB','MCX Brent Oil',
				'MCX Crude Oil WTI','MCX Natural Gas']

				COMMODITY_1 = {key: COMMODITY[key] for key in keys_to_extract_comm1}
				COMMODITY_2 = {key: COMMODITY[key] for key in keys_to_extract_comm2}
				COMMODITY_3 = {key: COMMODITY[key] for key in keys_to_extract_comm3}

				def format_func(option0):
					return COMMODITY[option0]

				if option0 == 'Metalli':
					COMMODITY = COMMODITY_1
				elif option0 == 'Beni Alimentari':
					COMMODITY = COMMODITY_2
				else:
					COMMODITY = COMMODITY_3

				option = st.selectbox("", options=list(COMMODITY.keys()), format_func=format_func)
				#st.write(f"..... {option}")
				#st.write(f"You selected option {option} tradotta {format_func(option)}")

				today=datetime.date.today().strftime('%d/%m/%Y')

				#asset = st.sidebar.selectbox('Selezionare la Commodity',commodity_)




				#asset = st.sidebar.selectbox('Selezionare la Commodity',commodity_)

				commo = investpy.get_commodity_historical_data(commodity=option, 
															from_date='01/01/1980', 
															to_date=today,
															as_json=False,
															order='ascending')
				data = commo.copy()
				data.index.name = None
				lib_ton = 2204.622621
				if option == 'Copper':
					data = data[['Close']].dropna()
					data['Close']*=lib_ton

				data_reversed = data.iloc[::-1]
				#st.dataframe(data_reversed)
				#################################
				section = 600 #st.slider('numero dati temporali', 
											# min_value=30,
											# max_value=min([2000, data.shape[0]]),
										# value=600,  
										# step=10)
				#section=600
				data2 = data[-section:]['Close'].to_frame('Price')
				data2['Date'] = data2.index
				data2 = (
					data2['Price']
					.dropna()
					.to_frame()
					.reset_index()
					.rename(columns={"index": "ds", 'Price': "y"})
				)
				#st.write("# Forecast - Modello Predittivo " +str(list(COMMODITY.values())[list(COMMODITY.keys()).index(option)]))

				st.write("#### Selezionare intervallo massimo di predizione(in giorni):")
				windows = st.slider('', 
											min_value=1,
											max_value=180,
											value=60,  
											step=1)


				model = Prophet()
				model.fit(data2)
				future = model.make_future_dataframe(periods=windows)
				forecast = model.predict(future)


				fig = plot_plotly(model, forecast)
				fig.update_layout( 
								yaxis_title='Prezzo '+str(list(COMMODITY.values())[list(COMMODITY.keys()).index(option)])+' $',
								xaxis_title="Data",
				)

				st.plotly_chart(fig)

				##########################################
				odierno = round((data_reversed['Close'][0])*tasso_camb,2)
				st.write("### Tasso di cambio $/€ odierno  :  " +str(tasso_camb))
				st.write("### Prezzo odierno : € "+str(odierno))
				
				today2 = datetime.date.today()
				trentadays = today2 + datetime.timedelta(days=30)
				week1 = today2 + datetime.timedelta(days=7)
				week2 = today2 + datetime.timedelta(days=14)
				month = today2 + datetime.timedelta(days=30)

				fore_week1 = forecast.loc[forecast['ds'] == str(week1),['yhat']].values
				fore_week1 = round(fore_week1[0][0],2)
				fore_week1 =round(fore_week1*tasso_camb,2)
	
				fore_week2 = forecast.loc[forecast['ds'] == str(week2),['yhat']].values
				fore_week2 = round(fore_week2[0][0],2)
				fore_week2 =round(fore_week2*tasso_camb,2)
				
				fore_month = forecast.loc[forecast['ds'] == str(month),['yhat']].values
				fore_month = fore_month[0][0]
				fore_month = round(fore_month*tasso_camb,2)

				st.write("* #### Previsione a 7 giorni : € "+str(fore_week1))
				st.write("* #### Previsione a 14 giorni : € "+str(fore_week2))
				st.write("* #### Previsione a 30 giorni : € "+str(fore_month))

				st.write("### oppure selezionare una data specifica di predizione :")
				start_date2 = st.date_input('', week2)
				start_date2 = str(start_date2)
				fore_value = forecast.loc[forecast['ds'] == start_date2,['yhat']].values
				fore_value = round(fore_value[0][0],2)
				fore_eur =round(fore_value*tasso_camb,2)
				#st.write("* ### Prezzo predetto in data "+start_date2+" : $ "+str(fore_value))
				#st.write("* ### Prezzo predetto in data "+start_date2+" : € "+str(fore_eur))

				#st.markdown(f"<span style='color: blue;font-size: 20px;font-weight: bold;'> - Prezzo {list(COMMODITY.values())[list(COMMODITY.keys()).index(option)]} predetto in data {start_date2} : $ {fore_value}</span>",
				#			unsafe_allow_html=True)
				st.markdown(f"<span style='color: blue;font-size: 20px;font-weight: bold;'> - Prezzo {list(COMMODITY.values())[list(COMMODITY.keys()).index(option)]} predetto in data {start_date2} : € {fore_eur}</span>",
							unsafe_allow_html=True)

				############## plot component ######################
				model.plot_components(forecast)
				#plt.title("Global Products")
				plt.legend()
				st.pyplot()

################################
				st.write("## Analisi storica commodity")
				#st.write("### Prezzo commodity "+str(list(COMMODITY.values())[list(COMMODITY.keys()).index(option)]+" in data:") )
				st.dataframe(data_reversed)
	
				#st.write("#### selezionare date antecedentia quella odierna: ")
	
				today_ = datetime.date.today()
				today3=datetime.date.today().strftime('%Y-%m-%d')
				#trentadays = today2 + datetime.timedelta(days=30)
				#st.write("#### Inserire la data di interesse")
				start_date = st.date_input('',today_)
				date = round(data_reversed['Close'][0],2)
				date_eur =round(date*tasso_camb,2)
				st.write("  * ### Prezzo giornaliero '"+str(list(COMMODITY.values())[list(COMMODITY.keys()).index(option)])+"' :  $" +str(date))
				st.write("  * ### Prezzo '"+str(list(COMMODITY.values())[list(COMMODITY.keys()).index(option)])+"' in euro :  € " +str(date_eur))
				#st.text(f"Tasso di cambio $/€ odierno : {tasso_camb}")
				#st.text(f"Valore commodity in € : {date_eur}")

				data4 = data['Close'].to_frame('Price')
				data4['Date'] = data4.index
				fig2 = px.line(data4,x='Date', y="Price",
							title = 'Andamento temporale prezzi '+str(list(COMMODITY.values())[list(COMMODITY.keys()).index(option)]))

				fig2.update_xaxes(
					rangeslider_visible= True,
					rangeselector=dict(
										buttons = list([
										dict(count = 3,label = '1y',step='year',stepmode = "backward"),
										dict(count = 9,label = '3y',step='year',stepmode = "backward"),
										dict(count = 15,label = '5y',step='year',stepmode = "backward"),
										dict(step= 'all')
											])        
										)
								)

				fig2.update_layout(yaxis_title='Prezzo '+str(list(COMMODITY.values())[list(COMMODITY.keys()).index(option)])+' $',
								xaxis_title="Intervallo temporale")
				st.plotly_chart(fig2)



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