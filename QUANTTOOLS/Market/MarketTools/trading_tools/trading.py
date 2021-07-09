from QUANTAXIS.QAUtil import QA_util_log_info, QA_util_get_pre_trade_date
from QUANTTOOLS.Message.message_func.wechat import send_actionnotice
from QUANTTOOLS.Trader.account_manage.base_func.Client import get_Client,check_Client
from QUANTTOOLS.Trader.account_manage.TradAction.BUY import BUY
from QUANTTOOLS.Trader.account_manage.TradAction.SELL import SELL
from QUANTTOOLS.Trader.account_manage.TradAction.HOLD import HOLD
from QUANTTOOLS.Market.MarketTools.trading_tools.BuildTradingFrame import build
from QUANTTOOLS.QAStockETL.QAFetch.QATdx import QA_fetch_get_stock_realtm_bid
from QUANTTOOLS.QAStockETL.QAFetch.QAQuery import QA_fetch_stock_name
from QUANTTOOLS.Model.FactorTools.QuantMk import get_quant_data_hour
from QUANTTOOLS.Trader.account_manage.base_func.Client import get_UseCapital, get_StockPos, get_hold
import time
import datetime

def open_control(trading_date):
    time_contrl_bf("09:30:00")
    QA_util_log_info('##JOB Now Start Trading ==== {}'.format(str(trading_date)), ui_log = None)

def close_control(strategy_id, trading_date):
    time_contrl_af("15:00:00")
    QA_util_log_info('##JOB Trading Finished ==================== {}'.format(trading_date), ui_log=None)
    send_actionnotice(strategy_id,'Trading Report:{}'.format(trading_date),'Trading Finished',direction = 'Trading',offset='Finished',volume=None)

def time_contrl_bf(tm_mark):
    tm = int(datetime.datetime.now().strftime("%H%M%S"))
    while tm <= int(time.strftime("%H%M%S",time.strptime(tm_mark, "%H:%M:%S"))):
        time.sleep(15)
        tm = int(datetime.datetime.now().strftime("%H%M%S"))
    return(tm_mark)

def time_contrl_af(tm_mark):
    tm = int(datetime.datetime.now().strftime("%H%M%S"))
    while tm >= int(time.strftime("%H%M%S",time.strptime(tm_mark, "%H:%M:%S"))):
        time.sleep(15)
        tm = int(datetime.datetime.now().strftime("%H%M%S"))
    return(tm_mark)

