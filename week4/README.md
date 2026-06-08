# Wikipediaのページ探索アルゴリズム

1. **find_shortest_path** 与えられたStartページからGoalページまでの最短経路を見つける
2. **find_most_popular_pages** リストの中のページランクを計算し、最も人気のあるページを出力する
3. **find_longest_path** 与えられたStartページからGoalページまでの最長経路を見つける

## 最短経路探索（find_shortest_path）
与えられたstartとgoalの間の最短経路を見つけるプログラムです。
* **実装のポイント**
- 文字のままではリンクを辿ることができないため、タイトル名からページIDを検索するための逆引き辞書を作りました。
- **deque**を使うことで計算量O(1)で先頭のデータを取り出すことを可能にしています。
- **BFS**で最短経路を探しています。

```python
# Homework #1: 最短経路を見つける
    # 'start': 開始ページのタイトル
    # 'goal': 目的（ゴール）ページのタイトル
    def find_shortest_path(self, start, goal):
        #------------------------#
        # Write your code here!  #
        #------------------------#
        # タイトル名からページIDを検索するための逆引き辞書
        title_to_id={}
        # 元の辞書から順番に取り出す
        for id, title in self.titles.items():
        # 新しい辞書に、キーと値をひっくり返して登録する
            title_to_id[title] = id
        start_id=title_to_id.get(start)
        goal_id=title_to_id.get(goal)
        if start_id is None or goal_id is None:
            print("スタートまたはゴールのページがデータセットにありません。")
            return None
        # 通ってきた経路をキューで管理する
        queue=collections.deque([[start_id]])
        visited=set([start_id])
        while queue:
            path=queue.popleft()
            current_id=path[-1]
            if current_id==goal_id:
                # IDのリストを、ページタイトルのリストに変換
                path_titles = []
                for node_id in path:
                    path_titles.append(self.titles[node_id])
                print("->".join(path_titles))
                return path
            # 今いるページからリンクされている次のページを順番に確認
            for next_id in self.links[current_id]:
                if next_id not in visited:
                    visited.add(next_id)
                    new_path=path+[next_id]
                    queue.append(new_path)
                    
        print("経路がありません")
        return None
```

## ページランクが高いものを見つける（find_most_popular_pages）
リストの中のページランクを計算しています。
* **実装のポイント**
- 各ページの15%のスコアや行き止まりページのスコアを全ページに均等に配る際、毎回全ページに対して足し算をすると計算量が莫大になってしまいます。そこで**pool**という変数に一旦全体の配分スコアを貯金しておき、1ターンの最後にまとめて全ページに配る(**pool/N**)ことで、ループの回数を減らしました。
- リンクを持たないページが存在すると、そのページに集まったページランクがどこにも配られず、全体の合計スコアが毎ターン減ってしまいます。これを防ぐため、**else:**の分岐を作り、行き止まりのページが持つスコアは100% **pool**に回収して全体に還元することで、常に全体の合計スコアが一定に保たれるようにしました。
- ページランクの更新は完全に数値が動かなくなるまで待つと処理が終わらないため、「前のターンと新しいターンのスコアの差」を計算し、その2乗の合計（**diff_sum**）が**0.01**を下回った時点で「十分に収束した」と判定して**break**する仕組みにしました。

```python
   # Homework #2: ページランクを計算し、最も人気のあるページを出力する
    def find_most_popular_pages(self):
        #------------------------#
        # Write your code here!  #
        #------------------------#
        N=len(self.titles)
        # 最初のページランクを初期化
        page_rank={}
        for id in self.titles.keys():
            page_rank[id]=1.0
        while True:
            # 次のターンのページランクを入れる箱を用意
            new_page_rank={}
            for id in self.titles.keys():
                new_page_rank[id]=0.0
            # 全員に均等に配るためのスコアを貯める変数
            pool=0.0
            
            for node_id in self.titles.keys():
                links=self.links[node_id]
                if len(links)>0:
                    share=(page_rank[node_id]*0.85)/len(links)
                    for destination in links:
                        new_page_rank[destination]+=share
                    pool+=page_rank[node_id]*0.15
                else:
                    pool+=page_rank[node_id]*1.0
            base_add=pool/N
            for node_id in self.titles.keys():
                new_page_rank[node_id]+=base_add
            # 新しいスコアと古いスコアの差の2乗の合計を計算
            diff_sum = 0.0
            for i in self.titles.keys():
                diff_sum+=(new_page_rank[i]-page_rank[i])**2
            print(f"現在の差分: {diff_sum}")
            
            if diff_sum<0.01:
                page_rank=new_page_rank
                break
            
            page_rank=new_page_rank
        
        print("The most popular pages are:")
        def get_score(item):
            return item[1]
            
        # その関数の名前（get_score）をキーとして渡して並べ替える
        sorted_ranks = sorted(page_rank.items(), key=get_score, reverse=True)
        for i in range(10):
            if i<len(sorted_ranks):
                node_id=sorted_ranks[i][0]
                score=sorted_ranks[i][1]
                print(f"{self.titles[node_id]}: {score}")
        print()
```

