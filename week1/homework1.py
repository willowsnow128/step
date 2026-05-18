import string
def better_solution(random_word,dictionary):
    sorted_random_word="".join(sorted(random_word))
    new_dictionary=[]
    for word in dictionary:
        sorted_word="".join(sorted(word))
        new_dictionary.append((sorted_word,word))
    new_dictionary.sort()
    anagrams=[]
    target=(sorted_random_word, "")
    
    left=0
    right=len(new_dictionary)
    while left<right:
        mid=(left+right)//2
        if new_dictionary[mid]<target:
            left=mid+1
        else:
            right=mid
    index=left
    
    while (index<len(new_dictionary) and new_dictionary[index][0]==sorted_random_word):
        if new_dictionary[index][1]!=random_word:
            anagrams.append(new_dictionary[index][1])
        index+=1
    return anagrams

dictionary = []
with open('words.txt','r',encoding='utf-8') as file:
    for line in file:
        word = line.strip()
        if word != "":
            dictionary.append(word)

random_word = input("アナグラムを探したい英単語を入力してください: ")

result = better_solution(random_word, dictionary)

if len(result) == 0:
    print("アナグラムは見つかりませんでした!")
else:
    for ans in result:
        print(ans)
        
        
"""実行結果
yanagisawa.yukia@YukiAir week1 % python3 homework1.py
アナグラムを探したい英単語を入力してください: tea
ate
eat
eta
tae
yanagisawa.yukia@YukiAir week1 % python3 homework1.py
アナグラムを探したい英単語を入力してください: xyz
アナグラムは見つかりませんでした。"""