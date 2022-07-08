import time


buf = {'hi': 2, 2: 2}

S = int(1e7)

s = time.time()
for i in range(S):
    if 'hi' in buf:
        pass
print(time.time()-s)



s=time.time()
for i in range(S):
    if buf.get('hi'):
        pass
print(time.time()-s)


