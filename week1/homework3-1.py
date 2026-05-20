scores=[1,3,2,2,1,3,3,1,1,4,4,2,2,1,1,3,4,1,1,1,2,3,3,4,3,4]
#辞書の読み込みと前計算
processed_dictionary=[]
with open('words.txt','r',encoding='utf-8') as dict_file:
    for line in dict_file:
        word=line.strip()
        if not word:
            continue
        
        word_count=[0]*26
        word_score=0
        for c in word:
            index=ord(c)-ord('a')
            word_count[index]+=1
            word_score+=scores[index]

        char_reqs=[(i,word_count[i]) for i in range(26) if word_count[i]>0]
        
        processed_dictionary.append((word,char_reqs,word_score))
#スコアが高い順に辞書全体を並び替える
processed_dictionary.sort(key=lambda x:x[2], reverse=True)

file_pairs = [
    ("small.txt", "small_answer_hw3-1.txt"),
    ("large.txt", "large_answer_hw3-1.txt")
]

for input_name, output_name in file_pairs:
    print(f"{input_name} の処理を開始")
    
    with open(input_name,'r',encoding='utf-8') as input_file, \
         open(output_name,'w',encoding='utf-8') as output_file:
             
        for line in input_file:
            query=line.strip()
            if not query:
                continue
            avail=[0]*26
            for c in query:
                avail[ord(c)-ord('a')]+=1
                
            best_words = []
            #スコアが高い順に単語を試していく
            for word,char_reqs,word_score in processed_dictionary:
                while True:
                    can_make=True
                    #必要な文字だけ確認
                    for idx, req_count in char_reqs:
                        if avail[idx]<req_count:
                            can_make=False
                            break
                            
                    if not can_make:
                        break 
                    #作れた場合は手持ちの文字から消費
                    for idx,req_count in char_reqs:
                        avail[idx]-=req_count
                        
                    best_words.append(word)
            output_file.write(" ".join(best_words) + "\n")
            
    print(f"{output_name} に結果を保存しました！\n")
    
"""結果
yanagisawa.yukia@YukiAir week1 % python3 score_checker.py small.txt small_answer_hw3-1.txt
You answer is correct! Your score is 200.
yanagisawa.yukia@YukiAir week1 % python3 score_checker.py large.txt large_answer_hw3-1.txt
You answer is correct! Your score is 557146.
"""