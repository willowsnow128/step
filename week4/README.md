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

