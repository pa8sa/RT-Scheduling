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

all_tasks: list[Task] = None

ready_queue = Queue()

R_lock = threading.Lock()

queue_lock = threading.Lock()

def wait_for_print():
    while globals.print_turn != 2:
        pass

    print_output()
    
    globals.print_turn_lock.acquire()
    globals.print_turn %= 4
    globals.print_turn += 1
    globals.print_turn_lock.release()

def print_output():
    global glob_R1, glob_R2, glob_task1, glob_task2, ready_queue
    print("Sub2:")
    print(f"\tR1: {glob_R1.count if glob_R1 else '-'} R2: {glob_R2.count if glob_R2 else '-'}")
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
    global all_tasks, ready_queue
    
    for task in all_tasks:
        ready_queue.put(task)

    task_list = list(all_tasks)
    task_list.sort(key=lambda task: task.duration)
    ready_queue = Queue()

    for task in task_list:
        if task.entering_time <= globals.time_unit + 1 and task.duration > 0:
            ready_queue.put(task)

finish_barrier = threading.Barrier(2, action=wait_for_print)

def core(index, resources: List[Resource_]):
    global ready_queue, glob_R1, glob_R2, glob_task1, glob_task2

    while True:
        if globals.time_unit == globals.breaking_point:
            return
        try:
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
            
            R_lock.acquire()
            if task.resource1_usage <= R1.count and task.resource2_usage <= R2.count:
                R1.count -= task.resource1_usage
                R2.count -= task.resource2_usage
            else:
                while True:
                    if task.resource1_usage <= R1.count and task.resource2_usage <= R2.count:
                        R1.count -= task.resource1_usage
                        R2.count -= task.resource2_usage
                        break
            R_lock.release()

            task.duration -= 1
            # print(f"\nTask {task.name} on core {index} with {task.duration} time remaining")

            if index == 0:
                glob_task1 = task
            elif index == 1:
                glob_task2 = task
            
            R_lock.acquire()
            R1.count += task.resource1_usage
            R2.count += task.resource2_usage
            R_lock.release()

            if task.duration == 0:
                task.state = 'completed'
                # print(f"\n[COMPLETED] Task {task.name} on core {index}")
                # print(f"\nTask {task.name} COMPLETED on core {index}")
            
            finish_barrier.wait()
            globals.global_finish_barrier.wait()
            
        except Exception as e:
            print(e)
            pass

def subSystem2(resources: List[Resource_], tasks: List[Task]):
    # return
    global ready_queue, all_tasks

    all_tasks = tasks
    
    for task in tasks:
        ready_queue.put(task)
            
    task_list = list(ready_queue.queue)
    task_list.sort(key=lambda task: task.duration)
    ready_queue = Queue()
    for task in task_list:
        if task.entering_time == 0:
            ready_queue.put(task)

    cores = []
    for i in range(2):
        t = threading.Thread(target=core, args=(i, resources))
        cores.append(t)
        t.start()
        
    for t in cores:
        t.join()
