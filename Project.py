import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import matplotlib.pyplot as plt


DATA_URL = (
"C:\\Users\\KIIT\Desktop\\Coding\\Data Analytics project\\Motor_Vehicle_Collisions_-_Crashes.csv"
)

st.title("Motor Vehicle Colliion in NYC")
st.markdown("Streamlit Dashboard that will analyze the motor vehicle collison in NYC")

@st.cache(persist=True)
def gather_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset = ['LATITUDE','LONGITUDE'],inplace = True)#Dropping the N/a values
    lowercase = lambda x: str(x).lower()#lowercasing the data
    data.rename(lowercase, axis='columns',inplace=True)
    data.rename(columns={'crash_date_crash_time': 'Date/Time'},inplace=True)
    return data

data = gather_data(100000)
original_data = data
st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of People injured",0,10)
st.map(data.query("injured_persons >= @injured_people")[["latitude","longitude"]].dropna(how="any"))

st.header("How many collisions occur in a given time of the day?")
hour = st.slider("Hour to look at",0,23)
data = data[data['Date/Time'].dt.hour == hour]

st.markdown("Vehicle Collision between %i:00 and %i:00"%(hour, (hour+1)%24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

st.write(pdk.Deck(
   map_style="mapbox://styles/mapbox/light-v9",
   initial_view_state={
         "latitude":midpoint[0],
         "longitude":midpoint[1],
         "zoom": 11,
         "pitch":50,

   },
   layers=[
       pdk.Layer(
       "HexagonLayer",
       data=data[['Date/Time','latitude','longitude']],
       get_position=['longitude','latitude'],
       radius=100,
       extruded = True,
       pickable =True,
       elevation_scale = 4,
       elevation_range=[0,1000],
       ),
   ],
))


st.subheader("Breakdown by minute between %i:00 and %i:00"%(hour,(hour+1)%24))
filtered = data[(data['Date/Time'].dt.hour >=hour) & (data['Date/Time'].dt.hour<(hour +1))]
hist = np.histogram(filtered['Date/Time'].dt.minute,bins=60,range=(0,60))[0]
chart_data = pd.DataFrame({'minute': range(60),'crashes':hist})
fig= plt.bar(chart_data, x='minute',y='crashes', hover_data=['minute','crashes'], height=400)
st.write(fig)

st.header("5 Most dangerous streets by affected type")
select = st.selectbox('Affected  type of people',['Pedestrians','Cyclist','Motorists'])
if select=='Pedestrians':
    st.write(original_data.query("injured_pedestrians >=1")[["on_street_name","injured_pedestrians"]].sort_values(by=['injured_pedestrians'],ascending=False).dropna(how='any')[:5])
elif select=='Cyclist':
    st.write(original_data.query("injured_cyclists >=1")[["on_street_name","injured_cyclists"]].sort_values(by=['injured_cyclists'],ascending=False).dropna(how='any')[:5])
else:
    st.write(original_data.query("injured_motorists >=1")[["on_street_name","injured_motorists"]].sort_values(by=['injured_motorists'],ascending=False).dropna(how='any')[:5])

if st.checkbox("Show Raw Data",False):
    st.subheader("Raw Data")
    st.write(data)

