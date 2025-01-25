import globals
import threading
from typing import List
import copy
from task import Task
from resource_ import Resource_

glob_task1: Task = None

r_lock = threading.Lock()
ready_queue = []
tasks_global = []

is_in_double_mode = False

'''
    R1 = 4
    R2 = 10
    
        duration  resource1_usage  resource2_usage  entering_time   period  recursion
    T31     2           2               3                0            10        2
    T32     1           2               3                0            5         2
'''
def optimum_sys_resources(tasks: List[Task]):
    global best_sys_to_borrow
    best_sys_to_borrow = -1
    best_sys_count = 100000
    sub_resources = [globals.sub1_resources, globals.sub2_resources, globals.sub4_resources]
    for i, resource in enumerate(sub_resources):
        counts = [resource[0].count + globals.sub3_resources[0].count, resource[1].count + globals.sub3_resources[1].count]
        if not not_enough_resource(counts, tasks):
            if counts[0] + counts[1] < best_sys_count:
                best_sys_count = counts[0] + counts[1]
                best_sys_to_borrow = i
                
    return best_sys_to_borrow

def borrow_resources(sys_to_borrow: int):
    global borrowed_count
    
    index_to_map = {
        0: [globals.sub1_resource_lock, globals.sub1_resources],
        1: [globals.sub2_resource_lock, globals.sub2_resources],
        2: [globals.sub4_resource_lock, globals.sub4_resources]
    }
        
    res_lock, res = index_to_map[sys_to_borrow]
    # print(f'BORROWED RES FROM {sys_to_borrow} MY RES = {globals.sub3_resources[0].count} {globals.sub3_resources[1].count} {res[0].count} {res[1].count}')
    
    res_lock.acquire()
    globals.sub3_resource_lock.acquire()
    
    globals.sub3_resources[0].count += res[0].count
    globals.sub3_resources[1].count += res[1].count
    
    borrowed_count = [res[0].count, res[1].count]
    
    res[0].count = 0
    res[1].count = 0
    
    globals.sub3_resource_lock.release()
    res_lock.release()

def not_enough_resource(counts, tasks: List[Task]):
    for task in tasks:
        if task.resource1_usage > counts[0] or task.resource2_usage > counts[1]:
            return True
    return False

def give_back_resource():
    global best_sys_to_borrow, borrowed_count, tasks_global, is_in_double_mode
    
    if best_sys_to_borrow == -1:
        return
    
    counts = [globals.sub3_resources[0].count - borrowed_count[0], globals.sub3_resources[1].count - borrowed_count[1]]
    
    tasks = [task for task in tasks_global if task.state != 'completed']
    # print([(task.name, task.state, task.resource1_usage, task.resource2_usage, counts) for task in tasks])
    
    # print(f'{tasks_global[0].name} {tasks_global[0].duration} NOT ENOUGH {not_enough_resource(counts, tasks)} SCHED {is_schedulable(tasks)}')
    
    if not_enough_resource(counts, tasks):
       return 
   
    if is_schedulable(tasks):
       is_in_double_mode = False
    
    index_to_map = {
        0: [globals.sub1_resource_lock, globals.sub1_resources],
        1: [globals.sub2_resource_lock, globals.sub2_resources],
        2: [globals.sub4_resource_lock, globals.sub4_resources]
    }
    
    _, res = index_to_map[best_sys_to_borrow]
    
    globals.sub3_resource_lock.acquire()
    
    res[0].count = borrowed_count[0]
    res[1].count = borrowed_count[1]
    
    globals.sub3_resources[0].count -= borrowed_count[0]
    globals.sub3_resources[1].count -= borrowed_count[1]
    
    borrowed_count = [0, 0]
    best_sys_to_borrow = -1
    
    globals.sub3_resource_lock.release()

def handle_availability(tasks: List[Task]):
    global tasks_global, is_in_double_mode
    counts = [globals.sub3_resources[0].count, globals.sub3_resources[1].count]
    
    if not is_schedulable(tasks) and not_enough_resource(counts, tasks):
        is_in_double_mode = True
        optimum_sys = optimum_sys_resources(tasks)
        borrow_resources(optimum_sys)
        
    elif not is_schedulable(tasks):
        is_in_double_mode = True
    elif not_enough_resource(counts, tasks):
        is_in_double_mode = True
        optimum_sys = optimum_sys_resources(tasks)
        borrow_resources(optimum_sys)

def wait_for_print():
    while globals.print_turn != 3:
        pass
    print_output()
    
    globals.print_turn_lock.acquire()
    globals.print_turn %= 4
    globals.print_turn += 1
    globals.print_turn_lock.release()

