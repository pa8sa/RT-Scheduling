import threading
import time
from task import Task
from resource_ import Resource_

def mainThread():
  print('Hello from main thread!')

  sub_system_threads = []

  for i in range(4):
    t = threading.Thread(target=globals()[f'subSystem{i+1}'])
    sub_system_threads.append(t)
    t.start()
    
  for t in sub_system_threads:
    t.join()
  
def subSystem1():
  print('Hello from sub-system 1!')
  
def subSystem2():
  print('Hello from sub-system 2!')
  
def subSystem3():
  print('Hello from sub-system 3!')

def subSystem4():
  print('Hello from sub-system 4!')

if __name__ == '__main__':
  t = threading.Thread(target=mainThread)
  t.start()
  t.join()