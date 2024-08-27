import pymysql
import pandas as pd
import numpy as np
import os
from common.utils.As_configuration import PARENT_FILE_PATH
from common.utils.As_configuration import SVG_WIDTH, SVG_HEIGHT, RADIUS_CONST, RAD


def fillRelCone(asrank, asrel):
    """
    asrel的cone字段填充，取source、target中最小cone
    :param asrank: 格式要求：id,cone
    :param asrel: 格式要求：'cone', 'source', 'target', 'rel'
    :param child_filename: 上级目录文件名
    :param par_directory: 文件名
    :param tag: 是否导出csv文件，默认不导出
    :return:
    """
    asrel = asrel.copy()
    asrank = asrank.copy()

    id_cone_dict = asrank.set_index('id')['cone'].to_dict()
    asrel['source_cone'] = asrel['source'].map(id_cone_dict)
    asrel['target_cone'] = asrel['target'].map(id_cone_dict)

    print(f'数量:', len(asrel))
    # 控制舍弃/填充
    asrel = asrel.dropna()
    # asrel = asrel.fillna(0)
    print(f'填充/舍弃后的数量:', len(asrel))

    # 选择as中cone值小的填充cone字段
    asrel['cone'] = asrel.apply(lambda x: min(x['source_cone'], x['target_cone']), axis=1)
    asrel['cone'] = asrel['cone'].astype(int)
    return asrel


def p2c_p2p(asrel, par_directory, child_filename, tag=False):
    p2pc_df = pd.DataFrame(columns=['id', 'provider', 'customer', 'peer'])

    node_rel = {}

    unique_nodes = set(asrel['source'].unique()) | set(asrel['target'].unique())
    p2pc_df['id'] = list(unique_nodes)

    for _, row in asrel.iterrows():

        source = row['source'].astype('int64')
        target = row['target'].astype('int64')
        rel = row['rel']
        if source not in node_rel:
            node_rel[source] = {'peer': set(), 'provider': set(), 'customer': set()}
        if target not in node_rel:
            node_rel[target] = {'peer': set(), 'provider': set(), 'customer': set()}

        if rel == 0:
            node_rel[source]['peer'].add(target)
            node_rel[target]['peer'].add(source)
        elif rel == -1:
            # p | c |-1
            node_rel[source]['customer'].add(target)
            node_rel[target]['provider'].add(source)
    for index, row in p2pc_df.iterrows():
        id_value = row['id']
        if id_value in node_rel:
            p2pc_df.at[index, 'peer'] = list(node_rel[id_value]['peer'])
            p2pc_df.at[index, 'provider'] = list(node_rel[id_value]['provider'])
            p2pc_df.at[index, 'customer'] = list(node_rel[id_value]['customer'])

    if tag:
        dir_name = f"{PARENT_FILE_PATH}{par_directory}"
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        p2pc_df.to_csv(f'{dir_name}/{child_filename}.csv', index=False)
    return p2pc_df