def print_output():
    global glob_task1, ready_queue, completed_tasks

    globals.sub3_core1.append_task(glob_task1)

    print("Sub3:")
    print(f"\tR1: {globals.sub3_resources[0].count if globals.sub3_resources else '-'} R2: {globals.sub3_resources[1].count if globals.sub3_resources else '-'}")
    print(f"\tReady Queue: {[task.name for task in list(ready_queue)]}")
    print(f"\tCore1:")
    print(f"\t\tRunning Task: {glob_task1.name if glob_task1 else 'idle'}")
    # print(f"\tCompleted Tasks: \n\t\t{[task.name if task.state=='completed' else '' for task in list(completed_tasks)]}")
    
    give_back_resource()
    
    sub3_state = {
        "R1": globals.sub1_resources[0].count,
        "R2": globals.sub1_resources[1].count,
        "ready_queue": [t.name for t in list(ready_queue)],
        "cores": [
            {"running_task": glob_task1.name if glob_task1 else "idle"},
        ],
        "completed_tasks": [task.name if task.state=='completed' else '' for task in list(completed_tasks)]
    }
    globals.current_time_data["sub3"] = sub3_state

finish_barrier = threading.Barrier(1, action=wait_for_print)

def is_schedulable(tasks: List[Task]):
    sorted_tasks = sorted(tasks, key=lambda task: task.period)
    util = 0.0
    N = len(sorted_tasks)
    for i, task in enumerate(sorted_tasks):
        util += task.duration / task.period
        if util > N * (2**(1/N) - 1):
            return False
    return True

def add_to_ready_queue(task: Task):
    with r_lock:
        if (task.name  in [t.name for t in ready_queue]):
            return
        ready_queue.append(task)
        ready_queue.sort(key=lambda task: task.priority, reverse=True)

def check_for_tasks():
    # print(f'\n[GLOBAL TASKS] {[(task.name, task.duration, task.entering_time, task.state) for task in tasks_global]}\n')
    
    for t in tasks_global:
        if (t.entering_time <= globals.time_unit and 
            t.state != 'completed' and 
            t.state != 'running' and 
            t.name not in [task.name for task in ready_queue]):
            
            # print(f'\n ADDED TO QUEUE TIME: {time_unit} - {t.name} {t.entering_time} {t.duration}\n')
            add_to_ready_queue(copy.deepcopy(t))
    
    for t in ready_queue:
        if t.entering_time > globals.time_unit:
            with r_lock:
                ready_queue.pop(t) 

def add_to_global(task: Task):
    global tasks_global
    for i, t in enumerate(tasks_global):
        if t.name == task.name:
            task.duration = t.duration
            tasks_global[i] = copy.deepcopy(task)
            break

def core():
    global glob_task1, ready_queue, tasks_global, is_in_double_mode, completed_tasks
    prev_task = None
    while True:
        if globals.time_unit == globals.breaking_point:
            return
        
        globals.global_start_barrier.wait()
        # print(f'========================================================================================================= time_unit {time_unit}')
        
        check_for_tasks()
        
        with r_lock:
            for i, t in enumerate(ready_queue):
                if prev_task and t.name == prev_task.name:
                    ready_queue.pop(i)
                    break
            # print(f'\n[READY QUEUE] {[(task.name, task.duration, task.entering_time, task.state) for task in ready_queue]}\n')
        
            if (len(ready_queue) == 0 and prev_task is None):
                glob_task1 = None
                
                finish_barrier.wait()
                globals.global_finish_barrier.wait()
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
        # print(f'\n[RUNNING] TIME: {globals.time_unit} - {task.name} duration: {task.duration}  recursion: {task.recursion} state: {task.state}\n')
        
        task.duration -= 2 if is_in_double_mode else 1

        glob_task1 = task
        
        if task.duration <= 0:
            task.recursion -= 1
            if task.recursion >= 1:
                task.entering_time = ((globals.time_unit // task.period) + 1) * task.period
                task.state = 'ready'
                add_to_global(task)
                
                # print(f'\n[WENT FOR NEXT RECURSION] TIME:{time_unit} {task.name}  duration: {task.duration} entering_time: {task.entering_time} {task.state}\n')
            else:
                task.state = 'completed'
                add_to_global(task)
                completed_tasks.append(task)
                
                # print(f'\n[COMPLETED] TIME: {time_unit} {task.name} duration: {task.duration} {task.state}\n')
                
            prev_task = None
        else:
            # print(f'\n[WENT FOR NEXT ROUND] TIME:{time_unit} {task.name}  duration: {task.duration} entering_time: {task.entering_time} {task.state}\n')
            prev_task = task
            
        finish_barrier.wait()
        globals.global_finish_barrier.wait()

def subSystem3(tasks: List[Task]):
    global tasks_global, is_in_double_mode, completed_tasks
    completed_tasks = []
    
    handle_availability(tasks)    
    
    for task in tasks:
        task.priority = 1/task.period
        
    tasks.sort(key=lambda task: task.priority, reverse=True)
    tasks_global = copy.deepcopy(tasks)
    
    t = threading.Thread(target=core)
    t.start()
    
    t.join()
