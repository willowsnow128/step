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
            diff_sum=0.0
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
    
    
"""実行結果
yanagisawa.yukia@YukiAir week4 % python3 homework2.py pages_small.txt links_small.txt  
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
現在の差分: 1.2643749999999994
現在の差分: 0.2229401692708332
現在の差分: 0.008348361673990843
The most popular pages are:
C: 1.3730703124999994
D: 1.3730703124999994
B: 1.196673177083333
E: 0.811782552083333
F: 0.811782552083333
A: 0.4336210937499999

yanagisawa.yukia@YukiAir week4 % python3 homework2.py pages_medium.txt links_medium.txt
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
現在の差分: 15955745.624429556
現在の差分: 1863788.0576856453
現在の差分: 347007.51057423744
現在の差分: 34283.99051937665
現在の差分: 9663.04549663048
現在の差分: 3502.2034034683625
現在の差分: 1449.7323217868652
現在の差分: 640.0322636852123
現在の差分: 294.0353455589922
現在の差分: 139.30722185621028
現在の差分: 67.69476765516887
現在の差分: 33.660465161523625
現在の差分: 17.08227382366007
現在の差分: 8.831382564306747
現在の差分: 4.641206782413022
現在の差分: 2.4747787307289744
現在の差分: 1.3363277652453949
現在の差分: 0.7294996891176712
現在の差分: 0.4019656849025952
現在の差分: 0.2232611909770569
現在の差分: 0.12484685915296602
現在の差分: 0.07021691003105439
現在の差分: 0.03968537400618492
現在の差分: 0.02252326867639412
現在の差分: 0.012828730991026542
現在の差分: 0.0073294707591120166
The most popular pages are:
英語: 1507.297700556478
ISBN: 959.7071288904509
2006年: 526.1013565988807
2005年: 502.26093241761237
2007年: 491.481850589156
東京都: 480.2739485131828
昭和: 459.3758140702666
2004年: 445.3697475728473
2003年: 404.73835956539045
2000年: 401.88955444725576

yanagisawa.yukia@YukiAir week4 % python3 homework2.py pages_large.txt links_large.txt 
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
現在の差分: 273037695.9472505
現在の差分: 55294472.185153335
現在の差分: 8226107.911010812
現在の差分: 1209756.3130266154
現在の差分: 102876.03836902774
現在の差分: 29946.769983089056
現在の差分: 11877.120138950866
現在の差分: 5321.681345494758
現在の差分: 2541.537787376674
現在の差分: 1256.8830456193903
現在の差分: 642.6673193280669
現在の差分: 336.339814425223
現在の差分: 180.32414658872946
現在の差分: 98.41452364867148
現在の差分: 54.67504211566275
現在の差分: 30.779002713489604
現在の差分: 17.549827332374775
現在の差分: 10.102513779956144
現在の差分: 5.8680274330961035
現在の差分: 3.4315628421986273
現在の差分: 2.0193324811315767
現在の差分: 1.1939666600902565
現在の差分: 0.709023208082537
現在の差分: 0.4224595818634323
現在の差分: 0.25247685052506447
現在の差分: 0.15124797311493748
現在の差分: 0.0907986658748637
現在の差分: 0.05460192445488232
現在の差分: 0.03288468949784046
現在の差分: 0.01982972180300133
現在の差分: 0.011970643102370629
現在の差分: 0.007232980258509997
The most popular pages are:
英語: 4576.828626117526
日本: 4569.220860331079
VIAF_(識別子): 3806.8189930091244
バーチャル国際典拠ファイル: 3320.3658112865664
アメリカ合衆国: 2714.5298344096527
ISBN: 2711.526648514297
ISNI_(識別子): 2060.6625996408834
国際標準名称識別子: 1865.4484409757633
地理座標系: 1815.8479149648497
SUDOC_(識別子): 1518.7882366990211
"""
    
    
    
    