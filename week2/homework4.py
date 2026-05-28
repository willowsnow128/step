import random, sys
import homework1 # 宿題1で作ったハッシュテーブルを使用する 

###########################################################################
#                                                                         #
#  最も最近アクセスされた要素を保存するキャッシュをゼロから実装しましょう。　　　　　   #
#                                                                         #
# Pythonの辞書(dict)やcollectionsライブラリは使用しないでください。              #
# データ構造を自分で実装することが目的です。                                     #
#                                                                         #
###########################################################################

class Page:
    def __init__(self, url, contents):
        # URL
        self.url = url
        # URLのコンテンツ
        self.contents = contents
        # 前のページ（双方向リストの前の要素へのリンク）
        self.prev = None
        # 次のページ（双方向リストの次の要素へのリンク）
        self.next = None

        
class Cache:
    # キャッシュの初期化を行う
    # 'limit': キャッシュの最大サイズ（保存できる件数の上限）
    def __init__(self, limit):
        assert(limit >= 1)
        self.limit = limit
        self.hit_count = 0 # キャッシュヒット時に増やす
        self.miss_count = 0 # キャッシュミス(みつからない時に増やす
        #------------------------#
        # ここに自分のコードを書く   #
        #------------------------#
        self.hash_table=homework1.HashTable()
        self.head=None # 最初はNone
        self.tail=None # 最初はNone
    
    # 指定されたページを双方向リストから切り離す
    def remove_page(self,page):
        # 前のデータの繋ぎ変え
        if page.prev is not None:
            page.prev.next=page.next
        else :
            # 自分が先頭だった場合はheadを更新
            self.head=page.next 
        # 後ろのデータの繋ぎ変え
        if page.next is not None:
            page.next.prev=page.prev
        else:
            # 自分が末尾だった場合はtailを更新
            self.tail=page.prev 

        # リンクをリセット
        page.prev=None
        page.next=None
    
    # 指定されたページを双方向リストの先頭に追加する
    def add_front(self, page):
        page.next=self.head
        page.prev=None

        if self.head is not None:
            self.head.prev=page
        
        self.head=page

        # 初めてのデータ追加だった場合は、それが末尾にもなる
        if self.tail is None:
            self.tail=page
    
        
    # ページにアクセスし、最も最近アクセスされたページを 'limit' の数だけ保存するように
    # キャッシュを更新する。この操作はほぼ O(1) で行う必要がある。
    # 'url': アクセスされたURL
    # 'contents': URLのコンテンツ（中身）
    def access_page(self, url, contents):
        # まずはハッシュテーブルを使って、URLがすでにキャッシュにあるか検索する
        page_data,found=self.hash_table.get(url)

        if found:
            # キャッシュにあった場合
            self.hit_count+=1
            page=page_data
            # 中身を最新に更新する
            page.contents=contents 
            
            # アクセスされたので一番新しいデータにするため、今いる場所から切り離して、リストの先頭に持ってくる
            self.remove_page(page)
            self.add_front(page)
            
        else:
            # キャッシュになかった場合
            self.miss_count+=1
            # 新しいページを作る
            new_page=Page(url, contents)
            
            # ハッシュテーブルに登録して、双方向リストの先頭（一番新しい場所）に追加する
            self.hash_table.put(url, new_page)
            self.add_front(new_page)

            # もしキャッシュの容量をオーバーしてしまったら、一番古いものを消す
            if self.hash_table.size()>self.limit:
                # 双方向リストの末尾を見れば一番古いものがすぐわかる
                oldest_page=self.tail
                
                # 双方向リストから一番古いページを切り離す
                self.remove_page(oldest_page)
                # ハッシュテーブルからも一番古いページのURLを削除する
                self.hash_table.delete(oldest_page.url)

    # キャッシュに保存されているURLのリストを返す。
    # URLは、最も最近アクセスされたものから順番（新しい順）に並べる。
    def get_pages(self):
        #------------------------#
        # ここに自分のコードを書く   #
        #------------------------#
        urls = []
        # 双方向リストの先頭(head)から順番に辿っていく
        current = self.head
        # current が None になる（＝末尾を通り過ぎる）まで繰り返す
        while current is not None:
            urls.append(current.url)
            # 次のページへ進む
            current = current.next
            
        return urls


    # キャッシュのヒット率を計算して返す。
    def get_hitrate(self):
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0

    
def cache_test():
    # キャッシュのサイズを4に設定
    cache = Cache(4)

    # 最初はページはキャッシュする
    assert cache.get_pages() == []

    # "a.com" にアクセスする。
    cache.access_page("a.com", "AAA")
    # "a.com" がキャッシュされる。
    assert cache.get_pages() == ["a.com"]

    # "b.com" にアクセスする。
    cache.access_page("b.com", "BBB")
    # キャッシュは次のように更新される：
    #   (new)<-- "b.com", "a.com" -->(old)
    assert cache.get_pages() == ["b.com", "a.com"]

    # "c.com" にアクセスする。
    cache.access_page("c.com", "CCC")
    # キャッシュは次のように更新される：
    #   (new)<-- "c.com", "b.com", "a.com" -->(old)
    assert cache.get_pages() == ["c.com", "b.com", "a.com"]

    # "d.com" にアクセスする。
    cache.access_page("d.com", "DDD")
    # キャッシュは次のように更新される：
    #   (new)<-- "d.com", "c.com", "b.com", "a.com" -->(old)
    assert cache.get_pages() == ["d.com", "c.com", "b.com", "a.com"]

    #  "d.com" に再度アクセスする。
    cache.access_page("d.com", "DDD")
    # キャッシュは次のように更新される：
    #   (new)<-- "d.com", "c.com", "b.com", "a.com" -->(old)
    assert cache.get_pages() == ["d.com", "c.com", "b.com", "a.com"]

    #  "a.com" に再度アクセスする。
    cache.access_page("a.com", "AAA")
    # キャッシュは次のように更新される：
    #   (new)<-- "a.com", "d.com", "c.com", "b.com" -->(old)
    assert cache.get_pages() == ["a.com", "d.com", "c.com", "b.com"]

    cache.access_page("c.com", "CCC")
    assert cache.get_pages() == ["c.com", "a.com", "d.com", "b.com"]
    cache.access_page("a.com", "AAA")
    assert cache.get_pages() == ["a.com", "c.com", "d.com", "b.com"]
    cache.access_page("a.com", "AAA")
    assert cache.get_pages() == ["a.com", "c.com", "d.com", "b.com"]

    # "e.com" にアクセスする。
    cache.access_page("e.com", "EEE")
    # キャッシュが上限に達したので最も古いページである "b.com" を削除する。
    # キャッシュは次のように更新される：
    #   (new)<-- "e.com", "a.com", "c.com", "d.com" -->(old)
    assert cache.get_pages() == ["e.com", "a.com", "c.com", "d.com"]

    # "f.com" にアクセスする。
    cache.access_page("f.com", "FFF")
    # キャッシュが上限に達したので最も古いページである "c.com" を削除する。
    # キャッシュは次のように更新される：
    #   (new)<-- "f.com", "e.com", "a.com", "c.com" -->(old)
    assert cache.get_pages() == ["f.com", "e.com", "a.com", "c.com"]

    # "e.com" に再度アクセスする。
    cache.access_page("e.com", "EEE")
    # キャッシュは次のように更新される：
    #   (new)<-- "e.com", "f.com", "a.com", "c.com" -->(old)
    assert cache.get_pages() == ["e.com", "f.com", "a.com", "c.com"]

    # "a.com"に再度アクセスする。
    cache.access_page("a.com", "AAA")
    # キャッシュは次のように更新される：
    #   (new)<-- "a.com", "e.com", "f.com", "c.com" -->(old)
    assert cache.get_pages() == ["a.com", "e.com", "f.com", "c.com"]

    print("Tests passed!")


def performance_test():
    # キャッシュのサイズを100に設定する。
    cache = Cache(100)

    # ジップの法則（現実のWebアクセスの偏りを再現する法則）に基づいて検索クエリを生成する。
    ALPHA = 1.5
    NUM_QUERIES = 1000000
    NUM_PAGES = 1000
    ranks = range(1, NUM_PAGES + 1)
    weights = [1.0 / (r ** ALPHA) for r in ranks]
    random.seed(1)
    queries = random.choices(ranks, weights=weights, k=NUM_QUERIES)    
    for query in queries:
        cache.access_page(str(query), "")

    # キャッシュの実装が正しければ、ヒット率は約91％になる。
    print("Cache hit rate = %d %%" % (cache.get_hitrate() * 100))
    print("Performance tests passed!")


if __name__ == "__main__":
    cache_test()
    performance_test()


"""実行結果
yanagisawa.yukia@YukiAir step % /opt/homebrew/bin/python3 /Users/yanagisaway
uukiai/step/week2/homework4.py
Tests passed!
Cache hit rate = 91 %
Performance tests passed!
"""