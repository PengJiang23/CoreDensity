import multiprocessing as mp
import numpy as np


def calculate_sparse_euclidean_distance(vec1, vec2):
    all_keys = set(vec1.keys()).union(set(vec2.keys()))
    squared_diff_sum = 0.0

    for key in all_keys:
        diff = vec1.get(key, 0.0) - vec2.get(key, 0.0)
        squared_diff_sum += diff ** 2

    return np.sqrt(squared_diff_sum)


def calculate_min_distance_key(no_sample_grid_feature, cluster_avg_vector):
    min_distance = float('inf')
    min_key = None

    for key, cluster_vector in cluster_avg_vector.items():
        distance = calculate_sparse_euclidean_distance(no_sample_grid_feature, cluster_vector)

        if distance < min_distance:
            min_distance = distance
            min_key = key

    return min_key


def process_grid_section(start_row, end_row, grid_size, grid_feature, coord_cluster_dict, cluster_avg_vector):
    cluster_dict_process = {}
    for i in range(start_row, end_row):
        for j in range(grid_size):
            if (i, j) in coord_cluster_dict:
                continue
            else:
                no_sample_grid_feature = grid_feature.get((i, j))
                if no_sample_grid_feature is not None:
                    belong_cluster = calculate_min_distance_key(no_sample_grid_feature, cluster_avg_vector)
                    if belong_cluster not in cluster_dict_process:
                        cluster_dict_process[belong_cluster] = [np.array([i, j])]
                    else:
                        cluster_dict_process[belong_cluster].append(np.array([i, j]))
                        print(cluster_dict_process, type(cluster_dict_process))
    return cluster_dict_process


def merge_cluster_dicts(cluster_dicts):
    merged_dict = {}
    for cluster_dict in cluster_dicts:
        for key, value in cluster_dict.items():
            if key not in merged_dict:
                merged_dict[key] = value
            else:
                merged_dict[key].extend(value)
    return merged_dict


def parallel_cluster_assignment(grid_size, grid_feature, coord_cluster_dict, cluster_avg_vector, num_processes=None):
    if num_processes is None:
        num_processes = 4  # 默认使用CPU核心数量

    # 计算每个进程需要处理的网格范围
    rows_per_process = grid_size // num_processes
    pool = mp.Pool(processes=num_processes)
    results = []

    for i in range(num_processes):
        start_row = i * rows_per_process
        end_row = (i + 1) * rows_per_process if i != num_processes - 1 else grid_size
        result = pool.apply_async(process_grid_section, args=(
            start_row, end_row, grid_size, grid_feature, coord_cluster_dict, cluster_avg_vector))
        results.append(result)

    pool.close()
    pool.join()

    # 收集并合并所有子进程的结果
    cluster_dicts = [result.get() for result in results]
    final_cluster_dict = merge_cluster_dicts(cluster_dicts)

    return final_cluster_dict
