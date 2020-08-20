
import numpy
import pandas as pd
import datetime
import math
import QUANTAXIS as QA
from QUANTAXIS.QAUtil import (DATABASE, QA_util_date_stamp,
                              QA_util_date_valid, QA_util_log_info, QA_util_code_tolist, QA_util_date_int2str,
                              QA_util_to_json_from_pandas, QA_util_today_str, QA_util_get_pre_trade_date,
                              QA_util_add_months)
from QUANTAXIS.QAFetch.QAQuery_Advance import QA_fetch_future_list_adv,QA_fetch_index_list_adv
from QUANTAXIS.QAFetch.QAQuery import QA_fetch_stock_basic_info_tushare,QA_fetch_stock_list
from QUANTTOOLS.QAStockETL.QAData.financial_mean import financial_dict, dict2
from QUANTTOOLS.QAStockETL.QAUtil.base_func import pct,index_pct,time_this_function,index_pct_log,pct_log
from QUANTAXIS.QAUtil.QADate_trade import QA_util_if_trade, QA_util_get_next_datetime,QA_util_get_real_date,QA_util_get_trade_range
from QUANTTOOLS.QAStockETL.QAFetch.QATdx import QA_fetch_get_stock_delist
from QUANTTOOLS.QAStockETL.QAUtil.QASQLStockIndex import QA_Sql_Stock_Index
from QUANTTOOLS.QAStockETL.QAUtil.QASQLStockIndexWeek import QA_Sql_Stock_IndexWeek
from QUANTTOOLS.QAStockETL.QAUtil.QASQLStockAlpha101 import QA_Sql_Stock_Alpha101
from QUANTTOOLS.QAStockETL.QAUtil.QASQLStockAlpha191 import QA_Sql_Stock_Alpha191
from QUANTTOOLS.QAStockETL.QAUtil.QASQLStockFinancial import QA_Sql_Stock_Financial
from QUANTTOOLS.QAStockETL.QAUtil.QASQLStockFinancialPE import QA_Sql_Stock_FinancialPercent
from QUANTTOOLS.QAStockETL.QAUtil.QASQLIndexIndex import QA_Sql_Index_Index
from QUANTTOOLS.QAStockETL.QAUtil.QASQLIndexIndexWeek import QA_Sql_Index_IndexWeek
from QUANTTOOLS.QAStockETL.QAUtil.QASQLIndexAlpha101 import QA_Sql_Index_Alpha101
from QUANTTOOLS.QAStockETL.QAUtil.QASQLIndexAlpha191 import QA_Sql_Index_Alpha191
from QUANTTOOLS.QAStockETL.QAUtil.base_func import normalization, standardize

def QA_fetch_stock_industry(stock_code):
    '''
    根据tushare 的数据库查找股票行业
    :param stock_code: '600001'
    :return: string 上市日期 eg： '2018-05-15'
    '''
    items = QA_fetch_stock_basic_info_tushare()
    for row in items:
        if row['code'] == stock_code:
            return row['industry']

def QA_fetch_stock_name(stock_code):
    '''
    根据tushare 的数据库查找股票名称
    :param stock_code: '600001'
    :return: string 上市日期 eg： '民生银行'
    '''
    items = QA_fetch_stock_basic_info_tushare()
    for row in items:
        if row['code'] == stock_code:
            return row['name']

def QA_fetch_index_name(stock_code):
    '''
    获取指数名称
    :param stock_code: '600001'
    :return: string 指数名称 eg： '上证指数'
    '''
    items = QA_fetch_index_list_adv().loc[str(stock_code)]
    return items['name']

def QA_fetch_index_cate(stock_code):
    '''
    获取指数名称
    :param stock_code: '600001'
    :return: string 指数名称 eg： '上证指数'
    '''
    try:
        items = QA_fetch_index_info(str(stock_code))
        return items['cate']
    except:
        return None

def QA_fetch_financial_report(code, start_date, end_date, type ='report', ltype='EN', db=DATABASE):
    """获取专业财务报表

    Arguments:
        code {[type]} -- [description]
        report_date {[type]} -- [description]

    Keyword Arguments:
        ltype {str} -- [description] (default: {'EN'})
        db {[type]} -- [description] (default: {DATABASE})

    Raises:
        e -- [description]

    Returns:
        pd.DataFrame -- [description]
    """

    if code is None:
        code = list(QA_fetch_future_list_adv()['code'])

    if isinstance(code, str):
        code = [code]

    if start_date is None:
        start = '1995-01-01'
    else:
        start = start_date

    if end_date is None:
        end = QA_util_today_str()
    else:
        end = end_date

    collection = db.financial
    num_columns = [item[:3] for item in list(financial_dict.keys())]
    CH_columns = [item[3:] for item in list(financial_dict.keys())]
    EN_columns = list(financial_dict.values())

    end = int(end.replace('-',''))
    start = int(start.replace('-',''))

    try:
        if type == 'report':
            cursor = collection.find({
                'code': {'$in': code}, "report_date": {
                    "$lte": end,
                    "$gte": start}}, {"_id": 0}, batch_size=10000)
            data = pd.DataFrame([item for item in cursor])
        elif type == 'crawl':
            cursor = collection.find({
                'code': {'$in': code}, "crawl_date": {
                    "$lte": end,
                    "$gte": start}}, {"_id": 0}, batch_size=10000)
            data = pd.DataFrame([item for item in cursor])
        else:
            QA_util_log_info("type must be one of [report, crawl]")

        if len(data) > 0:
            res_pd = pd.DataFrame(data)
            if ltype in ['CH', 'CN']:

                cndict = dict(zip(num_columns, CH_columns))
                cndict['283']='283'
                try:
                    cndict['284'] = '284'
                    cndict['285'] = '285'
                    cndict['286'] = '286'
                    cndict['287'] = '287'
                    cndict['295'] = '295'
                    cndict['296'] = '296'
                    cndict['302'] = '302'
                    cndict['303'] = '303'
                    cndict['307'] = '307'
                except:
                    pass
                cndict['_id']='_id'
                cndict['code']='code'
                cndict['report_date']='report_date'
                cndict['crawl_date']='crawl_date'
                res_pd.columns = res_pd.columns.map(lambda x: cndict[x])
            elif ltype is 'EN':
                endict=dict(zip(num_columns,EN_columns))
                endict['283']='283'
                try:
                    endict['284'] = '284'
                    endict['285'] = '285'
                    endict['286'] = '286'
                    endict['287'] = '287'
                    endict['295'] = '295'
                    endict['296'] = '296'
                    endict['302'] = '302'
                    endict['303'] = '303'
                    endict['307'] = '307'
                except:
                    pass
                endict['_id']='_id'
                endict['code']='code'
                endict['report_date']='report_date'
                endict['crawl_date']='crawl_date'
                res_pd.columns = res_pd.columns.map(lambda x: endict[x])

            #res_pd['crawl_date'] = res_pd['crawl_date'].apply(lambda x: datetime.datetime.fromtimestamp(math.floor(x)))
            #res_pd['report_date'] = res_pd['report_date'].apply(lambda x: datetime.datetime.fromtimestamp(math.floor(x)))
            res_pd['report_date'] = res_pd['report_date'].apply(lambda x: str(x)[0:4]+'-'+str(x)[4:6]+'-'+str(x)[6:8])
            return res_pd.replace(-4.039810335e+34, numpy.nan).set_index(['report_date', 'code'], drop=False)
        else:
            return None
    except Exception as e:
        raise e

