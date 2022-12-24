import os
import datetime as dt

extrai_rn = os.listdir("/home/lammoc/wrf_operacional/operacional/scripts/dados_ascii/extrai_rn_backup")
dates_in_dir = []
for file in extrai_rn:
    date_str = file.split(".")[0].split("_")[-1]
    year_str = date_str[:4]
    month_str = date_str[4:6]
    day_str = date_str[6:]
    try:
        date = dt.datetime(int(year_str), int(month_str), int(day_str))
    except:
        print(year_str+month_str+day_str)

    if int(year_str) >= 2022:
        dates_in_dir.append(date)
'''
dates_in_dir = sorted(dates_in_dir)
print("\n -- Initial Date: ")
print(dates_in_dir[0])
print(" -- Ending Date: ")
print(dates_in_dir[-1])
'''
init_dat = dt.datetime(2022,1,1)
end_dat = dt.datetime(2022,5,1)
jan_aug = []
missing = []
while init_dat < end_dat:
    if init_dat not in dates_in_dir:
        missing.append(init_dat)
    init_dat += dt.timedelta(days=1)

print("All missing dates")
print(missing)

"""
missing_dates_nb = {} # {yesterday : today}
for today in missing:
  yesterday = today - dt.timedelta(days=1)

  if yesterday not in dates_in_dir:
      print("\n\n Consecutive missing dates")
      print("Missing: "+ today.strftime('%Y%m%d'))
      print("And can't adapt with: "+ yesterday.strftime('%Y%m%d'))
      missing_dates_nb.update({float(yesterday.strftime('%Y%m%d')) : float(today.strftime('%Y%m%d'))})
"""
