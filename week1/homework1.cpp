#include <bits/stdc++.h>
using namespace std;
int main() {
    ifstream input("words.txt");
    if(!input) {
        cerr << "ファイルを開くのに失敗しました。" << endl;
        return 1;
    }
    vector<pair<string,string>> new_dictionary;
    string word;
    while(input >> word) {
        string sorted_word = word;
        sort(sorted_word.begin(),sorted_word.end());
        new_dictionary.push_back({sorted_word,word});
    }
    input.close();

    sort(new_dictionary.begin(),new_dictionary.end());
    string random_word;
    cout << "アナグラムを探したい文字列：";
    getline(cin, random_word);
    string sorted_random_word = random_word;
    sort(sorted_random_word.begin(),sorted_random_word.end());

    bool found = false;
    auto it=lower_bound(
        new_dictionary.begin(),
        new_dictionary.end(),
        sorted_random_word,
        [](const pair<string, string>& p, const string& value) {
            return p.first<value;
        }
    );

    while(it!=new_dictionary.end()&&it->first==sorted_random_word) {
        if(it->second!=random_word) {
            cout << it->second << endl;
            found=true;
        }
        it++;
    }
    if(!found) {
        cout << "アナグラムは見つかりませんでした！" << endl;
    }

    return 0;
}

/*実行結果
yanagisawa.yukia@YukiAir week1 % ./homework1                      
アナグラムを探したい文字列：listen
enlist
inlets
silent
tinsel
yanagisawa.yukia@YukiAir week1 % ./homework1
アナグラムを探したい文字列：xyz
アナグラムは見つかりませんでした！
*/