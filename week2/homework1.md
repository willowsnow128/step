# ゼロから作るハッシュテーブル（Python実装）

## 概要
Pythonの標準機能である `dict`（辞書）や `collections` ライブラリを一切使わずに、データ構造「ハッシュテーブル」をゼロから実装したプログラムです。

目標は、データの追加・検索・削除の平均計算量を **O(1)** にすることです。
これを達成するために、以下の3つの工夫を組み込んでいます。
1. **チェイン法（連結リスト）** によるハッシュ衝突の解決
2. **ローリングハッシュの考え方** を用いたハッシュ関数の改良
3. データ量に応じた **動的なサイズ調整（リハッシュ）**

---

## 各クラス・関数の役割と実装のポイント
### 1.ハッシュ関数 (`calculate_hash`)
文字列キーから保存場所（インデックス）を決めるための数値を計算します。
* **ポイント**: 
- 文字コードを単純に足すだけでは「abc」と「cba」が同じ値になってしまう（衝突する）ため、計算のたびに**素数（31）**を掛け合わせています。
- また、計算途中で数値が巨大化して処理が重くなるのを防ぐため、競技プログラミングでもよく使われる大きな素数 **998244353** で割った余りを利用しています。

```python
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
```

### 2.データ格納用クラス (Item)
キーと値のペアを保存する「箱」の役割を果たします。
* **ポイント**:
- 単なるデータ保持だけでなく**next**という属性を持たせています。
- これにより、同じバケツに複数のデータが集中した場合でも、データを単方向連結リストにして保存できます。

```python
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
```

### 3. ハッシュテーブル本体 (HashTable) 
##### **__init__** (初期化)
データを格納する配列（バケツ）を準備します。
初期サイズは、ハッシュ値が均等に散らばりやすいよう素数である**97**を設定しています。

```python
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
```

##### **put** (追加・更新)
キーと値のペアをハッシュテーブルに保存します。
* **実装の工夫**:
1. インデックスを計算し、そのバケツの連結リストを辿って同じキーがあれば値を上書きします。
2. 同じキーがなければ、新しい**Item**を作成します。このとき、連結リストの末尾ではなく先頭に追加することで、追加処理の計算量を**O(1)**に抑えています。
3. データ数がバケツのサイズの**70%**を超えたら、検索速度の低下を防ぐために**_rehash**を呼び出してバケツを拡張します。

```python
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
            self._rehash(self.bucket_size*2+1)
        # 新規追加なのでTrueを返す
        return True
```

##### **get** (検索)
指定されたキーの値を素早く取り出します。
* **動作の流れ**:
ハッシュ関数で一発でバケツを特定し、そのバケツの中の連結リストだけを順番に探します。

```python
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
```

##### **delete** (削除)
指定されたキーのデータを削除します。
* **実装の工夫**:
単方向連結リストから要素を削除するため、1つ前の要素 (prev_item)を記憶しながらリストを辿るように実装しています。
削除後にデータ数がバケツのサイズの**30%**を下回った場合は、メモリの無駄遣いを防ぐために**_rehash**を呼び出してバケツを縮小します。

```python
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
                
                    self._rehash(new_size)
                return True
            
            # 次の要素へ進む前に、現在の要素をprev_itemとして記憶しておく
            prev_item=current_item
            current_item=current_item.next

        # 見つからなかった場合はFalseを返す
        return False
```
##### **_rehash** (テーブルサイズの動的調整)
ハッシュテーブルの性能（O(1)）を維持するための最も重要な部分です。
* **動作の流れ**:
1. 現在のデータ量に合わせて、新しいサイズのバケツ（配列）を作り直します。
2. 新しいバケツのサイズは、偏りを防ぐために常に「奇数」になるように計算しています。
3. 古いバケツに入っているすべてのデータを、新しいバケツのサイズでインデックスを再計算し、すべて引っ越しさせます。

* **ポイント**:
場所を引っ越すときに、新しい**Item**を作り直すのではなく、既存の**Item**の**next**の繋ぎ変えだけで移動させることで、処理のオーバーヘッドを最小限に抑えています。

```python
# テーブルサイズを変更し、すべての要素を再配置する
    def _rehash(self, new_bucket_size):
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
```






