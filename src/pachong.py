
'''

https://m.diyifanwen.com/zuowen/xiaoxuezuowen/

'''

import re
import requests
from bs4 import BeautifulSoup

作文详情
url = 'https://www.diyifanwen.com/zuowen/xiaoxueshuxinzuowen/3713923.html'
response = requests.get(url)
response.encoding = 'gb2312'
soup = BeautifulSoup(response.text, 'html.parser')
A = soup.h1
B = A.findNextSiblings("p")

print(A.text.strip())

for i in B:
    print(i.text.strip())

同分类作文列表
url2 = 'https://www.diyifanwen.com/zuowen/xiaoxueshuxinzuowen'
response = requests.get(url2)
response.encoding = 'gb2312'
soup = BeautifulSoup(response.text, 'html.parser')
C = soup.find(id="AListBox")
D = C.findAll("li")
print(soup.h1.text.strip())
for item in D:
    print(item.a.get('href').replace("//", "https://"))
    

# 作文分类列表
url3 = 'https://www.diyifanwen.com/zuowen/xiaoxuezuowen/'
response = requests.get(url3)
response.encoding = 'gb2312'
soup = BeautifulSoup(response.text, 'html.parser')
E = soup.find_all(name='a', attrs={"class": "SLmore"})
# print(soup.find_all(name='a', attrs={"class": "SLmore"}))
for item in E:
    print(item.get('href').replace("//", "https://"))

'''
作文分类列表 - > 一个 list.txt
 
同分类作文列表 -> 读取上一步的list.txt

作文详情 

with open(file)

'''
