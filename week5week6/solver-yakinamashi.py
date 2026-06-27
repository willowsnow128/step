import sys
import math
import random  
from common import print_tour, read_input, format_tour

def distance(city1, city2):
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)

# ルート全体の距離を計算するお助け関数
def calc_total_dist(tour, cities):
    dist = 0
    N = len(tour)
    for i in range(N):
        dist += distance(cities[tour[i]], cities[tour[(i + 1) % N]])
    return dist

def solve(cities):
    N = len(cities)
    unvisited = set(range(N))
    tour = [0]
    unvisited.remove(0)

    # まずは貪欲法で初期ルートを作る
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

    # 焼きなまし法で改善する   
    # 今のルートの合計距離を計算して、ベストスコアとして保存しておく
    current_dist = calc_total_dist(tour, cities)
    best_dist = current_dist
    best_tour = tour.copy()
    
    # 焼きなましの設定
    T = 100.0       # 初期温度（最初は熱いので、改悪を許しやすい）
    T_min = 0.0001    # 終了温度（ここまで冷えたらループ終了）
    alpha = 0.99999    # 冷却率（1回のループでどれくらい温度を下げるか）
    
    # 温度が下がりきるまで繰り返す
    while T > T_min:
        # 順番に探すのではなくランダムに2つの道を選ぶ
        i = random.randint(0, N - 1)
        j = random.randint(0, N - 1)
        
        # 同じ道や、隣り合う道を選んでしまった場合はやり直し
        if i == j or abs(i - j) <= 1 or abs(i - j) == N - 1:
            continue
            
        # 処理しやすいように、必ずiの方が小さくなるように入れ替える
        if i > j:
            i, j = j, i

        # 選んだ2つの道の両端の都市を取得
        city_a = tour[i]
        city_b = tour[(i + 1) % N]
        city_c = tour[j]
        city_d = tour[(j + 1) % N]

        # つなぎかえる前と後の距離を計算
        d1 = distance(cities[city_a], cities[city_b]) + distance(cities[city_c], cities[city_d])
        d2 = distance(cities[city_a], cities[city_c]) + distance(cities[city_b], cities[city_d])

        # 距離の差（マイナスになれば距離が短くなったということ）
        diff = d2 - d1

        # 採用判定：距離が短くなった場合、または確率で当たりを引いた場合は繋ぎ直す
        # math.exp(-diff / T) という計算によって、温度Tが高いほど当たりを引きやすくなる
        if diff < 0 or random.random() < math.exp(-diff / T):
            
            # 経路を逆順にして繋ぎ直す
            tour[i+1:j+1] = reversed(tour[i+1:j+1])
            current_dist += diff
            
            # これまでの過去最高記録を更新したら保存する
            if current_dist < best_dist:
                best_dist = current_dist
                best_tour = tour.copy()

        # 最後に温度を少しだけ下げる
        T = T * alpha

    # 一番良かったルートを最終的な答えとする
    return best_tour

if __name__ == '__main__':
    for i in range(8):
        input_file = f'input_{i}.csv'
        output_file = f'output_{i}.csv'
        
        print(f'{input_file} を計算中...')
        cities = read_input(input_file)
        tour = solve(cities)
        
        with open(output_file, 'w') as f:
            f.write(format_tour(tour) + '\n')
            
        print(f'{output_file} に保存しました！\n')