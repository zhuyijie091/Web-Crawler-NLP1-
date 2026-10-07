#include <iostream>
#include <string>
#include <locale>
#include <codecvt>
#include "SegCN.hpp"
#include "utils.hpp"
using namespace std;


int main() {
    init_chinese_env();
    string input;
    Seg seg;

    cin >> input;
    wstring wstr = to_wstring(input);
    seg.segmentation(wstr);
    return 0;
}

