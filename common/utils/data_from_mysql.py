import pymysql
import pandas as pd
import os
from common.utils.As_configuration import DBS_NAME, DBS_USER, DBS_PASSWORD, DBS_HOST, DBS_PORT, PARENT_FILE_PATH


def download_asdata(sql, par_directory=None, child_filename=None, tag=False):
    """
    从数据库中取数据，导出csv文件
    :param par_directory: 上级目录文件名
    :param sql: 执行的sql语句
    :param tag: 是否导出csv文件，默认不导出
    :param child_filename: 生成的csv文件名
    :return: 数据库读取的数据
    """
    # 数据库连接
    db = pymysql.connect(host=DBS_HOST,
                         user=DBS_USER,
                         password=DBS_PASSWORD,
                         database=DBS_NAME,
                         port=DBS_PORT,
                         charset='utf8')

    cursor = db.cursor()
    cursor.execute(sql)
    # 拿到表头
    des = cursor.description
    title = [each[0] for each in des]
    # 拿到数据库查询的内容
    result_list = []
    for each in cursor.fetchall():
        result_list.append(list(each))
    # 保存成dataframe
    asdata_df = pd.DataFrame(result_list, columns=title)

    # 是否导出
    if tag:
        dir_name = f"{PARENT_FILE_PATH}{par_directory}"
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        asdata_df = asdata_df.sort_values(by='id', ascending=True)
        asdata_df = asdata_df.drop_duplicates(subset=['id'], keep='last')
        asdata_df.to_csv(f'{dir_name}/{child_filename}.csv', index=False, encoding='utf_8_sig')
    cursor.close()
    db.close()

    return asdata_df


