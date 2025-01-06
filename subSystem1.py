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

def core(index):
    while True:
        try:
            task: Task = index_to_ready_queue[index].get(timeout=1) 
            task.state = 'running'
            print(f"Core {index} running task {task.name}")

            if task.resource1_usage:
                R1_lock.acquire()
                print(f"Task {task.name} acquired R1")
            if task.resource2_usage:
                R2_lock.acquire()
                print(f"Task {task.name} acquired R2")

            exec_time = min(QUANTUM, task.remaining_duration)
            # time.sleep(exec_time)
            task.remaining_duration -= exec_time

            if task.resource1_usage:
                print(f"Task {task.name} released R1")
                R1_lock.release()
            if task.resource2_usage:
                print(f"Task {task.name} released R2")
                R2_lock.release()

            if task.remaining_duration > 0:
                task.state = 'waiting'
                print(f"Task {task.name} preempted with {task.remaining_duration} time remaining")
                waiting_queue.put(task)
            else:
                task.state = 'completed'
                print(f"Task {task.name} completed on core {index}")
                core_load[index] -= 1

        except Exception as e:
            break

def subSystem1(resources: List[Resource_], tasks: List[Task]):
    global ready_queue1, ready_queue2, ready_queue3, waiting_queue

    tasks = sorted(tasks, key=lambda x: x.entering_time)
    for task in tasks:
        waiting_queue.put(task)

    cores = []
    for i in range(3):
        t = threading.Thread(target=core, args=(i,))
        cores.append(t)
        t.start()
    
    is_first = 0
    while not waiting_queue.empty():
        if is_first <= 3:
            core_load[int(task.dest_cpu) - 1] += 1
            index_to_ready_queue[int(task.dest_cpu) - 1].put(task)
            task.state = 'ready'
            is_first += 1
    
        else:
            if not waiting_queue.empty():
                task = waiting_queue.get()
                weighted_round_robin(task)

    for t in cores:
        t.join()
