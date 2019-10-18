import pandas as pd
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
from scipy.signal import savgol_filter
import pytz
import argparse
"""
UDAGE:
python clean_data --ti telespor.csv --to telespor_clean.csv --ci capture.txt --co capture_clean.csv
"""
#Get and clean data that comes from telespor API eport
def clean_telespor(infile, outfile):
    df = pd.read_csv(infile, delimiter=";")
    df.columns = ['ID', 'timestamp', 'seqnr', 'persnr', 'telespornr', 'sender',
                  'receiver', 'position, valid', 'long', 'lat', 'position_time',
                  'Debug 1', 'Debug 2', 'battryvoltage', 'temperature', 'Alarm status',
                  'Alarm time ', 'UHF TX effect', 'dispersiontime', 'fieldstrength UHF',
                  'fieldstrength VHF', 'fieldstrength GSM', 'Debug', 'Firmware']
    to_drop = ['UHF TX effect', 'sender', 'receiver', 'dispersiontime',
               'telespornr', 'fieldstrength UHF', 'Alarm time ',
               'fieldstrength VHF', 'Alarm status',
               'Firmware', 'Debug', 'battryvoltage', 'position, valid',
               'Debug 2', 'fieldstrength GSM', 'Debug 1',
               'seqnr', 'persnr', 'timestamp']
    df.drop(columns=to_drop, inplace=True)
    df['position_time'] = pd.to_datetime(df['position_time'], utc=True)
    df.sort_values(by='position_time', inplace=True)
    df.reset_index(inplace=True, drop=True)
    
    #manually recorded starting time of the box
    intime = datetime.strptime('2019-10-11 10:17:00', "%Y-%m-%d %H:%M:%S")
    intime = pytz.utc.localize(intime)
    df = df[df.position_time>intime]

    df.drop_duplicates(subset=['position_time'], inplace=True)
    
    df.to_csv(outfile, index=False)
    return df

#Get and clean data captured in the box
def clean_capture(infile, outfile):
    df = pd.read_csv(infile)
    cols = ['ax', 'ay', 'az', 'gx', 'gy', 'gz']
    scaler = MinMaxScaler()
    df[cols] = scaler.fit_transform(df[cols])
    savgol_cols = ['{}_savgol'.format(col) for col in cols]
    for i, col in enumerate(cols):
        df[savgol_cols[i]] = savgol_filter(df[col], 101 ,3)

    df = df.sort_values(by='time').reset_index(drop=True) #ms
    start = df['time'].values[0]
    df['dt'] = df['time'] - start 
    df['dt'] = pd.to_timedelta(df['dt'], unit='ms')
    
    df.to_csv(outfile, index=False)
    return df

def merge_datasets(capture, telespor):
    start = telespor['position_time'].values[0]
    capture['timestamp'] = start + capture['dt']
    capture['timestamp'] = pd.to_datetime(capture['timestamp'], utc=True)
    capture = capture.resample('1S', on='timestamp').mean()
    data = capture.merge(telespor, left_on='timestamp', right_on='position_time', how='right')
    data.drop(columns=['time', 'diff_ms', 'batt', 'ID'], inplace=True)
    data.dropna().to_csv('all_data.csv', index=False)
    return data

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("--ti", default="telespor.csv", help="Raw CSV from Telespor API export")
    parser.add_argument("--to", default = "telespor_clean.csv", help="CSV file containing clean telespor data")
    parser.add_argument("--ci", default="capture.csv", help="Raw CSV from the box capture")
    parser.add_argument("--co", default = "capture_clean.csv", help="CSV file containing clean box capture data")
    args = parser.parse_args()

    telespor = clean_telespor(args.ti, args.to)
    capture = clean_capture(args.ci, args.co)
    data = merge_datasets(capture, telespor)
    
    
