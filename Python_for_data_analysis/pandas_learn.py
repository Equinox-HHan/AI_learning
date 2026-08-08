#机器学习和深度学习通常从数据预处理开始
#使用pandas包将原始数据转换为张量格式

#读取数据集：首先创建人工数据集并存储在.csv文件中
import os
import pandas as pd

cur_file_abs_path=os.path.abspath(__file__)
dir_name=os.path.dirname(cur_file_abs_path)
file_csv=os.path.join(dir_name,"pandas_csv.csv")
with open(file_csv,"w") as f:
    f.write("NumRooms,Alley,Price\n")
    f.write("NA,Pave,127500\n")
    f.write("2,NA,106000\n")
    f.write("4,NA,178100\n")
    f.write("NA,NA,140000\n")

data=pd.read_csv(file_csv)
print(data)


#处理缺失值：插值法或者删除法
#本次处理考虑插值法
inputs,outputs=data.iloc[:,0:2],data.iloc[:,2]
inputs["NumRooms"]=inputs["NumRooms"].fillna(inputs["NumRooms"].mean())
print(inputs)
inputs=pd.get_dummies(inputs,dummy_na=True)
print(inputs)

#都为数值类型转换为张量格式
import torch

X=torch.tensor(inputs.to_numpy(dtype=float))
Y=torch.tensor(outputs.to_numpy(dtype=float))
print(X,Y,sep="\n\n")
