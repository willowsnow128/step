# ゼロから作るキャッシュ（Python実装）

## 概要
Pythonの標準機能である `dict`（辞書）や `collections` ライブラリを一切使っていない、最も最近アクセスされた要素を保存し、容量を超えたら一番古い要素を削除するプログラムです。

目標は、データの検索・追加・古いデータの削除のすべての操作をO(1)で実現することです。
これを達成するために、以下の2つの工夫を組み込んでいます。
1. **双方向リスト**による「データへのアクセス順」の管理
2. 課題1で実装の**ハッシュテーブル**によるO(1)での高速なデータ検索
---

## 各クラス・関数の役割と実装のポイント
### データ格納用クラス (Page)
双方向リストの1つ1つの「箱（ノード）」の役割を果たします。
* **ポイント**: 
- 単方向ではなく、前後の両方に戻れるように**prev**と**next**の2つの属性を持たせています。これにより、リストの途中にいるデータでも、先頭から探すことなく自分の前後の繋がりをO(1)で付け替えることができます。

```python
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
```


### 2. キャッシュ本体 (Cache) 
#### **__init__** (初期化)
検索を担当するハッシュテーブルと、順番を記憶する双方向リストの「先頭（一番新しい）」と「末尾（一番古い）」の目印を用意しています。

```python
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
```

#### **remove_page** (削除)
#### **add_front** (追加)
* **実装の工夫**:
- 自分を削除する処理と先頭に追加する処理において、自分がheadやtailだった場合の例外処理も行います。

```python
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
```

#### **access_page** (ページの検索・追加・更新)
キャッシュ機能のメイン部分です。
* **動作の流れ**:
- 直接のリンクの保存: ハッシュテーブルには文字列ではなく、Pageオブジェクトそのもの（メモリ上のリンク）を保存しています。これにより、検索がヒットするとリスト内の場所を直接掴めるため、探す手間が省けます。
- 削除の高速化: キャッシュの容量が上限を超えた場合、ハッシュテーブルのサイズとlimitを比較します。何を消すか探す必要はなく、常にself.tailが指している「一番古いページ」を O(1) で特定して削除します。

```python
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
```

#### **get_pages** (キャッシュ一覧の取得)
現在キャッシュに入っているURLを、新しい順にリストにして返します。
* **動作の流れ**:
ハッシュテーブルは使わず、双方向リストの**head**から出発し、**next**をたどって**tail**まで順番に進むことで、簡単に最新順のリストを作成できます。

```python
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
```
