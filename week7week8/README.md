# Malloc Challenge!
### First-fit方式のメモリ割り当て（malloc）をBest-fit方式へと改良し、メモリの利用効率を向上させました。さらに「Freelist Bin（複数の空き箱リスト）」を実装することで、Best-fitの弱点であった探索時間の増加（Timeの悪化）を劇的に改善しました。

## 構造体の定義
- メモリを管理するための基礎となるデータ構造です。
- 単一のリストではなく、サイズごとに整理された複数のリスト（Bin）で空き領域を管理するため、管理センターである my_heap_t の受付を配列（4つの窓口）に変更しています。

```c
//
// Interfaces to get memory pages from OS
//
void *mmap_from_system(size_t size);
void munmap_to_system(void *ptr, size_t size);

// Binの数を定義
#define NUM_BINS 4

//
// Struct definitions
//
typedef struct my_metadata_t {
  // 使える空き箱スペース
  size_t size;
  // 次の空き箱がある場所
  struct my_metadata_t *next;
} my_metadata_t;

typedef struct my_heap_t {
  // 管理センターの受付をBinの数だけ配列にする
  my_metadata_t *free_heads[NUM_BINS];
  my_metadata_t dummies[NUM_BINS];
} my_heap_t;

//
// Static variables (DO NOT ADD ANOTHER STATIC VARIABLES!)
//
my_heap_t my_heap;
```
## ヘルパー関数(リストの操作)
- 新たに get_bin_index を追加し、領域のサイズから適切なBinの番号（0〜3）を自動計算できるようにしました。
- my_add_to_free_list や my_remove_from_free_list では、この関数を活用することで、手動で条件分岐を書かなくても「適切なサイズの窓口」へ自動で振り分けられるように工夫しています。

```c
// 新規追加：サイズから適切なBinの番号（0〜3）を計算する関数
int get_bin_index(size_t size) {
  if (size <= 64) return 0;
  if (size <= 256) return 1;
  if (size <= 1024) return 2;
  return 3;
}

//
// Helper functions (feel free to add/remove/edit!)
//

void my_add_to_free_list(my_metadata_t *metadata) {
  assert(!metadata->next);
  // サイズから適切なBinを見つける
  int bin_index = get_bin_index(metadata->size);
  
  // 見つけたBinの先頭に追加する
  metadata->next = my_heap.free_heads[bin_index];
  my_heap.free_heads[bin_index] = metadata;
}

void my_remove_from_free_list(my_metadata_t *metadata, my_metadata_t *prev) {
  if (prev) {
    prev->next = metadata->next;
  } else {
    // 先頭の要素を削除する場合は、どのBinの先頭かをサイズから判定する
    int bin_index = get_bin_index(metadata->size);
    my_heap.free_heads[bin_index] = metadata->next;
  }
  metadata->next = NULL;
}

// This is called at the beginning of each challenge.
void my_initialize() {
  // 4つ分のBinのダミーと先頭ポインタを初期化する
  for (int i = 0; i < NUM_BINS; i++) {
    my_heap.free_heads[i] = &my_heap.dummies[i];
    my_heap.dummies[i].size = 0;
    my_heap.dummies[i].next = NULL;
  }
}
```
## メイン実装（my_malloc）
- 要求されたサイズに応じて「一番小さな適切なBin」から探索をスタートし、見つからなければ「1つ大きなサイズのBin」へと探索を進める構造に変更しました。