def trade_roboot(target_tar, account, trading_date, percent, strategy_id, type='end', exceptions = None, test = False):

    QA_util_log_info('##JOB Now Get Account info ==== {}'.format(str(trading_date)), ui_log = None)
    client = get_Client()
    QA_util_log_info('##JOB Now Cancel Orders ===== {}'.format(str(trading_date)), ui_log = None)
    client.cancel_all(account)
    QA_util_log_info(target_tar, ui_log = None)
    sub_accounts, frozen, positions, frozen_positions = check_Client(client, account, strategy_id, trading_date, exceptions=exceptions)
    account_info = client.get_account(account)

    if target_tar is None:
        QA_util_log_info('触发清仓 ==================== {}'.format(trading_date), ui_log=None)
        send_actionnotice(strategy_id,'触发清仓:{}'.format(trading_date),'触发清仓',direction = 'SELL',offset='SELL',volume=None)
        #e = send_trading_message(account, strategy_id, account_info, None, "触发清仓", None, 0, direction = 'SELL', type='MARKET', priceType=4,price=None, client=client)

    QA_util_log_info('##JOB Now Build Trading Frame ===== {}'.format(str(trading_date)), ui_log = None)
    res = build(target_tar, positions, sub_accounts, percent)
    res1 = res
    QA_util_log_info(res[['NAME','INDUSTRY','deal','close','目标持股数','股票余额','可用余额','冻结数量']])

    send_actionnotice(strategy_id,'交易报告:{}'.format(trading_date),'开始交易',direction = 'HOLD',offset='HOLD',volume=None)

    while res.deal.apply(abs).sum() > 0:

        QA_util_log_info('##JOB Now Start Trading ===== {}'.format(str(trading_date)), ui_log = None)

        QA_util_log_info('##JOB Now Check Timing ===== {}'.format(str(trading_date)), ui_log = None)

        tm = int(datetime.datetime.now().strftime("%H%M%S"))
        target_ea = int(time.strftime("%H%M%S", time.strptime("09:25:00", "%H:%M:%S")))
        target_af = int(time.strftime("%H%M%S", time.strptime("15:00:00", "%H:%M:%S")))

        if tm >= target_af:
            QA_util_log_info('已过交易时段 {hour} ==================== {date}'.format(hour = tm, date = trading_date), ui_log=None)
            send_actionnotice(strategy_id,'交易报告:{}'.format(trading_date),'已过交易时段',direction = 'HOLD',offset='HOLD',volume=None)
            if test == False:
                break
        #if tm >= target_af:
        #    break

        QA_util_log_info('##JOB Now Start Selling ===== {}'.format(str(trading_date)), ui_log = None)
        if res[res['deal']<0].shape[0] == 0:
            QA_util_log_info('无卖出动作 ==================== {}'.format(trading_date), ui_log=None)
        else:
            for code in res[res['deal'] < 0].index:
                QA_util_log_info('##JOB Now Prepare Selling {code} Info ==== {date}'.format(code = code, date = str(trading_date)), ui_log = None)
                target_pos = float(res.loc[code]['目标持股数'])
                target = float(res.loc[code]['股票余额'])
                name = res.loc[code]['NAME']
                industry = res.loc[code]['INDUSTRY']
                deal_pos = abs(float(res.loc[code]['deal']))
                close = float(res.loc[code]['close'])

                QA_util_log_info('##JOB Now Start Selling {code} ==== {date}'.format(code = code, date = str(trading_date)), ui_log = None)
                SELL(client, account, strategy_id, account_info,trading_date, code, name, industry, deal_pos, target_pos, target, close, type = type, test = test)

                time.sleep(3)

            time.sleep(15)

        QA_util_log_info('##JOB Now Start Holding ===== {}'.format(str(trading_date)), ui_log = None)
        if res[res['deal'] == 0].shape[0] == 0:
            QA_util_log_info('无持续持仓动作 ==================== {}'.format(trading_date), ui_log=None)
        else:
            for code in res[res['deal'] == 0].index:
                QA_util_log_info('##JOB Now Prepare Holding {code} Info ===== {date}'.format(code = code, date = str(trading_date)), ui_log = None)
                target_pos = float(res.loc[code]['目标持股数'])
                target = float(res.loc[code]['股票余额'])
                name = res.loc[code]['NAME']
                industry = res.loc[code]['INDUSTRY']
                deal_pos = abs(float(res.loc[code]['deal']))
                close = float(res.loc[code]['close'])

                QA_util_log_info('##JOB Now Start Holding {code} ===== {date}'.format(code = code, date = str(trading_date)), ui_log = None)
                HOLD(strategy_id, account_info,trading_date, code, name, industry, target_pos, target)

                time.sleep(1)

        QA_util_log_info('##JOB Now Start Buying ===== {}'.format(str(trading_date)), ui_log = None)
        if res[res['deal'] > 0].shape[0] == 0:
            QA_util_log_info('无买入动作 ==================== {}'.format(trading_date), ui_log=None)
        else:
            for code in res[res['deal'] > 0].index:
                QA_util_log_info('##JOB Now Prepare Buying {code} Info ===== {date}'.format(code = code, date = str(trading_date)), ui_log = None)
                target_pos = float(res.loc[code]['目标持股数'])
                target = float(res.loc[code]['股票余额'])
                name = res.loc[code]['NAME']
                industry = res.loc[code]['INDUSTRY']
                deal_pos = abs(float(res.loc[code]['deal']))
                close = float(res.loc[code]['close'])

                QA_util_log_info('##JOB Now Start Buying {code} ===== {date}'.format(code = code, date = str(trading_date)), ui_log = None)
                BUY(client, account, strategy_id, account_info,trading_date, code, name, industry, deal_pos, target_pos, target, close, type, test = test)

                time.sleep(3)

            time.sleep(30)

        if type == 'end':
            QA_util_log_info('##JOB Now Cancel Orders ===== {}'.format(str(trading_date)), ui_log = None)
            client.cancel_all(account)

            QA_util_log_info('##JOB Now Refresh Account Info ==== {}'.format(str(trading_date)), ui_log = None)
            sub_accounts, frozen, positions, frozen_positions = check_Client(client, account, strategy_id, trading_date, exceptions=exceptions)
            sub_accounts = sub_accounts - frozen

            QA_util_log_info('##JOB Now ReBuild Trading Frame ==== {}'.format(str(trading_date)), ui_log = None)
            res = build(target_tar, positions, sub_accounts, percent)

        elif type == 'morning':
            QA_util_log_info('##JOB Now Morning Trading Success ==== {}'.format(str(trading_date)), ui_log = None)
            break
        else:
            QA_util_log_info('##Trading type must in [end, morning] ==== {}'.format(str(trading_date)), ui_log = None)
            break

    QA_util_log_info('交易完成 ==================== {}'.format(trading_date), ui_log=None)
    send_actionnotice(strategy_id,'交易报告:{}'.format(trading_date),'交易完成',direction = 'HOLD',offset='HOLD',volume=None)

    return(res1)


