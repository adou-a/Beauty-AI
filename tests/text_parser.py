#只要用户输入的单词部分

import re

def parser(n):
    n  =n.strip().lower()

    matches = re.sub(r'[^a-zA-Z]','',n)
    return  matches