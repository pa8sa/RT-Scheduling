import globals
import threading
from typing import List
from queue import Queue
from task import Task
from resource_ import Resource_

glob_R1: Resource_ = None
glob_R2: Resource_ = None
glob_task1: Task = None
glob_task2: Task = None

ready_queue = Queue()
waiting_queue = Queue()

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
    print(f"\tReady Queue: {[task.duration for task in list(ready_queue.queue)]}")
    print(f"\tCore1:")
    print(f"\t\tRunning Task: {glob_task1.name if glob_task1 else 'idle'}")
    print(f"\tCore2:")
    print(f"\t\tRunning Task: {glob_task2.name if glob_task2 else 'idle'}")

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
            task: Task = ready_queue.get()
            task.state = 'running'
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
        elif task.duration > 0:
            ready_queue.put(task)
        
        finish_barrier.wait()
        globals.global_finish_barrier.wait()

def subSystem4(resources: List[Resource_], tasks: List[Task]):
    global ready_queue, waiting_queue

    for task in tasks:
        # if task.entering_time == 0:
        ready_queue.put(task)
            
    cores = []
    for i in range(2):
        t = threading.Thread(target=core, args=(i, resources))
        cores.append(t)
        t.start()
        
    for t in cores:
        t.join()
