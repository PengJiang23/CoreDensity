import json
import os
from common.utils.As_configuration import RADIUS_CONST, RAD, PARENT_FILE_PATH
import pandas as pd
from datetime import datetime


def selectRadiusAscore(asrank, asrel, filename1, filename2, upfilename, tag=True):
    """
    选择半径小于RADIUS_CONST的节点，并得到该节点连接到的所有边关系rel_core和，涉及到的点(包括小于半径内的点)asrank_part
    :param asrank:
    :param asrel:
    :param filename1/2:asrank\rel 文件名
    :param upfilename: 上级目录文件名
    :param tag: 是否导出csv文件
    :return: asrank_part:涉及到的点集合, rel_core边集合
    """
    # 半径小于RADIUS_CONST的”核心“节点
    rank_core = asrank[asrank['r'] < RADIUS_CONST]
    print(f"半径小于{RADIUS_CONST}的节点数量：", len(rank_core))

    # 涉及核心的所有rel
    rel_core = asrel[(asrel['source'].isin(rank_core['id'])) | (asrel['target'].isin(rank_core['id']))]

    # 获得符合条件的as节点
    rel_sourceid = rel_core['source'].drop_duplicates()
    rel_targetid = rel_core['target'].drop_duplicates()
    rel_id = pd.concat([rel_sourceid, rel_targetid]).drop_duplicates()
    # 筛选符合条件（rel中id对应的数据）的as节点
    asrank_part = asrank[asrank['id'].isin(rel_id)]

    # 数据导出
    if tag:
        dir_name1 = f"../data11/dataprocessed/{upfilename}"
        dir_name2 = f"../data11/dataprocessed/{upfilename}"
        if not os.path.isdir(dir_name1):
            os.makedirs(dir_name1)
        asrank_part[['id', 'cone', 'angle', 'asrank', 'country', 'x', 'y', 'outdegree', 'indegree']].to_csv(
            f"../data11/dataprocessed/{upfilename}/{filename1}.csv", index=False)
        if not os.path.isdir(dir_name2):
            os.makedirs(dir_name2)
        rel_core[['cone', 'source', 'target', 'rel']].to_csv(
            f"../data11/dataprocessed/{upfilename}/{filename2}.csv", index=False)

    return asrank_part, rel_core


def rank_rel_sample(asrank, asrel, filename1, filename2, tag=False):
    """
    对rank、rel进行降采样
    :param asrank:
    :param asrel:
    :param filename1: asrank文件名
    :param filename2: asrel文件名
    :param tag: 是否导出csv文件
    :return: asrank_sample,asrel_sample
    """
    # 数据重采样，数据量还是太多，进一步筛选
    print("asrank数量：", len(asrank), "   asrel数量：", len(asrel))
    asrank1 = asrank[asrank['r'] < RADIUS_CONST]
    asrank2 = asrank[(asrank['r'] >= RADIUS_CONST) & (asrank['r'] < 290)]
    asrank3 = asrank[(asrank['r'] >= 290) & (asrank['r'] < 320)]
    asrank4 = asrank[(asrank['r'] >= 320) & (asrank['r'] < 340)]
    asrank5 = asrank[(asrank['r'] >= 340) & (asrank['r'] <= 350)]
    print('降采样前的数据量：', len(asrank1), len(asrank2), len(asrank3), len(asrank4), len(asrank5))
    # ascore降采样
    asrank2 = asrank2.sample(frac=0.8, replace=False, random_state=None)
    asrank3 = asrank3.sample(frac=0.5, replace=False, random_state=None)
    asrank4 = asrank4.sample(frac=0.3, replace=False, random_state=None)
    asrank5 = asrank5.sample(frac=0.07, replace=False, random_state=None)
    print('降采样后的数据量：', len(asrank1), len(asrank2), len(asrank3), len(asrank4), len(asrank5))

    asrank_sample = pd.concat([asrank1, asrank2, asrank3, asrank4, asrank5])

    # rel_core降采样
    asrel_sample = asrel[
        (asrel['source'].isin(asrank_sample['id'])) & (asrel['target'].isin(asrank_sample['id']))]

    # ascore数据导出
    if tag:
        dir_name = f"../data11/dataprocessed/assample/"
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        asrank_sample[['id', 'cone', 'angle', 'asrank', 'country', 'x', 'y']].to_csv(
            f'../data11/dataprocessed/assample/{filename1}.csv', index=False)
        asrel_sample[['cone', 'rel', 'source', 'target']].to_csv(
            f'../data11/dataprocessed/assample/{filename2}.csv', index=False)

    return asrank_sample, asrel_sample


def rank_update_rel(asrank, asrel):
    """
    asrank和asrel中的数据可能不完全一致（有可能会丢失部分数据，需要进行更新）
    根据asrank节点，去更新asrel（asrel中的as节点必须全部在asrank中存在）
    :param asrank:
    :param asrel:
    :return:
    """
    asrel = asrel[(asrel['source'].isin(asrank['id'])) & (asrel['target'].isin(asrank['id']))]
    return asrel


def rel_update_rank(asrank, asrel):
    """
    根据rel中的关系，去更新asrank中的节点
    :param asrank:
    :param asrel:
    :return:
    """
    rel_id = pd.concat([asrel['source'], asrel['target']]).drop_duplicates()
    asrank = asrank[asrank['id'].isin(rel_id)]
    return asrank


def fdeb_format(asrank, asrel):
    result1 = {}
    for index, row in asrank.iterrows():
        data = {"x": row['x'], "y": row['y'], 'z': 0}
        k_id = row['id']
        result1[str(k_id)] = data

    # 将数据转换成 JSON 数组格式
    result2 = []
    for index, row in asrel.iterrows():
        data = {"source": str(row['source']), "target": str(row['target'])}
        result2.append(data)

    current_time = datetime.now()
    formatted_time = current_time.strftime("%y%m%d")
    # 导出为 JSON 文件
    os.makedirs(f'data/{formatted_time}',exist_ok=True)
    with open(f'data/{formatted_time}/nnodes.json', 'w') as json_file:
        json.dump(result1, json_file, indent=4)

    with open(f'data/{formatted_time}/eedges.json', 'w') as json_file:
        json.dump(result2, json_file, indent=4)
