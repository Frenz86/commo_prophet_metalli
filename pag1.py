import streamlit as st
import investpy
import pandas as pd
import plotly.express as px
from datetime import datetime,date,timedelta
from matplotlib import pyplot as plt
from fbprophet import Prophet
from fbprophet.plot import plot_plotly

def main():
    ### Load COMMODITY
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

    option0 = st.selectbox( '',('Metalli', ''))
    #st.write('You selected:', option0)

    keys_to_extract_comm1 = ['Gold','Copper','Silver','Palladium','Platinum','Aluminum','Zinc','Lead','Nickel','Tin','Copper','Xetra-Gold',
    'MCX Aluminum Mini','MCX Aluminum','MCX Copper','MCX Copper Mini','MCX Gold 1 Kg','MCX Gold Guinea','MCX Gold Mini',
    'MCX Gold Petal','MCX Gold Petal Del','MCX Lead','MCX Lead Mini','MCX Nickel','MCX Nickel Mini','MCX Silver',
    'MCX Silver Micro','MCX Silver Mini','MCX Zinc','MCX Zinc Mini',]

    keys_to_extract_comm2 = ['US Coffee C','US Cotton #2','US Sugar #11','Orange Juice','US Cocoa','London Coffee','London Cocoa','London Sugar','Lumber',
    'MCX Cardamom','MCX Cotton','MCX Crude Palm Oil','MCX Kapas','MCX Mentha Oil','MCX Castor Seed','Live Cattle','Lean Hogs','Feeder Cattle',
    'US Soybean Meal','US Soybeans','US Wheat','US Corn','Oats','London Wheat','Rough Rice','US Soybean Oil']

    keys_to_extract_comm3= ['Brent Oil','Crude Oil WTI','London Gas Oil','Natural Gas','Heating Oil','Carbon Emissions','Gasoline RBOB','MCX Brent Oil',
    'MCX Crude Oil WTI','MCX Natural Gas']

    COMMODITY_1 = {key: COMMODITY[key] for key in keys_to_extract_comm1}
    #COMMODITY_2 = {key: COMMODITY[key] for key in keys_to_extract_comm2}
    #COMMODITY_3 = {key: COMMODITY[key] for key in keys_to_extract_comm3}

    def format_func(option0):
        return COMMODITY[option0]

    if option0 == 'Metalli':
        COMMODITY = COMMODITY_1
    # elif option0 == 'Beni Alimentari':
    # 	COMMODITY = COMMODITY_2
    # else:
    # 	COMMODITY = COMMODITY_3

    option = st.selectbox("", options=list(COMMODITY.keys()), format_func=format_func)

    today= date.today().strftime('%d/%m/%Y')

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
    section = 700 #st.slider('numero dati temporali', 
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
    df_clean = data2.copy()
    df_clean['ds']=pd.to_datetime(df_clean['ds'])
    df_clean['ds']=df_clean['ds'].dt.date
    
    index_start = df_clean.loc[df_clean['ds'].astype(str) == '2020-01-20']
    index_start = int(index_start.index[0])
    index_finish = df_clean.loc[df_clean['ds'].astype(str) == '2020-08-20']
    index_finish = int(index_finish.index[0])

    # st.write(index_start)
    # st.write(index_finish)    
    
    if  st.checkbox("Filtro Covid Attivo",True):
        st.write("Selezionare l'intervallo temporale da escludere (Crollo prezzi COVID):")
        slider_1, slider_2 = st.slider("",1,len(df_clean)-1,(index_start, index_finish))        
        #slider_1, slider_2 = st.slider("",1,len(df_clean)-1,(section-290, section-140))
        #slider_1, slider_2= st.slider("Inserire l'intervallo da escludere:", 0, 100, (25, 75), 0.5)
        #index1 because DATA column is index 1
        start_date = datetime.strptime(str(df_clean.iloc[slider_1][0]),'%Y-%m-%d') #lo 0 è la prima colonna dove si trova la data!!!!!!!!!!
        start_date = start_date.strftime('%Y-%m-%d')  # senza h --con ('%d %b %Y, %I:%M%p')
        end_date = datetime.strptime(str(df_clean.iloc[slider_2][0]),'%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')  # senza h --con ('%d %b %Y, %I:%M%p')
        st.info('Data inzio esclusione: **%s    **    Data fine esclusione: **%s**' % (start_date,end_date))

        inf = start_date
        sup = end_date

        mask_inf = (df_clean['ds'] <= datetime.strptime(inf, "%Y-%m-%d").date())
        df_inf =df_clean.loc[mask_inf]
        mask_sup = (df_clean['ds'] >= datetime.strptime(sup, "%Y-%m-%d").date())
        df_sup =df_clean.loc[mask_sup]

        data2 = pd.concat([df_inf,df_sup])
        #st.dataframe(data2)
    else:
        st.write("Non è stato escluso nessun intervallo temporale")
