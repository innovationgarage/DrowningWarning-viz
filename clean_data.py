import pytz
import argparse
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from datetime import datetime
import matplotlib.pyplot as plt
from geopy.distance import distance
from scipy.signal import savgol_filter
from sklearn.preprocessing import MinMaxScaler

"""
UDAGE:
python clean_data.py --ti telespor.csv --to telespor_clean.csv --ci capture.txt --co capture_clean.csv --allout all_data.csv --starttime '2019-10-11 10:17:00.0000'
"""
#Map categorical column to a colormap
def column2color(df, incol, outcol, cmap):
    if df[incol].nunique() <= len(cmap):
        cmap = cmap[:df[incol].nunique()]
        categories = list(df[incol].unique())
        col2col = dict(zip(categories, cmap))
        df[outcol] = df[incol].apply(lambda x: str(col2col[x]))
        return df

#Get and clean data that comes from telespor API eport
def readTelespor(infile):
    df = pd.read_csv(infile, delimiter=";")
    df.columns = ['ID', 'timestamp', 'seqnr', 'persnr', 'telespornr', 'sender',
                  'receiver', 'position, valid', 'long', 'lat', 'position_time',
                  'Debug 1', 'Debug 2', 'batteryvoltage', 'temperature', 'Alarm status',
                  'Alarm time ', 'UHF TX effect', 'dispersiontime', 'fieldstrength UHF',
                  'fieldstrength VHF', 'fieldstrength GSM', 'Debug', 'Firmware']
    to_drop = ['UHF TX effect', 'sender', 'receiver', 'dispersiontime',
               'telespornr', 'fieldstrength UHF', 'Alarm time ',
               'fieldstrength VHF', 'Alarm status',
               'Firmware', 'Debug', 'position, valid',
               'Debug 2', 'fieldstrength GSM', 'Debug 1',
               'seqnr', 'persnr', 'timestamp']
    df.drop(columns=to_drop, inplace=True)
    df['position_time'] = pd.to_datetime(df['position_time'], utc=True)
    df.sort_values(by='position_time', inplace=True)
    df.rename(columns={'position_time':'timestamp'}, inplace=True)
    df.reset_index(inplace=True, drop=True)
    return df

def measureEngineTime(df):
    df['t-1'] = df['timestamp'].shift(1)
    df['dt'] = df['timestamp'] - df['t-1']
#    df['engine_ON'] = df['batteryvoltage'].apply(lambda x: 1 if x==df.batteryvoltage.max() else 0)
    df['engine_ON'] = df['batteryvoltage']==df.batteryvoltage.max()
    summary = df.groupby('engine_ON')['dt'].sum().reset_index(level=[0])
    return df, summary

def calculateSpeed(df):
    df['t-1'] = df['timestamp'].shift(1)
    df['dt'] = df['timestamp'] - df['t-1']
    df['dt(s)'] = pd.to_numeric(df['dt'])*1e-9
    df['lat-1'] = df['lat'].shift(1)
    df['long-1'] = df['long'].shift(1)
    df = df[1:]
    df['distance(m)'] = df[['lat', 'long', 'lat-1', 'long-1']].apply(lambda x: distance((x[0], x[1]), (x[2], x[3])).m, axis=1)
    df['speed(m/s)'] = df['distance(m)'] / df['dt(s)']
    df['speed_knots'] = df['speed(m/s)'] * 1.94384449
    df['speed_knots'].fillna(-1, inplace=True)
    df.drop(columns=['t-1', 'dt', 'dt(s)', 'lat-1', 'long-1', 'distance(m)', 'speed(m/s)'], inplace=True)
    return df

def cleanTelespor(infile, outfile, drop_cols):
    df = readTelespor(infile)
    df, summary = measureEngineTime(df)
    print(summary)
    df = calculateSpeed(df)
    df.drop(columns=drop_cols, inplace=True)
    df.to_csv(outfile, index=False)
    return df, df.timestamp.min(), df.timestamp.max()

#Get and clean data captured in the box
def scaleColumns(df, cols):
    scaler = MinMaxScaler()
    df[cols] = scaler.fit_transform(df[cols])
    return df

def smoothColumns(df, cols):
    savgol_cols = ['{}_savgol'.format(col) for col in cols]
    for i, col in enumerate(cols):
        df[savgol_cols[i]] = savgol_filter(df[col], 101 ,3)
    return df

def cleanCapture(infile, outfile, starttime, do_scale=True, do_smooth=True):
    df = pd.read_csv(infile)
    cols = ['ax', 'ay', 'az', 'gx', 'gy', 'gz']
    a_sensitivity = 16384.
    g_sensitivity = 131.
    for col in ['ax', 'ay', 'az']:
        df[col] = df[col]/a_sensitivity #g force
    for col in ['gx', 'gy', 'gz']:
        df[col] = df[col]/g_sensitivity #degree per second
    if do_scale:
        df = scaleColumns(df, cols)
    if do_smooth:
        df = smoothColumns(df, cols)

    df = df.sort_values(by='time').reset_index(drop=True) #ms
    start = df['time'].values[0]
    df['dt'] = df['time'] - start 
    df['dt'] = pd.to_timedelta(df['dt'], unit='ms')
    df['timestamp'] = pd.to_datetime(starttime) + df['dt']
    df['timestamp'] = df['timestamp'].dt.tz_localize("Europe/Oslo")
    df['timestamp'] = df['timestamp'].dt.tz_convert("UTC")
    df.to_csv(outfile, index=False)
    return df, df.timestamp.min(), df.timestamp.max()

