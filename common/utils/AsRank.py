import numpy as np
import os
from common.utils.As_configuration import SVG_WIDTH, SVG_HEIGHT, RADIUS_CONST, RAD, PARENT_FILE_PATH


# asrank操作
def polarToCartesian(asrank, attr, radius=350):
    # 映射值域cone的min-max  映射到   0-350
    min_cone = asrank[attr].min()
    max_cone = asrank[attr].max()

    # cone原值域太大，进行值域缩放，用来后面求半径
    max_Domain = 1 - np.log((min_cone + 1) / (max_cone + 1))

    # cone的log处理
    asrank['cone_map'] = asrank[attr].apply(lambda x: (1 - np.log((x + 1) / (max_cone + 1))))

    # log处理后，对cone进行一个0-350区间映射
    asrank['r'] = asrank['cone_map'].apply(lambda x: (((x - 1) / (max_Domain - 1)) * radius))

    # 得到xy坐标 x=初始位置+rcosθ
    x = SVG_WIDTH / 2 + asrank['r'] * np.cos(asrank['longitude'] * RAD)
    y = SVG_HEIGHT / 2 - asrank['r'] * np.sin(asrank['longitude'] * RAD)

    asrank['x'] = x
    asrank['y'] = y
    # 将rank 的r字段全部数值变为绝对值
    asrank.sort_values(by=attr, ascending=False, inplace=True)
    asrank.drop_duplicates(subset=['id', attr], keep='last', inplace=True)

    return asrank


def asrank_xydict(asrank, par_directory, child_filename, tag=False):
    asrank['xy'] = asrank.apply(lambda row: [row['x'], row['y']], axis=1)
    asrank = asrank.drop(['x', 'y'], axis=1)
    if tag:
        dir_name = f"{PARENT_FILE_PATH}{par_directory}"
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        asrank[['id', 'xy']].to_csv(f'{dir_name}/{child_filename}.csv', index=False)

    return asrank
