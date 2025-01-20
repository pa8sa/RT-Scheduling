import globals
import threading
from typing import List
import copy
from task import Task
from resource_ import Resource_

time_unit = -1

def increment_time_unit():
    global time_unit
    time_unit+=1
    
start_barrier = threading.Barrier(1, increment_time_unit)

r_lock = threading.Lock()
ready_queue = []
tasks_global = []

'''
        duration  resource1_usage  resource2_usage  entering_time   period  recursion
    T31     2           2               3                0            10        2
    T32     1           2               3                0            5         2
    
'''

def add_to_ready_queue(task: Task):
    with r_lock:
        if (task.name  in [t.name for t in ready_queue]):
            return
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
    # print(f'\n[GLOBAL TASKS] {[(task.name, task.duration, task.entering_time, task.state) for task in tasks_global]}\n')
    
    for t in tasks_global:
        if (t.entering_time <= time_unit and 
            t.state != 'completed' and 
            t.state != 'running' and 
            t.name not in [task.name for task in ready_queue]):
            
            # print(f'\n ADDED TO QUEUE TIME: {time_unit} - {t.name} {t.entering_time} {t.duration}\n')
            add_to_ready_queue(copy.deepcopy(t))
    
    for t in ready_queue:
        if t.entering_time > time_unit:
            with r_lock:
                ready_queue.pop(t) 
            
def add_to_global(task: Task):
    global tasks_global
    for i, t in enumerate(tasks_global):
        if t.name == task.name:
            task.duration = t.duration
            tasks_global[i] = copy.deepcopy(task)
            break
    

def core(resources: List[Resource_]):
    prev_task = None
    while True:
        start_barrier.wait()
        # print(f'========================================================================================================= time_unit {time_unit}')
        if time_unit > 15:
            break
        
        check_for_tasks()
        
        with r_lock:
            for i, t in enumerate(ready_queue):
                if prev_task and t.name == prev_task.name:
                    ready_queue.pop(i)
                    break
            # print(f'\n[READY QUEUE] {[(task.name, task.duration, task.entering_time, task.state) for task in ready_queue]}\n')
        
            if (len(ready_queue) == 0 and prev_task is None):
                continue
            
        if prev_task is not None:
            if len(ready_queue) > 0 and ready_queue[0].priority >= prev_task.priority:
                task = ready_queue.pop(0)
                # print(f'\n[PREEMPTION] {task.name} preempted {prev_task.name} \n')
                prev_task.state = 'ready'
                add_to_ready_queue(prev_task)
                prev_task = None
            else:
                task = prev_task
        else:
            task = ready_queue.pop(0)
            
        task.state = 'running'
        # print(f'\n[RUNNING] TIME: {time_unit} - {task.name} duration: {task.duration}  recursion: {task.recursion} state: {task.state}\n')
        
        task.duration -= 1
        
        if task.duration == 0:
            task.recursion -= 1
            if task.recursion >= 1:
                task.entering_time = ((time_unit // task.period) + 1) * task.period
                task.state = 'ready'
                add_to_global(task)
                
                # print(f'\n[WENT FOR NEXT RECURSION] TIME:{time_unit} {task.name}  duration: {task.duration} entering_time: {task.entering_time} {task.state}\n')
            else:
                task.state = 'completed'
                add_to_global(task)
                
                # print(f'\n[COMPLETED] TIME: {time_unit} {task.name} duration: {task.duration} {task.state}\n')
                
            prev_task = None
        else:
            # print(f'\n[WENT FOR NEXT ROUND] TIME:{time_unit} {task.name}  duration: {task.duration} entering_time: {task.entering_time} {task.state}\n')
            prev_task = task
            
            
def subSystem3(resources: List[Resource_], tasks: List[Task]):
    global time_unit, tasks_global
    # print(is_schedulable(tasks))
    # return 
    
    t = threading.Thread(target=core, args=(resources,))
    t.start()
    
    for task in tasks:
        task.priority = 1/task.period
        
    tasks.sort(key=lambda task: task.priority, reverse=True)
    
    tasks_global = copy.deepcopy(tasks)
    
    t.join()