import pandas as pd
import config

def post_processing():
    order_result= pd.read_csv(config.ORDER_RESULT_DIR)
    final = pd.read_csv(config.FINAL_ORDER_RESULT_DIR)
    idx2id = pd.read_csv(config.IDX2ID_DIR, index_col = 'IDX')

    for df in [final, order_result]:
        df['SiteCode'] = df['SiteCode'].apply(lambda x : idx2id.loc[x,'ID'] )

    final.to_csv(config.FINAL_ORDER_RESULT_DIR, index=False)
    order_result.to_csv(config.ORDER_RESULT_DIR, index=False)