import globals
import threading
import time
from typing import List
from queue import Queue
from task import Task
from resource_ import Resource_

R1_lock = threading.Lock()
R2_lock = threading.Lock()

waiting_queue = Queue()
ready_queue1 = Queue()
ready_queue2 = Queue()
ready_queue3 = Queue()

cores_finished = 0

index_to_ready_queue = {
    0: ready_queue1,
    1: ready_queue2,
    2: ready_queue3
}

QUANTUM = 1

def wait_to_start_together():
    while True:
        if globals.sys1_ready_threads == 3:
            break

def wait_to_finish_together():
    while True:
        if globals.sys1_finish_threads == 3:
            break

def get_quantum(task: Task):
    return QUANTUM * task.weight

def load_balancing(task: Task, is_first):
    if is_first:
        ready_queue = index_to_ready_queue[int(task.dest_cpu) - 1]
        ready_queue.put(task)
        task.state = 'ready'
    else:
        queue_sizes = [sum(task.duration for task in list(index_to_ready_queue[i].queue)) for i in range(3)]
        chosen_core = queue_sizes.index(min(queue_sizes)) 
        
        print(f"\nTask {task.name} assigned to core {chosen_core}")
        index_to_ready_queue[chosen_core].put(task)
        task.state = 'ready'

def core(index, resources: List[Resource_]):
    global waiting_queue, alive_tasks, cores_finished
    ready_queue = index_to_ready_queue[index]
    
    while True:
        try:
            globals.sys1_ready_threads_lock.acquire()
            if globals.sys1_ready_threads == 2:
                print(f"---------------------- time unit: {globals.time_unit}")
                globals.sys1_finish_threads = 0 + cores_finished
                globals.time_unit += 1
            globals.sys1_ready_threads += 1
            print(f"ready threads: {globals.sys1_ready_threads}")
            globals.sys1_ready_threads_lock.release()
            wait_to_start_together()
            R1 = resources[0]
            R2 = resources[1]
            task: Task = ready_queue.get(timeout=1) 
            task.state = 'running'
            if task.resource1_usage <= R1.count and task.resource2_usage <= R2.count:
                R1_lock.acquire()
                R2_lock.acquire()
                print(f"\nTask {task.name} acquired Resources")
            else:
                print(f"\nTask {task.name} is waiting for resources")
                task.state = 'waiting'
                waiting_queue.put(task)
                
                globals.sys1_finish_threads_lock.acquire()
                if globals.sys1_finish_threads == 2:
                    globals.sys1_ready_threads = 0 + cores_finished
                globals.sys1_finish_threads += 1
                print(f"finsihed threads: {globals.sys1_finish_threads} core {index} task {task.name}")
                globals.sys1_finish_threads_lock.release()
                wait_to_finish_together()
                
                continue

            exec_time = min(get_quantum(task), task.duration)
            task.duration -= exec_time

            R1_lock.release()
            R2_lock.release()
            
            globals.sys1_finish_threads_lock.acquire()
            if globals.sys1_finish_threads == 2:
                globals.sys1_ready_threads = 0 + cores_finished
            globals.sys1_finish_threads += 1
            print(f"finsihed threads: {globals.sys1_finish_threads} core {index} task {task.name}")
            globals.sys1_finish_threads_lock.release()
            wait_to_finish_together()

            if task.duration > 0:
                task.state = 'waiting'
                print(f"\nTask {task.name} went back to WAITING QUEUE with {task.duration} time remaining")
                waiting_queue.put(task)
            else:
                task.state = 'completed'
                print(f"\nTask {task.name} COMPLETED on core {index}")
                alive_tasks -=1

        except Exception as e:
            cores_finished += 1
            globals.sys1_finish_threads_lock.acquire()
            if globals.sys1_finish_threads == 2:
                globals.sys1_ready_threads = 0 + cores_finished
            globals.sys1_finish_threads += 1
            globals.sys1_finish_threads_lock.release()
            break

# handle krdn Starvation
def subSystem1(resources: List[Resource_], tasks: List[Task]):
    global ready_queue1, ready_queue2, ready_queue3, waiting_queue, alive_tasks
    
    number_of_tasks = len(tasks)
    alive_tasks = len(tasks)
    
    min_duration = min(task.duration for task in tasks)
    for task in tasks:
        task.weight = max(1, task.duration // min_duration)
    
    for task in tasks:
        waiting_queue.put(task)

    cores = []
    for i in range(3):
        t = threading.Thread(target=core, args=(i,resources))
        cores.append(t)
        t.start()
    
    is_first = 0
    
    while alive_tasks > 0:
        if not waiting_queue.empty():
            task = waiting_queue.get()
            load_balancing(task, is_first < number_of_tasks)
            is_first += 1
            
        # time.sleep(0.1)

    for t in cores:
        t.join()
