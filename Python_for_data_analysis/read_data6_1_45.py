#处理JSON对象:JSON和Python语法非常相似
#使用loads将JSON转换成Python（反函数为dumps）
#函数,      末尾是否有 s,       操作对象,       核心作用
#json.load  否                  文件 (File)     从文件中读取并解析 JSON 数据
#json.loads 是 (s = string)     字符串 (String) 解析 JSON 格式的字符串
#json.dump  否                  文件 (File)     把数据写入文件并保存为 JSON
#json.dumps 是 (s = string)     字符串 (String) 把数据转换为 JSON 格式的字符串
import json
from math import sqrt

file_path=r"D:\Desktop\AI_learning\Python_for_data_analysis\file_dirs\example1.json"
with open(file_path,"r",encoding="utf-8")as file:
    data1=json.load(file)
print(data1)

asjson=json.dumps(data1)
path_to=r"D:\Desktop\AI_learning\Python_for_data_analysis\file_dirs\example1_1.json"
with open(path_to,"w",encoding="utf-8")as file:
    json.dump(data1,file)


#使用dataframe构造器
#或者直接使用read_json函数：比较复杂
import numpy as np
import pandas as pd

df=pd.DataFrame(data1["users"],columns=["id","name"])
print(df)

with open(file_path,"r",encoding="utf-8")as file:
    data2=json.load(file)
df_users=pd.json_normalize(data2,record_path=["users"])
print(df_users)

def isPrime(number:int):
    ans=[]
    is_prime=[True]*number
    is_prime[0],is_prime[1]=False,False
    num=int(sqrt(float(number)))
    for x in range(2,num):
        if is_prime[x]:
            for i in range(pow(x,2),number,x):
                is_prime[i]=False
    for x in range(number):
        if is_prime[x]:
            ans.append(x)
    return ans
outer_key=[x for x in "ABCD"]
inner_key=[x for x in "abcde"]
inner_value=[x for x in range(100) if x in isPrime(100)]
dic={"A":{"a":1,"b":2},"B":{"a":1}}
df3=pd.DataFrame(dic,dtype=np.float64)
print(df3)


#进行网络抓取：针对HTML和XML
#此处不进行练习

