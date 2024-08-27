import numpy as np
import pandas as pd
import multiprocessing as mp
import os
import time


def calculate_distance_to_grid(x0, y0, x1, y1, grid_x, grid_y, grid_step):
    """
    计算线段 (x0, y0) - (x1, y1) 到网格中心的垂直距离
    x0, y0: 线段的起点坐标
    x1, y1: 线段的终点坐标
    grid_x, grid_y: 中间网格的索引位置（即网格的左上角）
    grid_step: 网格的大小
    """

    # 计算中间网格的中心点坐标
    grid_center_x = grid_x * grid_step + grid_step / 2
    grid_center_y = grid_y * grid_step + grid_step / 2

    # 处理水平或垂直线段的情况直接计算
    if x0 == x1:  # 垂直线段
        return abs(grid_center_x - x0)
    elif y0 == y1:  # 水平线段
        return abs(grid_center_y - y0)

    # 向量表示线段起点到终点的向量
    line_vector_x = x1 - x0
    line_vector_y = y1 - y0

    # 计算线段的长度平方
    line_length_squared = line_vector_x ** 2 + line_vector_y ** 2

    # 向量表示线段起点到网格中心的向量
    to_center_vector_x = grid_center_x - x0
    to_center_vector_y = grid_center_y - y0

    # 计算投影因子 t，t 表示线段上最近点的位置参数（在[0,1]之间表示在线段内部）
    t = (to_center_vector_x * line_vector_x + to_center_vector_y * line_vector_y) / line_length_squared

    # 限制 t 在[0, 1]范围内，确保距离是垂直距离而不是端点到网格中心的距离
    t = max(0, min(1, t))

    # 计算线段上距离网格中心最近的点坐标
    closest_x = x0 + t * line_vector_x
    closest_y = y0 + t * line_vector_y

    # 返回最近点到网格中心的距离
    return np.sqrt((grid_center_x - closest_x) ** 2 + (grid_center_y - closest_y) ** 2)


def process_relations(sub_relation_data, node_dict, grid_size, grid_step):
    print(f"Process ID: {os.getpid()}")
    local_grid_vectors = np.empty((grid_size // grid_step, grid_size // grid_step), dtype=object)
    for i in range(grid_size // grid_step):
        for j in range(grid_size // grid_step):
            local_grid_vectors[i, j] = set()

    for _, row in sub_relation_data.iterrows():
        source_id = row['source']
        target_id = row['target']
        line_id = int(row['line_id'])

        if source_id in node_dict and target_id in node_dict:
            x0, y0 = node_dict[source_id]['grid_x'], node_dict[source_id]['grid_y']
            x1, y1 = node_dict[target_id]['grid_x'], node_dict[target_id]['grid_y']

            # 使用 Bresenham 算法遍历线段经过的每个网格
            dx = abs(x1 - x0)
            dy = abs(y1 - y0)
            sx = 1 if x0 < x1 else -1
            sy = 1 if y0 < y1 else -1
            err = dx - dy

            # # 起点和终点直接记录
            # local_grid_vectors[y0 // grid_step, x0 // grid_step].add(line_id)
            # local_grid_vectors[y1 // grid_step, x1 // grid_step].add(line_id)

            while True:
                grid_x = x0 // grid_step
                grid_y = y0 // grid_step
                local_grid_vectors[grid_y, grid_x].add(line_id)
                if x0 == x1 and y0 == y1:
                    break
                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x0 += sx
                if e2 < dx:
                    err += dx
                    y0 += sy

                # # 对每个中间网格计算距离
                # grid_x = x0 // grid_step
                # grid_y = y0 // grid_step
                # distance = calculate_distance_to_grid(node_dict[source_id]['grid_x'], node_dict[source_id]['grid_y'],
                #                                       node_dict[target_id]['grid_x'], node_dict[target_id]['grid_y'],
                #                                       grid_x, grid_y, grid_step)
                #
                # # 判断线段是否经过网格的内切圆
                # if distance <= grid_step * 0.5:  # 网格的内切圆半径为 grid_step / 2
                #     local_grid_vectors[grid_y, grid_x].add(line_id)

    return local_grid_vectors


def merge_grid_vectors(grid_vectors_list, grid_size, grid_step):
    """
    合并多个进程的grid_vectors
    :param grid_vectors_list:
    :param grid_size:
    :param grid_step:
    :return:
    """
    final_grid_vectors = np.empty((grid_size // grid_step, grid_size // grid_step), dtype=object)
    for i in range(grid_size // grid_step):
        for j in range(grid_size // grid_step):
            final_grid_vectors[i, j] = set()

    for grid_vectors in grid_vectors_list:
        for i in range(grid_size // grid_step):
            for j in range(grid_size // grid_step):
                final_grid_vectors[i, j].update(grid_vectors[i, j])

    return final_grid_vectors


def calculate_grid_density(node_data_file, relation_data_file, num_processes=4, grid_size=800, grid_step=1,
                           center_x=950, center_y=500, radius=401):
    start_time = time.time()

    # 加载数据
    node_data = pd.read_csv(node_data_file)
    relation_data = pd.read_csv(relation_data_file)
    relation_data['line_id'] = range(len(relation_data))

    # 得到每个点的极坐标，然后筛选在圆内的点
    node_data['r'] = np.sqrt((node_data['x'] - center_x) ** 2 + (node_data['y'] - center_y) ** 2)
    node_data['theta'] = np.arctan2(node_data['y'] - center_y, node_data['x'] - center_x)
    node_data = node_data[node_data['r'] <= radius]

    # 原始坐标范围转换为0，2*radius区间内，然后归一化映射到网格中
    node_data['grid_x'] = ((node_data['x'] - (center_x - radius)) / (2 * radius) * (grid_size - 1)).astype(int)
    node_data['grid_y'] = ((node_data['y'] - (center_y - radius)) / (2 * radius) * (grid_size - 1)).astype(int)
    node_dict = node_data.set_index('id')[['grid_x', 'grid_y']].to_dict(orient='index')

    # 切分relation_data并行处理
    chunk_size = len(relation_data) // num_processes
    chunks = [relation_data.iloc[i:i + chunk_size] for i in range(0, len(relation_data), chunk_size)]

    with mp.Pool(processes=num_processes) as pool:
        results = pool.starmap(process_relations, [(chunk, node_dict, grid_size, grid_step) for chunk in chunks])
        pool.close()
        pool.join()

    # 合并所有进程结果
    grid_vectors = merge_grid_vectors(results, grid_size, grid_step)

    # 获取网格的线条密度
    grid_density = np.array(
        [[len(grid_vectors[i, j]) for j in range(grid_size // grid_step)] for i in range(grid_size // grid_step)])

    end_time = time.time()
    # 打印总耗时
    print(f"Total computation time: {end_time - start_time:.2f} seconds")

    return grid_density, grid_vectors
