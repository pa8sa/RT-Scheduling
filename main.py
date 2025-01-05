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

def get_input():
  tasks = []
  Rs = []

  with open('in.txt', 'r') as f:
    lines = f.readlines()
    for i in range(4):
      r1, r2 = lines[i].strip().split(' ')
      R1 = Resource_(i, 'R1', r1)
      R2 = Resource_(i, 'R2', r2)
      Rs.append([R1, R2])

    i = 4
    # get subsystem 1 tasks
    subSystem1Tasks = []
    while lines[i] != '$':
      sub_system_number = 1
      name, duration, resource1_usage, resource2_usage, entering_time, dest_cpu = lines[i].strip().split(' ')
      task = Task(sub_system_number, name, duration, resource1_usage, resource2_usage, entering_time, dest_cpu=dest_cpu)
      subSystem1Tasks.append(task)
      i += 1

    # get subsystem 2 tasks
    subSystem2Tasks = []
    # get subsystem 3 tasks
    subSystem3Tasks = []
    # get subsystem 4 tasks
    subSystem4Tasks = []


    tasks.append(subSystem1Tasks)
    tasks.append(subSystem2Tasks)
    tasks.append(subSystem3Tasks)
    tasks.append(subSystem4Tasks)
    
    return Rs, tasks


def mainThread():
  print('Hello from main thread!')
  Rs, tasks = get_input()
  sub_system_threads = []

  for i in range(4):
    subSystem = iToSubMap[i]
    t = threading.Thread(target=subSystem, args=(Rs[i], tasks[i]))
    sub_system_threads.append(t)
    t.start()
    
  for t in sub_system_threads:
    t.join()
  
if __name__ == '__main__':
  t = threading.Thread(target=mainThread)
  t.start()
  t.join()