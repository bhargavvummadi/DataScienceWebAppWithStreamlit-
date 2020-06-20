import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk   #this is imp visulization for 3d
import plotly.express as px


DATA_URL='Motor_Vehicle_Collisions_-_Crashes.csv'

# st.title("Hello world")
# st.markdown('## Font as h2')
st.title("Motor Vehicle Collisions in New York City ")
st.markdown("App is a Streamlit dashboard NYC collisions 🚗")
@st.cache(persist=True)
def load_data(nrows):
    data=pd.read_csv(DATA_URL,nrows=nrows,parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset=['LATITUDE','LONGITUDE'],inplace=True)
    lowercase=lambda x: str(x).lower()
    data.rename(lowercase,axis='columns',inplace=True)
    data.rename(columns={'crash_date_crash_time':'date/time'},inplace=True)
    return data
data=load_data(100000)
original_data=data
st.header("What is no of persons injured in collision")
injured_person=st.slider("No of persons injured in accident",1,20)
st.map(data.query("injured_persons==@injured_person")[['latitude','longitude']].dropna(how="any"))

st.header("No of collisions occured at a given hour")
# hour=st.sidebar.slider("hour of collision",0,23)
#displays slider in side navbar of the web page
hour=st.slider("hour of collision",0,23)
data=data[data['date/time'].dt.hour==hour]
st.markdown("No of collisions occured between %i:00 and %i:00" % (hour,(hour+1) % 24))
midpoint=(np.average(data['latitude']),np.average(data['longitude']))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/dark-v9",
     mapbox_key=None, google_maps_key=None, 
     initial_view_state={
         "latitude":midpoint[0],
         "longitude":midpoint[1],
         "zoom":11,
         "pitch":50,
     },
        layers=[
            pdk.Layer(
                'HexagonLayer',
                data=data[['date/time','latitude','longitude']],
                get_position=['longitude', 'latitude'],
                radius=100,
                auto_highlight=True,
                elevation_scale=4,
                pickable=True,
                elevation_range=[0, 1000],
                extruded=True,
                coverage=1),  
            
        ]
     ,width="100%", height=500, tooltip=True, description=None, effects=None, map_provider="mapbox"
)
)


st.subheader(" Accidents between %i:00 and %i:00" %(hour,(hour+1)%24))
filtered_data=data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour+1)) 
]
hist=np.histogram(filtered_data['date/time'].dt.minute,bins=60,range=(0,60))[0]
char_data=pd.DataFrame({'minute':range(60),'crashes':hist})
fig=px.bar(char_data,x='minute',y='crashes',hover_data=['minute','crashes'],height=400)
st.write(fig)

st.header("Top 5 dangerous streets by affected type")
select=st.selectbox("Affected type of people",['Pedestrians','Cyclists','Motorists'])
if select=='Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[['on_street_name','injured_pedestrians']].sort_values(by="injured_pedestrians",ascending=False).dropna(how='any')[:5])
elif select=='Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[['on_street_name','injured_cyclists']].sort_values(by="injured_cyclists",ascending=False).dropna(how='any')[:5])
elif select=='Motorists':
    st.write(original_data.query("injured_motorists >= 1")[['on_street_name','injured_motorists']].sort_values(by="injured_motorists",ascending=False).dropna(how='any')[:5])

if st.checkbox("Show Raw Data",False):
    st.subheader("Raw Data:")
    st.write(data)