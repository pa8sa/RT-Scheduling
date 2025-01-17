import globals
import threading
from typing import List
from queue import Queue
from task import Task
from resource_ import Resource_

ready_queue = Queue()

R1_lock = threading.Lock()
R2_lock = threading.Lock()

queue_lock = threading.Lock()

def start_wait():
    globals.subsystems_ready_cycle_lock.acquire()
    globals.sys2_ready_threads_lock.acquire()

    globals.sys2_ready_threads += 1
    if globals.sys2_ready_threads == 2:
        globals.sys2_finish_threads = 0
        if globals.subsystems_ready_cycle == 1:
            globals.subsystems_finish_cycle = 0
            globals.time_unit += 1
            print(f"---------------------------------------------------------------------------------------- time unit: {globals.time_unit}")
        globals.subsystems_ready_cycle += 1
    print(f"ready threads: {globals.sys2_ready_threads}")

    globals.sys2_ready_threads_lock.release()
    globals.subsystems_ready_cycle_lock.release()

    globals.wait_for_subsystems_start_together()

def finish_wait():
    globals.subsystems_finish_cycle_lock.acquire()
    globals.sys2_finish_threads_lock.acquire()

    globals.sys2_finish_threads += 1
    if globals.sys2_finish_threads == 2:
        globals.sys2_ready_threads = 0
        if globals.subsystems_finish_cycle == 1:
            globals.subsystems_ready_cycle = 0
        globals.subsystems_finish_cycle += 1
    # print(f"finsihed threads: {globals.sys2_finish_threads} core {index} task {task.name}")

    globals.sys2_finish_threads_lock.release()
    globals.subsystems_finish_cycle_lock.release()

    globals.wait_for_subsystems_finish_together()

def core(index, resources: List[Resource_]):
    global ready_queue

    while True:
        if globals.time_unit == 40:
            return
        try:
            start_wait()
            
            R1 = resources[0]
            R2 = resources[1]

            queue_lock.acquire()
            if ready_queue.qsize() > 0:
                task: Task = ready_queue.get()
                task.state = 'running'            
            else:
                queue_lock.release()
                finish_wait()
                continue
            queue_lock.release()
            
            if task.resource1_usage <= R1.count and task.resource2_usage <= R2.count:
                R1_lock.acquire()
                R2_lock.acquire()
                # print(f"\nTask {task.name} acquired Resources")
            else:
                # print(f"\nTask {task.name} is waiting for resources")
                task.state = 'waiting'
                
            task.duration -= 1
            print(f"\nTask {task.name} on core {index} with {task.duration} time remaining")
            
            R1_lock.release()
            R2_lock.release()
            
            if task.duration > 0:
                queue_lock.acquire()
                task.state = 'waiting'
                ready_queue.put(task)
                
                task_list = list(ready_queue.queue)
                task_list.sort(key=lambda task: task.duration)
                ready_queue = Queue()
                for task in task_list:
                    ready_queue.put(task)

                queue_lock.release()
                # print(f"\nTask {task.name} went back to WAITING QUEUE with {task.duration} time remaining")
            else:
                task.state = 'completed'
                print(f"\n[COMPLETED] Task {task.name} on core {index}")
                # print(f"\nTask {task.name} COMPLETED on core {index}")
            
            finish_wait()
            
        except Exception as e:
            print(e)
            pass

def subSystem2(resources: List[Resource_], tasks: List[Task]):
    global ready_queue
    
    for task in tasks:
        ready_queue.put(task)
            
    task_list = list(ready_queue.queue)
    task_list.sort(key=lambda task: task.duration)
    ready_queue = Queue()
    for task in task_list:
        ready_queue.put(task)

    cores = []
    for i in range(2):
        t = threading.Thread(target=core, args=(i, resources))
        cores.append(t)
        t.start()
        
    # add tasks to queue based on entry time and sort based on duration remaining
        
    for t in cores:
        t.join()
