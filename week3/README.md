# 計算機プログラムの実装解説：四則演算と括弧の処理

本プログラムは、入力された数式文字列を解析し、正しい優先順位（括弧→掛け算・割り算→足し算・引き算）で計算を行う自作の計算機です。
複雑な処理を1つの関数にまとめるのではなく、**モジュール化**を意識して設計しました。

全体の処理は、大きく以下の6つのステップに分かれています。

1. **字句解析（tokenize）:** 文字列を「トークン」に切り分ける
2. **括弧の処理（resolve_parentheses）:** スタックを用いて括弧内を先に計算する
3. **関数の処理（evaluate_function）:** absなどの関数を計算して置き換える
4. **乗除の処理（evaluate_mul_div）:** 掛け算・割り算を計算してリストを更新する
5. **加減の処理（evaluate_add_sub）:** 残った足し算・引き算を計算する
6. **全体の処理（evaluate）:** 関数を順番に呼び出す


## 1. 字句解析（Tokenize）
入力された文字列のままでは扱いづらいため、意味のあるデータの塊である「トークン（辞書型）」に変換します。ここでは計算を行わず、すべての文字や数字を分類しています。

```python
def tokenize(line):
    tokens = []
    index = 0
    while index < len(line):
        if line[index].isdigit():
            (token, index) = read_number(line, index)
        elif line[index] == '+':
            (token, index) = read_plus(line, index)
        elif line[index] == '-':
            (token, index) = read_minus(line, index)
        # コード編集部分：掛け算の処理を追加
        elif line[index] == '*':
            (token, index) = read_multiplication(line, index)
        # コード編集部分：割り算の処理を追加
        elif line[index] == '/':
            (token, index) = read_division(line, index)
        # コード編集部分：（の処理を追加
        elif line[index] == '(':
            (token, index) = read_left_parentheses(line, index)
        # コード編集部分：)の処理を追加
        elif line[index] == ')':
            (token, index) = read_right_parentheses(line, index)
        # アルファベット(関数名)の処理を追加
        elif line[index].isalpha():
            (token, index) = read_function(line, index)
        else:
            print('Invalid character found: ' + line[index])
            exit(1)
        tokens.append(token)
    return tokens
```

## 2.括弧の処理(resolve_parentheses)
括弧の処理には、後入れ先出しのデータ構造である**スタック**を使いました。
* **ポイント**
- リストの一部を計算結果（新しいトークン）に置き換えた後、リストが短くなるため、読み取り位置（index）をstart_indexに巻き戻してズレを防ぐ処理を入れています。

```python
def resolve_parentheses(tokens):
    stack=[]
    index=0
    
    while index<len(tokens):
        if tokens[index]['type']=='LPAREN':
            # '('のインデックスをスタックにメモする
            stack.append(index)
            index+=1
        
        elif tokens[index]['type']=='RPAREN':
            # 一番新しい'('の位置を取り出す
            start_index=stack.pop()
            end_index=index
            
            # '('と')'の中身のトークンだけを取り出す
            inside_tokens=tokens[start_index+1:end_index]
            
            # 取り出した中身をevaluate関数に渡して計算結果をもらう
            answer_number=evaluate(inside_tokens)
            
            # 新しいNUMBERトークンを作る
            new_token={'type':'NUMBER','number':answer_number}
            
            # 元のtokensリストの'('から')'までの部分を、new_token1つに置き換える
            tokens[start_index:end_index+1]=[new_token]
            
            # リストの長さが変わったので、indexの位置を変える
            index=start_index
        
        else:
            index+=1
    return tokens

```

## 3.関数の処理（evaluate_function）
括弧の処理が終わったリストに対し、掛け算や割り算を行う前**abs**や**in**などの関数を処理します。
* **ポイント**
- 括弧の処理が終わった直後なので、リストの中にはFUNCトークンのすぐ右に、必ず計算対象の NUMBERトークンが来ています。

