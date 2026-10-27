# basic word-based tokenizer
import sys
a = str(sys.argv[1])
tokens = a.split(" ")
for i, t in enumerate(tokens):
    print(f'{i} ==> {t}')   