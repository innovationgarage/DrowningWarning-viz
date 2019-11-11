import pandas as pd
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
from scipy.signal import savgol_filter
import pytz
import argparse
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
def clean_telespor(infile, outfile, starttime, endtime):
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
    
    #manually recorded starting time of the box
    starttime = datetime.strptime(starttime, "%Y-%m-%d %H:%M:%S")
    starttime = pytz.utc.localize(starttime)
    df = df[df.timestamp>=starttime]

    #apply the endtime measured from the box
    endtime = pytz.utc.localize(endtime)
    df = df[df.timestamp<=endtime]
    
    df.drop_duplicates(subset=['timestamp'], inplace=True)

    # cmap = ['#b10026', '#fc4e2a', '#feb24c', '#ffffb2'] #Hight to low
    # df = column2color(df, 'batteryvoltage', 'bvcolor', cmap)
    
    df.to_csv(outfile, index=False)
    return df

#Get and clean data captured in the box
def clean_capture(infile, outfile, starttime):
    df = pd.read_csv(infile)
    cols = ['ax', 'ay', 'az', 'gx', 'gy', 'gz']
    scaler = MinMaxScaler()
    df[cols] = scaler.fit_transform(df[cols])
    
    # savgol_cols = ['{}_savgol'.format(col) for col in cols]
    # for i, col in enumerate(cols):
    #     df[savgol_cols[i]] = savgol_filter(df[col], 101 ,3)

    df = df.sort_values(by='time').reset_index(drop=True) #ms
    start = df['time'].values[0]
    df['dt'] = df['time'] - start 
    df['dt'] = pd.to_timedelta(df['dt'], unit='ms')
    df['timestamp'] = pd.to_datetime(starttime) + df['dt']
    endtime = df.timestamp.max()
    df.to_csv(outfile, index=False)
    return df, endtime

def merge_datasets(capture, telespor, merged_file):
    starttime = telespor['timestamp'].values[0]
    capture['timestamp'] = starttime + capture['dt']
    capture['timestamp'] = pd.to_datetime(capture['timestamp'], utc=True)
    capture.index = capture.timestamp
    telespor.index = telespor.timestamp
    combined = capture.join(telespor, how='outer', lsuffix='_cap', rsuffix='_ts')
    for col in ['lat', 'long', 'batteryvoltage', 'temperature',
                'ax', 'ay', 'az',
                'gx', 'gy', 'gz']:
        combined[col].interpolate(method='time', inplace=True)
    combined.reset_index(level=[0], inplace=True)
    combined.drop(columns=['time', 'diff_ms', 'ID'], inplace=True)

    combined.drop(columns=['temp', 'batt', 'dt',
                           'timestamp_cap', 'timestamp_ts',
                           'temperature'], inplace=True)

    combined.to_csv(merged_file, index=False)
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

    capture, endtime = clean_capture(args.ci, args.co, args.starttime)
    telespor = clean_telespor(args.ti, args.to, args.starttime, endtime)
    data = merge_datasets(capture, telespor, args.allout)
    
    