def trade_roboot2(target_tar, account, trading_date, percent, strategy_id, type='end', exceptions = None, test = False):

    QA_util_log_info('##JOB Now Check Timing ==== {}'.format(str(trading_date)), ui_log = None)

    tm = datetime.datetime.now().strftime("%H:%M:%S")
    morning_begin = "09:30:00"
    morning_end = "11:30:00"
    afternoon_begin = "13:00:00"
    afternoon_end = "15:00:00"
    marktm_list = ["10:30:00","11:30:00","14:00:00", "15:00:00"]
    action_list = ["09:30:00","10:30:00","13:00:00", "14:00:00"]

    ##init+确定时间
    a = marktm_list + [tm]
    a.sort()

    if a.index(tm) == 0:
        mark_tm = '15:00:00'
        action_tm = '09:30:00'
    else:
        mark_tm = a[a.index(tm)-1]
        action_tm = action_list[a.index(tm)]

    tm = int(time.strftime("%H%M%S",time.strptime(tm, "%H:%M:%S")))
    QA_util_log_info('##JOB Now Start Trading ==== {}'.format(str(trading_date)), ui_log = None)
    while tm <= int(time.strftime("%H%M%S",time.strptime(afternoon_end, "%H:%M:%S"))):

        QA_util_log_info('##JOB Now Get Account info ==== {}'.format(str(trading_date)), ui_log = None)
        client = get_Client()
        try:
            client.cancel_all(account)
            time.sleep(2)
        except:
            QA_util_log_info('##JOB Cancel Orders Failed==== {}'.format(str(trading_date)), ui_log = None)
        sub_accounts, frozen, positions, frozen_positions = check_Client(client, account, strategy_id, trading_date, exceptions=exceptions)
        positions = positions[positions['可用余额'] > 0]
        account_info = client.get_account(account)

        QA_util_log_info('##JOB Now Build Trading Frame ==== {}'.format(str(trading_date)), ui_log = None)

        if mark_tm == "15:00:00":
            stm = QA_util_get_pre_trade_date(trading_date) + ' ' + '15:00:00'
        else:
            stm = trading_date + ' ' + mark_tm

        QA_util_log_info('##JOB Now Time ==== {}'.format(str(stm)), ui_log = None)

        ##分析数据
        while tm < int(time.strftime("%H%M%S",time.strptime(mark_tm, "%H:%M:%S"))):
            if tm >= int(time.strftime("%H%M%S",time.strptime(mark_tm, "%H:%M:%S"))):
                data = get_quant_data_hour(QA_util_get_pre_trade_date(trading_date),trading_date,list(set(positions.code.tolist()+list(target_tar.index))), type= 'real')
                res1 = data.loc[stm][['SKDJ_K_30M','SKDJ_TR_30M','SKDJ_K_HR','SKDJ_TR_HR','SKDJ_CROSS1_HR','CROSS_JC_HR','CROSS_SC_HR','SKDJ_CROSS2_HR','MA5_HR','MA5_30M','MA10_HR','MA60_HR','CCI_HR','CCI_CROSS1_HR','CCI_CROSS2_HR']].sort_values('SKDJ_K_HR')
                target_list = [i for i in list(res1.index) if i not in positions.code.tolist()]
                ####job1 小时级报告 指数小时级跟踪
                QA_util_log_info('##JOB Now cross1 ==== {}: {}'.format(str(stm), data[data.SKDJ_CROSS1_HR == 1][['SKDJ_K_30M','SKDJ_TR_30M','SKDJ_TR_HR','SKDJ_CROSS1_HR','SKDJ_CROSS2_HR','MA5_HR']]), ui_log = None)
                QA_util_log_info('##JOB Now cross2 ==== {}: {}'.format(str(stm), data[data.SKDJ_CROSS2_HR == 1][['SKDJ_K_30M','SKDJ_TR_30M','SKDJ_TR_HR','SKDJ_CROSS1_HR','SKDJ_CROSS2_HR','MA5_HR']]), ui_log = None)
            else:
                time.sleep(60)
                tm = int(datetime.datetime.now().strftime("%H%M%S"))

        while tm < int(time.strftime("%H%M%S",time.strptime(morning_begin, "%H:%M:%S"))):
            time.sleep(15)
            tm = int(datetime.datetime.now().strftime("%H%M%S"))

        while tm >= int(time.strftime("%H%M%S",time.strptime(morning_end, "%H:%M:%S"))) and tm <= int(time.strftime("%H%M%S",time.strptime(afternoon_begin, "%H:%M:%S"))):
            time.sleep(600)
            tm = int(datetime.datetime.now().strftime("%H%M%S"))
            QA_util_log_info(tm)

        ##action
        while tm <= int(time.strftime("%H%M%S",time.strptime(action_tm, "%H:%M:%S"))) and action_tm is not None:

            if tm > int(time.strftime("%H%M%S",time.strptime(action_tm, "%H:%M:%S"))):
                for code in [positions.code.tolist(), target_list]:
                    name = QA_fetch_stock_name(code)
                    QA_util_log_info('##JOB Now Code {stm} ==== {code}({name})'.format(stm=str(stm),code=str(code),name=str(name)), ui_log = None)
                    try:
                        res2 = res1.loc[code]
                        QA_util_log_info('{code}{name}-{stm}:hourly: {hourly}'.format(code=code,name=name,stm=stm,hourly=res2.SKDJ_TR_HR))
                    except:
                        res2 = None
                        QA_util_log_info('error')
                    #try:

                    if res2 is not None and 'DR' not in name:

                        if code in positions.code.tolist():

                            QA_util_log_info('##JOB Now Selling Check ==== {}'.format(code), ui_log = None)
                            if res2.SKDJ_CROSS1_HR == True and res2.MA5_HR < 0 and res2.SKDJ_TR_30M < 1:
                                msg = 'SKDJ死叉'
                            #elif res2.MA10_HR < 0:
                            #    msg = '打穿MA10'
                            elif res2.SKDJ_TR_HR < 1 and res2.MA5_HR < 0 and res2.SKDJ_TR_30M < 1:
                                msg = 'SKDJ止损:跌破MA5'
                            elif res2.SKDJ_TR_30M < 1 and res2.MA5_30M < 0:
                                ##当日错误入场之后 次日及早离场
                                #msg = 'SKDJ止损:30Min跌破MA5'
                                msg = None
                            else:
                                msg = None
                                ###卖出信号1

                            if msg is not None:
                                QA_util_log_info('##JOB Now Selling ==== {}'.format(code), ui_log = None)
                                send_actionnotice(strategy_id,'{code}{name}:{stm}{msg}'.format(code=code,name=name,stm=stm, msg=msg),'卖出信号',direction = 'SELL',offset=mark_tm,volume=None)
                                deal_pos = get_StockPos(code, client, account)
                                target_pos = 0
                                industry = str(positions.set_index('code').loc[code].INDUSTRY)
                                try_times = 0
                                while deal_pos > 0 and try_times <= 5:
                                    client.cancel_all(account)
                                    QA_util_log_info('##JOB Now Start Selling {code} ==== {stm}{msg}'.format(code = code, stm = str(stm), msg=msg), ui_log = None)
                                    SELL(client, account, strategy_id, account_info, trading_date, code, name, industry, deal_pos, target_pos, target=None, close=0, type = 'end', test = test)
                                    time.sleep(3)
                                    deal_pos = get_StockPos(code, client, account)
                                    try_times += 1
                            else:
                                QA_util_log_info('##JOB Not On Selling ==== {}'.format(code))

                        if code in [i for i in list(target_tar.index) if i not in positions.code.tolist()]:
                            QA_util_log_info('##JOB Now Buying Ckeck==== {}'.format(code), ui_log = None)

                            QA_util_log_info('##JOB Not On Buying ==== {} SKDJ_CROSS2_HR:{} CROSS_JC_HR:{} SKDJ_K_30M:{} SKDJ_TR_30M:{}'.format(code, res2.SKDJ_CROSS2_HR, res2.CROSS_JC_HR, res2.SKDJ_K_30M, res2.SKDJ_TR_30M))
                            if res2.SKDJ_K_30M <= 50 and res2.SKDJ_CROSS2_HR == 1 and res2.SKDJ_TR_30M > 0:
                                msg = 'SKDJ金叉'
                            elif res2.CROSS_JC_HR == 1 and res2.SKDJ_K_30M <= 50 and res2.SKDJ_TR_30M > 0:
                                msg = 'MACD金叉'
                            else:
                                msg = None

                            if msg is not None:
                                if get_UseCapital(client, account) >= 3000:
                                    QA_util_log_info('##JOB Now Buying==== {}'.format(code), ui_log = None)
                                    ###买入信号
                                    send_actionnotice(strategy_id,'{code}{name}:{stm}{msg}'.format(code=code,name=name,stm=stm, msg=msg),'买入信号',direction = 'BUY',offset=mark_tm,volume=None)
                                    price = round(QA_fetch_get_stock_realtm_bid(code)+0.01,2)
                                    deal_pos = round(80000 / price,2)
                                    target_pos = deal_pos
                                    industry = str(target_tar.loc[code].INDUSTRY)
                                    QA_util_log_info('##JOB Now Start Buying {code} ===== {stm}{msg}'.format(code = code, stm = str(stm), msg=msg), ui_log = None)
                                    if get_hold(client, account) <= percent:
                                        BUY(client, account, strategy_id, account_info,trading_date, code, name, industry, deal_pos, target_pos, target=None, close=0, type = 'end', test = test)
                                        time.sleep(1)
                                    else:
                                        QA_util_log_info('##JOB Now Full {code} {percent}/{hold} ===== {stm}'.format(code = code,percent=percent,hold=get_hold(client, account), stm = str(stm)), ui_log = None)
                                else:
                                    QA_util_log_info('##JOB Now Not Enough Money==== {}'.format(code), ui_log = None)
                            else:
                                QA_util_log_info('##JOB Now Not On Buying==== {}'.format(code), ui_log = None)
            else:
                time.sleep(60)
                tm = int(datetime.datetime.now().strftime("%H%M%S"))

        ##update mark_tm action_tm
        if marktm_list.index(mark_tm) == len(marktm_list) - 1:
            mark_tm = marktm_list[0]
        else:
            mark_tm = marktm_list[marktm_list.index(mark_tm) + 1]

        if marktm_list.index(mark_tm) == len(marktm_list) -1:
            action_tm = None
        else:
            action_tm = action_list[action_list.index(action_tm) + 1]

        ###update time
        tm = int(datetime.datetime.now().strftime("%H%M%S"))

    ##收市
    if tm >= int(time.strftime("%H%M%S", time.strptime(afternoon_end, "%H:%M:%S"))):
        ###time out
        QA_util_log_info('##JOB Trading Finished ==================== {}'.format(trading_date), ui_log=None)
        send_actionnotice(strategy_id,'Trading Report:{}'.format(trading_date),'Trading Finished',direction = 'Trading',offset='Finished',volume=None)

if __name__ == '__main__':
    pass