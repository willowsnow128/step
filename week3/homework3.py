# 掛け算割り算を先に計算するところをモジュール化して独立させたコード
def read_number(line, index):
    number = 0
    while index < len(line) and line[index].isdigit():
        number = number * 10 + int(line[index])
        index += 1
    if index < len(line) and line[index] == '.':
        index += 1
        decimal = 0.1
        while index < len(line) and line[index].isdigit():
            number += int(line[index]) * decimal
            decimal /= 10
            index += 1
    token = {'type': 'NUMBER', 'number': number}
    return token, index


def read_plus(line, index):
    token = {'type': 'PLUS'}
    return token, index + 1


def read_minus(line, index):
    token = {'type': 'MINUS'}
    return token, index + 1

# コード編集部分：掛け算(*の処理を追加)
def read_multiplication(line, index):
    token = {'type': 'MUL'}
    return token, index+1

# コード編集部分：割り算(/の処理を追加)
def read_division(line, index):
    token = {'type': 'DIV'}
    return token, index+1

# コード編集部分：（の処理を追加
def read_left_parentheses(line, index):
    token = {'type': 'LPAREN'}
    return token, index+1

# コード編集部分：)の処理を追加
def read_right_parentheses(line, index):
    token = {'type': 'RPAREN'}
    return token, index+1



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
        else:
            print('Invalid character found: ' + line[index])
            exit(1)
        tokens.append(token)
    return tokens

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


def evaluate_mul_div(tokens):
    pass1_tokens=[]
    index=0
    while index<len(tokens):
        # 1周目は掛け算と割り算の処理を行う
        # 掛け算の処理
        if tokens[index]['type']=='MUL':
            prev_token=pass1_tokens.pop()
            next_token=tokens[index+1]
            new_number=prev_token['number']*next_token['number']
            pass1_tokens.append({'type':'NUMBER','number':new_number})
            # 次の数字も処理済みなので2個飛ばす
            index+=2
        # 割り算の処理
        elif tokens[index]['type']=='DIV':
            prev_token=pass1_tokens.pop()
            next_token=tokens[index+1]
            new_number=prev_token['number']/next_token['number']
            pass1_tokens.append({'type':'NUMBER','number':new_number})
            # 次の数字も処理済みなので2個飛ばす
            index+=2
    
        else:
            pass1_tokens.append(tokens[index])
            index+=1
    return pass1_tokens
            
            
def evaluate_add_sub(tokens):
    answer=0
    # 先頭にダミーの'+'を入れておく
    tokens.insert(0,{'type': 'PLUS'}) 
    index=1
    while index<len(tokens):
        if tokens[index]['type']=='NUMBER':
            if tokens[index-1]['type']=='PLUS':
                answer+=tokens[index]['number']
            elif tokens[index-1]['type']=='MINUS':
                answer-=tokens[index]['number']
            else:
                print('Invalid syntax')
                exit(1)
        index+=1
    return answer
            
    
# 1周目は掛け算と割り算の処理、2週目に足し算と割り算の処理を行うようにする
def evaluate(tokens):
    # 括弧の処理を行う関数を呼び出して、括弧をなくしたリストを受け取る
    tokens_after_parentheses = resolve_parentheses(tokens)
    
    # 掛け算・割り算の処理をする関数から帰ってきた新しいリスト(pass1_tokens)を別の変数に受け取る
    tokens_after_mul_div=evaluate_mul_div(tokens_after_parentheses)
    
    # その新しくなったリストを今度は足し算・引き算の関数に渡す
    final_answer = evaluate_add_sub(tokens_after_mul_div)
    
    return final_answer


def test(line):
    tokens = tokenize(line)
    actual_answer = evaluate(tokens)
    expected_answer = eval(line)
    if abs(actual_answer - expected_answer) < 1e-8:
        print("PASS! (%s = %f)" % (line, expected_answer))
    else:
        print("FAIL! (%s should be %f but was %f)" % (line, expected_answer, actual_answer))


# Add more tests to this function :)
def run_test():
    print("==== Test started! ====")
    test("1+2")
    test("1.0+2.1-3")
    # homework2：テストケースを網羅する！
    # 数字単独
    test("1")
    test("1.5")
    
    # 基本の四則演算
    test("1+2")
    test("5-3")
    test("3*4")
    test("10/2")
    
    # 小数の組み合わせ
    test("1.0+2")
    test("1+2.0")
    test("1.0+2.0")
    test("2.5*2")
    test("5.5/2.2")
    
    # 四則演算の順序確認
    test("2+3*4")  
    test("10-8/2") 
    test("3*4+2")  
    test("6/2-1")
    test("10-3-2") 
    test("10/2*3")
    
    # 長い式
    test("1.5+2.5*4-6/2")
    
    # homework3-括弧がある計算
    # 括弧の四則演算
    test("(1+2)")
    test("(1+2)*3")
    test("2*(3+4)")
    test("10/(2+3)")
    
    # 課題の例
    test("(3.0+4*(2-1))/5")
    
    # 括弧がたくさんある
    test("((1+2)*3+4)*5")
    test("10-((2+3)*2)")
    test("(1+2)*(3+4)")
    
    print("==== Test finished! ====\n")

run_test()

while True:
    print('> ', end="")
    line = input()
    tokens = tokenize(line)
    answer = evaluate(tokens)
    print("answer = %f\n" % answer)