# TSPチャレンジ！

## 概要
本プログラムは、巡回セールスマン問題を解くものです。
初期解の構築に貪欲法を使用し、その後の経路改善に「2-opt法」を使っています。
### 1.距離計算(**⁠distance⁠関数**)
```python
def distance(city1, city2):
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)
```
2つの都市の座標データ（x, y）を受け取り、三平方の定理を用いて直線距離を計算して返す関数です。

### 2.貪欲法
```python
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
```
solve⁠ 関数の前半では、「**現在地から最も近い未訪問の都市へ移動する**」という貪欲法を用いて、巡回ルートを考えています。
* **⁠unvisited**⁠: まだ訪問していない都市の番号を管理する集合（⁠set⁠）です。
* **tour⁠**: 最終的な訪問ルートを保存するリストです。最初はスタート地点として⁠0⁠番の都市を格納しています。

処理の流れ:
1. ⁠**while unvisited**:⁠ で未訪問の都市がなくなるまでループを回します。
2. 現在地(⁠**current_city**⁠)から、**⁠unvisited⁠**内の全都市との距離を計算し、最短距離となる都市(⁠**next_city⁠**)を探索します。
3. 最短の都市が見つかったら**tour⁠**に追加し、**⁠unvisited⁠**から削除して現在地を更新します。

### 3.経路の改善：2-opt法
```python
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
```

貪欲法で構築した初期解には、経路の「交差（無駄な遠回り）」が含まれることが多いため、これを解消します。

処理の流れ:
* **2つの辺の選択**: **tour⁠**の中から、繋ぎ直す候補となる2つの道（都市A→都市B、および 都市C→都市D）を選びます。
- ⁠j⁠のループを**⁠i+2⁠**から開始することで、隣り合う辺を選ばないようにしています。
- ⁠if i==0 and j==N-1: continue⁠ の処理により、配列の先頭と末尾（円環として繋がっている隣り合う辺）が選ばれた場合をスキップしています。
* **配列のインデックス参照(⁠% N⁠)**:
- リストの最後尾から先頭へ戻る「輪っか」の構造を表現するため、次の都市を参照する際に ⁠% N⁠（要素数で割った余り）を使用し、IndexErrorを防いでいます。
* **経路の繋ぎ直しと更新**:
- そのままの距離合計(⁠d1⁠)と、交差を解消するように繋ぎ直した場合の距離合計(⁠d2⁠)を比較します。
- 短くなる場合(⁠d2<d1⁠)、スライスと⁠reversed()⁠関数を用いて、間の都市の訪問順序を逆順にすることで経路を更新します。
- 改善が行われなくなる（⁠improved = False⁠のままループを抜ける）まで、この処理を繰り返します。

# TSPチャレンジその2

## 概要
本プログラムは、巡回セールスマン問題に対して、スコアの向上と実行時間の安定化を両立させるため、3つのアルゴリズムを組み合わせたハイブリッド手法を実装したものです。
単なる「2-optのみ」では局所最適解から抜け出せないという弱点があるため、確率的に改悪を受け入れる「焼きなまし法」を導入しました。また、実行時間が爆発するのを防ぐため、時間制限による制御を行っています。

---

## 1. 準備・モジュールのインポートと距離計算
```python
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
```

## 2. 最後に使う2-opt関数
```python
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
```
* **焼きなまし法** の後に2-optを行うことで、より最短経路を探すことができます。
- 経路の中から独立した2つの道（A-B と C-D）を総当たりで選びます。
- 繋ぎ直した後の距離（d2）が、現在の距離（d1）よりも短くなる場合（d2 < d1）のみ、配列のスライスとreversed() を用いてルートを反転させて繋ぎ直します。
- 円の隣り合う辺をスキップするため、j の開始位置を i + 2 にし、最初と最後の組み合わせ（i == 0 and j == N - 1）を continue で除外しています。

## 3. Solve関数
### 前半(貪欲法)
```python
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
```
* **実装のポイント**
- **初期設定**
- 未訪問の都市を高速に管理するため、unvisited に set（集合）型で都市番号を格納します。スタート地点を 0 番の都市に固定し、tour = [0] から出発します。
- **貪欲法**
現在地（current_city）から、まだ行っていないすべての都市（candidate）への距離をループで計測し、一番近い都市（next_city）を特定して移動します。これを未訪問の都市がなくなるまで繰り返すことで、この後の探索のベースとなる初期ルートを高速に作成します。

### 後半（焼きなまし法）
```python
# 焼きなまし法
    current_dist = calc_total_dist(tour, cities)
    best_dist = current_dist
    best_tour = tour.copy()
    
    # パラメータ設定
    TIME_LIMIT = 1.8  # 1つの課題につき1.8秒で強制終了
    T_start = 100.0   # 初期温度
    T_end = 0.0001    # 終了温度
    
    start_time = time.time()
    
    while True:
        current_time = time.time()
        elapsed = current_time - start_time
        
        # 1.8秒経過したらループを抜ける
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
```
* **実装のポイント**
- **時間制限による制御**
- time.time() を使って、1つの問題につき正確に1.8秒間だけループを回します。これにより、都市数 N が非常に大きな問題でもプログラムが終了します。

- **温度 T の動的制御**
経過時間（elapsed）の割合に応じて、温度 T を初期温度から終了温度まで滑らかに減少させます。

- **ランダムな近傍選択と遷移判定**
- random.randint を用いて、ランダムに2つの道を選択します。繋ぎ直した後の距離の差（diff = d2 - d1）を計算し、短くなる場合は当然採用します。
- もし長くなってしまう（改悪になる）場合でも、現在の温度 T に応じた確率（math.exp(-diff / T)）を下回ればあえて採用します。これによって、2-optで発生する局所最適解の谷を抜けるようにしています。
- **最も良かったものの保存**
- 終盤に改悪した状態で終了してしまわないよう、過去最高スコアを更新した瞬間のルートを常に best_tour = tour.copy() として別メモリに保存しておきます。