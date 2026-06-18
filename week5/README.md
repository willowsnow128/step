# solver-greedy.pyの説明

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

