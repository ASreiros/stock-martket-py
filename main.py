import requests
import os
import smtplib
import html

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
THRESHOLD = 0.01

params = {
	"function": "TIME_SERIES_DAILY_ADJUSTED",
	"symbol": STOCK,
	"apikey": os.environ.get("ALPHA_API_KEY")
}

url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=IBM&apikey=demo'
try:
	r = requests.get(url=url, params=params)
	r.raise_for_status()
except Exception as e:
	print(e)
else:
	data = r.json()
	day = data['Meta Data']['3. Last Refreshed']
	keysList = list(data["Time Series (Daily)"].keys())

	yesterday = float(data["Time Series (Daily)"][keysList[0]]["4. close"])

	diff = yesterday - float(data["Time Series (Daily)"][keysList[1]]["4. close"])

	line = yesterday*THRESHOLD
	change = round((diff/yesterday)*100, 2)

	text = f"Subject:{COMPANY_NAME}\n\n"
	if change >= 0:
		text += f"{STOCK}: +{abs(change)}%\n"
	else:
		text += f"{STOCK}: -{abs(change)}%\n"

	if abs(diff) > line:
		try:
			url_news = f'https://newsapi.org/v2/everything?q={COMPANY_NAME}&from={day}&sortBy=popularity&apiKey={os.environ.get("NEWS_API_KEY")}'
			news_response = requests.get(url_news)
			news_response.raise_for_status()
		except Exception as e:
			print(e)
		else:
			text +="Read below:\n\n"
			news_list = news_response.json()['articles']
			if len(news_list) >= 3:
				nr = 3
			else:
				nr = len(news_list)

			for article in news_list[:nr]:
				text += f"Headline: {article['title']}\n"
				text += f"Brief: {article['description']}\n"
				text += f"{article['url']}\n"
				text += f"----------------------\n"

			text = text.encode('utf-8')
			connection1 = smtplib.SMTP(os.environ.get("EMAIL_TEST_SMTP"), os.environ.get("EMAIL_TEST_PORT"))
			connection1.starttls()
			connection1.login(user=os.environ.get("EMAIL_TEST_NAME"), password=os.environ.get("EMAIL_TEST_PASSWORD"))
			connection1.sendmail(
				from_addr=os.environ.get("EMAIL_TEST_NAME"),
				to_addrs=os.environ.get("EMAIL_RECEPIENT"),
				msg=text)
			connection1.close()




