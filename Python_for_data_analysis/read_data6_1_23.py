#读写文本格式的数据
import pandas as pd
import os
import pathlib as pl


#最常使用的csv读取函数
df1=pd.read_csv("D:\\Desktop\\AI_learning\\Python_for_data_analysis\\csv_dirs\\6_1_example1.csv")
print(df1)
#针对默认列名或自定义列名
df2=pd.read_csv("D:\\Desktop\\AI_learning\\Python_for_data_analysis\\csv_dirs\\6_1_example2.csv",header=None)
df2_2=pd.read_csv("D:\\Desktop\\AI_learning\\Python_for_data_analysis\\csv_dirs\\6_1_example2.csv",names=["a","b","c","d","e"])
print(df2,df2_2,sep="\n\n")
#可以指定某一列作为index索引
df3=pd.read_csv(r"D:\Desktop\AI_learning\Python_for_data_analysis\csv_dirs\6_1_example2.csv",names=["A","B","C","D","E"],index_col="E")
print(df3)

#某些表格可能不是标准分隔则使用正则表达式标准化
#除此之外还可以使用skiprow=[]参数跳过行


#处理缺失值是文件读取中重要环节
df4=pd.read_csv(r"D:\Desktop\AI_learning\Python_for_data_analysis\csv_dirs\6_1_example3.csv")
print(df4,df4.isna(),sep="\n\n")
#na_value:将指定的字符串视为NA
df4_4=pd.read_csv(r"D:\Desktop\AI_learning\Python_for_data_analysis\csv_dirs\6_1_example3.csv",na_values=["A"])
print(df4_4,df4_4.isna(),sep="\n\n")
#keep_default_na=False：不在保留默认空缺值规则：" "和"NA"都会被当作字符串处理
df4_3=pd.read_csv(r"D:\Desktop\AI_learning\Python_for_data_analysis\csv_dirs\6_1_example3.csv",keep_default_na=False)
print(df4_3,df4_3.isna(),sep="\n\n")
#两者叠加：只有被指定的内容会被视为空值
df4_2=pd.read_csv(r"D:\Desktop\AI_learning\Python_for_data_analysis\csv_dirs\6_1_example3.csv",keep_default_na=False,na_values=["A"])
print(df4_2,df4_2.isna(),sep="\n\n")


#使用nrow参数选取读取范围
pd.options.display.max_rows=10
df5=pd.read_csv(r"D:\Desktop\AI_learning\Python_for_data_analysis\csv_dirs\6_1_example4.csv",sep="\t",names=["A","B","C","D"],nrows=3)
print(df5)


#将数据写入文本格式
df1=pd.read_csv("D:\\Desktop\\AI_learning\\Python_for_data_analysis\\csv_dirs\\6_1_example1.csv")
print(df1)
df1.to_csv(r"D:\Desktop\AI_learning\Python_for_data_analysis\csv_dirs\6_1_1_out.csv")
#还可以指定分隔符和空缺标记
#columns参数选定指定的列：如果要修改列名需要先rename再选中
#index参数为布尔值表示是否打印行索引
#通过stdout直接打印
import sys
df1.to_csv(sys.stdout,sep="|")
df1.to_csv(sys.stdout,na_rep="noNumber")
df1_new=df1.rename(columns={"a":"A","b":"B","c":"C","d":"D","message":"message"}).to_csv(sys.stdout,index=True,columns=["A","C","D"])
print(df1_new)


#有时候需要对csv文件做额外处理
#对单字符分隔符文件导入csv模块
import csv

f=open(r"D:\Desktop\AI_learning\Python_for_data_analysis\csv_dirs\6_1_example5.csv")
csv_reader=csv.reader(f)
#reader会对值产生列表
for line in csv_reader:
    print(line)
f.close()

#将文件读取到多行列表中设置头和数据行
#用字典推导式创建数据列的字典
with open(r"D:\Desktop\AI_learning\Python_for_data_analysis\csv_dirs\6_1_example5.csv")as file:
    lines=list(csv.reader(file))
    head,value=lines[0],lines[1:]
    dic={h:v for h,v in zip(head,zip(*value))}
print(dic)


