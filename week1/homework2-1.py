scores=[1,3,2,2,1,3,3,1,1,4,4,2,2,1,1,3,4,1,1,1,2,3,3,4,3,4]
def find_best_anagram(random_word,new_dictionary):
    random_count=[0]*26
    for c in random_word:
        index=ord(c)-ord('a')
        random_count[index]+=1
    best_word=""
    max_score=-1
    
    for word,word_count,word_score in new_dictionary:
        can_make=True
        for i in range(26):
            if word_count[i]>random_count[i]:
                can_make=False
                break
        if can_make:
            if word_score>max_score:
                max_score=word_score
                best_word=word
    return best_word,max_score

new_dictionary=[]
with open('words.txt','r',encoding='utf-8') as dict_file:
    for line in dict_file:
        word=line.strip()
        if word!="":
            word_count=[0]*26
            word_score=0
            for c in word:
                index=ord(c)-ord('a')
                word_count[index]+=1
                word_score+=scores[index]
            new_dictionary.append((word,word_count,word_score))

file_pairs=[
    ("small.txt","output_small.txt"),
    ("large.txt","output_large.txt")
]

for input_name,output_name in file_pairs:
    total_score=0
    best_words=[]
    with open(input_name,'r',encoding='utf-8') as input_file:
        for line in input_file:
            random_word=line.strip()
            if random_word=="":
                continue
            result_word,result_score=find_best_anagram(random_word,new_dictionary)
            best_words.append(result_word)
            if result_score>0:
                total_score+=result_score
    
    with open(output_name,'w',encoding='utf-8') as output_file:
        for word in best_words:
            output_file.write(word+'\n')
            
    print(f"{output_name} に単語のリストを保存しました。")
    print(f"{input_name} の総合計スコアは: {total_score} 点です。\n")
