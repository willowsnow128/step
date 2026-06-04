#include <bits/stdc++.h>
using namespace std;

// トークンを表す構造体（Pythonの辞書型の代わり）
struct Token {
    string type;
    double number = 0.0;
    string name = "";
};

// 関数のプロトタイプ宣言（再帰呼び出しのため）
double evaluate(vector<Token> tokens);

// 字句解析（Tokenize）用関数
void read_number(const string& line, int& index, Token& token) {
    double number = 0;
    while (index < line.length() && isdigit(line[index])) {
        number = number * 10 + (line[index] - '0');
        index++;
    }
    if (index < line.length() && line[index] == '.') {
        index++;
        double decimal = 0.1;
        while (index < line.length() && isdigit(line[index])) {
            number += (line[index] - '0') * decimal;
            decimal /= 10;
            index++;
        }
    }
    token.type = "NUMBER";
    token.number = number;
}

void read_function(const string& line, int& index, Token& token) {
    string name = "";
    while (index < line.length() && isalpha(line[index])) {
        name += line[index];
        index++;
    }
    token.type = "FUNC";
    token.name = name;
}

vector<Token> tokenize(const string& line) {
    vector<Token> tokens;
    int index = 0;
    while (index < line.length()) {
        Token token;
        if (isdigit(line[index])) {
            read_number(line, index, token);
        } else if (line[index] == '+') {
            token.type = "PLUS";
            index++;
        } else if (line[index] == '-') {
            token.type = "MINUS";
            index++;
        } else if (line[index] == '*') {
            token.type = "MUL";
            index++;
        } else if (line[index] == '/') {
            token.type = "DIV";
            index++;
        } else if (line[index] == '(') {
            token.type = "LPAREN";
            index++;
        } else if (line[index] == ')') {
            token.type = "RPAREN";
            index++;
        } else if (isalpha(line[index])) {
            read_function(line, index, token);
        } else {
            cout << "Invalid character found: " << line[index] << endl;
            exit(1);
        }
        tokens.push_back(token);
    }
    return tokens;
}


vector<Token> resolve_parentheses(vector<Token> tokens) {
    vector<int> stack;
    int index = 0;
    
    while (index < tokens.size()) {
        if (tokens[index].type == "LPAREN") {
            stack.push_back(index);
            index++;
        } else if (tokens[index].type == "RPAREN") {
            int start_index = stack.back();
            stack.pop_back();
            int end_index = index;
            
            // '('と')'の中身を切り出す
            vector<Token> inside_tokens(tokens.begin() + start_index + 1, tokens.begin() + end_index);
            
            // 取り出した中身をevaluate関数に渡して計算結果をもらう
            double answer_number = evaluate(inside_tokens);
            
            // 新しいNUMBERトークンを作る
            Token new_token;
            new_token.type = "NUMBER";
            new_token.number = answer_number;
            
            // 元のtokensリストの'('から')'までの部分を削除し、new_tokenを挿入する
            tokens.erase(tokens.begin() + start_index, tokens.begin() + end_index + 1);
            tokens.insert(tokens.begin() + start_index, new_token);
            
            // リストの長さが変わったので、indexの位置を変える
            index = start_index;
        } else {
            index++;
        }
    }
    return tokens;
}

vector<Token> evaluate_function(vector<Token> tokens) {
    vector<Token> pass_tokens;
    int index = 0;
    
    while (index < tokens.size()) {
        if (tokens[index].type == "FUNC") {
            string func_name = tokens[index].name;
            Token next_token = tokens[index + 1];
            double number_value = next_token.number;
            
            double new_number = 0;
            if (func_name == "abs") {
                new_number = abs(number_value);
            } else if (func_name == "int") {
                new_number = trunc(number_value); 
            } else if (func_name == "round") {
                new_number = round(number_value);
            } else {
                cout << "Unknown function: " << func_name << endl;
                exit(1);
            }
            
            Token new_token;
            new_token.type = "NUMBER";
            new_token.number = new_number;
            pass_tokens.push_back(new_token);
            
            index += 2;
        } else {
            pass_tokens.push_back(tokens[index]);
            index++;
        }
    }
    return pass_tokens;
}

