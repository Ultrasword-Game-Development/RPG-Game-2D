from dataclasses import dataclass

@dataclass
class TT:
    x: int
    y: int

import time

T = int(1e6)
st = time.time()

for i in range(T):
    TT(1,2)
print(time.time()-st)
st = time.time()
for i in range(T):
    [1,2]
print(time.time()-st)