##############

    #odierno = round((data_reversed['Close'][0])*tasso_camb,2)
    dollaro = round((data_reversed['Close'][0])*1,2)
    #st.write("### Tasso di cambio $/€ odierno  :  " +str(tasso_camb))
    st.write("### Prezzo odierno : $ "+str(dollaro))


##################
    st.write("#### Selezionare intervallo massimo di predizione(in giorni):")
    windows = st.slider('', 
                            min_value=1,
                            max_value=180,
                            value=60,  
                            step=1)

    model = Prophet(changepoint_prior_scale=0.5,
                    seasonality_mode='multiplicative',
                    changepoint_range=0.8,
                    seasonality_prior_scale=2,
                    #holidays_prior_scale= 1,
                    #seasonality_mode='additive',
                    #growth='logistic', 
                    yearly_seasonality= 10
                    )

    model.fit(data2)
    future = model.make_future_dataframe(periods=windows,freq = 'B')
    forecast = model.predict(future)

    today2 = date.today()
    trentadays = today2 + timedelta(days=30)
    week1 = today2 + timedelta(days=7)
    week2 = today2 + timedelta(days=14)
    month = today2 + timedelta(days=30)

    fore_week1 = forecast.loc[forecast['ds'] == str(week1),['yhat']].values
    fore_week1 = round(fore_week1[0][0],2)
    #fore_week1 =round(fore_week1*tasso_camb,2)

    fore_week2 = forecast.loc[forecast['ds'] == str(week2),['yhat']].values
    fore_week2 = round(fore_week2[0][0],2)
    #fore_week2 =round(fore_week2*tasso_camb,2)
    
    fore_month = forecast.loc[forecast['ds'] == str(month),['yhat']].values
    fore_month = round(fore_month[0][0],2)
    #fore_month = round(fore_month*tasso_camb,2)

    st.write("* #### Previsione a 7 giorni : $ "+str(fore_week1))
    st.write("* #### Previsione a 14 giorni : $ "+str(fore_week2))
    st.write("* #### Previsione a 30 giorni : $ "+str(fore_month))

    st.write("### Se si preferisce, selezionare una data specifica di predizione :")
    start_date2 = st.date_input('', week2)
    start_date2 = str(start_date2)
    fore_value = forecast.loc[forecast['ds'] == start_date2,['yhat']].values
    fore_value = round(fore_value[0][0],2)
    #fore_eur =round(fore_value*tasso_camb,2)
    #st.write("* ### Prezzo predetto in data "+start_date2+" : $ "+str(fore_value))
    #st.write("* ### Prezzo predetto in data "+start_date2+" : € "+str(fore_eur))

    #st.markdown(f"<span style='color: blue;font-size: 20px;font-weight: bold;'> - Prezzo {list(COMMODITY.values())[list(COMMODITY.keys()).index(option)]} predetto in data {start_date2} : $ {fore_value}</span>",
    #			unsafe_allow_html=True)
    st.markdown(f"<span style='color: blue;font-size: 20px;font-weight: bold;'> - Prezzo {list(COMMODITY.values())[list(COMMODITY.keys()).index(option)]} predetto in data {start_date2} : $ {fore_value} </span>",
                unsafe_allow_html=True)
######################## new tass di cambio ##########################
    tassvar = st.slider('Selezionare un tasso di cambio $/€ ', 
                min_value=0.60,
                max_value=1.10,
                value=tasso_camb,  
                step=0.01)
    fore_eur2 =round(fore_value*tassvar,2)
    st.markdown(f"<span style='color: blue;font-size: 20px;font-weight: bold;'> - Prezzo {list(COMMODITY.values())[list(COMMODITY.keys()).index(option)]} predetto in data {start_date2} : € {fore_eur2}</span>",
                unsafe_allow_html=True)
