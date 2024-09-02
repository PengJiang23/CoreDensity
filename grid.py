import numpy as np
import pandas as pd
from grid_processing import calculate_grid_density
import pickle
from distanceMatrixmp import parallel_distance_matrix_calculation
from collections import defaultdict
from noSampleGridCluster import parallel_cluster_assignment

grid_density, grid_vectors = calculate_grid_density('rank.csv', 'rel.csv', num_processes=4)

# 找出高密度区域和低密度区域的阈值
high_density_threshold = np.percentile(grid_density, 90)
low_density_threshold = np.percentile(grid_density, 10)

# 获取网格所在坐标
high_density_coords = np.argwhere(grid_density >= high_density_threshold)
low_density_coords = np.argwhere(grid_density <= low_density_threshold)

# 随机采样10%的高密度区域和10%的低密度区域
np.random.seed(0)
high_density_samples = high_density_coords[
    np.random.choice(len(high_density_coords), len(high_density_coords) // 10, replace=False)]
low_density_samples = low_density_coords[
    np.random.choice(len(low_density_coords), len(low_density_coords) // 10, replace=False)]


def overlap(vec1, vec2):
    """
    grid重叠系数计算
    :param vec1:
    :param vec2:
    :return:
    """
    vec1 = np.array(list(vec1))
    vec2 = np.array(list(vec2))
    intersection = len(set(vec1).intersection(set(vec2)))
    min_set = min(len(vec1), len(vec2))
    return intersection / min_set if min_set > 0 else 0


def calc_neighborhood(sampled_coords, grid_vectors):
    """
    计算邻近的网格重叠系数
    :param sampled_coords:
    :param grid_vectors:
    :return:
    """
    overlap_scores = {}

    for coord in sampled_coords:
        y, x = coord
        sampled_set = grid_vectors[y, x]
        neighbors = []

        # 获取邻近的网格
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dy == 0 and dx == 0:
                    continue  # 跳过自身
                ny, nx = y + dy, x + dx
                if 0 <= ny < grid_vectors.shape[0] and 0 <= nx < grid_vectors.shape[1]:
                    neighbors.append((ny, nx))

        for ny, nx in neighbors:
            neighbor_set = grid_vectors[ny, nx]
            overlap1 = overlap(sampled_set, neighbor_set)
            overlap_scores[(y, x, ny, nx)] = overlap1

    return overlap_scores


num_samples = len(high_density_samples)
all_samples = high_density_samples

overlap_scores = calc_neighborhood(all_samples, grid_vectors)

# 执行多进程计算
distance_matrix, grid_dict = parallel_distance_matrix_calculation(all_samples, overlap_scores)


def create_sparse_feature_vectors(grid_vectors):
    """
    创建稀疏特征向量
    :param grid_vectors:
    :return:
    """
    feature_vectors = {}

    for y in range(grid_vectors.shape[0]):
        for x in range(grid_vectors.shape[1]):
            line_ids = grid_vectors[y, x]
            if line_ids:  # 仅存储非空的网格
                # 稀疏表示为一个字典，key为线条ID，value为1（因为存在该线条）
                sparse_vector = {line_id: 1 for line_id in line_ids}
                feature_vectors[(y, x)] = sparse_vector

    return feature_vectors


grid_feature = create_sparse_feature_vectors(grid_vectors)


def hierarchical_clustering(distance_matrix):
    # 初始化标签为每个元素的索引
    labels = np.arange(distance_matrix.shape[0])

    while len(labels) > 10:
        # 只考虑上三角矩阵，排除对角线（不包含自身）
        upper_triangle_indices = np.triu_indices(distance_matrix.shape[0], k=1)

        # 找到最小距离的索引
        min_index = np.argmin(distance_matrix[upper_triangle_indices])
        i, j = upper_triangle_indices[0][min_index], upper_triangle_indices[1][min_index]

        # 打印当前合并的簇
        # print(f"Merging clusters: {labels[i]} and {labels[j]} with distance {distance_matrix[i, j]}")
        # print(distance_matrix)

        # 计算新簇与其他簇的距离（使用上三角矩阵和平均链接法）
        new_distances = (distance_matrix[i, :] + distance_matrix[j, :]) / 2.0

        # 删除已合并的行和列
        mask = np.ones(distance_matrix.shape[0], dtype=bool)
        mask[[i, j]] = False
        distance_matrix = distance_matrix[mask, :][:, mask]

        # 添加新簇与其他簇的距离（新行列）
        distance_matrix = np.vstack([distance_matrix, new_distances[mask]])
        new_distances = np.append(new_distances[mask], 0)  # 添加0以保持对角线
        distance_matrix = np.hstack([distance_matrix, new_distances[:, None]])

        # 平铺展开标签并创建新标签
        def flatten_label(label):
            return str(label).strip('()').split(',')

        new_label_elements = flatten_label(labels[i]) + flatten_label(labels[j])
        new_label = f"({','.join(sorted(set(new_label_elements), key=int))})"

        # 更新标签
        labels = labels[mask]
        labels = np.append(labels, new_label)

    return labels


final_labels = hierarchical_clustering(distance_matrix)
np.save('final_labels.npy', final_labels)

cluster_dict = {}
for i, label in enumerate(final_labels):
    if ',' in label:
        elements = label.strip('()').split(',')
        for elem in elements:
            key = int(elem)
            if i not in cluster_dict:
                cluster_dict[i] = []
            cluster_dict[i].append(grid_dict[key])
    else:
        cluster_dict[i] = grid_dict[int(label)]

# 初始化 cluster_avg_vector
cluster_avg_vector = defaultdict(lambda: {})


def process_vector_list(v):
    sum_vector = defaultdict(float)

    for item in v:
        if isinstance(item, np.ndarray):
            item_tuple = tuple(item)
            try:
                feature_vector = grid_feature[item_tuple]
                for index, value in feature_vector.items():
                    sum_vector[index] += value
            except KeyError:
                continue
        elif isinstance(item, list):
            nested_sum_vector = process_vector_list(item)
            for index, value in nested_sum_vector.items():
                sum_vector[index] += value

    return sum_vector


# 遍历 cluster_dict
for k, v in cluster_dict.items():
    # 如果簇中只有一个元素，直接使用该元素的特征向量作为平均特征向量
    if isinstance(v, np.ndarray):
        try:
            cluster_avg_vector[k] = grid_feature[v[0], v[1]]
        except KeyError:
            continue
    # 如果簇中有多个元素，计算总特征向量然后求平均
    else:
        sum_vector = process_vector_list(v)
        if sum_vector:
            avg_vector = {index: value / len(v) for index, value in sum_vector.items()}
            cluster_avg_vector[k] = avg_vector

sample_grid_list = []
for value in cluster_dict.values():
    if isinstance(value, np.ndarray):

        sample_grid_list.append(value)
    elif isinstance(value, list):
        for item in value:
            sample_grid_list.append(item)

sample_grid_set = {tuple(grid) for grid in sample_grid_list}

coord_cluster_dict = {}

for k, v in cluster_dict.items():
    if isinstance(v, np.ndarray):
        coord_cluster_dict[tuple(v)] = k
    elif isinstance(v, list):
        for item in v:
            coord_cluster_dict[tuple(item)] = k

grid_size = 800

normal_dict = {k: v for k, v in cluster_avg_vector.items()}
no_cluster_dict = parallel_cluster_assignment(grid_size, grid_feature, coord_cluster_dict, normal_dict, 8)

with open('final_cluster_dict.pkl', 'wb') as f:
    pickle.dump(no_cluster_dict, f)
