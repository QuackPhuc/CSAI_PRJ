from queue import PriorityQueue
a = PriorityQueue().queue
a.append(1)
a.append(4)
a.append(3)
f = lambda x: abs(x-10)
a.sort(key=f)
print(a.pop())