```python
def evaluate_function(tokens):
    pass_tokens=[]
    index=0
    while index < len(tokens):
        if tokens[index]['type']=='FUNC':
            # 関数の名前を取得（'abs', 'int', 'round' など）
            func_name=tokens[index]['name']
            # 括弧の処理が終わっているので次のtokenは必ず数字になっている
            next_token=tokens[index + 1]
            number_value=next_token['number']
            
            # 関数名に合わせて計算を行う
            if func_name == 'abs':
                new_number = abs(number_value)
            elif func_name == 'int':
                new_number = int(number_value)
            elif func_name == 'round':
                new_number = round(number_value)
            else:
                print('Unknown function: ' + func_name)
                exit(1)
                
            # 計算済みのNUMBERトークンを新しいリストに追加
            pass_tokens.append({'type': 'NUMBER', 'number': new_number})
            
            # FUNCとNUMBERの2つ分を処理したので、indexを2つ進める
            index+=2
            
        else:
            # FUNC以外（ただの数字や＋、＊など）はそのままスルーして追加
            pass_tokens.append(tokens[index])
            index += 1
            
    return pass_tokens
```

## 4.乗除の処理（evaluate_mul_div）
括弧がなくなったリストを左から読み、*と/を優先して計算します。
* **ポイント**
- 記号を見つけたら.pop()で直前の数字を取り出し、直後の数字と計算します。その結果を新しいリスト**pass1_tokens**に追加していくことで、乗除だけが完了した新しいリストを作成しています。

```python
def evaluate_mul_div(tokens):
    pass1_tokens=[]
    index=0
    while index<len(tokens):
        # MULとDIVをひとまとめにして判定する
        if tokens[index]['type'] in ['MUL', 'DIV']:
            # 共通の処理：前後の数字を取り出す
            prev_token=pass1_tokens.pop()
            next_token=tokens[index+1]
            
            # 実際の計算部分だけ分岐させる
            if tokens[index]['type']=='MUL':
                new_number=prev_token['number']*next_token['number']
            else: # DIVの場合
                new_number=prev_token['number']/next_token['number']
                
            # 共通の処理：新しいトークンを追加してインデックスを進める
            pass1_tokens.append({'type': 'NUMBER', 'number': new_number})
            index+=2
        else:
            pass1_tokens.append(tokens[index])
            index+=1
    return pass1_tokens
```

## 5.加減の処理（evaluate_add_sub）
乗除が終わったリストに対して、最終的な足し算・引き算を行います。

```Python
def evaluate_add_sub(tokens):
    answer=0
    # 先頭にダミーの'+'を入れておく
    tokens.insert(0,{'type': 'PLUS'}) 
    index=1
    while index < len(tokens):
        if tokens[index]['type'] == 'NUMBER':
            # 1つ前の記号（PLUSかMINUS）を変数に入れておく
            operator_type=tokens[index-1]['type']
            if operator_type in ['PLUS', 'MINUS']:
                # 計算部分だけを分岐
                if operator_type=='PLUS':
                    answer+=tokens[index]['number']
                else: # MINUSの場合
                    answer-=tokens[index]['number']
            else:
                print('Invalid syntax')
                exit(1)
        index += 1
    return answer
```

## 6.evaluate関数(全体)
細かく分けた関数を、順番に呼び出します。

```Python
# 1周目は掛け算と割り算の処理、2週目に足し算と割り算の処理を行うようにする
def evaluate(tokens):
    # 括弧の処理を行う関数を呼び出して、括弧をなくしたリストを受け取る
    tokens_after_parentheses = resolve_parentheses(tokens)
    
    # 掛け算・割り算の処理をする関数から帰ってきた新しいリスト(pass1_tokens)を別の変数に受け取る
    tokens_after_mul_div=evaluate_mul_div(tokens_after_parentheses)
    
    # その新しくなったリストを今度は足し算・引き算の関数に渡す
    final_answer = evaluate_add_sub(tokens_after_mul_div)
    
    return final_answer
```





