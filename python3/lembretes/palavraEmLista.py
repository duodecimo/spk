#!/bin/python

list = ["word1", "word2", "word3"]
try:
   print(list.index("word2"))
except ValueError:
   print("word1 not in list.")
   
# resultado
# 1
