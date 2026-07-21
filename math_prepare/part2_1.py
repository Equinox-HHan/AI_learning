#python中的列表推导式和生成器

#列表推导式语法[expression for item in iterable if condition]
#求出0-10之间的偶数的平方
squares1=[x**2 for x in range(0,10) if x%2==0]
print(squares1)
print(type(squares1))
print("\n")


#生成器表达式和生成器函数
#生成器是惰性求值，需要显示表达
squares2=(x**2 for x in range(0,10) if x&1==1)
print(squares2)
print(type(squares2))
for item in squares2:
    print(item,end=" ")
print("\n")


#生成器函数
def func(num):
    count=0;
    while count<=num:
        yield count;
        count+=1;
counter=func(10);
print(next(counter));
print(next(counter));
print(next(counter));


#lambda函数和高阶函数
#三剑客：map，sort，filter
#特殊函数zip(返回一个迭代器)
number=[1,2,3,4,5]
number1=map(lambda x:pow(x,3),number)
number1=list(number1)
number2=filter(lambda x:(x&1)==1,number)
number2=list(number2)
for n1,n2 in zip(number1,number2):
    print(n1,n2,sep="---",end="\n")
student=[{"a":10},{"b":17},{"c":20},{"d":21}]
student=sorted(student,key=lambda x:list(x.values()),reverse=True)
print(student)
print('\n')

#直接粘合（列表或者字典都行）+木桶效应+特殊占位+反向解包
names1=['xiaoming','xiaobai','xiaohan']
ages1=[17,21,20]
combined=list(zip(names1,ages1))
print(combined)
names2=["Alice", "Bob", "Charlie", "David"]  
ages2=[24, 50]                                
print(list(zip(names2, ages2)))
from itertools import zip_longest
names3=["Alice", "Bob", "Charlie", "David"]  
ages3=[24, 50]
print(list(zip_longest(names3,ages3,fillvalue=None)))
name1_1,age1_1=zip(*combined)
print(name1_1)
print(age1_1)

#高阶函数装饰器和语法糖的结合
#保留原函数的元数据
from functools import wraps
def outer(func):
    @wraps(func)
    def inner(*args,**kwargs):
        print("start")
        result=func(*args,**kwargs)
        print("end")
        return result
    return inner
@outer
def calculate(x,y):
    return x^y
print(f"最终结果:{calculate(10,21):.2f}")
