import sys
import math
from common import print_tour, read_input, format_tour

def distance(city1, city2):
    # 2点間の距離を計算
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)

def solve(cities):
    N = len(cities)
    # まだ行っていない都市の集合
    unvisited = set(range(N))
    # ルートを保存するリスト（都市0からスタート）
    tour = [0]
    unvisited.remove(0)

    # 貪欲法
    current_city = 0
    while unvisited:
        next_city = None
        min_dist = float('inf')

        # current_cityから一番近い都市をunvisitedの中から探す
        for candidate in unvisited:
            dist = distance(cities[current_city], cities[candidate])
            if dist < min_dist:
                min_dist = dist
                next_city = candidate

        # 一番近い都市が見つかったら、ルートに追加して未訪問リストから消す
        tour.append(next_city)
        unvisited.remove(next_city)
        current_city = next_city

    # 2-opt法
    improved = True
    while improved:
        # 改善が行われなかったらループを抜ける
        improved = False 
        
        # 経路の中から、繋ぎ直す2つの辺（A-BとC-D）を選ぶ
        for i in range(N):
            for j in range(i + 2, N):
                # 最初と最後の都市の組み合わせは隣接してしまうのでスキップ
                if i == 0 and j == N - 1:
                    continue

                # 4つの都市のインデックスを取得
                # 最後の都市の時に最初に戻れるように%Nをする
                city_a = tour[i]
                city_b = tour[(i + 1) % N]
                city_c = tour[j]
                city_d = tour[(j + 1) % N]

                # 現在の2つの辺の長さの合計(A-BとC-D)
                d1 = distance(cities[city_a], cities[city_b]) + distance(cities[city_c], cities[city_d])
                # 繋ぎ直したあとの2つの辺の長さの合計(A-CとB-D)
                d2 = distance(cities[city_a], cities[city_c]) + distance(cities[city_b], cities[city_d])

                # 繋ぎ直した方が距離が短くなるなら経路を更新する
                if d2 < d1:
                    # BからCまでの訪問順序を逆順にすることで繋ぎ直す
                    tour[i+1:j+1] = reversed(tour[i+1:j+1])
                    # 改善されたので、もう一度最初からチェックする
                    improved = True

    return tour

if __name__ == '__main__':
    # 0から6までのoutputを順番に処理するループ
    for i in range(7):
        input_file = f'input_{i}.csv'
        output_file = f'output_{i}.csv'
        
        print(f'{input_file} を計算中...')
        
        # データを読み込む
        cities = read_input(input_file)
        
        # 経路を計算する
        tour = solve(cities)
        
        # 結果をファイルに書き込んで保存する
        with open(output_file, 'w') as f:
            f.write(format_tour(tour) + '\n')
            
        print(f'{output_file} に保存しました！\n')