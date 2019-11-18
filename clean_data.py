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
python clean_data.py --ti telespor.csv --to telespor_clean.csv --ci capture.txt --co capture_clean.csv --allout all_data.csv --starttime '2019-10-11 10:17:00'
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
def readTelespor(infile, starttime=None, endtime=None):
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

    if starttime:
        #manually recorded starting time of the box
        starttime = datetime.strptime(starttime, "%Y-%m-%d %H:%M:%S")
        starttime = pytz.utc.localize(starttime)
        df = df[df.timestamp>=starttime]
        print('starttime', df.timestamp.min())
    if endtime:        
        #apply the endtime measured from the box
        endtime = pytz.utc.localize(endtime)
        df = df[df.timestamp<=endtime]
        print('endtime', df.timestamp.max())
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
    df['speed(knots)'] = df['speed(m/s)'] * 1.94384449
    df['speed(knots)'].fillna(-1, inplace=True)
    return df

def cleanTelespor(infile, outfile, starttime=None, endtime=None):
    df = readTelespor(infile, starttime=starttime, endtime=endtime)
    df, summary = measureEngineTime(df)
    print(summary)
    df = calculateSpeed(df)
    df.to_csv(outfile, index=False)
    return df

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
    if do_scale:
        df = scaleColumns(df, cols)
    if do_smooth:
        df = smoothColumns(df, cols)

    df = df.sort_values(by='time').reset_index(drop=True) #ms
    start = df['time'].values[0]
    df['dt'] = df['time'] - start 
    df['dt'] = pd.to_timedelta(df['dt'], unit='ms')
    df['timestamp'] = pd.to_datetime(starttime) + df['dt']
    endtime = df.timestamp.max()
    df.to_csv(outfile, index=False)
    return df, endtime

def merge_datasets(capture, telespor, interp_cols, drop_cols):
    telespor['timestamp'] = pd.to_datetime(telespor['timestamp'], utc=True)
    capture['timestamp'] = pd.to_datetime(capture['timestamp'], utc=True)
    starttime = telespor['timestamp'].values[0]
    capture['dt'] = pd.to_timedelta(capture['dt'])
    capture['timestamp'] = starttime + capture['dt']
    capture['timestamp'] = pd.to_datetime(capture['timestamp'], utc=True)
    capture.index = capture.timestamp
    telespor.index = telespor.timestamp
    combined = capture.join(telespor, how='outer', lsuffix='_cap', rsuffix='_ts')

    for col in interp_cols:
#        print('BEFORE: ', col, combined[col].shape, combined[col].dropna().shape)
        combined[col].interpolate(method='time', inplace=True)
#        print('AFTER: ', col, combined[col].shape, combined[col].dropna().shape)
        
    combined.reset_index(level=[0], inplace=True)
    combined.drop(columns=drop_cols, inplace=True)

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

    capture, endtime = cleanCapture(args.ci, args.co, args.starttime)
    telespor = cleanTelespor(args.ti, args.to, args.starttime, endtime)
    interp_cols = ['lat', 'long',
                   'batteryvoltage', 'temperature', 'engine_ON', 'speed(knots)',
                   'ax', 'ay', 'az',
                   'gx', 'gy', 'gz',
                   'ax_savgol', 'ay_savgol', 'az_savgol',
                   'gx_savgol', 'gy_savgol', 'gz_savgol']
    drop_cols = ['time', 'diff_ms', 'ID',
                 'temp', 'batt', 'timestamp_cap', 'timestamp_ts', 'temperature',
                 'ax', 'ay', 'az', 'gx', 'gy', 'gz',
                 't-1', 'lat-1', 'long-1', 'distance(m)', 'speed(m/s)',
                 'dt_ts', 'dt_cap', 'dt(s)']

    data = merge_datasets(capture, telespor, interp_cols, drop_cols)
    data.to_csv(args.allout, index=False)    

#Why is the starttime (first timestamp) after merging if about at hour lter than the set starttime?
