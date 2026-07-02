//
// >>>> malloc challenge! <<<<
//
// Your task is to improve utilization and speed of the following malloc
// implementation.
// Initial implementation is the same as the one implemented in simple_malloc.c.
// For the detailed explanation, please refer to simple_malloc.c.

#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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

#define NUM_BINS 4

typedef struct my_heap_t {
  // 管理センターの受付をBinの数（4つ）だけ配列にする
  my_metadata_t *free_heads[NUM_BINS];
  my_metadata_t dummies[NUM_BINS];
} my_heap_t;
//
// Static variables (DO NOT ADD ANOTHER STATIC VARIABLES!)
//
my_heap_t my_heap;

// サイズから適切なBinの番号（0〜3）を計算する関数
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

//
// Interfaces of malloc (DO NOT RENAME FOLLOWING FUNCTIONS!)
//

// This is called at the beginning of each challenge.
void my_initialize() {
  // 4つ分のBinのダミーと先頭ポインタを初期化する
  for (int i = 0; i < NUM_BINS; i++) {
    my_heap.free_heads[i] = &my_heap.dummies[i];
    my_heap.dummies[i].size = 0;
    my_heap.dummies[i].next = NULL;
  }
}
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
  my_metadata_t *metadata = NULL;
  my_metadata_t *prev = NULL;
  my_metadata_t *best_metadata = NULL;
  my_metadata_t *best_prev = NULL;

  // 要求サイズが入る可能性のある一番小さなBinの番号を計算
  int start_bin = get_bin_index(size);

  // start_binから順番により大きなBinを探していく
  for (int i = start_bin; i < NUM_BINS; i++) {
    my_metadata_t *current = my_heap.free_heads[i];
    my_metadata_t *current_prev = NULL;

    // 現在のBinの中でBest-fitを探す
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

// This is called at the end of each challenge.
void my_finalize() {
  // Nothing is here for now.
  // feel free to add something if you want!
}

void test() {
  // Implement here!
  assert(1 == 1); /* 1 is 1. That's always true! (You can remove this.) */
}

/*
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
*/