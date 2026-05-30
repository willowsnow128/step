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
        else:
            print('Invalid character found: ' + line[index])
            exit(1)
        tokens.append(token)
    return tokens


# 1周目は掛け算と割り算の処理、2週目に足し算と割り算の処理を行うようにする
def evaluate(tokens):
    # 新しいリスト(1周目で更新していく)を用意する
    pass1_tokens=[]
    index=0
    while index<len(tokens):
        # 掛け算の*がきたら自分の前と後ろを掛け算して新しい数として保存する
        if tokens[index]['type']=='MUL':
            prev_token=pass1_tokens.pop()
            next_token=tokens[index+1]
            new_number=prev_token['number']*next_token['number']
            pass1_tokens.append({'type':'NUMBER', 'number':new_number})
            # 次の数字も処理済みなので2個飛ばす
            index+=2
        
        # 割り算の/がきたら自分の前と後ろを割り算して新しい数として保存する
        elif tokens[index]['type']=='DIV':
            prev_token=pass1_tokens.pop()
            next_token=tokens[index+1]
            new_number=prev_token['number']/next_token['number']
            pass1_tokens.append({'type': 'NUMBER','number': new_number})
            # 次の数字も処理済みなので2個飛ばす
            index+=2
        
        else:
            # それ以外（数字、＋、-）はそのまま新しいリストに入れる
            pass1_tokens.append(tokens[index])
            index+=1
    
    answer = 0
    pass1_tokens.insert(0, {'type': 'PLUS'}) # Insert a dummy '+' token
    index = 1
    while index < len(pass1_tokens):
        if pass1_tokens[index]['type'] == 'NUMBER':
            if pass1_tokens[index - 1]['type'] == 'PLUS':
                answer += pass1_tokens[index]['number']
            elif pass1_tokens[index - 1]['type'] == 'MINUS':
                answer -= pass1_tokens[index]['number']
            else:
                print('Invalid syntax')
                exit(1)
        index += 1
    return answer


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
    
    # 0がある、マイナスになる、割り切れない
    test("0+5")
    test("5*0")
    test("0/3")
    test("3-5")  
    test("10/3")
    
    
    
    print("==== Test finished! ====\n")

run_test()

while True:
    print('> ', end="")
    line = input()
    tokens = tokenize(line)
    answer = evaluate(tokens)
    print("answer = %f\n" % answer)