#coding :utf-8

working_dir = 'D:\\model\\current'
percent = 1
exceptions = None
top = 20

stock_xg_set = ['ALPHA_057',
                'AD_WK',
                'MA45',
                'MA_VOL60',
                'LONG_TR_WK',
                'ALPHA_097',
                'WR2_WK',
                'MA35',
                'MA60',
                'MA_VOL40',
                'AVG30_TOR',
                'MA30',
                'ALPHA_074',
                'ALPHA_068',
                'AVG30_RNG',
                'GMMA3',
                'ALPHA_072',
                'ALPHA_062',
                'GMMA35_HR',
                'MA_VOL10',
                'ALPHA_047',
                'ALPHA_076',
                'ALPHA_155',
                'AVG30',
                'ALPHA_101',
                'ALPHA_024',
                'MA50',
                'ALPHA_052',
                'MA_VOL50',
                'ALPHA_163',
                'ALPHA_035',
                'ALPHA_070',
                'MAMT_30',
                'DEA_HR',
                'MA15_D',
                'ATR',
                'AVG5_TOR',
                'MA60_HR',
                'WR',
                'PB_90DN',
                'ATRR',
                'PS_60UP',
                'WR_WK',
                'ALPHA_042',
                'GMMA12_WK',
                'SHORT10_WK',
                'ALPHA_089',
                'LONG60',
                'MTMMA_WK',
                'WS_HR',
                'MACD',
                'PB_30DN',
                'AVG20_TOR',
                'WS',
                'ALPHA_008',
                'PS_30DN',
                'LB_WK',
                'AMA_HR',
                'MA_VOL8_WK',
                'ALPHA_006',
                'ALPHA_168',
                'ALPHA_189',
                'ALPHA_174',
                'MA50_HR',
                'KDJ_D_HR',
                'PS_30UP',
                'PB',
                'MA_VOL10_WK',
                'ALPHA_041',
                'RNG_60',
                'PS_60DN',
                'MA_VOL5_WK',
                'GMMA50_HR',
                'WIDTH',
                'CCI',
                'DDD_HR',
                'SHA_LOW_WK',
                'GMMA15_C',
                'MACD_TR_WK',
                'RNG_90',
                'ADDI_WK',
                'MA8_WK',
                'ALPHA_100',
                'MA_VOL15_WK',
                'AVG60_RNG',
                'MA10_WK',
                'MA_VOL15',
                'CDLHIKKAKE_WK',
                'PS_30VAL',
                'SS',
                'SKDJ_D',
                'GMMA12',
                'MA_VOL20_WK',
                'VSTD_WK',
                'KDJ_K_HR',
                'AVG20',
                'PB_60DN',
                'CCI_WK',
                'GMMA40_HR',
                'AVG10_RNG']

stock_day_set = ['ALPHA_174',
                 'ATR_HR',
                 'SS_WK',
                 'ALPHA_067',
                 'AVG10',
                 'MA30_C_WK',
                 'AVG30_RNG',
                 'MA35_HR',
                 'MA40_WK',
                 'MA30_WK',
                 'RSI2',
                 'ALPHA_024',
                 'AVG20',
                 'AD_WK',
                 'WR',
                 'ADDI_WK',
                 'PB',
                 'ALPHA_003',
                 'MAMT_60',
                 'MAMT_10',
                 'ALPHA_083',
                 'AVG60_RNG',
                 'MA35_WK',
                 'BOLL',
                 'ATRR_HR',
                 'WR1_WK',
                 'MA60',
                 'WR_WK',
                 'MA45',
                 'MA_VOL35',
                 'ALPHA_076',
                 'MAMT_30',
                 'AVG30',
                 'DDD',
                 'RNG_90',
                 'BIAS3_WK',
                 'ALPHA_047',
                 'ALPHA_035',
                 'BIAS3',
                 'ALPHA_089',
                 'MA_VOL60',
                 'AMT_30',
                 'MA30',
                 'WR1',
                 'AMA',
                 'VR_HR',
                 'CCI_CROSS3_WK',
                 'AVG60',
                 'LONG_TR_WK',
                 'UB',
                 'ALPHA_139',
                 'BIAS2_WK',
                 'AVG60_TOR',
                 'PRICE_PCG_HR',
                 'LONG_AMOUNT_HR',
                 'DIF_HR',
                 'GMMA45',
                 'PB_30UP',
                 'MACD_TR_WK',
                 'ALPHA_065',
                 'ALPHA_109',
                 'GMMA35_HR',
                 'ALPHA_062',
                 'PB_60DN',
                 'LONG60V',
                 'WS',
                 'ALPHA_020',
                 'AMT_10',
                 'ALPHA_042',
                 'RNG_60',
                 'PS_60UP',
                 'ALPHA_071',
                 'GMMA40',
                 'DI2_HR',
                 'VSTD_WK',
                 'ALPHA_072',
                 'KDJ_K',
                 'SR',
                 'MA60_HR',
                 'GMMA40_HR',
                 'ALPHA_170',
                 'ALPHA_126',
                 'TOTAL_MARKET',
                 'WIDTH',
                 'MA_VOL15_WK',
                 'AVG20_C_MARKET',
                 'MA15',
                 'MA_VOL40_WK',
                 'GMMA35',
                 'AVG30_TOR',
                 'BIAS1',
                 'UB_HR',
                 'DDI',
                 'PS_30UP',
                 'MA_VOL35_WK',
                 'ALPHA_157',
                 'GMMA_VOL30',
                 'LAG20']