#### 実装のポイント
* 外側に for ループを配置してBinを切り替え、内側の while ループでそのBinの中のBest-fitを探す2段構成にしています。
* 条件を満たす空き領域が見つかった瞬間に break で探索を打ち切るため、すべてのメモリを全探索していた前回の実装に比べ、実行時間を圧倒的に短縮できました。
```c
void *my_malloc(size_t size) {
  my_metadata_t *metadata = NULL;
  my_metadata_t *prev = NULL;
  my_metadata_t *best_metadata = NULL;
  my_metadata_t *best_prev = NULL;

  // 1. 要求サイズが入る可能性のある一番小さなBinの番号を計算
  int start_bin = get_bin_index(size);

  // 2. start_bin から順番により大きなBinを探していく
  for (int i = start_bin; i < NUM_BINS; i++) {
    my_metadata_t *current = my_heap.free_heads[i];
    my_metadata_t *current_prev = NULL;

    // 現在のBinの中で Best-fit を探す
    while (current) {
      if (current->size >= size) {
        if (!best_metadata || current->size < best_metadata->size) {
          best_metadata = current;
          best_prev = current_prev;
        }
      }
      current_prev = current;
      current = current->next;
    }

    // もし現在のBinで使える箱が見つかったら、これ以上大きなBinを探す必要はないのでループを抜ける
    if (best_metadata) {
      break;
    }
  }

  // 見つかったベストな空き領域を代入
  metadata = best_metadata;
  prev = best_prev;
```

## メモリ領域の新規確保と分割処理
- 新規確保したページや、大きすぎる箱を分割して余った領域も、ヘルパー関数を通じて自動的に適切なサイズのBinに収納されます。

```c
  if (!metadata) {
    size_t buffer_size = 4096;
    my_metadata_t *new_metadata = (my_metadata_t *)mmap_from_system(buffer_size);
    new_metadata->size = buffer_size - sizeof(my_metadata_t);
    new_metadata->next = NULL;
    // my_add_to_free_listが自動で一番大きなサイズのBin(インデックス3)に入れてくれます
    my_add_to_free_list(new_metadata);
    return my_malloc(size);
  }

  void *ptr = metadata + 1;
  size_t remaining_size = metadata->size - size;
  my_remove_from_free_list(metadata, prev);
  
  if (remaining_size > sizeof(my_metadata_t)) {
    metadata->size = size;
    my_metadata_t *new_metadata = (my_metadata_t *)((char *)ptr + size);
    new_metadata->size = remaining_size - sizeof(my_metadata_t);
    new_metadata->next = NULL;
    // 余った箱も、新しいサイズに応じた適切なBinに自動で振り分けられます
    my_add_to_free_list(new_metadata);
  }
  return ptr;
}
```

## メモリの解放
- 使い終わったメモリをリストに返却します。ここでもサイズに応じて自動で正しいBinに戻されます。
```c
void my_free(void *ptr) {
  my_metadata_t *metadata = (my_metadata_t *)ptr - 1;
  // ここでもサイズに応じて正しいBinに返却されます
  my_add_to_free_list(metadata);
}
```
## 結果と考察
- Freelist Binを実装した結果、Best-fitのみの実装時に発生していた実行時間の増加を解消することができました。特に要素数が多くなるChallenge #4では、Time が 6890ms から655msへと約10分の1に短縮されており、データ構造の工夫による計算量削減の効果が確認できました。
```c
best-fitのみの結果
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
```c
```c
freelist binを追加した時のスコア
====================================================
Challenge #1    |   simple_malloc =>       my_malloc
--------------- + --------------- => ---------------
       Time [ms]|               9 =>             844
Utilization [%] |              70 =>              70
====================================================
Challenge #2    |   simple_malloc =>       my_malloc
--------------- + --------------- => ---------------
       Time [ms]|               4 =>             655
Utilization [%] |              40 =>              40
====================================================
Challenge #3    |   simple_malloc =>       my_malloc
--------------- + --------------- => ---------------
       Time [ms]|              78 =>             712
Utilization [%] |               9 =>              51
====================================================
Challenge #4    |   simple_malloc =>       my_malloc
--------------- + --------------- => ---------------
       Time [ms]|           17911 =>             655
Utilization [%] |              15 =>              72
====================================================
Challenge #5    |   simple_malloc =>       my_malloc
--------------- + --------------- => ---------------
       Time [ms]|           11596 =>             695
Utilization [%] |              15 =>              75

Challenge done!
Please copy & paste the following data in the score sheet!
844,70,655,40,712,51,655,72,695,75,
```






