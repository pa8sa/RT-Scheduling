import globals
import threading
import time
from typing import List
from queue import Queue
from task import Task
from resource_ import Resource_

R_lock = threading.Lock()
alive_lock = threading.Lock()

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

def add_task_to_ready_queue(task: Task, is_first):
    if is_first:
        ready_queue = index_to_ready_queue[int(task.dest_cpu) - 1]
        ready_queue.put(task)
        task.state = 'ready'
    else:
        queue_sizes = [sum(task.duration for task in list(index_to_ready_queue[i].queue)) for i in range(3)]
        chosen_core = queue_sizes.index(min(queue_sizes)) 
        
        index_to_ready_queue[chosen_core].put(task)
        task.state = 'ready'
        
def push_migration():
    global ready_queue1, ready_queue2, ready_queue3
    
    if globals.time_unit % 2 != 0 :
        return
    
    queue_sizes = [
        ready_queue1.qsize(),
        ready_queue2.qsize(),
        ready_queue3.qsize()
    ]

    max_load_core = queue_sizes.index(max(queue_sizes))
    min_load_core = queue_sizes.index(min(queue_sizes))

    if queue_sizes[max_load_core] - queue_sizes[min_load_core] > 1:  
        source_queue = index_to_ready_queue[max_load_core]
        destination_queue = index_to_ready_queue[min_load_core]

        if not source_queue.empty():
            task = source_queue.get()
            destination_queue.put(task)
            print(
                f"\n [PUSH MIGRATION] Task {task.name} migrated from core {max_load_core} to core {min_load_core} for load balancing."
            )
    
def pull_migration(core_index):
    ready_queue = index_to_ready_queue[core_index]
    if not ready_queue.empty():
        return  
    
    queue_sizes = [
        ready_queue1.qsize(),
        ready_queue2.qsize(),
        ready_queue3.qsize()
    ]
    
    max_load_core = queue_sizes.index(max(queue_sizes))
    destination_queue = index_to_ready_queue[max_load_core]
    
    if destination_queue.qsize() - ready_queue.qsize() > 1:
        task = destination_queue.get()
        ready_queue.put(task)
        print(
            f"\n [PULL MIGRATION] Task {task.name} migrated from core {max_load_core} to core {core_index} for load balancing."
        )


def core(index, resources: List[Resource_]):
    global waiting_queue, alive_tasks, cores_finished
    
    while True:
        ready_queue = index_to_ready_queue[index]
        try:
            globals.sys1_ready_threads_lock.acquire()
            pull_migration(index)
            if globals.sys1_ready_threads == 2:
                push_migration()
                print(f"---------------------------------------------------------------------------------------- time unit: {globals.time_unit}")
                globals.sys1_finish_threads = 0 + cores_finished
                globals.time_unit += 1
            globals.sys1_ready_threads += 1
            globals.sys1_ready_threads_lock.release()
            wait_to_start_together()
            
            R1 = resources[0]
            R2 = resources[1]
            if ready_queue.empty():
                globals.sys1_finish_threads_lock.acquire()
                if globals.sys1_finish_threads == 2:
                    globals.sys1_ready_threads = 0 + cores_finished
                globals.sys1_finish_threads += 1
                globals.sys1_finish_threads_lock.release()
                wait_to_finish_together()
                continue
            
            task: Task = ready_queue.get()
            task.state = 'running'
            print (f"\n [RUNNING] Task {task.name} is RUNNING on core {index}")
            with R_lock:
                if task.resource1_usage <= R1.count and task.resource2_usage <= R2.count:
                    R1.count -= task.resource1_usage
                    R2.count -= task.resource2_usage
                else:
                    task.state = 'waiting'
                    waiting_queue.put(task)
                    
                    globals.sys1_finish_threads_lock.acquire()
                    if globals.sys1_finish_threads == 2:
                        globals.sys1_ready_threads = 0 + cores_finished
                    globals.sys1_finish_threads += 1
                    globals.sys1_finish_threads_lock.release()
                    wait_to_finish_together()
                    
                    continue

            exec_time = min(get_quantum(task), task.duration)
            task.duration -= exec_time

            with R_lock:
                R1.count += task.resource1_usage
                R2.count += task.resource2_usage

            if task.duration > 0:
                task.state = 'waiting'
                print(f"\n [WAITING QUEUE] Task {task.name} went back to WAITING QUEUE with {task.duration} time remaining")
                waiting_queue.put(task)
            else:
                with alive_lock:
                    alive_tasks -= 1
                task.state = 'completed'
                print(f"\n [COMPLETED] Task {task.name} COMPLETED on core {index}")

                
            globals.sys1_finish_threads_lock.acquire()
            if globals.sys1_finish_threads == 2:
                globals.sys1_ready_threads = 0 + cores_finished
            globals.sys1_finish_threads += 1
            globals.sys1_finish_threads_lock.release()
            
            wait_to_finish_together()
            
        except Exception as e:
            cores_finished += 1
            globals.sys1_finish_threads_lock.acquire()
            if globals.sys1_finish_threads == 2:
                globals.sys1_ready_threads = 0 + cores_finished
            globals.sys1_finish_threads += 1
            globals.sys1_finish_threads_lock.release()
            print(f'{index} EXCEPTION:  {e}')
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
    
    while True:
        with alive_lock:
            if alive_tasks == 0:
                print(f'\n [FINISHED] subsystem 1')
                break
            
        if not waiting_queue.empty():
            task = waiting_queue.get()
            add_task_to_ready_queue(task, is_first < number_of_tasks)
            is_first += 1
            
    for t in cores:
        t.join()
