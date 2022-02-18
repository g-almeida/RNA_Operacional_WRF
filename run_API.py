import datetime
import API as obs

x = 0
while x < 2:

    now = datetime.datetime.now()

    if str(now.minute) == '0':

        data = obs.api_niteroi('chuva')
        hour = now.hour
        data.to_csv(str(hour) + '_rain.csv')
    print(now)
    x=1