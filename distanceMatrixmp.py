import numpy as np
import multiprocessing as mp


def calculate_partial_matrix(start_idx, end_idx, grid_dict, overlap_scores, distance_matrix, num_samples):
    for i in range(start_idx, end_idx):
        for j in range(i + 1, num_samples):
            coord1 = grid_dict[i]
            coord2 = grid_dict[j]
            y1, x1 = coord1[0], coord1[1]
            y2, x2 = coord2[0], coord2[1]

            overlap_key1 = (y1, x1, y2, x2)
            overlap_key2 = (y2, x2, y1, x1)

            if overlap_key1 in overlap_scores.keys():
                overlap = overlap_scores[overlap_key1]
                distance_matrix[i, j] = 1 - overlap
                distance_matrix[j, i] = 1 - overlap
            elif overlap_key2 in overlap_scores.keys():
                overlap = overlap_scores[overlap_key2]
                distance_matrix[i, j] = 1 - overlap
                distance_matrix[j, i] = 1 - overlap


def parallel_distance_matrix_calculation(all_samples, overlap_scores, num_processes=4):
    num_samples = len(all_samples)
    distance_matrix = np.ones((num_samples, num_samples))

    # 给每个采样网格编号,从0开始
    grid_dict = {i: sample for i, sample in enumerate(all_samples)}

    # 划分任务区间
    chunk_size = num_samples // num_processes
    ranges = [(i * chunk_size, (i + 1) * chunk_size if i != num_processes - 1 else num_samples) for i in
              range(num_processes)]

    # 创建进程池并分配任务
    with mp.Pool(processes=num_processes) as pool:
        processes = [
            pool.apply_async(calculate_partial_matrix,
                             args=(start_idx, end_idx, grid_dict, overlap_scores, distance_matrix, num_samples))
            for start_idx, end_idx in ranges
        ]

        # 等待所有进程完成
        for process in processes:
            process.get()

    return distance_matrix, grid_dict
