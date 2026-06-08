import sys
import collections

class Wikipedia:

    # ページのグラフを初期化
    def __init__(self, pages_file, links_file):

        # ページIDからページタイトルへのマッピング
        # 例えば、self.titles[1234]はIDが1234であるページのタイトルを返す
        self.titles = {}

        # ページリンクの集合
        # 例えば、self.links[1234]はIDが1234のページからリンクされている
        # ページIDの配列を返す
        self.links = {}

        # pagesファイルを読み込んで、self.titlesに格納する
        with open(pages_file) as file:
            for line in file:
                (id, title) = line.rstrip().split(" ")
                id = int(id)
                assert not id in self.titles, id
                self.titles[id] = title
                self.links[id] = []
        print("Finished reading %s" % pages_file)

        # linksファイルを読み込んで、self.linksに格納する
        with open(links_file) as file:
            for line in file:
                (src, dst) = line.rstrip().split(" ")
                (src, dst) = (int(src), int(dst))
                assert src in self.titles, src
                assert dst in self.titles, dst
                self.links[src].append(dst)
        print("Finished reading %s" % links_file)
        print()


    # 例: 最も長いタイトルを見つける
    def find_longest_titles(self):
        titles = sorted(self.titles.values(), key=len, reverse=True)
        print("The longest titles are:")
        count = 0
        index = 0
        while count < 15 and index < len(titles):
            if titles[index].find("_") == -1:
                print(titles[index])
                count += 1
            index += 1
        print()


    # 例: 最も多くリンクされているページを見つける
    def find_most_linked_pages(self):
        link_count = {}
        for id in self.titles.keys():
            link_count[id] = 0

        for id in self.titles.keys():
            for dst in self.links[id]:
                link_count[dst] += 1

        print("The most linked pages are:")
        link_count_max = max(link_count.values())
        for dst in link_count.keys():
            if link_count[dst] == link_count_max:
                print(self.titles[dst], link_count_max)
        print()

    # Homework #3 (optional):
    # ヒューリスティックを用いて、最長経路を探索する
    # 'start': 開始ページのタイトル
    # 'goal': 目的ページのタイトル
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


    # Helper function for Homework #3:
    # 見つかった経路が正しい形式かどうかを確認するために、この関数を使用する
    # 'path': 見つかった経路を格納するページIDの配列
    #     path[0] は開始ページ. path[-1] は目的ページ.
    #     path[0] -> path[1] -> ... -> path[-1] は開始ページから目的ページへの経路を表す
    # 'start': 開始ページのタイトル
    # 'goal': 目的ページのタイトル
    def assert_path(self, path, start, goal):
        assert(start != goal)
        assert(len(path) >= 2)
        assert(self.titles[path[0]] == start)
        assert(self.titles[path[-1]] == goal)
        for i in range(len(path) - 1):
            assert(path[i + 1] in self.links[path[i]])
        visited = {}
        for node in path:
            assert(node not in visited)
            visited[node] = True


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: %s pages_file links_file" % sys.argv[0])
        exit(1)

    wikipedia = Wikipedia(sys.argv[1], sys.argv[2])
    # Homework #3 (optional)
    wikipedia.find_longest_path("渋谷", "池袋")
    
    
"""実行結果
yanagisawa.yukia@YukiAir week4 % python3 homework3.py pages_medium.txt links_medium.txt
Finished reading pages_medium.txt
Finished reading links_medium.txt

見つかった経路の長さ: 335193 ページ（335192 ステップ）
ルート: 渋谷 -> ... (中略) ... -> 池袋
assert_path: 経路のルールチェックをパスしました！
yanagisawa.yukia@YukiAir week4 % python3 homework3.py pages_large.txt links_large.txt 
Finished reading pages_large.txt
Finished reading links_large.txt

見つかった経路の長さ: 747982 ページ（747981 ステップ）
ルート: 渋谷 -> ... (中略) ... -> 池袋
assert_path: 経路のルールチェックをパスしました！
"""
    
    
    
    