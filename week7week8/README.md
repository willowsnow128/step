# Malloc Challenge!
### First-fit方式のメモリ割り当て（malloc）をBest-fit方式へと改良し、メモリの利用効率を向上させる実装を行いました。

## 構造体の定義
- メモリを管理するための基礎となるデータ構造です。各空き領域の先頭に付与する「メタデータ（荷札）」と、空き領域のリスト全体を管理する「ヒープ（管理センター）」を定義しています。
- 空き領域はnextポインタを用いた単方向リストとして数珠つなぎで管理されます。my_heap.dummyを番兵として置くことで、リストが空の際の例外処理を省いています。
```c
//
// Interfaces to get memory pages from OS
//

void *mmap_from_system(size_t size);
void munmap_to_system(void *ptr, size_t size);

//
// Struct definitions
//

typedef struct my_metadata_t {
  //使える空き箱スペース
  size_t size;
  //次の空き箱がある場所
  struct my_metadata_t *next;
} my_metadata_t;

typedef struct my_heap_t {
  //空き箱リストの1番最初の空き箱の場所をキープしておくためのポインタ
  my_metadata_t *free_head;
  //空き箱がない時にエラーが起きないように使うためのもの
  my_metadata_t dummy;
} my_heap_t;
```
## ヘルパー関数(リストの操作)
- my_malloc で最適な領域を見つけた際の切り離しや、my_free で返却された領域をリストに戻す際に、これらの関数を呼び出してポインタを安全に繋ぎ変えます。

```c

//
// Helper functions (feel free to add/remove/edit!)
//

//使い終わった空き箱（metadata）を、空き箱リストの一番先頭（先頭ノード）に追加する関数
void my_add_to_free_list(my_metadata_t *metadata) {
  assert(!metadata->next);
  //追加する空き箱の next（次の住所）を、「現在のリストの一番最初の箱」にする
  metadata->next = my_heap.free_head;
  my_heap.free_head = metadata;
}

void my_remove_from_free_list(my_metadata_t *metadata, my_metadata_t *prev) {
  //もし取り出したい箱の前に箱がすでにある場合
  if (prev) {
    prev->next = metadata->next;
  } else { //ない場合
    my_heap.free_head = metadata->next;
  }
  //今の自分のデータと次のデータの関係をなくして切り離す
  metadata->next = NULL;
}
//
// Interfaces of malloc (DO NOT RENAME FOLLOWING FUNCTIONS!)
//

// This is called at the beginning of each challenge.
void my_initialize() {
  my_heap.free_head = &my_heap.dummy;
  my_heap.dummy.size = 0;
  my_heap.dummy.next = NULL;
}
```
## メイン実装（my_malloc）
- 初期実装のFirst-fit（最初に見つかった領域を即採用する方式）から、空きリストを全探索して最も要求サイズに近い領域を探すBest-fit方式へとアルゴリズムを変更しました。

#### 実装のポイント
* 探索ループの条件をwhile(current)とし、リストの終端（NULL）に到達するまで探索を継続するようにしました。
* 条件を満たす空き領域が見つかるたびに、現在の暫定ベスト（best_metadata->size）とサイズを比較し、より小さい（ぴったりな）箱を記録し続けます。
* この変更により、小さなデータが不必要に巨大な空き箱を消費してしまうのを防ぎ、メモリの利用効率を向上させることができました！
```c
// この my_malloc()は、プログラム内で新しいデータ用のメモリが要求されるたびに呼び出される
// 引数で渡される size（欲しいバイト数）は、必ず8の倍数に調整されており、8バイトから4000バイトの間であることが保証されている
// 指定された2つの関数以外、C言語の標準ライブラリ関数（他のmallocなど）を使ってはいけない。
/* 最初にあったコード
while (metadata && metadata->size < size) {
    prev = metadata;
    metadata = metadata->next;
  }
これだと、先に来た小さいデータが大きい箱を埋めてしまうことになる！
*/
void *my_malloc(size_t size) {
  my_metadata_t *metadata = my_heap.free_head;
  my_metadata_t *prev = NULL;
  // Best-fit: 空きリスト全体を調べて、要求サイズを満たす最小の空き領域を探す
  my_metadata_t *best_metadata = NULL;
  my_metadata_t *best_prev = NULL;
  
  my_metadata_t *current = my_heap.free_head;
  my_metadata_t *current_prev = NULL;

  //リストの先頭からNULLになるまで全部見る
  while (current) {
    // 要求されたサイズ以上の空き領域が見つかった場合
    if (current->size >= size) {
      // まだ候補が見つかっていない、または今まで見つけた候補よりもさらにぴったりな場合
      if (!best_metadata || current->size < best_metadata->size) {
        best_metadata = current;
        best_prev = current_prev;
      }
    }
    // 次の空き領域へ進む
    current_prev = current;
    current = current->next;
  }

  // 見つかったベストな空き領域を代入
  metadata = best_metadata;
  prev = best_prev;
```

