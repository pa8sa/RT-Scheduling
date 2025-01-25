import threading
from task import Task
from resource_ import Resource_
from subSystem1 import subSystem1
from subSystem2 import subSystem2
from subSystem3 import subSystem3
from subSystem4 import subSystem4
import globals
from core import Core

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
      name, duration, resource1_usage, resource2_usage, entering_time, period, recursion = lines[i].strip().split(' ')
      task = Task(sub_system_number, name, int(duration), int(resource1_usage), int(resource2_usage), int(entering_time), period=int(period), recursion=int(recursion))
      subSystem3Tasks.append(task)
      i += 1
      
    i += 1
    
    # get subsystem 4 tasks
    subSystem4Tasks = []
    while lines[i] != '$':
      sub_system_number = 4
      name, duration, resource1_usage, resource2_usage, entering_time, prerequisite_task_name = lines[i].strip().split(' ')
      task = Task(sub_system_number, name, int(duration), int(resource1_usage), int(resource2_usage), int(entering_time), prerequisite_task_name = None if prerequisite_task_name == '-' else prerequisite_task_name)
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
  
  globals.sub1_resources = resources[0]
  globals.sub2_resources = resources[1]
  globals.sub3_resources = resources[2]
  globals.sub4_resources = resources[3]

  for i in range(4):
    t = threading.Thread(target=iToSubMap[i], args=(tasks[i], ))
      
    sub_system_threads.append(t)
    t.start()
        
  for t in sub_system_threads:
    t.join()
    
  print('\n\n\n')
    
  globals.sub1_core1.start()
  globals.sub1_core2.start()
  globals.sub1_core3.start()
  globals.sub2_core1.start()
  globals.sub2_core2.start()
  globals.sub3_core1.start()
  globals.sub4_core1.start()
  globals.sub4_core2.start()
  
  print(f'Core 1 of Subsystem 1:')
  print(f'\tAvg Waiting Time: {globals.sub1_core1.avg_waiting_time}')
  print(f'\tAvg Turnaround Time: {globals.sub1_core1.avg_turnaround_time}')
  print(f'\tAvg Response Time: {globals.sub1_core1.avg_response_time}\n')
  
  print(f'Core 2 of Subsystem 1:')
  print(f'\tAvg Waiting Time: {globals.sub1_core2.avg_waiting_time}')
  print(f'\tAvg Turnaround Time: {globals.sub1_core2.avg_turnaround_time}')
  print(f'\tAvg Response Time: {globals.sub1_core2.avg_response_time}\n')
  
  print(f'Core 3 of Subsystem 1:')
  print(f'\tAvg Waiting Time: {globals.sub1_core3.avg_waiting_time}')
  print(f'\tAvg Turnaround Time: {globals.sub1_core3.avg_turnaround_time}')
  print(f'\tAvg Response Time: {globals.sub1_core3.avg_response_time}\n')
  
  print(f'Core 1 of Subsystem 2:')
  print(f'\tAvg Waiting Time: {globals.sub2_core1.avg_waiting_time}')
  print(f'\tAvg Turnaround Time: {globals.sub2_core1.avg_turnaround_time}')
  print(f'\tAvg Response Time: {globals.sub2_core1.avg_response_time}\n')
  
  print(f'Core 2 of Subsystem 2:')
  print(f'\tAvg Waiting Time: {globals.sub2_core2.avg_waiting_time}')
  print(f'\tAvg Turnaround Time: {globals.sub2_core2.avg_turnaround_time}')
  print(f'\tAvg Response Time: {globals.sub2_core2.avg_response_time}\n')
  
  print(f'Core 1 of Subsystem 3:')
  print(f'\tAvg Waiting Time: {globals.sub3_core1.avg_waiting_time}')
  print(f'\tAvg Turnaround Time: {globals.sub3_core1.avg_turnaround_time}')
  print(f'\tAvg Response Time: {globals.sub3_core1.avg_response_time}\n')
  
  print(f'Core 1 of Subsystem 4:')
  print(f'\tAvg Waiting Time: {globals.sub4_core1.avg_waiting_time}')
  print(f'\tAvg Turnaround Time: {globals.sub4_core1.avg_turnaround_time}')
  print(f'\tAvg Response Time: {globals.sub4_core1.avg_response_time}\n')
  
  print(f'Core 2 of Subsystem 4:')
  print(f'\tAvg Waiting Time: {globals.sub4_core2.avg_waiting_time}')
  print(f'\tAvg Turnaround Time: {globals.sub4_core2.avg_turnaround_time}')
  print(f'\tAvg Response Time: {globals.sub4_core2.avg_response_time}\n')

  print('\n')

  Core.info_of_each_task(1, [globals.sub1_core1, globals.sub1_core2, globals.sub1_core3], len(tasks[0]))
  Core.info_of_each_task(2, [globals.sub2_core1, globals.sub2_core2], len(tasks[1]))
  Core.info_of_each_task(3, [globals.sub3_core1], len(tasks[2]))
  Core.info_of_each_task(4, [globals.sub4_core1, globals.sub4_core2], len(tasks[3]))

  print('\n')
  
  for task in tasks[0]:
    print(f'task {task.name} in subsystem 1 total waiting time: {task.waiting_time}')
  for task in tasks[3]:
    print(f'task {task.name} in subsystem 4 total waiting time: {task.waiting_time}')

if __name__ == '__main__':
  t = threading.Thread(target=mainThread)
  t.start()
  t.join()