stock_hour_set = ['ATRR_30M',
                  'GMMA12_30M',
                  'SHORT10V_30M',
                  'GMMA_VOL3_D_30M',
                  'ATRR_HR',
                  'ADTM_CROSS1_HR',
                  'GMMA10_30M',
                  'GMMA30_C_30M',
                  'MA_VOL3_HR',
                  'SR_30M',
                  'KDJ_J_30M',
                  'MACD_HR',
                  'GMMA30_C_HR',
                  'MR_30M',
                  'GMMA40_HR',
                  'MA_VOL60_30M',
                  'MA30_C_HR',
                  'GMMA3_C_30M',
                  'MA_VOL5_HR',
                  'BIAS2_30M',
                  'TR_30M',
                  'BIAS1_HR',
                  'RSV_30M',
                  'GMMA45_30M',
                  'GMMA_VOL10_30M',
                  'ATR_30M',
                  'CCI_30M',
                  'WS_30M',
                  'GMMA_VOL30_D_30M',
                  'DIF_30M',
                  'VRSI_30M',
                  'GMMA15_C_HR',
                  'AD_30M',
                  'GMMA_VOL12_30M',
                  'MA_VOL30_HR',
                  'GMMA35_HR',
                  'LONG_AMOUNT_HR',
                  'AD_HR',
                  'MA60_D_30M',
                  'TR_HR',
                  'WR1_HR',
                  'AMA_30M',
                  'MA3_HR',
                  'PRICE_PCG_HR',
                  'LONG60_30M',
                  'GMMA5_30M',
                  'SHORT60_HR',
                  'ROC_30M',
                  'MTMMA_30M',
                  'MA5_C_30M']

index_xg_set = ['MTM_HR',
                 'MA5',
                 'SKDJ_TR',
                 'MACD_TR_WK',
                 'GMMA3',
                 'LONG60_HR',
                 'ADDI_HR',
                 'RSI2_HR',
                 'SKDJ_CROSS1_WK',
                 'RSI2_WK',
                 'MA_VOL5_C_WK',
                 'RSI1_WK',
                 'GMMA35_HR',
                 'MA12_HR',
                 'SHORT_TR_WK',
                 'RSI1_C_WK',
                 'ATRR_HR',
                 'OSC_CROSS1_WK',
                 'SAR_MARK',
                 'BOLL',
                 'CDLADVANCEBLOCK_WK',
                 'DDD_HR',
                 'RSI3',
                 'MA_VOL5_WK',
                 'CDLHANGINGMAN_WK',
                 'RSI3_C_WK',
                 'GMMA10',
                 'SHORT10_WK',
                 'MA5_C_WK',
                 'SHORT60_HR']


index_day_set = ['SKDJ_D',
                 'MA3',
                 'GMMA3_D',
                 'MA5',
                 'GMMA8',
                 'SKDJ_K',
                 'WR2',
                 'RSI1_C',
                 'WR1',
                 'RSI3_C',
                 'GMMA5',
                 'KDJ_CROSS1',
                 'MA5_D',
                 'CDLHARAMI',
                 'BIAS1',
                 'CDLHOMINGPIGEON',
                 'GMMA10',
                 'SKDJ_CROSS2',
                 'SKDJ_TR',
                 'KDJ_CROSS2',
                 'CDLINVERTEDHAMMER',
                 'SKDJ_CROSS1',
                 'MAOSC',
                 'SS',
                 'ROCMA',
                 'LONG60',
                 'SHORT20',
                 'SHORT_AMOUNT',
                 'MR',
                 'KDJ_D']

index_hour_set = ['MA3_HR',
                  'SKDJ_D_HR',
                  'GMMA8_HR',
                  'KDJ_D_HR',
                  'RSI1_C_HR',
                  'MA5_HR',
                  'WR2_HR',
                  'SKDJ_CROSS2_HR',
                  'GMMA3_D_HR',
                  'SKDJ_TR_HR',
                  'SKDJ_CROSS1_HR',
                  'WR1_HR',
                  'KDJ_CROSS1_HR',
                  'GMMA10_HR',
                  'SKDJ_K_HR',
                  'KDJ_CROSS2_HR',
                  'MA5_D_HR',
                  'WR_CROSS2_HR',
                  'GMMA3_C_HR',
                  'GMMA5_HR',
                  'RSI2_C_HR',
                  'KDJ_K_HR',
                  'MA_VOL3_HR',
                  'GMMA_VOL3_HR',
                  'MA_VOL35_HR',
                  'GMMA_VOL3_D_HR',
                  'UB_HR',
                  'MS_HR',
                  'KDJ_J_HR',
                  'WR_CROSS1_HR']
