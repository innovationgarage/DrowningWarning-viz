import pandas as pd
from scipy import stats
from scipy.signal import savgol_filter
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
import pytz
from geopy.distance import distance

def read_ts(infile, starttime=None, endtime=None):
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
    if endtime:        
        #apply the endtime measured from the box
        endtime = pytz.utc.localize(endtime)
        df = df[df.timestamp<=endtime]
    return df

def enginetime_from_ts(df):
    df['t-1'] = df['timestamp'].shift(1)
    df['dt'] = df['timestamp'] - df['t-1']
    df['engine_ON'] = df['batteryvoltage'].apply(lambda x: 1 if x==df.batteryvoltage.max() else 0)
    summary = df.groupby('engine_ON')['dt'].sum().reset_index(level=[0])
    return summary

def calculate_speed(df):
    df['t-1'] = df['timestamp'].shift(1)
    df['dt'] = df['timestamp'] - df['t-1']
    df['dt(s)'] = pd.to_numeric(df['dt'])*1e-9
    df['lat-1'] = df['lat'].shift(1)
    df['long-1'] = df['long'].shift(1)
    df = df[1:]
    df['distance(m)'] = df[['lat', 'long', 'lat-1', 'long-1']].apply(lambda x: distance((x[0], x[1]), (x[2], x[3])).m, axis=1)
    df['speed(m/s)'] = df['distance(m)'] / df['dt(s)']
    df['speed(knots)'] = df['speed(m/s)'] * 1.94384449
    return df

def scaleColumns(df, cols):
    scaler = MinMaxScaler()
    df[cols] = scaler.fit_transform(df[cols])
    return df

def main():
    infile = '../Maribell/data/first/telespor.csv'
    starttime = '2019-10-11 10:17:00'
    cols = ['batteryvoltage', 'speed(knots)']
    raw = read_ts(infile, starttime=starttime, endtime=None)
    summary = enginetime_from_ts(raw)
    df = calculate_speed(raw)
    scaled_df = scaleColumns(df, cols)
    plt.plot(scaled_df.timestamp, scaled_df['speed(knots)'], lw=3, label='speed (scaled)')
    plt.plot(scaled_df.timestamp, scaled_df.batteryvoltage, lw=3, label='battery (scaled)')
    plt.legend()
    plt.show()
    

# def getRange(df, startindex, endindex):
#     signal = df[startindex:endindex]
#     signal.reset_index(level=[0], drop=True, inplace=True)
#     return signal

# def smoothTriangle(data, degree):
#     triangle=np.concatenate((np.arange(degree + 1), np.arange(degree)[::-1])) # up then down
#     smoothed=[]

#     for i in range(degree, len(data) - degree * 2):
#         point=data[i:i + len(triangle)] * triangle
#         smoothed.append(np.sum(point)/np.sum(triangle))
#     # Handle boundaries
#     smoothed=[smoothed[0]]*int(degree + degree/2) + smoothed
#     while len(smoothed) < len(data):
#         smoothed.append(smoothed[-1])
#     return smoothed


# raw = pd.read_csv('all_data_1.csv')
# raw['timestamp'] = pd.to_datetime(raw['timestamp'])
# cols = ['ax', 'ay', 'az', 'gx', 'gy', 'gz']

# scaler = MinMaxScaler()
# raw[cols] = scaler.fit_transform(raw[cols])

# background = (30000, 40000)
# bg = getRange(raw, background[0], background[1])

# # dists = {}
# # fig, axs = plt.subplots(2,3)
# # ax = axs.flatten()
# # for i, col in enumerate(cols):
# #     sns.distplot(bg[col], ax=ax[i], fit=stats.norm)
# #     (mu, sigma) = stats.norm.fit(bg[col].values)
# #     print("mu={0}, sigma={1}".format(mu, sigma))
# #     dists[col] = (mu,sigma)
# # plt.show()

# start = 200000
# finish = 250000
# df = getRange(raw, start, finish)

# fig, axs = plt.subplots(2,3)
# ax = axs.flatten()
# for i, col in enumerate(cols):
#     y = df[col]
#     ax[i].plot(y, 'b')
#     if int(dists[col][1])%2 == 0: 
#         window = int(dists[col][1]) + 1
#     else: 
#         window = int(dists[col][1])

#     print(col, window)
#     w = savgol_filter(y, window, 2)
#     ax[i].plot(w, 'r')
#     df['{}_savgol'.format(col)] = w

# fig, axs = plt.subplots(2,3)
# ax = axs.flatten()
# for i, col in enumerate(cols):
#     y = df[col]
#     ax[i].plot(y, 'b')

#     w = smoothTriangle(y, 10)
#     ax[i].plot(w, 'r')
#     df['{}_triangle'.format(col)] = w
# plt.show()