## 最長経路を探索する(find_longest_path)
* **実装のポイント**
- まず、ゴール地点から逆向きに**BFS**を行い、全ページに対して「ゴールまでの最短距離マップ（**dist_to_goal**）」を事前計算しました。その後、スタート地点から**DFS**を行う際、次に行くページの候補を「ゴールまでの距離が**遠い順**」に優先して選ぶようにしています。
- 再帰上限に引っかからないように**stack**配列(リスト)を用意し、**while**ループを用いた非再帰のDFSとして実装しました。これにより、メモリの許す限りどこまでも深い経路を探索できるようになりました。
- DFSで次に行くページを選ぶ際、候補のリストを「ゴールに近い順（昇順）」に並べ替えてスタックに積んでいます。こうすることで、リストの最後尾に「一番遠いページ」が配置されるため、要素を取り出す際に**pop()**（末尾からの取り出し）を使うことができます。先頭からデータを取り出すより処理が高速（計算量O(1)）になり、大規模データの探索時間を短縮できました。

```python
def find_longest_path(self, start, goal):
        #------------------------#
        # Write your code here!  #
        #------------------------#
        title_to_id={}
        for id, title in self.titles.items():
            title_to_id[title]=id
        start_id=title_to_id.get(start)
        goal_id=title_to_id.get(goal)

        if start_id is None or goal_id is None:
            print("スタートまたはゴールが見つかりません。")
            return
        # BFS：ゴールから逆走して「距離マップ」を作る
        # 矢印を逆向きにした「逆引き辞典」を作る
        reverse_links=collections.defaultdict(list)
        for u, neighbors in self.links.items():
            for v in neighbors:
                reverse_links[v].append(u)

        dist_to_goal={}
        queue=collections.deque([goal_id])
        # ゴール自身の距離は0
        dist_to_goal[goal_id]=0 

        # ゴールからBFSで広がっていく
        while queue:
            curr=queue.popleft()
            d=dist_to_goal[curr]
            for prev in reverse_links[curr]:
                if prev not in dist_to_goal:
                    dist_to_goal[prev]=d+1
                    queue.append(prev)
                    
        # DFS：距離マップを見ながら遠回りする
        visited=set([start_id])
        path=[start_id]
        longest_path=[]

        # 次の候補を計算して、距離が遠い順に取り出せるようにする関数
        def get_sorted_neighbors(curr_id):
            valid=[]
            for nxt in self.links[curr_id]:
                if nxt not in visited and nxt in dist_to_goal:
                    valid.append(nxt)
            
            # 後で pop() を使って「末尾」から取り出すため、あえて「昇順（距離が近い順）」に並べておく、リストの最後尾に一番遠いページが来るようにする
            def get_distance(node_id):
                return dist_to_goal[node_id]
            valid.sort(key=get_distance)
            return valid

        # スタックには「(今いるページID, 次に行ける候補リスト)」をセットで入れる
        stack = [(start_id, get_sorted_neighbors(start_id))]

        # スタックが空になる（全ての可能性を探し尽くす）までループ
        while stack:
            # スタックの一番上（現在地）を確認
            curr_id, neighbors=stack[-1]

            # ゴールに到着したら、記録を残して終了！
            if curr_id==goal_id:
                longest_path=list(path)
                break

            # まだ行ける候補が残っている場合
            if neighbors:
                # 候補リストの末尾（＝一番距離が遠いページ）を1つ取り出す
                nxt=neighbors.pop()
                
                # 他のルートですでに訪問済みになっていないか最終確認して進む
                if nxt not in visited:
                    visited.add(nxt)
                    path.append(nxt)
                    # 次のページの情報をスタックの一番上に積んで、さらに奥へ進む
                    stack.append((nxt, get_sorted_neighbors(nxt)))
            else:
                # もう行ける候補がない場合（行き止まり）は、バックトラック
                # スタックと現在の経路から取り除き1歩戻る
                stack.pop()
                path.pop()

        # 結果の出力とチェック
        if longest_path:
            # 経路の長さを出力
            print(f"見つかった経路の長さ: {len(longest_path)} ページ（{len(longest_path) - 1} ステップ）")
            
            # 全部出力するとターミナルが溢れるので、最初と最後だけ表示する
            start_title = self.titles[longest_path[0]]
            end_title = self.titles[longest_path[-1]]
            print(f"ルート: {start_title} -> ... (中略) ... -> {end_title}")
            
            # チェック関数で、正しい経路か確認
            self.assert_path(longest_path, start, goal)
            print("assert_path: 経路のルールチェックをパスしました！")
        else:
            print("経路が見つかりませんでした。")
```