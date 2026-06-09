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
    
    
    
    
'''実行結果
yanagisawa.yukia@YukiAir week4 % python3 homework1.py pages_small.txt links_small.txt
Finished reading pages_small.txt
Finished reading links_small.txt

The longest titles are:
A
B
C
D
E
F

The most linked pages are:
B 3

スタートまたはゴールのページがデータセットにありません。
A->B->D
yanagisawa.yukia@YukiAir week4 % python3 homework1.py pages_medium.txt links_medium.txt
Finished reading pages_medium.txt
Finished reading links_medium.txt

The longest titles are:
日本国とアメリカ合衆国との間の相互協力及び安全保障条約第六条に基づく施設及び区域並びに日本国における合衆国軍隊の地位に関する協定の実施に伴う刑事特別法
一般社団法人及び一般財団法人に関する法律及び公益社団法人及び公益財団法人の認定等に関する法律の施行に伴う関係法律の整備等に関する法律案
日本国とアメリカ合衆国との間の相互協力及び安全保障条約第6条に基づく施設及び区域並びに日本国における合衆国軍隊の地位に関する協定
日本国とアメリカ合衆国との間の相互協力及び安全保障条約第六条に基づく施設及び区域並びに日本国における合衆国軍隊の地位に関する協定
国際的な協力の下に規制薬物に係る不正行為を助長する行為等の防止を図るための麻薬及び向精神薬取締法等の特例等に関する法律
民放5局史上最大のコラボレーション!地デジ夏祭り2006全部見せます!ナゴヤのテレビ"過去""現在"そして"未来"
アイルランドの貧民の子供たちが両親及び国の負担となることを防ぎ、国家社会の有益なる存在たらしめるための穏健なる提案
ドナウダンプフシファールトゼレクトリツィテーテンハウプトベトリープスヴェルクバウウンターベアムテンゲゼルシャフト
マルキ・ド・サドの演出のもとにシャラントン精神病院患者たちによって演じられたジャン＝ポール・マラーの迫害と暗殺
くりぃむしちゅーも観ながらいろいろゴチャゴチャ言ってますけども…笑いのタマゴLサイズ（おひとり様何回でも）
偽造カード等及び盗難カード等を用いて行われる不正な機械式預貯金払戻し等からの預貯金者の保護等に関する法律
ルイージ・アメデーオ・ジュゼッペ・マリーア・フェルディナンド・フランチェスコ・ディ・サヴォイア＝アオスタ
中居正広のテレビ50年名番組だョ!全員集合笑った泣いた感動したあのシーンをもう一度夢の総決算スペシャル
タウマタファカタンギハンガコアウアウオタマテアトゥリプカカピキマウンガホロヌクポカイフェヌアキタナタフ
アウグステ・ヴィクトリア・フォン・シュレースヴィヒ＝ホルシュタイン＝ゾンダーブルク＝アウグステンブルク

The most linked pages are:
ISBN 52641

渋谷->マクドナルド->Twitter->パレートの法則
A->D
yanagisawa.yukia@YukiAir week4 % python3 homework1.py pages_large.txt links_large.txt 
Finished reading pages_large.txt
Finished reading links_large.txt

The longest titles are:
Lopadotemachoselachogaleokranioleipsanodrimhypotrimmatosilphiokarabomelitokatakechymenokichlepikossyphophattoperisteralektryonoptekephalliokigklopeleiolagoiosiraiobaphetraganopterygon
Lopadotemachoselachogaleokranioleipsanodrimhypotrimmatosilphioparaomelitokatakechymenokichlepikossyphophattoperisteralektryonoptekephalliokigklopeleiolagoiosiraiobaphetraganopterygon
N-アセチルムラモイル-L-アラニル-D-グルタミル-L-リシル-(N6-トリグリシン)-D-アラニル-D-アラニン-ジホスホウンデカプレニル-N-アセチルグルコサミン:グリシングリシルトランスフェラーゼ
10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
地域公共交通の活性化及び再生に関する法律に基づく道路運送高度化実施計画、乗継円滑化実施計画及び新地域旅客運送事業計画の認定に係る都道府県公安委員会の意見の聴取に関する命令
性をめぐる個人の尊厳が重んぜられる社会の形成に資するために性行為映像制作物への出演に係る被害の防止を図り及び出演者の救済に資するための出演契約等に関する特則等に関する法律
ネットという無数の声雄が割拠する世界から、最新最強の武器バイノーラルマイクを駆使し、ファンのみんなに癒しと感動を与える声優を、とにかく!全力を尽くして熱く応援するラジオ
昭和二十六年十二月五日附連合国最高司令官覚書「若干の外かく地域の日本からの政治上及び行政上の分離に関する件」に伴う鹿兒島県大島郡十島村に関する暫定措置に関する政令
イラクにおける自衛隊の部隊等による対応措置を直ちに終了させるためのイラクにおける人道復興支援活動及び安全確保支援活動の実施に関する特別措置法を廃止する法律案
レオーネ・セクスタス・デニス・オズウルフ・フラウダティフィリウス・トルマッシュ＝トルマッシュ・デ・オレラーナ・プランタジェネット・トルマッシュ＝トルマッシュ
地域における一般乗合旅客自動車運送事業及び銀行業に係る基盤的なサービスの提供の維持を図るための私的独占の禁止及び公正取引の確保に関する法律の特例に関する法律
鈴懸の木の道で「君の微笑みを夢に見る」と言ってしまったら僕たちの関係はどう変わってしまうのか、僕なりに何日か考えた上でのやや気恥ずかしい結論のようなもの
6086555670238378989670371734243169622657830773351885970528324860512791691264
日本国とアメリカ合衆国との間の相互協力及び安全保障条約第六条に基づく施設及び区域並びに日本国における合衆国軍隊の地位に関する協定の実施に伴う刑事特別法
ベンティアドショットヘーゼルナッツバニラアーモンドキャラメルエキストラホイップキャラメルソースモカソースランバチップチョコレートクリームフラペチーノ

The most linked pages are:
日本 366422

渋谷->マクドナルド->Twitter->パレートの法則
A->D
'''