import pandas as pd
from datetime import datetime
import pytz

"""
Some cleaning happens here but are not crucial!
"""

df = pd.read_csv('telespor_clean.csv')
df['position_time'] = pd.to_datetime(df['position_time'])

#manually recorded starting time of the box
intime = datetime.strptime('2019-10-11 10:17:00', "%Y-%m-%d %H:%M:%S")
intime = pytz.utc.localize(intime)

df = df[df.position_time>intime]
df.to_csv('telespor_clean_relevant.csv', index=False)
