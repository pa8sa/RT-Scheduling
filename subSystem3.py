import globals
import threading
from typing import List
import copy
from task import Task
from resource_ import Resource_

time_unit = -1
ready_queue = []
all_queue = []
tasks_global = []

'''
        duration  resource1_usage  resource2_usage  entering_time   period  recursion
    T31     2           2               3                0            10       1
    T32     1           2               3                0            5        2
    
'''

def add_to_ready_queue(task: Task):
    ready_queue.append(task)
    ready_queue.sort(key=lambda task: task.priority, reverse=True)

def is_schedulable(tasks: List[Task]):
    sorted_tasks = sorted(tasks, key=lambda task: task.period)
    util = 0.0
    N = len(sorted_tasks)
    for i, task in enumerate(sorted_tasks):
        util += task.duration / task.period
        if util > N * (2**(1/N) - 1):
            return False
    return True

def check_for_tasks():
    print(f'\n[TASKS] {[(task.name, task.duration, task.entering_time) for task in tasks_global]}\n')
    for t in tasks_global:
        if t.entering_time <= time_unit and t.duration > 0:
            print(f'\n ADDED TO QUEUE {t.entering_time} {t.duration}\n')
            add_to_ready_queue(copy.deepcopy(t))

def core(resources: List[Resource_]):
    prev_task = None
    while True:
        
        if time_unit > 10:
            break
        
        check_for_tasks()
        
        if (len(ready_queue) == 0 and prev_task is None):
            continue
        
        if prev_task is not None:
            task = prev_task
        else:
            task = ready_queue.pop(0)
            
        print(f'\n[RUNNING] TIME: {time_unit} - {task.name} {task.duration} \n')
        
        task.state = 'running'
        task.duration -= 1
        task.recursion -= 1
        
        if task.duration == 0:
            if task.recursion >= 1:
                task.entering_time = ((time_unit // task.period) + 1) * task.period
                task.state = 'ready'
                
                for i, t in enumerate(tasks_global):
                    if t.name == task.name:
                        tasks_global.pop(i)
                        task.duration = t.duration
                        tasks_global.append(copy.deepcopy(task))
                        print(f'\n[WENT FOR NEXT ROUND] TIME:{time_unit} {t.duration} {task.entering_time}\n')
            else:
                for i, t in enumerate(tasks_global):
                    if t.name == task.name:
                        tasks_global.pop(i)
                task.state = 'completed'
                print(f'\n[COMPLETED] TIME: {time_unit} {task.name} {task.duration} \n')
                
            prev_task = None
        else:
            prev_task = task
            
            
def subSystem3(resources: List[Resource_], tasks: List[Task]):
    global time_unit, tasks_global
    
    t = threading.Thread(target=core, args=(resources,))
    t.start()
    
    for task in tasks:
        task.priority = 1/task.period
        
    tasks.sort(key=lambda task: task.priority, reverse=True)
    
    tasks_global = copy.deepcopy(tasks)
    
    while True:
        time_unit+=1
        print(f'========================================================================================================= time_unit {time_unit}')
    
        if time_unit > 10:
            break
    
    t.join()