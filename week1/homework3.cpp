#include <bits/stdc++.h>
using namespace std;

const vector<int> SCORES = {1,3,2,2,1,3,3,1,1,4,4,2,2,1,1,3,4,1,1,1,2,3,3,4,3,4};
// 辞書データ用の構造体
struct WordData {
    string word;
    vector<int> count;
    int score;
};

pair<string,int> solve_dfs(const string& query, const vector<WordData>& dict) {
    vector<int> avail(26,0);
    for(char c:query) {
        avail[c-'a']++;
    }
    //作れる可能性のある単語だけを候補に絞る
    vector<WordData> candidates;
    for(const auto& w:dict) {
        bool ok=true;
        for(int i=0; i<26; i++) {
            if(w.count[i]>avail[i]) {
                ok=false;
                break;
            }
        }
        if(ok) {
            candidates.push_back(w);
        }
    }
    //候補をスコアが高い順に並び替える
    sort(candidates.begin(),candidates.end(),[](const WordData& a,const WordData& b) {
        return a.score>b.score;
    });

    int max_score=-1;
    vector<string> best_words;

    auto dfs=[&](auto& self,vector<int>& cur_avail,int cur_score,vector<string>& cur_words, int start_idx) -> void {
        if(cur_score>max_score) {
            max_score=cur_score;
            best_words=cur_words;
        }
        int max_possible=0;
        //残りの文字をすべて使った場合の限界スコアを計算
        for(int i=0; i<26; i++) {
            max_possible+=cur_avail[i]*SCORES[i];
        }
        //今のスコア+限界スコアがmax_scoreを超えないなら探索を打ち切る
        if(cur_score+max_possible<=max_score) {
            return;
        }
        //候補の単語を順番に試す
        for(int i=start_idx; i<candidates.size(); i++) {
            const auto& cand=candidates[i];
            
            bool ok=true;
            for (int j=0; j<26; j++) {
                if (cand.count[j]>cur_avail[j]) {
                    ok=false;
                    break;
                }
            }

            if(ok) {
                //文字を消費
                for(int j=0; j<26; j++) cur_avail[j]-=cand.count[j];
                cur_words.push_back(cand.word);
                //次の深さ
                self(self,cur_avail,cur_score+cand.score,cur_words, i);
                //探索から戻ってきたら文字を元に戻す
                cur_words.pop_back();
                for(int j=0; j<26; j++) cur_avail[j]+=cand.count[j];
            }
        }
    };

    vector<string> init_words;
    dfs(dfs,avail,0,init_words,0);

    string result_str = "";
    for(size_t i=0; i<best_words.size(); i++) {
        result_str+=best_words[i];
        if(i+1<best_words.size()) result_str+=" ";
    }

    return {result_str, max_score};
}

int main() {
    vector<WordData> dict;
    ifstream dictFile("words.txt");
    
    string w;
    while (dictFile >> w) {
        vector<int> cnt(26,0);
        int sc=0;
        for(char c:w) {
            cnt[c-'a']++;
            sc+=SCORES[c-'a'];
        }
        dict.push_back({w,cnt,sc});
    }
    dictFile.close();
    string input_name="small.txt";
    string output_name="small_answer_hw3.txt";
    
    ifstream inputFile(input_name);
    ofstream outputFile(output_name);

    string query;
    while (inputFile >> query) {
        pair<string, int> result=solve_dfs(query,dict);
        outputFile << result.first << endl;
    }

    inputFile.close();
    outputFile.close();
    
    cout << output_name << " に保存しました。\n";

    return 0;
}