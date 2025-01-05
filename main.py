import threading
import time
from task import Task
from resource_ import Resource_
from subSystem1 import subSystem1
from subSystem2 import subSystem2
from subSystem3 import subSystem3
from subSystem4 import subSystem4

iToSubMap ={
  0: subSystem1,
  1: subSystem2,
  2: subSystem3,
  3: subSystem4
}

def mainThread():
  print('Hello from main thread!')

  sub_system_threads = []

  for i in range(4):
    subSystem = iToSubMap[i]
    t = threading.Thread(target=subSystem)
    sub_system_threads.append(t)
    t.start()
    
  for t in sub_system_threads:
    t.join()
  
if __name__ == '__main__':
  t = threading.Thread(target=mainThread)
  t.start()
  t.join()