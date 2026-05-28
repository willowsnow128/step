import random, sys, time

# ハッシュ関数
# 'key': 文字列
# 戻り値: ハッシュ値
def calculate_hash(key):
    assert type(key) == str
    # ハッシュ関数を改良
    hash_value=0
    for i in key:
        # 今までの計算結果に素数を掛け、新しい文字のコードを足す
        # 998244353で割った余りをとることで、数値が大きくなりすぎるのを防ぐ
        hash_value=(hash_value*31+ord(i))%998244353
    return hash_value
    


# ハッシュテーブル内の1つのキーと値のペアを表すItemオブジェクト
class Item:
    # 'key': 要素のキー(文字列)
    # 'value': 要素の値
    # 'next': 連結リストの次の要素 これが連結リストの最後の要素である場合、'next'はNone になる
    def __init__(self, key, value, next):
        assert type(key) == str
        self.key = key
        self.value = value
        self.next = next

# キーと値のペアを格納する、ハッシュテーブルのメインのデータ構造
# キーは文字列である必要があり、値は任意の型を使用できる
# 'self.bucket_size': バケツのサイズ（配列の要素数）
# 'self.buckets': バケツの配列。self.buckets[hash%self.bucket_size]には、ハッシュ値が'hash'になる要素の連結リストが格納される
# 'self.item_count': ハッシュテーブル内の要素の総数
class HashTable:
    # ハッシュテーブルの初期化
    def __init__(self):
        # バケツの初期サイズを97に決定(ハッシュの衝突を減らすために素数になっている)
        self.bucket_size = 97
        self.buckets = [None] * self.bucket_size
        self.item_count = 0

    # ハッシュテーブルに要素を追加する、キーがすでに存在する場合、対応する値は新しい値に更新される
    # 'key': 要素のキー
    # 'value': 要素の値
    # 戻り値: 新しい要素が追加された場合はTrue。キーがすでに存在し、値が更新された場合はFalse
    def put(self, key, value):
        assert type(key) == str
        check_size(self.size(), self.bucket_size)  # Don't remove this code.
        #------------------------#
        # ここに自分のコードを書く   #
        #------------------------#
        # 保存場所の計算
        hash_value=calculate_hash(key)
        index=hash_value%self.bucket_size
        # 対象の連結リストの先頭を取得
        current_item=self.buckets[index]
        # 同じキーがないか探し、あれば上書きする
        while current_item is not None:
            if current_item.key==key:
                # キーが見つかったので値を更新
                current_item.value=value
                # 新規追加ではないためFalseを返す
                return False
            # 次の要素へ進む
            current_item=current_item.next

        # 新しい要素を追加する
        # 現在の連結リストの先頭 (self.buckets[index]) を、新しいItemのnextとして繋ぐ
        new_item=Item(key, value, self.buckets[index])
        # バケツの先頭を、新しく作った Item に置き換える
        self.buckets[index]=new_item
        # 要素数を1つ増やす
        self.item_count+=1
        # データ数がバケツサイズの70%を超えたら、サイズを約2倍に拡張する
        if self.item_count>=self.bucket_size*0.7:
            # ハッシュの衝突を減らすため、なるべく奇数（理想は素数）を維持する
            self.rehash(self.bucket_size*2+1)
        # 新規追加なのでTrueを返す
        return True


    # ハッシュテーブルから要素を取得する
    # 'key': 要素のキー。
    # 戻り値: 要素が見つかった場合は(要素の値,True)を返す、それ以外の場合は(None,False)を返す
    def get(self, key):
        assert type(key) == str
        check_size(self.size(), self.bucket_size)  # これは消しちゃだめ
        #------------------------#
        # ここに自分のコードを書く   #
        #------------------------#
        # 保存場所（インデックス）の計算
        hash_value=calculate_hash(key)
        index=hash_value%self.bucket_size
        # 連結リストを先頭から辿る
        current_item=self.buckets[index]

        while current_item is not None:
            if current_item.key==key:
                # 見つかったら、値とTrueのペアを返す
                return (current_item.value, True)
            current_item=current_item.next
        # 最後まで探して見つからなかったらNoneとFalseを返す
        return (None, False)

    # ハッシュテーブルから要素を削除する
    # 'key': 要素のキー。
    # 戻り値: 要素が見つかって正常に削除された場合はTrue。それ以外の場合はFalse。
    def delete(self, key):
        assert type(key) == str
        #------------------------#
        # ここに自分のコードを書く   #
        #------------------------#
        assert type(key) == str

        # 保存場所（インデックス）の計算
        hash_value=calculate_hash(key)
        index=hash_value%self.bucket_size

        current_item=self.buckets[index]
        # 1つ前の要素を記録するための変数
        prev_item=None  

        # 連結リストを辿りながら削除対象を探す
        while current_item is not None:
            if current_item.key==key:
                # 削除対象が見つかった場合の処理
                if prev_item is None:
                    # 削除対象がリストの先頭だった場合
                    # バケツの先頭を、2番目の要素に付け替える
                    self.buckets[index]=current_item.next
                else:
                    # 削除対象がリストの2番目以降だった場合
                    # 1つ前の要素のnextを、削除対象の次の要素に繋ぎ変える
                    prev_item.next=current_item.next
                
                # 要素数を1つ減らす
                self.item_count-=1
                # check_sizeの制約（データ数30%以上）を下回ったら縮小する
                if self.item_count<self.bucket_size*0.3:
                    # サイズを半分にする。ただし、初期サイズの97よりは小さくしない
                    new_size=max(97, self.bucket_size//2)
                    # 偶数になってしまったら+1して奇数にしておく
                    if new_size%2==0:
                        new_size+=1
                
                    self.rehash(new_size)
                return True
            
            # 次の要素へ進む前に、現在の要素をprev_itemとして記憶しておく
            prev_item=current_item
            current_item=current_item.next

        # 見つからなかった場合はFalseを返す
        return False

    # ハッシュテーブル内の要素の総数を返す
    def size(self):
        return self.item_count
    
    # テーブルサイズを変更し、すべての要素を再配置する
    def rehash(self, new_bucket_size):
        # 古いバケツの処理
        old_buckets=self.buckets
        
        # 新しいサイズの空のバケツを用意する
        self.bucket_size=new_bucket_size
        self.buckets=[None]*self.bucket_size
        
        # 古いバケツから新しいバケツへ要素をすべて移動する
        for current_item in old_buckets:
            while current_item is not None:
                # 繋ぎ変える前に、次の要素を記憶しておく
                next_item=current_item.next
                
                # 新しいバケツでの保存場所を再計算
                hash_value=calculate_hash(current_item.key)
                index=hash_value%self.bucket_size
                
                # 既存のItemオブジェクトを再利用して、新しいバケツの先頭に割り込ませる
                current_item.next=self.buckets[index]
                self.buckets[index]=current_item
                
                # 記憶しておいた次の要素へ進む
                current_item=next_item


# ハッシュテーブルが「妥当な」バケツサイズを持っているか確認する
# バケツのサイズが100未満であるか、バケツの30%以上が使用されている場合、妥当であると判断される
# 注: この関数は変更してはいけない
def check_size(item_count, bucket_size):
    assert (bucket_size < 100 or item_count >= bucket_size * 0.3)


# ハッシュテーブルの機能的な動作をテストする
def functional_test():
    hash_table = HashTable()

    assert hash_table.put("aaa", 1) == True
    assert hash_table.get("aaa") == (1, True)
    assert hash_table.size() == 1

    assert hash_table.put("bbb", 2) == True
    assert hash_table.put("ccc", 3) == True
    assert hash_table.put("ddd", 4) == True
    assert hash_table.get("aaa") == (1, True)
    assert hash_table.get("bbb") == (2, True)
    assert hash_table.get("ccc") == (3, True)
    assert hash_table.get("ddd") == (4, True)
    assert hash_table.get("a") == (None, False)
    assert hash_table.get("aa") == (None, False)
    assert hash_table.get("aaaa") == (None, False)
    assert hash_table.size() == 4

    assert hash_table.put("aaa", 11) == False
    assert hash_table.get("aaa") == (11, True)
    assert hash_table.size() == 4

    assert hash_table.delete("aaa") == True
    assert hash_table.get("aaa") == (None, False)
    assert hash_table.size() == 3

    assert hash_table.delete("a") == False
    assert hash_table.delete("aa") == False
    assert hash_table.delete("aaa") == False
    assert hash_table.delete("aaaa") == False

    assert hash_table.delete("ddd") == True
    assert hash_table.delete("ccc") == True
    assert hash_table.delete("bbb") == True
    assert hash_table.get("aaa") == (None, False)
    assert hash_table.get("bbb") == (None, False)
    assert hash_table.get("ccc") == (None, False)
    assert hash_table.get("ddd") == (None, False)
    assert hash_table.size() == 0

    assert hash_table.put("abc", 1) == True
    assert hash_table.put("acb", 2) == True
    assert hash_table.put("bac", 3) == True
    assert hash_table.put("bca", 4) == True
    assert hash_table.put("cab", 5) == True
    assert hash_table.put("cba", 6) == True
    assert hash_table.get("abc") == (1, True)
    assert hash_table.get("acb") == (2, True)
    assert hash_table.get("bac") == (3, True)
    assert hash_table.get("bca") == (4, True)
    assert hash_table.get("cab") == (5, True)
    assert hash_table.get("cba") == (6, True)
    assert hash_table.size() == 6

    assert hash_table.delete("abc") == True
    assert hash_table.delete("cba") == True
    assert hash_table.delete("bac") == True
    assert hash_table.delete("bca") == True
    assert hash_table.delete("acb") == True
    assert hash_table.delete("cab") == True
    assert hash_table.size() == 0

    # リハッシュのテスト
    for i in range(100):
        hash_table.put(str(i), str(i))
    for i in range(100):
        assert hash_table.get(str(i)) == (str(i), True)
    for i in range(100):
        assert hash_table.delete(str(i)) == True
    hash_table.put("abc", 1)
    hash_table.put("acb", 2)
    assert hash_table.get("abc") == (1, True)
    assert hash_table.get("acb") == (2, True)
    print("Functional tests passed!")


# ハッシュテーブルのパフォーマンス（実行速度）をテストする
# 目標は、ハッシュテーブルがほぼO(1)で動作するようにすること
# もしハッシュテーブルがほぼO(1)で動作するなら、各イテレーションの実行時間はハッシュテーブル内の要素数に依存しないはず
# 目標を達成するには、1) リハッシュの実装（ヒント: ハッシュテーブル内の要素数があるしきい値に達したときにハッシュテーブルを拡張 / 縮小する）と、
# 2) ハッシュ関数の調整（ヒント: ハッシュの衝突を減らす方法を考える）が必要
def performance_test():
    hash_table = HashTable()

    for iteration in range(100):
        begin = time.time()
        random.seed(iteration)
        for i in range(10000):
            rand = random.randint(0, 100000000)
            hash_table.put(str(rand), str(rand))
        random.seed(iteration)
        for i in range(10000):
            rand = random.randint(0, 100000000)
            hash_table.get(str(rand))
        end = time.time()
        print("%d %.6f" % (iteration, end - begin))

    for iteration in range(100):
        random.seed(iteration)
        for i in range(10000):
            rand = random.randint(0, 100000000)
            hash_table.delete(str(rand))

    assert hash_table.size() == 0
    print("Performance tests passed!")


if __name__ == "__main__":
    functional_test()
    performance_test()
    

"""実行結果
yanagisawa.yukia@YukiAir step % /opt/homebrew/bin/python3 /Users/yanagisaway
uukiai/step/week2/homework1.py
Functional tests passed!
0 0.041971
1 0.043852
2 0.028831
3 0.060183
4 0.028965
5 0.031211
6 0.031794
7 0.086979
8 0.034343
9 0.030621
10 0.030576
11 0.031900
12 0.031665
13 0.033069
14 0.149404
15 0.038081
16 0.030391
17 0.032549
18 0.032291
19 0.030628
20 0.032916
21 0.031875
22 0.031402
23 0.032432
24 0.031317
25 0.107529
26 0.032377
27 0.031825
28 0.278321
29 0.031410
30 0.045438
31 0.030856
32 0.032469
33 0.031211
34 0.030820
35 0.032368
36 0.030923
37 0.032720
38 0.031137
39 0.031175
40 0.032718
41 0.031249
42 0.032680
43 0.031347
44 0.033179
45 0.031294
46 0.031543
47 0.033213
48 0.031985
49 0.034128
50 0.032306
51 0.032358
52 0.260805
53 0.032615
54 0.033712
55 0.031721
56 0.515736
57 0.057418
58 0.030314
59 0.032194
60 0.031128
61 0.030532
62 0.032342
63 0.031079
64 0.032576
65 0.031093
66 0.032535
67 0.031152
68 0.031049
69 0.032145
70 0.031299
71 0.032786
72 0.030836
73 0.031044
74 0.033509
75 0.031715
76 0.033424
77 0.031703
78 0.033219
79 0.401460
80 0.031113
81 0.032669
82 0.031314
83 0.033150
84 0.031323
85 0.031230
86 0.033244
87 0.031222
88 0.033192
89 0.031866
90 0.031282
91 0.033263
92 0.031496
93 0.033201
94 0.031761
95 0.032026
96 0.033325
97 0.031863
98 0.033162
99 0.031867
Performance tests passed!
"""