vector<Token> evaluate_mul_div(vector<Token> tokens) {
    vector<Token> pass1_tokens;
    int index = 0;
    
    while (index < tokens.size()) {
        if (tokens[index].type == "MUL") {
            Token prev_token = pass1_tokens.back();
            pass1_tokens.pop_back(); 
            Token next_token = tokens[index + 1];
            
            Token new_token;
            new_token.type = "NUMBER";
            new_token.number = prev_token.number * next_token.number;
            pass1_tokens.push_back(new_token);
            
            index += 2;
        } else if (tokens[index].type == "DIV") {
            Token prev_token = pass1_tokens.back();
            pass1_tokens.pop_back();
            Token next_token = tokens[index + 1];
            
            Token new_token;
            new_token.type = "NUMBER";
            new_token.number = prev_token.number / next_token.number;
            pass1_tokens.push_back(new_token);
            
            index += 2;
        } else {
            pass1_tokens.push_back(tokens[index]);
            index++;
        }
    }
    return pass1_tokens;
}

double evaluate_add_sub(vector<Token> tokens) {
    double answer = 0;
    
    // 先頭にダミーの'+'を入れておく
    Token dummy_plus;
    dummy_plus.type = "PLUS";
    tokens.insert(tokens.begin(), dummy_plus);
    
    int index = 1;
    while (index < tokens.size()) {
        if (tokens[index].type == "NUMBER") {
            if (tokens[index - 1].type == "PLUS") {
                answer += tokens[index].number;
            } else if (tokens[index - 1].type == "MINUS") {
                answer -= tokens[index].number;
            } else {
                cout << "Invalid syntax" << endl;
                exit(1);
            }
        }
        index++;
    }
    return answer;
}

double evaluate(vector<Token> tokens) {
    vector<Token> tokens_after_parentheses = resolve_parentheses(tokens);
    vector<Token> tokens_after_function = evaluate_function(tokens_after_parentheses);
    vector<Token> tokens_after_mul_div = evaluate_mul_div(tokens_after_function);
    double final_answer = evaluate_add_sub(tokens_after_mul_div);
    
    return final_answer;
}

// テスト用関数

void test(const string& line, double expected_answer) {
    vector<Token> tokens = tokenize(line);
    double actual_answer = evaluate(tokens);
    
    // 誤差を考慮した浮動小数点数の比較
    if (abs(actual_answer - expected_answer) < 1e-8) {
        cout << "PASS! (" << line << " = " << expected_answer << ")" << endl;
    } else {
        cout << "FAIL! (" << line << " should be " << expected_answer << " but was " << actual_answer << ")" << endl;
    }
}

void run_test() {
    cout << "==== Test started! ====" << endl;
    
    // 数字単独
    test("1", 1.0);
    test("1.5", 1.5);
    
    // 基本の四則演算
    test("1+2", 3.0);
    test("5-3", 2.0);
    test("3*4", 12.0);
    test("10/2", 5.0);
    
    // 小数の組み合わせ
    test("1.0+2", 3.0);
    test("1+2.0", 3.0);
    test("1.0+2.0", 3.0);
    test("2.5*2", 5.0);
    test("5.5/2.2", 2.5);
    
    // 四則演算の順序確認
    test("2+3*4", 14.0);
    test("10-8/2", 6.0);
    test("3*4+2", 14.0);
    test("6/2-1", 2.0);
    test("10-3-2", 5.0);
    test("10/2*3", 15.0);
    
    // 長い式
    test("1.5+2.5*4-6/2", 8.5);

    // 括弧の四則演算
    test("(1+2)", 3.0);
    test("(1+2)*3", 9.0);
    test("2*(3+4)", 14.0);
    test("10/(2+3)", 2.0);
    
    // 課題の例
    test("(3.0+4*(2-1))/5", 1.4);
    
    // 括弧がたくさんある
    test("((1+2)*3+4)*5", 65.0);
    test("10-((2+3)*2)", 0.0);
    test("(1+2)*(3+4)", 21.0);
    
    // homework4 関数の例
    test("abs(1-2.2)", 1.2);
    test("int(1.55)", 1.0);
    test("round(1.55)", 2.0);
    
    // 関数と四則演算の組み合わせ
    test("2*abs(3-5)", 4.0);
    test("int(4.8)/2", 2.0);
    
    // 課題の例
    test("12+abs(int(round(1.55)+abs(int(2.3+4))))", 20.0);
    
    cout << "==== Test finished! ====\n" << endl;
}

int main() {
    // 最初にテストを実行
    run_test();
    
    // 対話モード
    string line;
    while (true) {
        cout << "> ";
        if (!getline(cin, line)) break;
        if (line.empty()) continue; // Enterだけ押された場合はスキップ
        
        vector<Token> tokens = tokenize(line);
        double answer = evaluate(tokens);
        cout << "answer = " << answer << "\n" << endl;
    }
    
    return 0;
}