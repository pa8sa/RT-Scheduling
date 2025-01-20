import threading
from task import Task
from resource_ import Resource_
from subSystem1 import subSystem1
from subSystem2 import subSystem2
from subSystem3 import subSystem3
from subSystem4 import subSystem4

iToSubMap = {
  0: subSystem1,
  1: subSystem2,
  2: subSystem3,
  3: subSystem4
}

def get_input():
  tasks = []
  resources = []

  with open('in.txt', 'r') as f:
    lines = f.readlines()
    for i in range(4):
      r1, r2 = lines[i].strip().split(' ')
      R1 = Resource_(i, 'R1', int(r1))
      R2 = Resource_(i, 'R2', int(r2))
      resources.append([R1, R2])

    i = 4
    
    # get subsystem 1 tasks
    subSystem1Tasks = []
    while lines[i] != '$\n':
      sub_system_number = 1
      name, duration, resource1_usage, resource2_usage, entering_time, dest_cpu = lines[i].strip().split(' ')
      task = Task(sub_system_number, name, int(duration), int(resource1_usage), int(resource2_usage), int(entering_time), dest_cpu=int(dest_cpu))
      subSystem1Tasks.append(task)
      i += 1

    i += 1

    # get subsystem 2 tasks
    subSystem2Tasks = []
    while lines[i] != '$\n':
      sub_system_number = 2
      name, duration, resource1_usage, resource2_usage, entering_time = lines[i].strip().split(' ')
      task = Task(sub_system_number, name, int(duration), int(resource1_usage), int(resource2_usage), int(entering_time))
      subSystem2Tasks.append(task)
      i += 1
      
    i += 1
    
    # get subsystem 3 tasks
    subSystem3Tasks = []
    while lines[i] != '$\n':
      sub_system_number = 3
      name, duration, resource1_usage, resource2_usage, entering_time = lines[i].strip().split(' ')
      task = Task(sub_system_number, name, int(duration), int(resource1_usage), int(resource2_usage), int(entering_time))
      subSystem3Tasks.append(task)
      i += 1
      
    i += 1
    
    # get subsystem 4 tasks
    subSystem4Tasks = []
    while lines[i] != '$':
      sub_system_number = 4
      name, duration, resource1_usage, resource2_usage, entering_time, prerequisite_task_name = lines[i].strip().split(' ')
      task = Task(sub_system_number, name, int(duration), int(resource1_usage), int(resource2_usage), int(entering_time), prerequisite_task_name=None if prerequisite_task_name == '-' else prerequisite_task_name)
      subSystem4Tasks.append(task)
      i += 1

    tasks.append(subSystem1Tasks)
    tasks.append(subSystem2Tasks)
    tasks.append(subSystem3Tasks)
    tasks.append(subSystem4Tasks)
    
    return resources, tasks

def mainThread():
  resources, tasks = get_input()
  sub_system_threads = []

  for i in range(4):
    subSystem = iToSubMap[i]
    t = threading.Thread(target=subSystem, args=(resources[i], tasks[i]))
    sub_system_threads.append(t)
    t.start()
        
  for t in sub_system_threads:
    t.join()

if __name__ == '__main__':
  t = threading.Thread(target=mainThread)
  t.start()
  t.join()
