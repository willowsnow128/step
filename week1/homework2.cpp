#include <bits/stdc++.h>
using namespace std;
const vector<int> scores={1,3,2,2,1,3,3,1,1,4,4,2,2,1,1,3,4,1,1,1,2,3,3,4,3,4};
pair<string,int> find_best_anagram(const string& random_word,const vector<string>& dictionary) {
    vector<int> random_count(26,0);
    //今見ている文字のカウント
    for(char c:random_word) {
        random_count[c-'a']++;
    }
    string best_word="";
    int max_score=-1;
    //辞書の単語のカウント
    for(const string& word:dictionary) {
        vector<int> word_count(26,0);
        for(char c:word) {
            word_count[c-'a']++;
        }
        bool can_make=true;
        for(int i=0; i<26; i++) {
            if(word_count[i]>random_count[i]) {
                can_make=false;
                break;
            }
        }
        if(can_make) {
            int current_score=0;
            for(char c:word) {
                current_score+=scores[c-'a'];
            }
            if(current_score>max_score) {
                max_score=current_score;
                best_word=word;
            }
        }
    }
    return {best_word,max_score};
}

int main() {
    vector<string> dictionary;
    ifstream dictfile("words.txt");
    string dict_word;
    while(dictfile>>dict_word) {
        dictionary.push_back(dict_word);
    }
    dictfile.close();
    vector<pair<string,string>> file_pairs={
        {"small.txt","output_small.txt"},
        {"large.txt","output_large.txt"}
    };
    for(const auto& file_pair:file_pairs) {
        string input_name=file_pair.first;
        string output_name=file_pair.second;
        
        ifstream input(input_name);
        ofstream output(output_name);

        string random_word;
        int total_score=0;
        while(input>>random_word) {
            pair<string, int> result = find_best_anagram(random_word, dictionary);
            output << result.first << endl;
            if (result.second > 0) {
                total_score += result.second; 
            }
        }
        cout << input_name << "の総合計スコアは:" << total_score << "点です" << endl;
        input.close();
        output.close();
        cout << output_name << "に保存完了" << endl;
        
    }
    return 0;

}