import pandas as pd
import time
to_timestamp = lambda strdate: time.mktime(time.strptime(str(strdate), '%Y-%m-%d %H:%M:%S'))
import requests as r

START_DATE


if __name__ == '__main__':
	# Read and format data
	dfs = {0: {'df': pd.read_excel('../data/raw/Датасет3_Дтп.xlsx')}}
	for event_type in dfs.keys():
	    df = dfs[event_type]['df']
	    df['time'] = df['Время регистрации']
	    df['lat'] = df['Широта']
	    df['lon'] = df['Долгота']
	    df = df.drop('Время регистрации	Категория	Идентификатор Еас адреса	Идентификатор Еас здания	Широта	Долгота	Район'.split('\t'), axis=1)
	    dfs[event_type]['df'] = df
	

	    

   

