'''

https://www.diyifanwen.com/zuowen/sinianjishige/
https://www.diyifanwen.com/zuowen/sinianjiyanjianggao/
https://www.diyifanwen.com/zuowen/sinianjiyouji/
https://www.diyifanwen.com/zuowen/sinianjizhoujizuowen/
https://www.diyifanwen.com/zuowen/wunianjidushubiji/
https://www.diyifanwen.com/zuowen/wunianjiyingyongwen/
https://www.diyifanwen.com/zuowen/wunianjigaixiexuxiezuowen/
https://www.diyifanwen.com/zuowen/wunianjikuoxiesuoxiezuowen/
https://www.diyifanwen.com/zuowen/wunianjishige/
https://www.diyifanwen.com/zuowen/wunianjisuibi/
https://www.diyifanwen.com/zuowen/wunianjizhouji/
https://www.diyifanwen.com/zuowen/yinianjidushubiji/
https://www.diyifanwen.com/zuowen/yinianjihuatizu

'''

import json

A = {"第一类": {"一个文章" :"内容"}, 
     "第二类": {"一个文章": "内容"}}

A = {}
A['第一类'] = {}
A['第二类'] = {}

A['第一类']['一个文章'] = "内容"
A['第二类']['另一个文章'] = "内容"

A_json = json.dumps(A, ensure_ascii=False)
print((A_json))
print(json.loads(A_json))

names = "asd"
articles = "qwe"
dic = dict(zip(names, articles))
primary_articles[kind] = dic



# with open("list.json", "w+") as list_file:
#     list_file.write(A_json)
