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

typedef struct my_heap_t {
  //空き箱リストの1番最初の空き箱の場所をキープしておくためのポインタ
  my_metadata_t *free_head;
  //空き箱がない時にエラーが起きないように使うためのもの
  my_metadata_t dummy;
} my_heap_t;

//
// Static variables (DO NOT ADD ANOTHER STATIC VARIABLES!)
//
my_heap_t my_heap;

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
*/