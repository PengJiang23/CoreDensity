import numpy as np
from scipy.spatial.distance import cosine
from multiprocessing import Process, Manager
import os
import pickle
from tqdm import tqdm


def calculate_similarity(vector1, vector2):
    keys = set(vector1.keys()).union(set(vector2.keys()))
    v1 = np.array([vector1.get(k, 0) for k in keys])
    v2 = np.array([vector2.get(k, 0) for k in keys])
    return 1 - cosine(v1, v2)


def process_grid_section(start_x, end_x, start_y, end_y, marked_grid, coord_cluster_dict, grid_feature,
                         cluster_avg_vector, save_interval, save_file):
    total_grids = (end_x - start_x) * (end_y - start_y)
    processed = 0

    for x in range(start_x, end_x):
        for y in range(start_y, end_y):
            # 更新标记
            marked_grid[x, y] = 1

            # 如果网格没有特征向量，跳过
            if (x, y) not in grid_feature:
                continue

            # 如果网格已经有聚类标签，跳过
            if (x, y) in coord_cluster_dict:
                continue

            # 快速分配聚类
            max_similarity = -1
            best_cluster = None
            for cluster_id, avg_vector in cluster_avg_vector.items():
                similarity = calculate_similarity(grid_feature[(x, y)], avg_vector)
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_cluster = cluster_id

            # 分配聚类标签
            if best_cluster is not None:
                coord_cluster_dict[(x, y)] = best_cluster

            processed += 1

            # 定期保存进度
            if processed % save_interval == 0:
                with open(save_file, 'wb') as f:
                    pickle.dump((marked_grid, dict(coord_cluster_dict)), f)
                print(f"已保存进度: {processed} 个网格处理完成。")

    # 处理完当前块后再次保存进度
    with open(save_file, 'wb') as f:
        pickle.dump((marked_grid, dict(coord_cluster_dict)), f)
    print(f"处理完当前块：{start_x}-{end_x} x {start_y}-{end_y}，已保存进度。")


def main(grid_feature=None, cluster_avg_vector=None):
    grid_size = 700
    save_interval = 10000  # 每处理一定数量的网格保存一次
    save_file = "marked_grid.pkl"

    # 尝试从文件恢复 marked_grid
    if os.path.exists(save_file):
        with open(save_file, 'rb') as f:
            marked_grid, coord_cluster_dict = pickle.load(f)
        print("恢复之前的进度")
    else:
        marked_grid = np.zeros((grid_size, grid_size), dtype=int)
        coord_cluster_dict = {}

    manager = Manager()
    coord_cluster_dict = manager.dict(coord_cluster_dict)

    # 分割网格为4部分
    mid_x, mid_y = grid_size // 2, grid_size // 2
    processes = []

    # 启动4个进程，每个进程处理一个区域
    processes.append(Process(target=process_grid_section, args=(
        0, mid_x, 0, mid_y, marked_grid, coord_cluster_dict, grid_feature, cluster_avg_vector, save_interval,
        save_file)))
    processes.append(Process(target=process_grid_section, args=(
        mid_x, grid_size, 0, mid_y, marked_grid, coord_cluster_dict, grid_feature, cluster_avg_vector, save_interval,
        save_file)))
    processes.append(Process(target=process_grid_section, args=(
        0, mid_x, mid_y, grid_size, marked_grid, coord_cluster_dict, grid_feature, cluster_avg_vector, save_interval,
        save_file)))
    processes.append(Process(target=process_grid_section, args=(
        mid_x, grid_size, mid_y, grid_size, marked_grid, coord_cluster_dict, grid_feature, cluster_avg_vector,
        save_interval, save_file)))

    # 启动所有进程
    for p in processes:
        p.start()

    # 等待所有进程完成
    for p in processes:
        p.join()

    # 最终结果
    print("所有进程完成。")
    print("Marked grid:")
    print(marked_grid)
    print("Updated coord_cluster_dict:")
    print(dict(coord_cluster_dict))


if __name__ == "__main__":
    main()
