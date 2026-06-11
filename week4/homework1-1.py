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

    # Homework #1: 最短経路を見つける
    # 'start': 開始ページのタイトル
    # 'goal': 目的（ゴール）ページのタイトル
    def find_shortest_path(self, start, goal):
        title_to_id = {}
        for id, title in self.titles.items():
            title_to_id[title] = id
            
        start_id = title_to_id.get(start)
        goal_id = title_to_id.get(goal)
        
        if start_id is None or goal_id is None:
            print("スタートまたはゴールのページがデータセットにありません。")
            return None

        queue = collections.deque([start_id])
        previous_node = {}
        # スタート地点は「前」がないのでNoneにしておく
        previous_node[start_id] = None  
        
        while queue:
            current_id = queue.popleft()
            
            # ゴールに到着した場合
            if current_id == goal_id:
                # 経路を復元する
                path_ids = []
                curr = goal_id
                
                # currがNone（スタート地点のさらに前）になるまで遡り続ける
                while curr is not None:
                    path_ids.append(curr)
                    # 辞書を見て、1つ前のページに戻る
                    curr = previous_node[curr]  
                    
                path_ids.reverse()
                
                # IDのリストをタイトルのリストに変換して出力
                path_titles = []
                for node_id in path_ids:
                    path_titles.append(self.titles[node_id])
                print(" -> ".join(path_titles))
                
                return path_ids
                
            # 今いるページからリンクされている次のページを順番に確認
            for next_id in self.links[current_id]:
                if next_id not in previous_node:
                    previous_node[next_id] = current_id
                    queue.append(next_id)
                    
        print("経路がありません")
        return None


    # Homework #2: ページランクを計算し、最も人気のあるページを出力する
    def find_most_popular_pages(self):
        #------------------------#
        # Write your code here!  #
        #------------------------#
        pass


    # Homework #3 (optional):
    # ヒューリスティックを用いて、最長経路を探索する
    # 'start': 開始ページのタイトル
    # 'goal': 目的ページのタイトル
    def find_longest_path(self, start, goal):
        #------------------------#
        # Write your code here!  #
        #------------------------#
        pass


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
    # Example
    wikipedia.find_longest_titles()
    # Example
    wikipedia.find_most_linked_pages()
    # Homework #1
    wikipedia.find_shortest_path("渋谷", "パレートの法則")
    wikipedia.find_shortest_path("A", "D")
    # Homework #2
    wikipedia.find_most_popular_pages()
    # Homework #3 (optional)
    wikipedia.find_longest_path("渋谷", "池袋")
    
    
    
    