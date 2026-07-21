import torch
from torch.distributions import multinomial
from d2l import torch as d2l  # ← d2l-zh 全书的标准导入，提供 d2l.plt、d2l.set_figsize 等

# 公平骰子：6 面各 1/6 概率
fair_probs = torch.ones(6) / 6

# 单次投掷
print("投掷 1 次:", multinomial.Multinomial(1, fair_probs).sample())

# 投掷 10 次（模拟一次扔 10 颗骰子）
print("投掷 10 次:", multinomial.Multinomial(10, fair_probs).sample())

# 大数定律：投 1000 次，频率会趋近 1/6 ≈ 0.167
counts = multinomial.Multinomial(1000, fair_probs).sample()
print("1000 次的频率:", counts / 1000)

# 500 组实验，每组 10 次投掷
counts = multinomial.Multinomial(10, fair_probs).sample((500,))
cum_counts = counts.cumsum(dim=0)
estimates = cum_counts / cum_counts.sum(dim=1, keepdim=True)

# 可视化：观察概率估计随实验组数增加而收敛
d2l.set_figsize((6, 4.5))
for i in range(6):
    d2l.plt.plot(estimates[:, i].numpy(),
                 label=("P(die=" + str(i + 1) + ")"))
d2l.plt.axhline(y=0.167, color='black', linestyle='dashed')
d2l.plt.gca().set_xlabel('Groups of experiments')
d2l.plt.gca().set_ylabel('Estimated probability')
d2l.plt.legend()
d2l.plt.show()