def QA_fetch_stock_financial_calendar(code, start, end=None, type = 'day', format='pd',collections=DATABASE.report_calendar):
    '获取股票日线'
    #code= [code] if isinstance(code,str) else code
    # code checking
    code = QA_util_code_tolist(code)

    if start is None:
        start = '1995-01-01'
    else:
        start = start

    if end is None:
        end = QA_util_today_str()
    else:
        end = end

    if QA_util_date_valid(end):

        __data = []
        if type == 'report':
            cursor = collections.find({
                'code': {'$in': code}, "report_date": {
                    "$lte": QA_util_date_stamp(end),
                    "$gte": QA_util_date_stamp(start)}}, {"_id": 0}, batch_size=10000)
            res = pd.DataFrame([item for item in cursor])
        elif type == 'day':
            cursor = collections.find({
                'code': {'$in': code}, "real_date": {
                    "$lte": QA_util_date_stamp(end),
                    "$gte": QA_util_date_stamp(start)}}, {"_id": 0}, batch_size=10000)
            res = pd.DataFrame([item for item in cursor])
        elif type == 'crawl':
            cursor = collections.find({
                'code': {'$in': code}, "crawl_date": {
                    "$lte": QA_util_date_stamp(end),
                    "$gte": QA_util_date_stamp(start)}}, {"_id": 0}, batch_size=10000)
            res = pd.DataFrame([item for item in cursor])
        else:
            QA_util_log_info("type must be one of [report, day, crawl]")

        try:
            #res = res.drop_duplicates(
            #    (subset=['report_date', 'code']))
            res = res[['code', 'name', 'pre_date', 'first_date', 'second_date',
                        'third_date', 'real_date', 'codes', 'report_date', 'crawl_date']]
            res['real_date'] = res['real_date'].apply(lambda x: datetime.datetime.fromtimestamp(math.floor(x)))
            res['crawl_date'] = res['crawl_date'].apply(lambda x: datetime.datetime.fromtimestamp(math.floor(x)))
            res['report_date'] = res['report_date'].apply(lambda x: datetime.datetime.fromtimestamp(math.floor(x)))
        except:
            res = None

        if format in ['P', 'p', 'pandas', 'pd']:
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            QA_util_log_info("QA Error QA_fetch_stock_financial_calendar format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" " % format)
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_stock_financial_calendar data parameter start=%s end=%s is not right' % (start, end))


def QA_fetch_stock_divyield(code, start, end=None, format='pd',type = 'day', collections=DATABASE.stock_divyield):
    '获取股票日线'
    #code= [code] if isinstance(code,str) else code
    # code checking
    code = QA_util_code_tolist(code)

    if QA_util_date_valid(end):

        __data = []
        if type == 'report':
            cursor = collections.find({
                'a_stockcode': {'$in': code}, "report_date": {
                    "$lte": QA_util_date_stamp(end),
                    "$gte": QA_util_date_stamp(start)}}, {"_id": 0}, batch_size=10000)
            res = pd.DataFrame([item for item in cursor])
        elif type == 'day':
            cursor = collections.find({
                'a_stockcode': {'$in': code}, "reg_date": {
                    "$lte": QA_util_date_stamp(end),
                    "$gte": QA_util_date_stamp(start)}}, {"_id": 0}, batch_size=10000)
            res = pd.DataFrame([item for item in cursor])
        elif type == 'crawl':
            cursor = collections.find({
                'a_stockcode': {'$in': code}, "crawl_date": {
                    "$lte": QA_util_date_stamp(end),
                    "$gte": QA_util_date_stamp(start)}}, {"_id": 0}, batch_size=10000)
            res = pd.DataFrame([item for item in cursor])
        else:
            QA_util_log_info("type must be one of [report, day, crawl]")
        #res=[QA_util_dict_remove_key(data, '_id') for data in cursor]

        try:
            res = res.drop_duplicates(
                (['dir_dcl_date', 'a_stockcode']))
            res = res.ix[:, ['a_stockcode', 'a_stocksname', 'div_info', 'div_type_code', 'bonus_shr',
                             'cash_bt', 'cap_shr', 'epsp', 'ps_cr', 'ps_up', 'reg_date', 'dir_dcl_date',
                             'a_stockcode1', 'ex_divi_date', 'prg', 'report_date', 'crawl_date']]
            res['reg_date'] = res['reg_date'].apply(lambda x: datetime.datetime.fromtimestamp(math.floor(x)))
            res['crawl_date'] = res['crawl_date'].apply(lambda x: datetime.datetime.fromtimestamp(math.floor(x)))
            res['report_date'] = res['report_date'].apply(lambda x: datetime.datetime.fromtimestamp(math.floor(x)))
        except:
            res = None
        if format in ['P', 'p', 'pandas', 'pd']:
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            QA_util_log_info("QA Error QA_fetch_stock_divyield format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" " % format)
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_stock_divyield data parameter start=%s end=%s is not right' % (start, end))

def QA_fetch_financial_TTM(code, start, end = None, format='pd', collections=DATABASE.financial_TTM):
    '获取财报TTM数据'
    #code= [code] if isinstance(code,str) else code
    # code checking
    code = QA_util_code_tolist(code)

    if QA_util_date_valid(end):
        __data = []

        cursor = collections.find({
            'CODE': {'$in': code}, "date": {
                "$lte": QA_util_date_stamp(end),
                "$gte": QA_util_date_stamp(start)}}, batch_size=10000)
        #res=[QA_util_dict_remove_key(data, '_id') for data in cursor]

        res = pd.DataFrame([item for item in cursor])
        try:
            res = res.drop('_id', axis=1).drop_duplicates((['REPORT_DATE', 'CODE']))
        except:
            res = None
        if format in ['P', 'p', 'pandas', 'pd']:
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            QA_util_log_info("QA Error QA_fetch_financial_TTM format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" " % format)
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_financial_TTM data parameter start=%s end=%s is not right' % (start, end))

def QA_fetch_stock_fianacial(code, start, end = None, format='pd', collections=DATABASE.stock_financial_analysis):
    '获取quant基础数据'
    #code= [code] if isinstance(code,str) else code
    # code checking
    code = QA_util_code_tolist(code)
    if QA_util_date_valid(end):
        cursor = collections.find({
            'CODE': {'$in': code}, "date_stamp": {
                "$lte": QA_util_date_stamp(end),
                "$gte": QA_util_date_stamp(start)}}, batch_size=10000)
        #res=[QA_util_dict_remove_key(data, '_id') for data in cursor]
        res = pd.DataFrame([item for item in cursor])
        try:
            res.columns = [i.lower() if i == 'CODE' else i for i in list(res.columns)]
            res = res.drop(['date_stamp','_id'], axis=1).drop_duplicates((['code', 'date']))
            res['RNG_RES'] = res['AVG60_RNG'] *60 / res['RNG_60']
        except:
            res = None
        if format in ['P', 'p', 'pandas', 'pd']:
            #res['report_date'] = pd.to_datetime(res['report_date']/1000, unit='s')
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            QA_util_log_info("QA Error QA_fetch_stock_fianacial format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" " % format)
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_financial_TTM data parameter start=%s end=%s is not right' % (start, end))

def QA_fetch_stock_alpha(code, start, end=None, format='pd', collections=DATABASE.stock_alpha):
    '获取股票日线'
    #code= [code] if isinstance(code,str) else code
    # code checking
    code = QA_util_code_tolist(code)

    if QA_util_date_valid(end):

        __data = []
        cursor = collections.find({
            'code': {'$in': code}, "date_stamp": {
                "$lte": QA_util_date_stamp(end),
                "$gte": QA_util_date_stamp(start)}}, {"_id": 0}, batch_size=10000)
        #res=[QA_util_dict_remove_key(data, '_id') for data in cursor]

        res = pd.DataFrame([item for item in cursor])
        try:
            res = res.drop_duplicates(
                (['code', 'date'])).drop(['date_stamp'],axis=1).set_index(['date','code'])
        except:
            res = None
        if format in ['P', 'p', 'pandas', 'pd']:
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            QA_util_log_info("QA Error QA_fetch_stock_alpha format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" " % format)
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_stock_alpha data parameter start=%s end=%s is not right' % (start, end))

def QA_fetch_stock_shares(code, start, end=None, format='pd',type = 'day', collections=DATABASE.stock_shares):
    '获取股票日线'
    #code= [code] if isinstance(code,str) else code
    # code checking
    code = QA_util_code_tolist(code)

    if QA_util_date_valid(end):

        __data = []
        if type == 'day':
            cursor = collections.find({
                'code': {'$in': code}, "begin_date": {
                    "$lte": QA_util_date_stamp(end),
                    "$gte": QA_util_date_stamp(start)}}, {"_id": 0}, batch_size=10000)
            res = pd.DataFrame([item for item in cursor])
        elif type == 'crawl':
            cursor = collections.find({
                'code': {'$in': code}, "crawl_date": {
                    "$lte": QA_util_date_stamp(end),
                    "$gte": QA_util_date_stamp(start)}}, {"_id": 0}, batch_size=10000)
            res = pd.DataFrame([item for item in cursor])
        else:
            QA_util_log_info("type must be one of [day, crawl]")

        try:
            res = res.ix[:, ['begin_date','code','crawl_date','exe_shares',
                             'nontra_ashares','nontra_bshares','pre_shares','reason',
                             'send_date','total_shares','tra_ashares','tra_bshares','tra_hshares']]
            res['begin_date'] = res['begin_date'].apply(lambda x: datetime.datetime.fromtimestamp(math.floor(x)))
            res['crawl_date'] = res['crawl_date'].apply(lambda x: datetime.datetime.fromtimestamp(math.floor(x)))
        except:
            res = None
        if format in ['P', 'p', 'pandas', 'pd']:
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            QA_util_log_info("QA Error QA_fetch_stock_shares format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" " % format)
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_stock_shares data parameter start=%s end=%s is not right' % (start, end))


def QA_fetch_financial_report_wy(code, start_date = None, end_date = None, type ='report', ltype='EN', db=DATABASE):
    """获取专业财务报表

    Arguments:
        code {[type]} -- [description]
        report_date {[type]} -- [description]

    Keyword Arguments:
        ltype {str} -- [description] (default: {'EN'})
        db {[type]} -- [description] (default: {DATABASE})

    Raises:
        e -- [description]

    Returns:
        pd.DataFrame -- [description]
    """

    if code is None:
        code = list(QA_fetch_future_list_adv()['code'])

    if isinstance(code, str):
        code = [code]

    if start_date is None:
        start = '1995-01-01'
    else:
        start = start_date

    if end_date is None:
        end = QA_util_today_str()
    else:
        end = end_date

    collection = db.stock_financial_wy
    num_columns = [item[:3] for item in list(financial_dict.keys())]
    CH_columns = [item[3:] for item in list(financial_dict.keys())]
    EN_columns = list(financial_dict.values())

    try:
        if type == 'report':
            cursor = collection.find({
                'code': {'$in': code}, "report_date": {
                    "$lte": QA_util_date_stamp(end),
                    "$gte": QA_util_date_stamp(start)}}, {"_id": 0}, batch_size=10000)
            data = pd.DataFrame([item for item in cursor])
        elif type == 'crawl':
            cursor = collection.find({
                'code': {'$in': code}, "crawl_date": {
                    "$lte": QA_util_date_stamp(end),
                    "$gte": QA_util_date_stamp(start)}}, {"_id": 0}, batch_size=10000)
            data = pd.DataFrame([item for item in cursor])
        else:
            QA_util_log_info("type must be one of [report, crawl]")

        if len(data) > 0:
            res_pd = pd.DataFrame(data)
            res_pd = res_pd[list(dict2.keys())]
            res_pd.columns = res_pd.columns.map(lambda x: dict2[x])
            res_pd['netProAftExtrGainLoss']=res_pd['netProfitsBelToParComOwner'] - res_pd['nonOperatingIncome']

            """
            if ltype in ['CH', 'CN']:

                cndict = dict(zip(num_columns, CH_columns))
                cndict['283']='283'
                try:
                    cndict['284'] = '284'
                    cndict['285'] = '285'
                    cndict['286'] = '286'
                except:
                    pass
                cndict['_id']='_id'
                cndict['code']='code'
                cndict['report_date']='report_date'
                cndict['crawl_date']='crawl_date'
                res_pd.columns = res_pd.columns.map(lambda x: cndict[x])
            elif ltype is 'EN':
                endict=dict(zip(num_columns,EN_columns))
                endict['283']='283'
                try:
                    endict['284'] = '284'
                    endict['285'] = '285'
                    endict['286'] = '286'
                except:
                    pass
                endict['_id']='_id'
                endict['code']='code'
                endict['report_date']='report_date'
                endict['crawl_date']='crawl_date'
                res_pd.columns = res_pd.columns.map(lambda x: endict[x])
            """
            res_pd['crawl_date'] = res_pd['crawl_date'].apply(lambda x: datetime.datetime.fromtimestamp(math.floor(x)))
            res_pd['report_date'] = res_pd['report_date'].apply(lambda x: datetime.datetime.fromtimestamp(math.floor(x)))
            return res_pd.replace(-4.039810335e+34, numpy.nan).set_index(['report_date', 'code'], drop=False)
        else:
            return None
    except Exception as e:
        raise e

def QA_fetch_stock_technical_index(code, start, end=None, type='day', format='pd'):
    '获取股票日线'
    #code= [code] if isinstance(code,str) else code
    # code checking
    if type == 'day':
        collections=DATABASE.stock_technical_index
    elif type == 'week':
        collections=DATABASE.stock_technical_week
    elif type == 'month':
        collections=DATABASE.stock_technical_month
    else:
        QA_util_log_info("type should be in ['day', 'week', 'month']")
    code = QA_util_code_tolist(code)
    if QA_util_date_valid(end):

        __data = []
        cursor = collections.find({
            'code': {'$in': code}, "date_stamp": {
                "$lte": QA_util_date_stamp(end),
                "$gte": QA_util_date_stamp(start)}}, {"_id": 0}, batch_size=10000)
        #res=[QA_util_dict_remove_key(data, '_id') for data in cursor]

        res = pd.DataFrame([item for item in cursor])
        try:
            res = res.drop_duplicates(
                (['code', 'date']))
            res['date'] = res['date'].apply(lambda x: str(x)[0:10])
            res = res.drop(['date_stamp'],axis=1).set_index(['date','code'])
        except:
            res = None
        if format in ['P', 'p', 'pandas', 'pd']:
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            QA_util_log_info("QA Error QA_fetch_stock_technical_index format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" " % format)
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_stock_technical_index data parameter start=%s end=%s is not right' % (start, end))

def QA_fetch_stock_financial_percent(code, start, end=None, format='pd', collections=DATABASE.stock_financial_percent):
    '获取股票日线'
    #code= [code] if isinstance(code,str) else code
    # code checking
    code = QA_util_code_tolist(code)

    if QA_util_date_valid(end):

        __data = []
        cursor = collections.find({
            'code': {'$in': code}, "date_stamp": {
                "$lte": QA_util_date_stamp(end),
                "$gte": QA_util_date_stamp(start)}}, {"_id": 0}, batch_size=10000)
        #res=[QA_util_dict_remove_key(data, '_id') for data in cursor]

        res = pd.DataFrame([item for item in cursor])
        try:
            res = res.drop_duplicates(
                (['code', 'date'])).drop(['date_stamp'],axis=1).set_index(['date','code'])
        except:
            res = None
        if format in ['P', 'p', 'pandas', 'pd']:
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            QA_util_log_info("QA Error QA_fetch_stock_financial_percent format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" " % format)
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_stock_financial_percent data parameter start=%s end=%s is not right' % (start, end))

@time_this_function
def QA_fetch_stock_quant_data(code, start, end=None, block = True, type='normalization', format='pd', collections=DATABASE.stock_quant_data):
    '获取股票日线'
    #code= [code] if isinstance(code,str) else code
    # code checking
    code = QA_util_code_tolist(code)
    financial = QA_Sql_Stock_Financial
    index = QA_Sql_Stock_Index
    week = QA_Sql_Stock_IndexWeek
    alpha = QA_Sql_Stock_Alpha191
    alpha101 = QA_Sql_Stock_Alpha101
    pe = QA_Sql_Stock_FinancialPercent

    if QA_util_date_valid(end):

        __data = []
        QA_util_log_info(
            'JOB Get Stock Financial data start=%s end=%s' % (start, end))
        pe_res = pe(start,end).groupby('code').fillna(method='ffill').reset_index()
        pe_res = pe_res[pe_res.code.isin(code)]
        financial_res = financial(start,end).groupby('code').fillna(method='ffill').reset_index()
        financial_res = financial_res[financial_res.code.isin(code)]

        QA_util_log_info(
            'JOB Get Stock Tech Index data start=%s end=%s' % (start, end))

        index_res = index(start,end).groupby('code').fillna(method='ffill').reset_index()
        index_res = index_res[index_res.code.isin(code)]
        QA_util_log_info(
            'JOB Get Stock Tech Week data start=%s end=%s' % (start, end))

        week_res = week(start,end).groupby('code').fillna(method='ffill').reset_index()
        week_res = week_res[week_res.code.isin(code)]
        QA_util_log_info(
            'JOB Get Stock Alpha191 data start=%s end=%s' % (start, end))
        alpha_res = alpha(start,end).groupby('code').fillna(method='ffill').reset_index()
        alpha_res = alpha_res[alpha_res.code.isin(code)]
        QA_util_log_info(
            'JOB Get Stock Alpha101 data start=%s end=%s' % (start, end))
        alpha101_res = alpha101(start,end).groupby('code').fillna(method='ffill').fillna(0).reset_index()
        alpha101_res = alpha101_res[alpha101_res.code.isin(code)]
        try:
            res = financial_res.drop_duplicates(
                (['code', 'date'])).set_index(['date','code']).join(
                index_res.drop_duplicates(
                    (['code', 'date'])).set_index(['date','code'])).join(
                week_res.drop_duplicates(
                    (['code', 'date'])).set_index(['date','code'])).join(
                alpha_res.drop_duplicates(
                    (['code', 'date'])).set_index(['date','code'])).join(
                alpha101_res.drop_duplicates(
                    (['code', 'date'])).set_index(['date','code'])).join(
                pe_res.drop_duplicates(
                    (['code', 'date'])).set_index(['date','code']))

            for columnname in res.columns:
                if res[columnname].dtype == 'float64':
                    res[columnname]=res[columnname].astype('float32')
                if res[columnname].dtype == 'float32':
                    res[columnname]=res[columnname].astype('float32')
                if res[columnname].dtype == 'int64':
                    res[columnname]=res[columnname].astype('int8')
                if res[columnname].dtype == 'int32':
                    res[columnname]=res[columnname].astype('int8')
                if res[columnname].dtype == 'int16':
                    res[columnname]=res[columnname].astype('int8')

            if block is True:
                block = QA.QA_fetch_stock_block(code).reset_index(drop=True).drop_duplicates(['blockname','code'])
                block = pd.crosstab(block['code'],block['blockname'])
                block.columns = ['S_' + i for i  in  list(block.columns)]
                res = res.join(block, on = 'code', lsuffix='_caller', rsuffix='_other')
            else:
                pass

            col_tar = ['DAYS','INDUSTRY']
            if type == 'standardize':
                QA_util_log_info('##JOB stock quant data standardize trans ============== from {from_} to {to_} '.format(from_= start,to_=end))
                res = res[[x for x in list(res.columns) if x not in col_tar]].groupby('date').apply(standardize).join(res[col_tar])
            elif type == 'normalization':
                QA_util_log_info('##JOB stock quant data normalization trans ============== from {from_} to {to_} '.format(from_= start,to_=end))
                res = res[[x for x in list(res.columns) if x not in col_tar]].groupby('date').apply(normalization).join(res[col_tar])
            else:
                QA_util_log_info('##JOB type must be in [standardize, normalization]')
                pass
        except:
            res = None

        if format in ['P', 'p', 'pandas', 'pd']:
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            QA_util_log_info("QA Error QA_fetch_stock_quant_data format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" " % format)
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_stock_quant_data date parameter start=%s end=%s is not right' % (start, end))

def QA_fetch_stock_target(codes, start_date, end_date, type='close', method = 'value'):
    if QA_util_if_trade(end_date):
        pass
    else:
        end_date = QA_util_get_real_date(end_date)
    end = QA_util_get_next_datetime(end_date,10)
    rng1 = QA_util_get_trade_range(start_date, end_date)
    data = QA.QA_fetch_stock_day_adv(codes,start_date,end)
    market = QA.QA_fetch_index_day(['000001'],start_date,end,format='pd')['close'].reset_index()
    if method == 'value':
        market = index_pct(market)[['date','INDEX_TARGET','INDEX_TARGET3','INDEX_TARGET4','INDEX_TARGET5','INDEX_TARGET10']]
    elif method == 'log':
        market = index_pct_log(market)[['date','INDEX_TARGET','INDEX_TARGET3','INDEX_TARGET4','INDEX_TARGET5','INDEX_TARGET10']]
    else:
        market = None
    res1 = data.to_qfq().data
    res1.columns = [x + '_qfq' for x in res1.columns]
    data = data.data.join(res1).fillna(0).reset_index()
    if method == 'value':
        res = data.groupby('code').apply(pct, type=type)[['date','code','PRE_DATE','OPEN_MARK','PASS_MARK',
                                                                          'TARGET','TARGET3','TARGET4','TARGET5',
                                                                          'TARGET10','AVG_TARGET']]
    elif method == 'log':
        res = data.groupby('code').apply(pct_log, type=type)[['date','code','PRE_DATE','OPEN_MARK','PASS_MARK',
                                                                          'TARGET','TARGET3','TARGET4','TARGET5',
                                                                          'TARGET10','AVG_TARGET']]
    else:
        res = None

    res = pd.merge(res,market,on='date')
    res['date'] = res['date'].apply(lambda x: str(x)[0:10])
    res['next_date'] = res['date'].apply(lambda x: QA_util_get_pre_trade_date(x, -2))
    res['PRE_DATE'] = res['PRE_DATE'].apply(lambda x: str(x)[0:10])
    res = res.set_index(['date','code']).loc[rng1]
    res['INDEX_TARGET'] = res['TARGET'] - res['INDEX_TARGET']
    res['INDEX_TARGET3'] = res['TARGET3'] - res['INDEX_TARGET3']
    res['INDEX_TARGET4'] = res['TARGET4'] - res['INDEX_TARGET4']
    res['INDEX_TARGET5'] = res['TARGET5'] - res['INDEX_TARGET5']
    res['INDEX_TARGET10'] = res['TARGET10'] - res['INDEX_TARGET10']
    for columnname in res.columns:
        if res[columnname].dtype == 'float64':
            res[columnname]=res[columnname].astype('float16')
        if res[columnname].dtype == 'int64':
            res[columnname]=res[columnname].astype('int8')
    return(res)

def QA_fetch_stock_quant_pre(code, start, end=None, block = True, type='close', method='value', format='pd'):
    QA_util_log_info(
        'JOB Get Stock Quant data start=%s end=%s' % (start, end))
    res = QA_fetch_stock_quant_data(code, start, end, block)
    QA_util_log_info(
        'JOB Get Stock Target data start=%s end=%s' % (start, end))
    target = QA_fetch_stock_target(code, start, end, type=type, method=method)
    res = res.join(target)
    if format in ['P', 'p', 'pandas', 'pd']:
        return res
    elif format in ['json', 'dict']:
        return QA_util_to_json_from_pandas(res)
        # 多种数据格式
    elif format in ['n', 'N', 'numpy']:
        return numpy.asarray(res)
    elif format in ['list', 'l', 'L']:
        return numpy.asarray(res).tolist()
    else:
        QA_util_log_info("QA Error QA_fetch_stock_quant_data format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" " % format)
        return None

def QA_fetch_financial_code(ndays=10):
    START = str(QA_util_get_pre_trade_date(QA_util_today_str(),ndays))
    code = list(QA_fetch_stock_financial_calendar(QA.QA_fetch_stock_list_adv().code.tolist(),start = START)['code'])
    market_day = pd.DataFrame(QA_fetch_stock_basic_info_tushare())[['code','timeToMarket']]
    market_day['TM'] = market_day['timeToMarket'].apply(lambda x:str(QA_util_add_months(QA_util_date_int2str(int(x)),0) if x >0 else None)[0:10])
    code = list(market_day[market_day['TM'] >= START]['code'].values) + code
    return(code)


def QA_fetch_interest_rate(start, end=None, format='pd', collections=DATABASE.interest_rate):
    '获取股票日线'
    #code= [code] if isinstance(code,str) else code
    # code checking
    if end is None:
        end = QA_util_today_str()
    if start is None:
        start = '1999-01-01'

    if QA_util_date_valid(end):

        __data = []
        cursor = collections.find({
            "date_stamp": {
                "$lte": QA_util_date_stamp(end),
                "$gte": QA_util_date_stamp(start)}}, {"_id": 0}, batch_size=10000)
        #res=[QA_util_dict_remove_key(data, '_id') for data in cursor]

        res = pd.DataFrame([item for item in cursor])
        try:
            res = res.drop(columns=['crawl_date','date_stamp'])
        except:
            res = None
        if format in ['P', 'p', 'pandas', 'pd']:
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            QA_util_log_info("QA Error Interest Rate format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" " % format)
            return None
    else:
        QA_util_log_info(
            'QA Error Interest Rate data parameter start=%s end=%s is not right' % (start, end))


def QA_fetch_index_alpha(code, start, end=None, format='pd', collections=DATABASE.index_alpha):
    '获取股票日线'
    #code= [code] if isinstance(code,str) else code
    # code checking
    code = QA_util_code_tolist(code)

    if QA_util_date_valid(end):

        __data = []
        cursor = collections.find({
            'code': {'$in': code}, "date_stamp": {
                "$lte": QA_util_date_stamp(end),
                "$gte": QA_util_date_stamp(start)}}, {"_id": 0}, batch_size=10000)
        #res=[QA_util_dict_remove_key(data, '_id') for data in cursor]

        res = pd.DataFrame([item for item in cursor])
        try:
            res = res.drop_duplicates(
                (['code', 'date'])).set_index(['date','code']).drop('date_stamp', 1)
        except:
            res = None
        if format in ['P', 'p', 'pandas', 'pd']:
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            QA_util_log_info("QA Error QA_fetch_index_alpha format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" " % format)
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_index_alpha data parameter start=%s end=%s is not right' % (start, end))

def QA_fetch_index_technical_index(code, start, end=None, type='day', format='pd'):
    '获取股票日线'
    #code= [code] if isinstance(code,str) else code
    # code checking
    if type == 'day':
        collections=DATABASE.index_technical_index
    elif type == 'week':
        collections=DATABASE.index_technical_week
    elif type == 'month':
        collections=DATABASE.index_technical_month
    else:
        QA_util_log_info("type should be in ['day', 'week', 'month']")
    code = QA_util_code_tolist(code)
    if QA_util_date_valid(end):

        __data = []
        cursor = collections.find({
            'code': {'$in': code}, "date_stamp": {
                "$lte": QA_util_date_stamp(end),
                "$gte": QA_util_date_stamp(start)}}, {"_id": 0}, batch_size=10000)
        #res=[QA_util_dict_remove_key(data, '_id') for data in cursor]

        res = pd.DataFrame([item for item in cursor])
        try:
            res = res.drop_duplicates(
                (['code', 'date']))
            res['date'] = res['date'].apply(lambda x: str(x)[0:10])
            res = res.drop(['date_stamp'],axis=1).set_index(['date','code'])
        except:
            res = None
        if format in ['P', 'p', 'pandas', 'pd']:
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            QA_util_log_info("QA Error QA_fetch_index_technical_index format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" " % format)
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_index_technical_index data parameter start=%s end=%s is not right' % (start, end))

def QA_fetch_index_target(codes, start_date, end_date, method = 'value'):
    if QA_util_if_trade(end_date):
        pass
    else:
        end_date = QA_util_get_real_date(end_date)
    end = QA_util_get_next_datetime(end_date,10)
    rng1 = QA_util_get_trade_range(start_date, end_date)
    data = QA.QA_fetch_index_day_adv(codes,start_date,end).data.fillna(0).reset_index()
    if method == 'value':
        res = data.groupby('code').apply(index_pct)[['date','code',
                                                    'INDEX_TARGET','INDEX_TARGET3',
                                                    'INDEX_TARGET4','INDEX_TARGET5',
                                                    'INDEX_TARGET10']]
    elif method == 'log':
        res = data.groupby('code').apply(index_pct_log)[['date','code',
                                                        'INDEX_TARGET','INDEX_TARGET3',
                                                        'INDEX_TARGET4','INDEX_TARGET5',
                                                        'INDEX_TARGET10']]
    else:
        res = None
    res['date'] = res['date'].apply(lambda x: str(x)[0:10])
    res = res.set_index(['date','code']).loc[rng1]
    for columnname in res.columns:
        if res[columnname].dtype == 'float64':
            res[columnname]=res[columnname].astype('float16')
        if res[columnname].dtype == 'int64':
            res[columnname]=res[columnname].astype('int8')
    return(res)

@time_this_function
def QA_fetch_index_quant_data(code, start, end = None, type = 'normalization', format='pd'):
    '获取股票日线'
    #code= [code] if isinstance(code,str) else code
    # code checking
    code = QA_util_code_tolist(code)
    index = QA_Sql_Index_Index
    week = QA_Sql_Index_IndexWeek
    alpha = QA_Sql_Index_Alpha191
    alpha101 = QA_Sql_Index_Alpha101

    if QA_util_date_valid(end):

        __data = []

        QA_util_log_info(
            'JOB Get Index Tech Index data start=%s end=%s' % (start, end))
        index_res = index(start,end).groupby('code').fillna(method='ffill').reset_index()
        index_res = index_res[index_res.code.isin(code)]

        QA_util_log_info(
            'JOB Get Index Tech Week data start=%s end=%s' % (start, end))
        week_res = week(start,end).groupby('code').fillna(method='ffill').reset_index()
        week_res = week_res[week_res.code.isin(code)]

        QA_util_log_info(
            'JOB Get Index Alpha191 data start=%s end=%s' % (start, end))
        alpha_res = alpha(start,end).groupby('code').fillna(method='ffill').reset_index()
        alpha_res = alpha_res[alpha_res.code.isin(code)]

        QA_util_log_info(
            'JOB Get Index Alpha101 data start=%s end=%s' % (start, end))
        alpha101_res = alpha101(start,end).groupby('code').fillna(method='ffill').fillna(0).reset_index()
        alpha101_res = alpha101_res[alpha101_res.code.isin(code)]

        try:
            res = index_res.drop_duplicates(
                    (['code', 'date'])).set_index(['date','code']).join(
                week_res.drop_duplicates(
                    (['code', 'date'])).set_index(['date','code'])).join(
                alpha_res.drop_duplicates(
                    (['code', 'date'])).set_index(['date','code'])).join(
                alpha101_res.drop_duplicates(
                    (['code', 'date'])).set_index(['date','code']))

            for columnname in res.columns:
                if res[columnname].dtype == 'float64':
                    res[columnname]=res[columnname].astype('float16')
                if res[columnname].dtype == 'float32':
                    res[columnname]=res[columnname].astype('float16')
                if res[columnname].dtype == 'int64':
                    res[columnname]=res[columnname].astype('int8')
                if res[columnname].dtype == 'int32':
                    res[columnname]=res[columnname].astype('int8')
                if res[columnname].dtype == 'int16':
                    res[columnname]=res[columnname].astype('int8')

        except:
            res = None

        if type == 'standardize':
            res = res.groupby('date').apply(standardize).reset_index()
        elif type == 'normalization':
            res = res.groupby('date').apply(normalization).reset_index()
        else:
            res = res.reset_index()
            QA_util_log_info('##JOB type must be in [standardize, normalization]')

        if format in ['P', 'p', 'pandas', 'pd']:
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            QA_util_log_info("QA Error QA_fetch_index_quant_data format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" " % format)
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_index_quant_data date parameter start=%s end=%s is not right' % (start, end))

def QA_fetch_index_quant_pre(code, start, end=None, method='value', format='pd'):
    QA_util_log_info(
        'JOB Get Index Quant data start=%s end=%s' % (start, end))
    res = QA_fetch_index_quant_data(code, start, end)
    QA_util_log_info(
        'JOB Get Index Target data start=%s end=%s' % (start, end))
    target = QA_fetch_index_target(code, start, end, method=method)
    res = res.join(target)
    if format in ['P', 'p', 'pandas', 'pd']:
        return res
    elif format in ['json', 'dict']:
        return QA_util_to_json_from_pandas(res)
        # 多种数据格式
    elif format in ['n', 'N', 'numpy']:
        return numpy.asarray(res)
    elif format in ['list', 'l', 'L']:
        return numpy.asarray(res).tolist()
    else:
        QA_util_log_info("QA Error QA_fetch_index_quant_data format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" " % format)
        return None

def QA_fetch_stock_alpha101(code, start, end=None, format='pd', collections=DATABASE.stock_alpha101):
    '获取股票日线'
    #code= [code] if isinstance(code,str) else code
    # code checking
    code = QA_util_code_tolist(code)

    if QA_util_date_valid(end):

        __data = []
        cursor = collections.find({
            'code': {'$in': code}, "date_stamp": {
                "$lte": QA_util_date_stamp(end),
                "$gte": QA_util_date_stamp(start)}}, {"_id": 0}, batch_size=10000)
        #res=[QA_util_dict_remove_key(data, '_id') for data in cursor]

        res = pd.DataFrame([item for item in cursor])
        try:
            res = res.drop_duplicates(
                (['code', 'date'])).drop(['date_stamp'],axis=1).set_index(['date','code'])
        except:
            res = None
        if format in ['P', 'p', 'pandas', 'pd']:
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            QA_util_log_info("QA Error QA_fetch_stock_alpha101 format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" " % format)
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_stock_alpha101 data parameter start=%s end=%s is not right' % (start, end))

def QA_fetch_index_alpha101(code, start, end=None, format='pd', collections=DATABASE.index_alpha101):
    '获取股票日线'
    #code= [code] if isinstance(code,str) else code
    # code checking
    code = QA_util_code_tolist(code)

    if QA_util_date_valid(end):

        __data = []
        cursor = collections.find({
            'code': {'$in': code}, "date_stamp": {
                "$lte": QA_util_date_stamp(end),
                "$gte": QA_util_date_stamp(start)}}, {"_id": 0}, batch_size=10000)
        #res=[QA_util_dict_remove_key(data, '_id') for data in cursor]

        res = pd.DataFrame([item for item in cursor])
        try:
            res = res.drop_duplicates(
                (['code', 'date'])).drop(['date_stamp'],axis=1).set_index(['date','code'])
        except:
            res = None
        if format in ['P', 'p', 'pandas', 'pd']:
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            QA_util_log_info("QA Error QA_fetch_index_alpha101 format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" " % format)
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_index_alpha101 data parameter start=%s end=%s is not right' % (start, end))

def QA_fetch_usstock_list(collections=DATABASE.usstock_list):
    '获取股票列表'

    return pd.DataFrame([item for item in collections.find()]).drop(
        '_id',
        axis=1,
        inplace=False
    ).set_index(
        'code',
        drop=False
    )

def QA_fetch_hkstock_list(collections=DATABASE.hkstock_list):
    '获取股票列表'

    return pd.DataFrame([item for item in collections.find()]).drop(
        '_id',
        axis=1,
        inplace=False
    ).set_index(
        'code',
        drop=False
    )

def QA_fetch_usstock_day(
        code,
        start,
        end,
        format='numpy',
        frequence='day',
        collections=DATABASE.usstock_day
):
    """'获取股票日线'

    Returns:
        [type] -- [description]

        感谢@几何大佬的提示
        https://docs.mongodb.com/manual/tutorial/project-fields-from-query-results/#return-the-specified-fields-and-the-id-field-only

    """

    start = str(start)[0:10]
    end = str(end)[0:10]
    #code= [code] if isinstance(code,str) else code

    # code checking
    code = QA_util_code_tolist(code)

    if QA_util_date_valid(end):

        cursor = collections.find(
            {
                'code': {
                    '$in': code
                },
                "date_stamp":
                    {
                        "$lte": QA_util_date_stamp(end),
                        "$gte": QA_util_date_stamp(start)
                    }
            },
            {"_id": 0},
            batch_size=10000
        )
        #res=[QA_util_dict_remove_key(data, '_id') for data in cursor]

        res = pd.DataFrame([item for item in cursor])
        try:
            res = res.assign(
                volume=res.vol,
                date=pd.to_datetime(res.date)
            ).drop_duplicates((['date',
                                'code'])).query('volume>1').set_index(
                'date',
                drop=False
            )
            res = res.loc[:,
                  [
                      'code',
                      'open',
                      'high',
                      'low',
                      'close',
                      'volume',
                      'amount',
                      'date'
                  ]]
        except:
            res = None
        if format in ['P', 'p', 'pandas', 'pd']:
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            QA_util_log_info(
                "QA Error QA_fetch_usstock_day format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" "
                % format
            )
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_usstock_day data parameter start=%s end=%s is not right'
            % (start,
               end)
        )

def QA_fetch_hkstock_day(
        code,
        start,
        end,
        format='numpy',
        frequence='day',
        collections=DATABASE.hkstock_day
):
    """'获取股票日线'

    Returns:
        [type] -- [description]

        感谢@几何大佬的提示
        https://docs.mongodb.com/manual/tutorial/project-fields-from-query-results/#return-the-specified-fields-and-the-id-field-only

    """

    start = str(start)[0:10]
    end = str(end)[0:10]
    #code= [code] if isinstance(code,str) else code

    # code checking
    code = QA_util_code_tolist(code)

    if QA_util_date_valid(end):

        cursor = collections.find(
            {
                'code': {
                    '$in': code
                },
                "date_stamp":
                    {
                        "$lte": QA_util_date_stamp(end),
                        "$gte": QA_util_date_stamp(start)
                    }
            },
            {"_id": 0},
            batch_size=10000
        )
        #res=[QA_util_dict_remove_key(data, '_id') for data in cursor]

        res = pd.DataFrame([item for item in cursor])
        try:
            res = res.assign(
                volume=res.vol,
                date=pd.to_datetime(res.date)
            ).drop_duplicates((['date',
                                'code'])).query('volume>1').set_index(
                'date',
                drop=False
            )
            res = res.loc[:,
                  [
                      'code',
                      'open',
                      'high',
                      'low',
                      'close',
                      'volume',
                      'amount',
                      'date'
                  ]]
        except:
            res = None
        if format in ['P', 'p', 'pandas', 'pd']:
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            QA_util_log_info(
                "QA Error QA_fetch_hkstock_day format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" "
                % format
            )
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_hkstock_day data parameter start=%s end=%s is not right'
            % (start,
               end)
        )

def QA_fetch_usstock_adj(
        code,
        start,
        end,
        format='pd',
        collections=DATABASE.usstock_adj
):
    """获取股票复权系数 ADJ

    """

    start = str(start)[0:10]
    end = str(end)[0:10]
    #code= [code] if isinstance(code,str) else code

    # code checking
    code = QA_util_code_tolist(code)

    if QA_util_date_valid(end):

        cursor = collections.find(
            {
                'code': {
                    '$in': code
                },
                "date": {
                    "$lte": end,
                    "$gte": start
                }
            },
            {"_id": 0},
            batch_size=10000
        )
        #res=[QA_util_dict_remove_key(data, '_id') for data in cursor]

        res = pd.DataFrame([item for item in cursor])
        res.date = pd.to_datetime(res.date)
        return res.set_index('date', drop=False)

def QA_fetch_usstock_cik(collections=DATABASE.usstock_cik):
    '获取股票列表'

    return pd.DataFrame([item for item in collections.find()]).drop(
        '_id',
        axis=1,
        inplace=False
    ).set_index(
        'code',
        drop=False
    )

def QA_fetch_usstock_financial_report():
    pass

def QA_fetch_usstock_financial_calendar():
    pass

def QA_fetch_stock_industryinfo(code, format='pd', collections=DATABASE.stock_industryinfo):
    code = QA_util_code_tolist(code)
    try:
        data = pd.DataFrame(
            [
                item for item in collections
                .find({'code': {
                '$in': code
            }},
                {"_id": 0},
                batch_size=10000)
            ]
        )
        #data['date'] = pd.to_datetime(data['date'])
        return data.set_index('code', drop=False)
    except Exception as e:
        QA_util_log_info(e)
        return None

def QA_fetch_index_info(code, format='pd', collections=DATABASE.index_info):
    code = QA_util_code_tolist(code)
    try:
        data = pd.DataFrame(
            [
                item for item in collections
                .find({'code': {
                '$in': code
            }},
                {"_id": 0},
                batch_size=10000)
            ]
        )
        #data['date'] = pd.to_datetime(data['date'])
        return data.set_index('code', drop=False)
    except Exception as e:
        #QA_util_log_info(code, e)
        return None

def QA_fetch_stock_delist(collections=DATABASE.stock_delist):
    '获取股票列表'

    return pd.DataFrame([item for item in collections.find()]).drop(
        '_id',
        axis=1,
        inplace=False
    ).set_index(
        'code',
        drop=False
    )

def QA_fetch_stock_all():
    stock_delist = QA_fetch_stock_delist()[['code','name','sse']]
    code_list = QA_fetch_stock_list()[['code','name','sse']]
    code_list = code_list.append(stock_delist)
    return(code_list)

def QA_fetch_stock_week(
        code,
        start,
        end,
        format='numpy',
        collections=DATABASE.stock_week
):
    """'获取股票日线'

    Returns:
        [type] -- [description]

        感谢@几何大佬的提示
        https://docs.mongodb.com/manual/tutorial/project-fields-from-query-results/#return-the-specified-fields-and-the-id-field-only

    """

    start = str(start)[0:10]
    end = str(end)[0:10]
    #code= [code] if isinstance(code,str) else code

    # code checking
    code = QA_util_code_tolist(code)

    if QA_util_date_valid(end):

        cursor = collections.find(
            {
                'code': {
                    '$in': code
                },
                "date_stamp":
                    {
                        "$lte": QA_util_date_stamp(end),
                        "$gte": QA_util_date_stamp(start)
                    }
            },
            {"_id": 0},
            batch_size=10000
        )
        #res=[QA_util_dict_remove_key(data, '_id') for data in cursor]

        res = pd.DataFrame([item for item in cursor])
        try:
            res = res.assign(
                volume=res.vol,
                date=pd.to_datetime(res.date)
            ).drop_duplicates((['date',
                                'code'])).query('volume>1').set_index(
                'date',
                drop=False
            )
            res = res.loc[:,
                  [
                      'code',
                      'open',
                      'high',
                      'low',
                      'close',
                      'volume',
                      'amount',
                      'date'
                  ]]
        except:
            res = None
        if format in ['P', 'p', 'pandas', 'pd']:
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            print(
                "QA Error QA_fetch_stock_week format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" "
                % format
            )
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_stock_week data parameter start=%s end=%s is not right'
            % (start,
               end)
        )

def QA_fetch_stock_month(
        code,
        start,
        end,
        format='numpy',
        collections=DATABASE.stock_month
):
    """'获取股票日线'

    Returns:
        [type] -- [description]

        感谢@几何大佬的提示
        https://docs.mongodb.com/manual/tutorial/project-fields-from-query-results/#return-the-specified-fields-and-the-id-field-only

    """

    start = str(start)[0:10]
    end = str(end)[0:10]
    #code= [code] if isinstance(code,str) else code

    # code checking
    code = QA_util_code_tolist(code)

    if QA_util_date_valid(end):

        cursor = collections.find(
            {
                'code': {
                    '$in': code
                },
                "date_stamp":
                    {
                        "$lte": QA_util_date_stamp(end),
                        "$gte": QA_util_date_stamp(start)
                    }
            },
            {"_id": 0},
            batch_size=10000
        )
        #res=[QA_util_dict_remove_key(data, '_id') for data in cursor]

        res = pd.DataFrame([item for item in cursor])
        try:
            res = res.assign(
                volume=res.vol,
                date=pd.to_datetime(res.date)
            ).drop_duplicates((['date',
                                'code'])).query('volume>1').set_index(
                'date',
                drop=False
            )
            res = res.loc[:,
                  [
                      'code',
                      'open',
                      'high',
                      'low',
                      'close',
                      'volume',
                      'amount',
                      'date'
                  ]]
        except:
            res = None
        if format in ['P', 'p', 'pandas', 'pd']:
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            print(
                "QA Error QA_fetch_stock_month format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" "
                % format
            )
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_stock_month data parameter start=%s end=%s is not right'
            % (start,
               end)
        )

def QA_fetch_stock_year(
        code,
        start,
        end,
        format='numpy',
        collections=DATABASE.stock_year
):
    """'获取股票日线'

    Returns:
        [type] -- [description]

        感谢@几何大佬的提示
        https://docs.mongodb.com/manual/tutorial/project-fields-from-query-results/#return-the-specified-fields-and-the-id-field-only

    """

    start = str(start)[0:10]
    end = str(end)[0:10]
    #code= [code] if isinstance(code,str) else code

    # code checking
    code = QA_util_code_tolist(code)

    if QA_util_date_valid(end):

        cursor = collections.find(
            {
                'code': {
                    '$in': code
                },
                "date_stamp":
                    {
                        "$lte": QA_util_date_stamp(end),
                        "$gte": QA_util_date_stamp(start)
                    }
            },
            {"_id": 0},
            batch_size=10000
        )
        #res=[QA_util_dict_remove_key(data, '_id') for data in cursor]

        res = pd.DataFrame([item for item in cursor])
        try:
            res = res.assign(
                volume=res.vol,
                date=pd.to_datetime(res.date)
            ).drop_duplicates((['date',
                                'code'])).query('volume>1').set_index(
                'date',
                drop=False
            )
            res = res.loc[:,
                  [
                      'code',
                      'open',
                      'high',
                      'low',
                      'close',
                      'volume',
                      'amount',
                      'date'
                  ]]
        except:
            res = None
        if format in ['P', 'p', 'pandas', 'pd']:
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            print(
                "QA Error QA_fetch_stock_year format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" "
                % format
            )
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_stock_year data parameter start=%s end=%s is not right'
            % (start,
               end)
        )

def QA_fetch_index_week(
        code,
        start,
        end,
        format='numpy',
        collections=DATABASE.index_week
):
    """'获取股票日线'

    Returns:
        [type] -- [description]

        感谢@几何大佬的提示
        https://docs.mongodb.com/manual/tutorial/project-fields-from-query-results/#return-the-specified-fields-and-the-id-field-only

    """

    start = str(start)[0:10]
    end = str(end)[0:10]
    #code= [code] if isinstance(code,str) else code

    # code checking
    code = QA_util_code_tolist(code)

    if QA_util_date_valid(end):

        cursor = collections.find(
            {
                'code': {
                    '$in': code
                },
                "date_stamp":
                    {
                        "$lte": QA_util_date_stamp(end),
                        "$gte": QA_util_date_stamp(start)
                    }
            },
            {"_id": 0},
            batch_size=10000
        )
        #res=[QA_util_dict_remove_key(data, '_id') for data in cursor]

        res = pd.DataFrame([item for item in cursor])
        try:
            res = res.assign(
                volume=res.vol,
                date=pd.to_datetime(res.date)
            ).drop_duplicates((['date',
                                'code'])).query('volume>1').set_index(
                'date',
                drop=False
            )
            res = res.loc[:,
                  [
                      'code',
                      'open',
                      'high',
                      'low',
                      'close',
                      'volume',
                      'amount',
                      'date'
                  ]]
        except:
            res = None
        if format in ['P', 'p', 'pandas', 'pd']:
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            print(
                "QA Error QA_fetch_index_week format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" "
                % format
            )
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_index_week data parameter start=%s end=%s is not right'
            % (start,
               end)
        )

def QA_fetch_index_month(
        code,
        start,
        end,
        format='numpy',
        collections=DATABASE.index_month
):
    """'获取股票日线'

    Returns:
        [type] -- [description]

        感谢@几何大佬的提示
        https://docs.mongodb.com/manual/tutorial/project-fields-from-query-results/#return-the-specified-fields-and-the-id-field-only

    """

    start = str(start)[0:10]
    end = str(end)[0:10]
    #code= [code] if isinstance(code,str) else code

    # code checking
    code = QA_util_code_tolist(code)

    if QA_util_date_valid(end):

        cursor = collections.find(
            {
                'code': {
                    '$in': code
                },
                "date_stamp":
                    {
                        "$lte": QA_util_date_stamp(end),
                        "$gte": QA_util_date_stamp(start)
                    }
            },
            {"_id": 0},
            batch_size=10000
        )
        #res=[QA_util_dict_remove_key(data, '_id') for data in cursor]

        res = pd.DataFrame([item for item in cursor])
        try:
            res = res.assign(
                volume=res.vol,
                date=pd.to_datetime(res.date)
            ).drop_duplicates((['date',
                                'code'])).query('volume>1').set_index(
                'date',
                drop=False
            )
            res = res.loc[:,
                  [
                      'code',
                      'open',
                      'high',
                      'low',
                      'close',
                      'volume',
                      'amount',
                      'date'
                  ]]
        except:
            res = None
        if format in ['P', 'p', 'pandas', 'pd']:
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            print(
                "QA Error QA_fetch_index_month format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" "
                % format
            )
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_index_month data parameter start=%s end=%s is not right'
            % (start,
               end)
        )

def QA_fetch_index_year(
        code,
        start,
        end,
        format='numpy',
        collections=DATABASE.index_year
):
    """'获取股票日线'

    Returns:
        [type] -- [description]

        感谢@几何大佬的提示
        https://docs.mongodb.com/manual/tutorial/project-fields-from-query-results/#return-the-specified-fields-and-the-id-field-only

    """

    start = str(start)[0:10]
    end = str(end)[0:10]
    #code= [code] if isinstance(code,str) else code

    # code checking
    code = QA_util_code_tolist(code)

    if QA_util_date_valid(end):

        cursor = collections.find(
            {
                'code': {
                    '$in': code
                },
                "date_stamp":
                    {
                        "$lte": QA_util_date_stamp(end),
                        "$gte": QA_util_date_stamp(start)
                    }
            },
            {"_id": 0},
            batch_size=10000
        )
        #res=[QA_util_dict_remove_key(data, '_id') for data in cursor]

        res = pd.DataFrame([item for item in cursor])
        try:
            res = res.assign(
                volume=res.vol,
                date=pd.to_datetime(res.date)
            ).drop_duplicates((['date',
                                'code'])).query('volume>1').set_index(
                'date',
                drop=False
            )
            res = res.loc[:,
                  [
                      'code',
                      'open',
                      'high',
                      'low',
                      'close',
                      'volume',
                      'amount',
                      'date'
                  ]]
        except:
            res = None
        if format in ['P', 'p', 'pandas', 'pd']:
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            print(
                "QA Error QA_fetch_index_year format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" "
                % format
            )
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_index_year data parameter start=%s end=%s is not right'
            % (start,
               end)
        )