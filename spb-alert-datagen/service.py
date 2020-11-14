import time
import logging
import random
import requests
import pandas as pd
from threading import Thread


def generator(values):
	for value in values:
		yield value


def main():
	data_list = [
		"raw_data/Датасет1_Отключения_ГВС.xlsx",
		"raw_data/Датасет2_Отключения_ХВС.xlsx",
		"raw_data/Датасет3_Дтп.xlsx",
		"raw_data/Датасет4_Пожары.xlsx"
	]
	result_dataframe: pd.DataFrame = None
	i = 0
	cat = {
		3: "fire",
		2: "accident",
		1: "bad_cold_water",
		0: "bad_hot_water"
	}
	for df in list(map(pd.read_excel, data_list)):
		df["Категория"] = cat[i]
		if result_dataframe is None:
			result_dataframe = df
		else:
			result_dataframe = result_dataframe.append(df)
		i += 1
	result_dataframe = result_dataframe[["Время регистрации", "Широта", "Долгота", "Категория"]]
	to_datetime = lambda timestamp: timestamp.strftime('%m/%d/%y %H:%M')
	result_dataframe["Время регистрации"] = list(map(to_datetime, result_dataframe["Время регистрации"].tolist()))

	data = sorted(result_dataframe.values, key=lambda x: x[0])
	row_gen = generator(data)

	def run():
		try:
			while True:
				sleep_time = random.randint(0, 3)
				row = next(row_gen)
				time.sleep(sleep_time)
				url = "http://localhost:8888/api.pushEvent"
				event = {
					"date": row[0],
					"lat": row[1],
					"lon": row[2],
					"event": row[3]
				}
				logging.warning(event)
				requests.post(url, event)
		except Exception as e:
			logging.warning(e)

	threads = 4
	threads_instances = [Thread(target=run) for _ in range(threads)]
	for thread in threads_instances:
		thread.start()
	for thread in threads_instances:
		thread.join()


if __name__ == '__main__':
	main()
