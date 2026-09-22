import pandas as pd
import re

file_path = r"c:\Users\Asus\Desktop\Personal\rgc lcg\isl_wise_train_detail_03082015_v1.csv"
df = pd.read_csv(file_path, header=None, quotechar="'")
df.columns = ['Train_No', 'Train_Name', 'SEQ', 'Station_Code', 'Station_Name', 'Arrival_Time', 'Departure_Time', 'Distance', 'Source_Code', 'Source_Name', 'Dest_Code', 'Dest_Name']

for col in df.columns:
    if df[col].dtype == object:
        df[col] = df[col].astype(str).str.strip().str.replace("'", "")

# Better matching for Mumbai
mumbai_exact = ['MUMBAI CENTRAL', 'CHURCHGATE', 'DADAR', 'MUMBAI CST', 'BANDRA TERMINUS', 'LOKMANYATILAK T', 'C SHIVAJI MAH T']
def is_mumbai(name):
    return name.upper() in mumbai_exact or 'MUMBAI' in name.upper() or 'DADAR' in name.upper() or 'BANDRA' in name.upper()

def is_navi_mumbai(name):
    nm_exact = ['VASHI', 'NERUL', 'BELAPUR', 'CBD BELAPUR', 'PANVEL', 'AIROLI', 'GHANSOLI', 'KOPARKHAIRANE', 'JUINAGAR', 'SANPADA', 'TURBHE', 'SEAWOODS', 'URAN']
    return name.upper() in nm_exact

df['is_mumbai'] = df['Station_Name'].apply(is_mumbai)
df['is_navi_mumbai'] = df['Station_Name'].apply(is_navi_mumbai)

mumbai_stations = df[df['is_mumbai']]['Station_Name'].unique()
navi_mumbai_stations = df[df['is_navi_mumbai']]['Station_Name'].unique()

print(f"Mumbai Exact: {list(mumbai_stations)}")
print(f"Navi Mumbai Exact: {list(navi_mumbai_stations)}")

mumbai_trains = set(df[df['is_mumbai']]['Train_No'])
navi_mumbai_trains = set(df[df['is_navi_mumbai']]['Train_No'])
connecting = mumbai_trains.intersection(navi_mumbai_trains)

print(f"Total trains serving Mumbai: {len(mumbai_trains)}")
print(f"Total trains serving Navi Mumbai: {len(navi_mumbai_trains)}")
print(f"Trains connecting Mumbai <-> Navi Mumbai: {len(connecting)}")

if connecting:
    sample_train = list(connecting)[0]
    st = df[df['Train_No'] == sample_train].sort_values('SEQ')
    print(f"Sample Connecting Train: {sample_train} - {st['Train_Name'].iloc[0]}")
    print(f"Source: {st['Source_Name'].iloc[0]}, Dest: {st['Dest_Name'].iloc[0]}")
    print(f"Route: {' -> '.join(st['Station_Name'].tolist())}")
    
# Find if there's any mention of local lines
print(df[df['Station_Name'].str.contains('CHURCHGATE', na=False)])
