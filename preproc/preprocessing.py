import pandas as pd
import argparse
import os

def preprocessing():
    args = parse_args()
    if args.raw:
        directory = 'data/raw'
        # 파일 불러오기
        terminals = pd.read_csv(os.path.join(directory, 'terminals.csv'), encoding='cp949')
        od_matrix = pd.read_csv(os.path.join(directory, 'od_matrix.csv'))
        veh_table = pd.read_csv(os.path.join(directory, 'vehicles.csv'))
        orders = pd.read_csv(os.path.join(directory, 'orders.csv'), encoding='cp949')

        # 주문 데이터 가공
        orders['하차가능시간_시작'] = 60 * orders['하차가능시간_시작'].str[:-3].astype('Int64')
        orders['하차가능시간_종료'] = 60 * orders['하차가능시간_종료'].str[:-3].astype('Int64')
        orders.Group = ((orders.date.str[-1]).astype('Int64') - 1) * 4 + orders.Group
        orders = orders[
            ['주문ID', '하차지_위도', '하차지_경도', '터미널ID', '착지ID', 'CBM', '하차가능시간_시작', '하차가능시간_종료', '하차작업시간(분)', 'Group']]

        directory = 'data'
        terminals.to_csv(os.path.join(directory, 'terminals.txt'), sep=' ', index=False, header=False)
        od_matrix.to_csv(os.path.join(directory, 'od_matrix.txt'), sep=' ', index=False, header=False)
        veh_table.to_csv(os.path.join(directory, 'vehicles.txt'), sep=' ', index=False, header=False)
        orders.to_csv(os.path.join(directory, 'orders.txt'), sep=' ', index=False, header=False)

def parse_args():
    parser = argparse.ArgumentParser(description='Testing Files')
    parser.add_argument('-r', '--raw', dest='raw', action='store_true',
                        help = 'use_raw_data')
    args = parser.parse_args()
    return args