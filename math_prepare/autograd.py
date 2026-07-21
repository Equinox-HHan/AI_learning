import torch
import pandas
import matplotlib

#自动求导基本用法
x=torch.arange(4.0)
x.requires_grad_(True)
print(x.grad)
y=2*torch.dot(x,x)
y.backward()
print(x.grad)

#梯度累加要放置梯度爆炸
x.grad=None
y=x.sum()
y.backward()
print(x.grad)

#对向量自动求导
x.grad=None
y=x*x
y.sum().backward()
print(x.grad)

#梯度分离
x.grad=None
y=x*x
u=y.detach()
z=u*x
z.sum().backward()
print(x.grad==u)

#自动求导在控制流当中的运用
def func(a):
    b=a*2
    while b.norm()<1000:
        b=b*2
    if b.sum()>0:
        c=b
    else:
        c=100*b
    return c

a=torch.randn(size=(),requires_grad=True)
d=func(a)
d.backward()
print(a.grad==d/a)