##########################################################################

    fig = plot_plotly(model, forecast)
    fig.update_layout( 
                    yaxis_title='Prezzo '+str(list(COMMODITY.values())[list(COMMODITY.keys()).index(option)])+' $',
                    xaxis_title="Data",
    )
#################### vertical line ############
    fig.add_vline(x=date.today(), line_width=3, line_dash="dash", line_color="red")

##############################################
    st.plotly_chart(fig)

    ##########################################

    ############## plot component ######################
    model.plot_components(forecast)
    #plt.title("Global Products")
    plt.legend()
    st.pyplot()

    forecast_ = forecast.iloc[::-1]
    forecast_ = forecast_[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    forecast_.columns=["Data", "Prezzo", "Prezzo Min","Prezzo Max"]
    #st.dataframe(forecast_)
    
    data_reversed_ = data_reversed.copy()
    data_reversed_ = data_reversed_.iloc[::-1]
    data_reversed_.index =data_reversed_.index.set_names(['Data'])
    data_reversed_ = data_reversed_.reset_index()
    #st.dataframe(data_reversed_)
    st.write("## Analisi Performance Predictive")
    data_reversed_ = data_reversed_[['Data','Close']]
    aa = pd.merge(forecast_, data_reversed_, how='left', on='Data')
    aa.columns=["Data", "Prezzo", "Prezzo Min","Prezzo Max","Prezzo Reale"]
    aa['Delta'] = abs(aa['Prezzo']-aa["Prezzo Reale"])
    aa['err%'] = aa['Delta']/aa["Prezzo Reale"]*100
    aa[['err%']] = aa[['err%']].applymap("{0:.2f} %".format)
    aa = aa.round(decimals=2)
    aa[["Prezzo", "Prezzo Min","Prezzo Max","Prezzo Reale","Delta"]] = aa[["Prezzo", "Prezzo Min","Prezzo Max","Prezzo Reale","Delta"]].applymap("$ {0:.2f}".format)
    aa['Data'] = pd.to_datetime(aa['Data']).dt.normalize()
    st.dataframe(aa)

################################
    st.write("## Analisi storica commodity")
    #st.write("### Prezzo commodity "+str(list(COMMODITY.values())[list(COMMODITY.keys()).index(option)]+" in data:") )
    data_reversed1 = data_reversed[['Close']].applymap("$ {0:.2f}".format)
    data_reversed1['Close']=data_reversed1
    data_reversed1.columns=["Prezzi Storici"]
    #data_reversed1=data_reversed['Close']
    st.dataframe(data_reversed1)

    #st.write("#### selezionare date antecedentia quella odierna: ")

    today_ = date.today()
    today3 = date.today().strftime('%Y-%m-%d')
    #trentadays = today2 + datetime.timedelta(days=30)
    #st.write("#### Inserire la data di interesse")
    start_date = st.date_input('',today_)
    date666 = round(data_reversed['Close'][0],2)
    date_eur =round(date666*tasso_camb,2)
    st.write("  * ### Prezzo giornaliero '"+str(list(COMMODITY.values())[list(COMMODITY.keys()).index(option)])+"' :  $ " +str(date666))
    #st.text(f"Tasso di cambio $/€ odierno applicato: {tasso_camb}")
    #st.write("  * ### Prezzo '"+str(list(COMMODITY.values())[list(COMMODITY.keys()).index(option)])+"' in euro :  € " +str(date_eur))
    #st.text(f"Tasso di cambio $/€ odierno : {tasso_camb}")
    #st.text(f"Valore commodity in € : {date_eur}")

    data4 = data['Close'].to_frame('Price')
    data4['Date'] = data4.index
    data4['Date'] = pd.to_datetime( data4['Date'])
    data4['Date'] = data4['Date'].dt.date
    #st.dataframe(data4)
    fig2 = px.line(data4,x='Date', y="Price",
                title = ('Andamento temporale prezzi '+str(list(COMMODITY.values())[list(COMMODITY.keys()).index(option)])))

    #df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')

    #fig2 = px.line(df, x='Date', y='AAPL.High', title='Time Series with Range Slider and Selectors')

    fig2.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=5, label="5y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )

    fig2.update_layout(yaxis_title='Prezzo '+str(list(COMMODITY.values())[list(COMMODITY.keys()).index(option)])+' $ ',
                    xaxis_title="Intervallo temporale")
    st.plotly_chart(fig2)

if __name__ == '__main__':
	main()