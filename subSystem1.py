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

index_to_ready_queue = {
    0: ready_queue1,
    1: ready_queue2,
    2: ready_queue3
}

QUANTUM = 0.5

core_load = [0, 0, 0]
core_weights = [1, 1, 1]

def weighted_round_robin(task: Task):
    global core_load
    min_load = float('inf')
    chosen_core = -1

    for i in range(3):
        effective_load = core_load[i] / core_weights[i]
        if effective_load < min_load:
            min_load = effective_load
            chosen_core = i

    core_load[chosen_core] += 1
    index_to_ready_queue[chosen_core].put(task)
    task.state = 'ready'
    print(f"Task {task.name} assigned to core {chosen_core}")
    return chosen_core

def core(index, resources: List[Resource_]):
    ready_queue = index_to_ready_queue[index]
    
    while True:
        try:
            R1 = resources[0]
            R2 = resources[1]
            task: Task = ready_queue.get(timeout=1) 
            task.state = 'running'
            print(f'\nR usage {task.resource1_usage, task.resource2_usage} count {R1.count, R2.count}\n')
            # check if resources are available
            if task.resource1_usage <= R1.count and task.resource2_usage <= R2.count:
                R1_lock.acquire()
                R2_lock.acquire()
                print(f"Task {task.name} acquired Resources")
            # if resources are not available, put the task back in the waiting queue
            else:
                print(f"Task {task.name} is waiting for resources")
                task.state = 'waiting'
                waiting_queue.put(task)
                continue

            exec_time = min(QUANTUM, task.remaining_duration)
            # time.sleep(exec_time)
            print(f'before exec {task.remaining_duration}')
            task.remaining_duration -= exec_time
            print(f'after exec {task.remaining_duration}')

            R1_lock.release()
            R2_lock.release()

            if task.remaining_duration > 0:
                task.state = 'waiting'
                print(f"Task {task.name} preempted with {task.remaining_duration} time remaining")
                ready_queue.put(task)
            else:
                task.state = 'completed'
                print(f"Task {task.name} completed on core {index}")

        except Exception as e:
            break

# handle krdn Starvation
def subSystem1(resources: List[Resource_], tasks: List[Task]):
    global ready_queue1, ready_queue2, ready_queue3, waiting_queue

    number_of_tasks = len(tasks)
    for task in tasks:
        waiting_queue.put(task)

    cores = []
    for i in range(3):
        t = threading.Thread(target=core, args=(i,resources))
        cores.append(t)
        t.start()
    
    is_first = 0
    while not waiting_queue.empty():
        task = waiting_queue.get()
        
        if is_first < number_of_tasks:
            # print(f"Task {task.name} assigned to {int(task.dest_cpu) - 1}")
            index_to_ready_queue[int(task.dest_cpu) - 1].put(task)
            task.state = 'ready'
            is_first += 1
    
        else:
            weighted_round_robin(task)

    for t in cores:
        t.join()