## メモリ領域の新規確保と分割処理
- リスト内に適当な空き箱がなかった場合のシステムへの要求と、見つかった箱が大きすぎた場合の分割処理です。

```c
  if (!metadata) {
    // There was no free slot available. We need to request a new memory region
    // from the system by calling mmap_from_system().
    //
    //     | metadata | free slot |
    //     ^
    //     metadata
    //     <---------------------->
    //            buffer_size
    size_t buffer_size = 4096;
    my_metadata_t *metadata = (my_metadata_t *)mmap_from_system(buffer_size);
    metadata->size = buffer_size - sizeof(my_metadata_t);
    metadata->next = NULL;
    // Add the memory region to the free list.
    my_add_to_free_list(metadata);
    // Now, try my_malloc() again. This should succeed.
    return my_malloc(size);
  }

  // |ptr| is the beginning of the allocated object.
  //
  // ... | metadata | object | ...
  //     ^          ^
  //     metadata   ptr
  //metadataの後ろから実際に中身が入る場所
  void *ptr = metadata + 1;
  size_t remaining_size = metadata->size - size;
  // Remove the free slot from the free list.
  my_remove_from_free_list(metadata, prev);
  
  //余ったサイズがmy_matadata_tが入るくらい大きいか否か
  if (remaining_size > sizeof(my_metadata_t)) {
    // Shrink the metadata for the allocated object
    // to separate the rest of the region corresponding to remaining_size.
    // If the remaining_size is not large enough to make a new metadata,
    // this code path will not be taken and the region will be managed
    // as a part of the allocated object.
    metadata->size = size;
    // Create a new metadata for the remaining free slot.
    //
    // ... | metadata | object | metadata | free slot | ...
    //     ^          ^        ^
    //     metadata   ptr      new_metadata
    //                 <------><---------------------->
    //                   size       remaining size
    my_metadata_t *new_metadata = (my_metadata_t *)((char *)ptr + size);
    new_metadata->size = remaining_size - sizeof(my_metadata_t);
    new_metadata->next = NULL;
    // Add the remaining free slot to the free list.
    my_add_to_free_list(new_metadata);
  }
  return ptr;
}
```

## メモリの解放
- 使い終わったメモリをリストに返却します。
```c
// This is called every time an object is freed.  You are not allowed to
// use any library functions other than mmap_from_system / munmap_to_system.
void my_free(void *ptr) {
  // Look up the metadata. The metadata is placed just prior to the object.
  //
  // ... | metadata | object | ...
  //     ^          ^
  //     metadata   ptr
  my_metadata_t *metadata = (my_metadata_t *)ptr - 1;
  // Add the free slot to the free list.
  my_add_to_free_list(metadata);
}
```
## 結果
yanagisawa.yukia@YukiAir malloc % make run
./malloc_challenge.bin
Welcome to the malloc challenge!
size_of(uint8_t *) = 8
size_of(size_t) = 8
Running tests...
Finished!

====================================================
Challenge #1    |   simple_malloc =>       my_malloc
--------------- + --------------- => ---------------
       Time [ms]|               6 =>            1000
Utilization [%] |              70 =>              70
====================================================
Challenge #2    |   simple_malloc =>       my_malloc
--------------- + --------------- => ---------------
       Time [ms]|               4 =>             651
Utilization [%] |              40 =>              40
====================================================
Challenge #3    |   simple_malloc =>       my_malloc
--------------- + --------------- => ---------------
       Time [ms]|              79 =>             786
Utilization [%] |               9 =>              51
====================================================
Challenge #4    |   simple_malloc =>       my_malloc
--------------- + --------------- => ---------------
       Time [ms]|           17851 =>            6890
Utilization [%] |              15 =>              72
====================================================
Challenge #5    |   simple_malloc =>       my_malloc
--------------- + --------------- => ---------------
       Time [ms]|           11552 =>            4060
Utilization [%] |              15 =>              75

Challenge done!
Please copy & paste the following data in the score sheet!
1000,70,651,40,786,51,6890,72,4060,75,






