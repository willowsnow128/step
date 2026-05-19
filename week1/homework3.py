scores=[1,3,2,2,1,3,3,1,1,4,4,2,2,1,1,3,4,1,1,1,2,3,3,4,3,4]
def solve_multiple_anagrams(random_word,processed_dictionary):
    random_count=[0]*26
    for c in random_word:
        random_count[ord(c)-ord('a')]+=1
    candidates=[]
    for word,w_count,w_score in processed_dictionary:
        can_make = True
        for i in range(26):
            if w_count[i]>random_count[i]:
                can_make=False
                break
        if can_make:
            candidates.append((word, w_count, w_score))
    best_words=[]
    max_score=-1
    
    def dfs(available_count,current_score,current_words,start_index):
        nonlocal best_words,max_score
        if current_score>max_score:
            max_score=current_score
            best_words=list(current_words)
        for i in range(start_index,len(candidates)):
            word,w_count,w_score=candidates[i]
            can_make=True
            for j in range(26):
                if w_count[j]>available_count[j]:
                    can_make=False
                    break
            if can_make:
                next_count=[available_count[j]-w_count[j] for j in range(26)]
                current_words.append(word)
                
                dfs(next_count,current_score+w_score,current_words,i)
                current_words.pop()
    dfs(random_count,0,[],0)
    result_str=" ".join(best_words)
    return result_str,max_score

processed_dictionary=[]
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
            processed_dictionary.append((word,word_count,word_score))

file_pairs=[
    ("small.txt", "small_answer_hw3.txt"),
    ("large.txt", "large_answer_hw3.txt")
]
                
for input_name,output_name in file_pairs:
    print(f"{input_name} の処理を開始")
    best_answers = [] 
    with open(input_name, 'r', encoding='utf-8') as input_file:
        for line in input_file:
            random_word=line.strip()
            if random_word=="":
                continue     
            result_str, result_score=solve_multiple_anagrams(random_word, processed_dictionary)
            best_answers.append(result_str)   
    with open(output_name,'w',encoding='utf-8') as output_file:
        for answer in best_answers:
            output_file.write(answer+'\n')
        
    print(f"{output_name} に結果を保存しました！\n")