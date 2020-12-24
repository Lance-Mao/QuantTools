import cx_Oracle
import pandas as pd
import numpy as np
from QUANTAXIS.QAUtil import QA_util_log_info
from QUANTTOOLS.QAStockETL.QAData.database_settings import (Oracle_Database, Oracle_User, Oracle_Password, Oralce_Server, MongoDB_Server, MongoDB_Database)

ORACLE_PATH2 = '{user}/{password}@{server}:1521/{database}'.format(database = Oracle_Database, password = Oracle_Password, server = Oralce_Server, user = Oracle_User)

sql_text = '''select to_char(ORDER_DATE, 'yyyy-mm-dd') as "date",
CODE AS "code",VR
,VRSI
,VRSI_C
,VSTD
,BOLL
,UB
,LB
,WIDTH
,WR
,MR
,SR
,WS
,MS
,SS
,MIKE_WRSC
,MIKE_WRJC
,MIKE_WSSC
,MIKE_WSJC
,MIKE_TR
,MIKE_BOLL
,ASI
,ASIT
,OBV
,OBV_C
,PVT
,VPT
,MAVPT
,VPT_CROSS1
,VPT_CROSS2
,VPT_CROSS3
,VPT_CROSS4
,KDJ_K
,KDJ_D
,KDJ_J
,KDJ_CROSS1
,KDJ_CROSS2
,WR1
,WR2
,WR_CROSS1
,WR_CROSS2
,ROC
,ROCMA
,RSI1
,RSI2
,RSI3
,RSI1_C
,RSI2_C
,RSI3_C
,RSI_CROSS1
,RSI_CROSS2
,CCI
,CCI_CROSS1
,CCI_CROSS2
,CCI_CROSS3
,CCI_CROSS4
,BIAS1
,BIAS2
,BIAS3
,BIAS_CROSS1
,BIAS_CROSS2
,OSC
,MAOSC
,OSC_CROSS1
,OSC_CROSS2
,OSC_CROSS3
,OSC_CROSS4
,ADTM
,MAADTM
,ADTM_CROSS1
,ADTM_CROSS2
,DIF
,DEA
,MACD
,CROSS_JC
,CROSS_SC
,MACD_TR
,DI1
,DI2
,ADX
,ADXR
,ADX_C
,DI_M
,DI_CROSS1
,DI_CROSS2
,ADX_CROSS1
,ADX_CROSS2
,DDD
,AMA
,DMA_CROSS1
,DMA_CROSS2
,MTM
,MTMMA
,MTM_CROSS1
,MTM_CROSS2
,MTM_CROSS3
,MTM_CROSS4
,MA1
,MA2
,MA3
,MA4
,BBI
,BBI_CROSS1
,BBI_CROSS2
,MFI
,MFI_C
,TR
,ATR
,ATRR
,RSV
,SKDJ_K
,SKDJ_D
,SKDJ_CROSS1
,SKDJ_CROSS2
,DDI
,ADDI
,AD
,DDI_C
,AD_C
,ADDI_C
,SHA_LOW
,SHA_UP
,BODY
,BODY_ABS
,PRICE_PCG
,MA5
,MA10
,MA20
,MA60
,MA120
,MA180
,SHORT10
,SHORT20
,SHORT60
,LONG60
,LONG120
,LONG180
,SHORT_CROSS1
,SHORT_CROSS2
,LONG_CROSS1
,LONG_CROSS2
,LONG_AMOUNT
,SHORT_AMOUNT
,CDL2CROWS
,CDL3BLACKCROWS
,CDL3INSIDE
,CDL3LINESTRIKE
,CDL3OUTSIDE
,CDL3STARSINSOUTH
,CDL3WHITESOLDIERS
,CDLABANDONEDBABY
,CDLADVANCEBLOCK
,CDLBELTHOLD
,CDLBREAKAWAY
,CDLCLOSINGMARUBOZU
,CDLCONCEALBABYSWALL
,CDLCOUNTERATTACK
,CDLDARKCLOUDCOVER
,CDLDOJI
,CDLDOJISTAR
,CDLDRAGONFLYDOJI
,CDLENGULFING
,CDLEVENINGDOJISTAR
,CDLEVENINGSTAR
,CDLGAPSIDESIDEWHITE
,CDLGRAVESTONEDOJI
,CDLHAMMER
,CDLHANGINGMAN
,CDLHARAMI
,CDLHARAMICROSS
,CDLHIGHWAVE
,CDLHIKKAKE
,CDLHIKKAKEMOD
,CDLHOMINGPIGEON
,CDLIDENTICAL3CROWS
,CDLINNECK
,CDLINVERTEDHAMMER
,CDLKICKING
,CDLKICKINGBYLENGTH
,CDLLADDERBOTTOM
,CDLLONGLEGGEDDOJI
,CDLLONGLINE
,CDLMARUBOZU
,CDLMATCHINGLOW
,CDLMATHOLD
,CDLMORNINGDOJISTAR
,CDLMORNINGSTAR
,CDLONNECK
,CDLPIERCING
,CDLRICKSHAWMAN
,CDLRISEFALL3METHODS
,CDLSEPARATINGLINES
,CDLSHOOTINGSTAR
,CDLSHORTLINE
,CDLSPINNINGTOP
,CDLSTALLEDPATTERN
,CDLSTICKSANDWICH
,CDLTAKURI
,CDLTASUKIGAP
,CDLTHRUSTING
,CDLTRISTAR
,CDLUNIQUE3RIVER
,CDLUPSIDEGAP2CROWS
,CDLXSIDEGAP3METHODS
,MA5_C
,MA10_C
,MA20_C
,MA60_C
,MA120_C
,MA180_C
from STOCK_TECHNICAL
where order_Date >=
to_date('{from_}', 'yyyy-mm-dd')
and order_Date <=
to_date('{to_}', 'yyyy-mm-dd')
'''

def QA_Sql_Stock_Index(from_ , to_, sql_text = sql_text, ui_log= None):
    QA_util_log_info(
        '##JOB01 Now Fetch Stock QuantData Index ==== from {from_} to {to_}'.format(from_=from_,to_=to_), ui_log)
    sql_text = sql_text.format(from_=from_,to_=to_)
    conn = cx_Oracle.connect(ORACLE_PATH2)
    data = pd.read_sql(sql=sql_text, con=conn)
    conn.close()
    data = data.drop_duplicates((['code', 'date'])).set_index(['date','code'])
    data = data.assign(SKDJ_TR = (data.SKDJ_K > data.SKDJ_D)*1,
                       TERNS = ((data.SHORT20 > 0) & (data.LONG60 > 0) & (data.LONG_AMOUNT > 0)) * 1)
    return(data)