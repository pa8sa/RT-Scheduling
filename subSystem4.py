import globals
import threading
import random
from typing import List
from queue import Queue
from task import Task
from resource_ import Resource_

all_tasks = None

glob_R1: Resource_ = None
glob_R2: Resource_ = None
glob_task1: Task = None
glob_task2: Task = None

ready_queue = Queue()
waiting_queue = Queue()

completed_tasks = []

queue_lock = threading.Lock()
R_lock = threading.Lock()

def wait_for_print():
    while globals.print_turn != 4:
        pass

    print_output()
    
    globals.print_turn_lock.acquire()
    globals.print_turn %= 4
    globals.print_turn += 1
    globals.print_turn_lock.release()

def print_output():
    global glob_R1, glob_R2, glob_task1, glob_task2
    print("Sub4:")
    print(f"\tR1: {glob_R1.count if glob_R1 else '-'} R2: {glob_R2.count if glob_R2 else '-'}")
    print(f"\tWaiting Queue: {[task.name for task in list(waiting_queue.queue)]}")
    print(f"\tReady Queue: {[task.name for task in list(ready_queue.queue)]}")
    print(f"\tEach Durations: {[task.duration for task in list(ready_queue.queue)]}")
    print(f"\tCore1:")
    print(f"\t\tRunning Task: {glob_task1.name if glob_task1 else 'idle'}")
    print(f"\t\tDuration Remaining: {glob_task1.duration if glob_task1 else '-'}")
    print(f"\tCore2:")
    print(f"\t\tRunning Task: {glob_task2.name if glob_task2 else 'idle'}")
    print(f"\t\tDuration Remaining: {glob_task2.duration if glob_task2 else '-'}")
    
    update_queue()
    
def update_queue():
    global ready_queue, waiting_queue
    if not waiting_queue.empty():
        task = waiting_queue.get()
        task.state = 'ready'
        ready_queue.put(task)
    for i in range(len(all_tasks)):
        if all_tasks[i].entering_time == globals.time_unit + 1:
            ready_queue.put(all_tasks[i])
            all_tasks[i].state = 'ready'
    
    sorted_list = sorted(list(ready_queue.queue), key=lambda task: (task.entering_time, task.duration))
    ready_queue = Queue()
    for task in sorted_list:
        ready_queue.put(task)

finish_barrier = threading.Barrier(2, action=wait_for_print)

def core(index, resources: List[Resource_]):
    # return
    global ready_queue, waiting_queue, glob_R1, glob_R2, glob_task1, glob_task2
    
    while True:
        if globals.time_unit == globals.breaking_point:
            return
        
        globals.global_start_barrier.wait()
        
        R1 = resources[0]
        R2 = resources[1]

        glob_R1 = R1
        glob_R2 = R2
        
        queue_lock.acquire()
        if not ready_queue.empty():
            task = None
            for _ in range(ready_queue.qsize()):
                task: Task = ready_queue.get()
                if task.prerequisite_task_name is None or task.prerequisite_task_name in [task.name for task in completed_tasks]:
                    task.state = 'running'
                    break
                else:
                    ready_queue.put(task)
                    task = None
            if not task:
                if index == 0:
                    glob_task1 = None
                elif index == 1:
                    glob_task2 = None
                    
                queue_lock.release()
                finish_barrier.wait()
                globals.global_finish_barrier.wait()
                continue
        else:
            if index == 0:
                glob_task1 = None
            elif index == 1:
                glob_task2 = None
                
            queue_lock.release()
            finish_barrier.wait()
            globals.global_finish_barrier.wait()
            continue
        queue_lock.release()
        
        # print(f"core {index} running task: {task.name}")
        
        R_lock.acquire()
        if task.resource1_usage <= R1.count and task.resource2_usage <= R2.count:
            R1.count -= task.resource1_usage
            R2.count -= task.resource2_usage
        else:
            task.state = 'waiting'
            print(f"task {task.name} is waiting R1: {R1.count} R2: {R2.count} +++++++++++++++++++++++++++++")
            waiting_queue.put(task)

            if index == 0:
                glob_task1 = None
            elif index == 1:
                glob_task2 = None
            
            R_lock.release()
            finish_barrier.wait()
            globals.global_finish_barrier.wait()
            
            continue
        R_lock.release()

        random_number = random.randint(1, 10)
        if random_number <= 3:
            if index == 0:
                glob_task1 = Task(name=f'failed to run {task.name}')
            elif index == 1:
                glob_task2 = Task(name=f'failed to run {task.name}')

            with R_lock:
                R1.count += task.resource1_usage
                R2.count += task.resource2_usage
            
            queue_lock.acquire()
            ready_queue.put(task)
            queue_lock.release()
            
            finish_barrier.wait()
            globals.global_finish_barrier.wait()
            continue
        
        task.duration -= 1
        
        if index == 0:
            glob_task1 = task
        elif index == 1:
            glob_task2 = task
        
        with R_lock:
            R1.count += task.resource1_usage
            R2.count += task.resource2_usage
        
        if task.duration == 0:
            task.state = 'completed'
            queue_lock.acquire()
            completed_tasks.append(task)
            queue_lock.release()
        elif task.duration > 0:
            queue_lock.acquire()
            ready_queue.queue.appendleft(task)
            queue_lock.release()
        
        finish_barrier.wait()
        globals.global_finish_barrier.wait()

def subSystem4(resources: List[Resource_], tasks: List[Task]):
    global ready_queue, waiting_queue, all_tasks

    all_tasks = tasks

    for task in tasks:
        if task.entering_time == 0:
            ready_queue.put(task)

    sorted_list = sorted(list(ready_queue.queue), key=lambda task: (task.entering_time, task.duration))
    ready_queue = Queue()
    for task in sorted_list:
        ready_queue.put(task)
            
    cores = []
    for i in range(2):
        t = threading.Thread(target=core, args=(i, resources))
        cores.append(t)
        t.start()
        
    for t in cores:
        t.join()
