import numpy as np
from tqdm import tqdm  # tqdm库用于显示进度条


def overlap(vec1, vec2):
    """
    计算grid重叠系数
    :param vec1: NumPy数组
    :param vec2: NumPy数组
    :return: 重叠系数
    """
    if len(vec1) == 0 or len(vec2) == 0:
        return 0  # 如果有一个集合为空，重叠系数直接为0

    intersection = np.intersect1d(vec1, vec2, assume_unique=True).size
    min_set = min(len(vec1), len(vec2))
    return intersection / min_set if min_set > 0 else 0


def calculate_distance_matrix(all_samples, grid_vectors):
    num_samples = len(all_samples)
    distance_matrix = np.zeros((num_samples, num_samples))  # 初始化距离矩阵，并将对角线设为0

    # 给每个采样网格编号,从0开始
    grid_dict = {i: sample for i, sample in enumerate(all_samples)}

    # 使用tqdm显示进度条
    for i in tqdm(range(num_samples), desc="Calculating Distance Matrix"):
        for j in range(i + 1, num_samples):
            coord1 = grid_dict[i]
            coord2 = grid_dict[j]
            y1, x1 = coord1[0], coord1[1]
            y2, x2 = coord2[0], coord2[1]

            # 获取真实坐标对应的vec
            vec1 = grid_vectors[y1, x1]
            vec2 = grid_vectors[y2, x2]

            # 计算overlap score
            overlap_score = overlap(vec1, vec2)

            # 计算距离矩阵的值
            distance = 1 - overlap_score
            distance_matrix[i, j] = distance
            distance_matrix[j, i] = distance  # 利用对称性填充下三角区域

    return distance_matrix, grid_dict