def merge_datasets(capture, telespor, interp_cols, drop_cols):
    capture.set_index('timestamp', inplace=True)
    telespor.set_index('timestamp', inplace=True)
    combined = capture.join(telespor, how='outer', lsuffix='_cap', rsuffix='_ts')

    combined.drop(columns=drop_cols, inplace=True)    
    for col in interp_cols:
#        print('BEFORE: ', col, combined[col].shape, combined[col].dropna().shape)
        combined[col].interpolate(method='time', inplace=True)
#        print('AFTER: ', col, combined[col].shape, combined[col].dropna().shape)
        
    combined.reset_index(level=[0], inplace=True)


    return combined
    
if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("--ti", default="telespor.csv", help="Raw CSV from Telespor API export")
    parser.add_argument("--to", default = "telespor_clean.csv", help="CSV file containing clean telespor data")
    parser.add_argument("--ci", default="capture.csv", help="Raw CSV from the box capture")
    parser.add_argument("--co", default = "capture_clean.csv", help="CSV file containing clean box capture data")
    parser.add_argument("--allout", default = "all_data.csv", help="CSV file containing the merged data")
    parser.add_argument("--starttime", default = '2019-10-11 10:17:00', help="the start timestamp")
    
    args = parser.parse_args()
    do_scale = False
    do_smooth = False

#######################################TEST###########################################
def fixTimeRange(capture, capture_start, capture_end, telespor, telespor_start, telespor_end):
    #I do this first because the frequency of data in capture is higher than that in telespor
    if capture_start>telespor_start:
        telespor = telespor[telespor.timestamp>=capture_start]
        telespor_start = telespor.timestamp.min()
    if capture_start<telespor_start:
        capture = capture[capture.timestamp>=telespor_start]
        capture_start = capture.timestamp.min()
    if capture_end<telespor_end:
        telespor = telespor[telespor.timestamp<=capture_end]
        telespor_end = telespor.timestamp.max()
    if capture_end>telespor_end:
        capture = capture[capture.timestamp>=telespor_end]
        capture_end = capture.timestamp.max()

    print('CAPTURE:', capture_start, capture_end)
    print('TELESPOR:', telespor_start, telespor_end)
    
    return capture, capture_start, capture_end, telespor, telespor_start, telespor_end
        
args = {}
args['ti'] = "data/first/telespor.csv"
args["to"] =  "data/first/telespor_clean.csv"
args["ci"] =  "data/first/capture_246058.txt"
args["co"] =  "data/first/capture_clean.csv"
args["allout"] =  "all_merged_1.csv"
args["starttime"] = '2019-10-11 10:17:00.000'
do_scale = False
do_smooth = False
if do_smooth:
    interp_cols = ['lat', 'long',
                   'batteryvoltage', 'temperature', 'engine_ON', 'speed_knots',
                   'ax', 'ay', 'az',
                   'gx', 'gy', 'gz',
                   'ax_savgol', 'ay_savgol', 'az_savgol',
                   'gx_savgol', 'gy_savgol', 'gz_savgol']
    drop_cols = ['time', 'diff_ms', 'ID',
                 'temp', 'batt', 'timestamp_cap', 'timestamp_ts', 'temperature',
                 'ax', 'ay', 'az', 'gx', 'gy', 'gz',
                 't-1', 'lat-1', 'long-1', 'distance(m)', 'speed(m/s)',
                 'dt_ts', 'dt_cap', 'dt(s)']        
else:
    interp_cols = ['lat', 'long',
                   'batteryvoltage', 'engine_ON', 'speed_knots',
                   'ax', 'ay', 'az',
                   'gx', 'gy', 'gz']
    drop_cols = ['ID', 'temperature']
    # drop_cols = ['time', 'diff_ms', 'ID',
    #              'temp', 'batt', 'timestamp_cap', 'timestamp_ts', 'temperature',
    #              't-1', 'lat-1', 'long-1', 'distance(m)', 'speed(m/s)',
    #              'dt_ts', 'dt_cap', 'dt(s)']

capture, capture_start, capture_end = cleanCapture(args["ci"], args["co"], args["starttime"], do_scale, do_smooth)
telespor, telespor_start, telespor_end = cleanTelespor(args["ti"], args["to"], drop_cols)

my_start = pd.to_datetime("2019-10-11 11:00:00+00:00", utc=True)
my_end = pd.to_datetime("2019-10-11 17:00:00+00:00", utc=True) 

capture.set_index('timestamp', inplace=True)
capture = capture.resample('10S').mean()

telespor.set_index('timestamp', inplace=True)
telespor = telespor.resample('10S').mean()

telespor.reset_index(level=[0], inplace=True)
capture.reset_index(level=[0], inplace=True)
telespor = telespor[telespor.timestamp>=my_start]
telespor = telespor[telespor.timestamp<=my_end]
telespor.reset_index(level=[0], inplace=True, drop=True)
capture = capture[capture.timestamp>=my_start]
capture = capture[capture.timestamp<=my_end]
capture.reset_index(level=[0], inplace=True, drop=True)

merged = pd.merge(capture, telespor, how='left', on='timestamp', sort=True)

for col in ['lat', 'long', 'batteryvoltage']:
    merged[col] = merged[col].fillna(method='ffill')
    merged[col] = merged[col].fillna(method='bfill') 
    merged['engine_ON'] = merged['batteryvoltage']==merged.batteryvoltage.max()

merged = calculateSpeed(merged)    
merged.to_csv(args["allout"], index=False)        
