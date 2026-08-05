#对数据进行操作分两步进行：1.获取数据 2.将数据读入计算机并进行计算
#n维数组也称为张量（Tensor）所有深度学习框架斗鱼ndarray高度相似
#但是因为支持GPU加速和自动微分，所以深度学习框架更加强大

import torch #来自PyTorch
import numpy as np #来自numpy

torch_x=torch.arange(12)
numpy_x=np.arange(12)
print(torch_x.dtype,numpy_x.dtype)
#创建行向量的方法是一样的，并且数据类型默认整数

#所有深度学习还是numpy都使用shape属性查张量形状
#numpy.size但是pytorch.numel()检查总元素数量
print(torch_x.shape,numpy_x.shape)
print(torch_x.numel(),numpy_x.size)

#numpy和pytorch改变数组形状方法相同
#可以使用-1占位进行维度自动推导
torch_x=torch_x.reshape((3,4))
numpy_x=numpy_x.reshape((3,4))
print(torch_x,numpy_x,sep="\n\n")

#numpy和pytorch创建全01数组方法一样
torch_0=torch.zeros((2,3,4))
numpy_0=np.zeros((2,3,4))
print(torch_0,numpy_0,sep="\n\n")

#从标准正态分布中随机采样
np_ran=np.random.normal(0,1,size=(3,4))
pt_ran=torch.randn(3,4)
print(np_ran,pt_ran,sep="\n\n")

#或者直接传入列表构造张量
lis=[x for x in range(20) if x%2==0]
np_lis=np.array(lis)
pt_lis=torch.tensor(lis)
print(np_lis,pt_lis,sep="\n\n")


#对于具有同一形状的任意两个张量常见的运算符都是按元素运算
#除此之外还能执行线性代数运算包括点积和矩阵乘法
#还可以将两组张量拼接而非叠加
X=np.random.normal(0,1,size=(3,4))
Y=np.arange(12).reshape((3,4))
Z=np.concatenate([X,Y],axis=0)
print(Z)
O=torch.arange(12,dtype=torch.float64).reshape(3,4)
P=torch.randn(3,4).reshape(3,4)
Q=torch.cat([O,P],dim=1)
print(Q)


#广播机制：numpy和pytorch广播机制是完全一致的
#从右往左扫描维度：如果维度不同会在少维度数组左补1

a=np.arange(3).reshape((1,3))
b=np.arange(2).reshape((2,1))
print(a,b,sep="\n\n")
c=torch.arange(3).reshape((1,3))
d=torch.arange(2).reshape((2,1))
print(c,d,sep="\n\n")
print(a+b,c+d,sep="\n\n")
