import datetime, csv, random

data = {"timestamp" : datetime.datetime.now().isoformat("_"), "ambient" : random.gauss(10,5), "prox" : random.gauss(10,5)}
with open("log.csv", "ab") as f:
	writer = csv.DictWriter(f, fieldnames = data.keys())
	writer.writerow(data)
