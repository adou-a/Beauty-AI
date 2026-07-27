#只要用户输入的单词部分

import re


n  =input('').strip().lower()


matches = re.sub(r'[^a-zA-Z]','',n)
print(matches)