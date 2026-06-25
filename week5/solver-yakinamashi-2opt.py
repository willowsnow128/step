import sys
import math
import random
import time  # 時間を計測するために追加
from common import print_tour, read_input, format_tour

def distance(city1, city2):
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)

def calc_total_dist(tour, cities):
    dist = 0
    N = len(tour)
    for i in range(N):
        dist += distance(cities[tour[i]], cities[tour[(i + 1) % N]])
    return dist

# 2-opt関数
def two_opt(tour, cities):
    N = len(tour)
    improved = True
    while improved:
        improved = False
        for i in range(N):
            for j in range(i + 2, N):
                if i == 0 and j == N - 1:
                    continue
                city_a = tour[i]
                city_b = tour[(i + 1) % N]
                city_c = tour[j]
                city_d = tour[(j + 1) % N]
                d1 = distance(cities[city_a], cities[city_b]) + distance(cities[city_c], cities[city_d])
                d2 = distance(cities[city_a], cities[city_c]) + distance(cities[city_b], cities[city_d])
                if d2 < d1:
                    tour[i+1:j+1] = reversed(tour[i+1:j+1])
                    improved = True
    return tour

def solve(cities):
    N = len(cities)
    unvisited = set(range(N))
    tour = [0]
    unvisited.remove(0)

    # 貪欲法
    current_city = 0
    while unvisited:
        next_city = None
        min_dist = float('inf')
        for candidate in unvisited:
            dist = distance(cities[current_city], cities[candidate])
            if dist < min_dist:
                min_dist = dist
                next_city = candidate
        tour.append(next_city)
        unvisited.remove(next_city)
        current_city = next_city

    # 焼きなまし法
    current_dist = calc_total_dist(tour, cities)
    best_dist = current_dist
    best_tour = tour.copy()
    
    # パラメータ設定
    TIME_LIMIT = 600
    T_start = 200.0   # 初期温度
    T_end = 0.0001    # 終了温度
    
    start_time = time.time()
    
    while True:
        current_time = time.time()
        elapsed = current_time - start_time
        
        if elapsed > TIME_LIMIT:
            break
            
        # 時間の経過に合わせて温度を下げる
        T = T_start * ((T_end / T_start) ** (elapsed / TIME_LIMIT))
        
        i = random.randint(0, N - 1)
        j = random.randint(0, N - 1)
        if i == j or abs(i - j) <= 1 or abs(i - j) == N - 1:
            continue
        if i > j:
            i, j = j, i

        city_a = tour[i]
        city_b = tour[(i + 1) % N]
        city_c = tour[j]
        city_d = tour[(j + 1) % N]

        d1 = distance(cities[city_a], cities[city_b]) + distance(cities[city_c], cities[city_d])
        d2 = distance(cities[city_a], cities[city_c]) + distance(cities[city_b], cities[city_d])
        diff = d2 - d1

        if diff < 0 or random.random() < math.exp(-diff / T):
            tour[i+1:j+1] = reversed(tour[i+1:j+1])
            current_dist += diff
            if current_dist < best_dist:
                best_dist = current_dist
                best_tour = tour.copy()

    # 焼きなまし法で見つけたベストなルートを、2-optに渡して磨き上げる
    final_tour = two_opt(best_tour, cities)
    
    return final_tour

if __name__ == '__main__':
    for i in range(6,8):
        input_file = f'input_{i}.csv'
        output_file = f'output_{i}.csv'
        
        print(f'{input_file} を計算中...')
        cities = read_input(input_file)
        tour = solve(cities)
        
        with open(output_file, 'w') as f:
            f.write(format_tour(tour) + '\n')
            
        print(f'{output_file} に保存しました！\n')