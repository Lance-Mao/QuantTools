import numpy as np
import easyquotation
import pandas as pd
from QUANTAXIS import QA_fetch_stock_day_adv,QA_fetch_index_day_adv,QA_fetch_stock_min_adv
from QUANTAXIS.QAUtil import (QA_util_today_str,QA_util_get_pre_trade_date,QA_util_get_trade_range,QA_util_get_real_date,QA_util_if_trade)
from QUANTTOOLS.QAStockETL.QAFetch import QA_fetch_stock_half_adv
from QUANTTOOLS.QAStockETL.QAUtil.QAAlpha191 import Alpha_191
from QUANTTOOLS.QAStockETL.QAUtil.QAAlpha101 import get_alpha


def stock_alpha(code, date=None):
    np.seterr(invalid='ignore')
    if date == None:
        end_date = QA_util_today_str()
    else:
        end_date = date
    start_date = QA_util_get_pre_trade_date(date, 250)
    try:
        price = QA_fetch_stock_day_adv(code, start_date, end_date).to_qfq().data.reset_index().dropna(axis=0, how='any')
        return(Alpha_191(price, date).alpha())
    except:
        return(None)

def index_alpha(code, date=None):
    np.seterr(invalid='ignore')
    if date == None:
        end_date = QA_util_today_str()
    else:
        end_date = date
    start_date = QA_util_get_pre_trade_date(date, 250)
    try:
        price = QA_fetch_index_day_adv(code, start_date, end_date ).data.reset_index().dropna(axis=0, how='any')
        return(Alpha_191(price, date).alpha())
    except:
        return(None)

def stock_alpha101(code, start=None, end = None):
    np.seterr(invalid='ignore')
    if end is None:
        end_date = QA_util_today_str()
    else:
        end_date = end

    if start is None:
        start = QA_util_today_str()
    else:
        start = start

    start_date = QA_util_get_pre_trade_date(start, 270)
    deal_date_list = QA_util_get_trade_range(start, end)

    try:
        price = QA_fetch_stock_day_adv(code, start_date, end_date ).to_qfq()
        pctchange = price.close_pct_change()
        price = price.data
        price['pctchange'] = pctchange
        return(get_alpha(price).loc[deal_date_list].reset_index())
    except:
        return(None)

def index_alpha101(code, start=None, end = None):
    np.seterr(invalid='ignore')
    if end is None:
        end_date = QA_util_today_str()
    else:
        end_date = end

    if start is None:
        start = QA_util_today_str()
    else:
        start = start

    start_date = QA_util_get_pre_trade_date(start, 270)
    deal_date_list = QA_util_get_trade_range(start, end)
    try:
        price = QA_fetch_index_day_adv(code, start_date, end_date )
        pctchange = price.close_pct_change()
        price = price.data
        price['pctchange'] = pctchange
        return(get_alpha(price).loc[deal_date_list].reset_index())
    except:
        return(None)

def stock_alpha101_half(code, start=None, end = None):
    np.seterr(invalid='ignore')
    if end is None:
        end_date = QA_util_today_str()
    else:
        end_date = end

    if start is None:
        start = QA_util_today_str()
    else:
        start = start

    start_date = QA_util_get_pre_trade_date(start, 270)
    deal_date_list = QA_util_get_trade_range(start, end)

    try:
        price = QA_fetch_stock_half_adv(code, start_date, end_date).to_qfq().data
        print(get_alpha(price))
        return(get_alpha(price).loc[deal_date_list].reset_index())
    except:
        return(None)

def stock_alpha101_half_realtime(code, start = None, end = None):
    end =QA_util_today_str()

    if QA_util_if_trade(end):
        pass
    else:
        end = QA_util_get_real_date(end)

    if start is None:
        start = end

    start_date = QA_util_get_pre_trade_date(start, 270)
    deal_date_list = QA_util_get_trade_range(start, end)
    try:
        price = QA_fetch_stock_half_adv(code, start_date, end).to_qfq().data
        quotation = easyquotation.use('sina')
        res = pd.DataFrame(quotation.stocks(code) ).T[['date','open','high','low','now','turnover','volume','close']]
        res = res.reset_index().rename(columns={'index':'code',
                                                'close':'pctchange',
                                                'now':'close',
                                                'turnover':'volume',
                                                'volume':'amount'})
        res = res.assign(pctchange=res.close/res.pctchange-1).set_index(['date','code'])
        res = price.append(res.astype('float64')).groupby('code').apply(get_alpha)
        res = res.reset_index(level=2).drop('code',axis=1).reset_index().set_index(['date','code'])
        return(res.loc[deal_date_list])
    except:
        return(None)

def half_ohlc(data):
    data = data.reset_index().set_index('datetime')
    res = data.resample('12H').agg({'open': 'first', 'high': 'max',  'low': 'min', 'close': 'last','volume': 'sum','amount': 'sum'})
    return(res)