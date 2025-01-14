'''

'''
import pandas as pd
from selenium import webdriver
import requests
import json
import datetime
import time

def get_headers(headers):
    url = 'https://xueqiu.com/'
    options = webdriver.ChromeOptions()
    # 设置中文
    for (key,value) in headers.items():
        options.add_argument('%s="%s"' % (key, value))
    options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    cookies=driver.get_cookies()
    driver.quit()
    ck = dict()
    for i in cookies:
        ck[i['name']] = i['value']
    headers.update({"Cookie":' ;'.join([k+'='+v for (k,v) in ck.items()])})
    return(headers)

def read_data_from_xueqiu(url, headers = None):
    if headers == None:
        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                   'Accept-Language': 'zh-CN,zh;q=0.9',
                   'Cache-Control': 'max-age=0',
                   'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
                   'Connection': 'keep-alive'
                   }
    headers = get_headers(headers)
    response = requests.get(url,headers=headers)
    res_dict = json.loads(response.text)
    return(res_dict)

def read_financial_report(code, exchange, report_type):
    stockfi_url = 'https://stock.xueqiu.com/v5/stock/finance/{exchange}/{report_type}.json?symbol={code}&type=all&is_detail=true&count=1000&timestamp={timestamp}'.format(code=code,exchange=exchange, report_type=report_type, timestamp= int(time.mktime(datetime.datetime.now().timetuple())*1000))
    data = read_data_from_xueqiu(stockfi_url)
    columns_list = []
    for i in data['data']['list']:
        columns_list = columns_list +list(data['data']['list'][0].keys())
    columns_list = list(set(columns_list))
    if report_type != 'income':
        columns_list.remove('ctime')
        columns_list.remove('sd')
        columns_list.remove('ed')
    res = pd.DataFrame()
    for j in data['data']['list']:
        a = dict()
        for i in columns_list:
            if isinstance(j[i],list):
                a[i] = j[i][0]
            else:
                a[i] = j[i]
        res = res.append(pd.DataFrame(a,index=[0]))
    res = res.assign(report_date = res.report_date.apply(lambda x:x/1000))
    res = res.assign(report_date = res.report_date.apply(lambda x:str(datetime.datetime.fromtimestamp(x))[0:10]))
    return(res)

def read_stock_day(code, start_date, end_date, period='day', type='normal'):
    start_date = datetime.datetime.strptime(str(start_date),"%Y-%m-%d")
    end_date = datetime.datetime.strptime(str(end_date),"%Y-%m-%d")
    cnt = (end_date-start_date).days
    if cnt < 350:
        cnt = 350
    else:
        cnt = cnt
    stockday_url = 'https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol={code}&begin={timestamp}&period={period}&type={type}&count=-{cnt}&indicator=kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance'.format(code=code, cnt = cnt,period=period,type=type,timestamp= int(time.mktime(datetime.datetime.now().timetuple())*1000))
    data = read_data_from_xueqiu(stockday_url)
    data = pd.DataFrame(data['data']['item'],columns=data['data']['column']).assign(code = data['data']['symbol'])
    data = data.assign(timestamp = data.timestamp.apply(lambda x:x/1000))
    data = data.assign(datetime = pd.to_datetime(data.timestamp.apply(lambda x:str(datetime.datetime.fromtimestamp(x)))))
    data = data.assign(date = pd.to_datetime(data.timestamp.apply(lambda x:str(datetime.datetime.fromtimestamp(x))[0:10])))
    return(data)

def read_stock_week(code, start_date, end_date):
    start_date = datetime.datetime.strptime(str(start_date),"%Y-%m-%d")
    end_date = datetime.datetime.strptime(str(end_date),"%Y-%m-%d")
    cnt = (end_date-start_date).days
    if cnt < 350:
        cnt = 350
    else:
        cnt = cnt
    stockday_url = 'https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol={code}&begin={timestamp}&period=day&type=normal&count=-{cnt}&indicator=kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance'.format(code=code, cnt = cnt, timestamp= int(time.mktime(datetime.datetime.now().timetuple())*1000))
    data = read_data_from_xueqiu(stockday_url)
    data = pd.DataFrame(data['data']['item'],columns=data['data']['column']).assign(code = data['data']['symbol'])
    data = data.assign(timestamp = data.timestamp.apply(lambda x:x/1000))
    data = data.assign(date = pd.to_datetime(data.timestamp.apply(lambda x:str(datetime.datetime.fromtimestamp(x))[0:10])))
    return(data)

if __name__ == '__main__':
    pass