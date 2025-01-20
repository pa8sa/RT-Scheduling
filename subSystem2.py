import globals
import threading
from typing import List
from queue import Queue
from task import Task
from resource_ import Resource_

timeunit = -1

glob_R1: Resource_ = None
glob_R2: Resource_ = None
glob_task1: Task = None
glob_task2: Task = None

def print_output():
    global timeunit, glob_R1, glob_R2, glob_task1, glob_task2, ready_queue
    print("---------------------------------------- time unit: ", timeunit)
    print("Sub2:")
    print(f"\tR1: {glob_R1.count} R2: {glob_R2.count}")
    print(f"\tReady Queue: {[task.name for task in list(ready_queue.queue)]}")
    print(f"\tEach Durations: {[task.duration for task in list(ready_queue.queue)]}")
    print(f"\tCore1:")
    print(f"\t\tRuning Task: {glob_task1.name if glob_task1 else 'idle'}")
    print(f"\t\tDuration Remaining: {glob_task1.duration if glob_task1 else '-'}")
    print(f"\tCore2:")
    print(f"\t\tRuning Task: {glob_task2.name if glob_task2 else 'idle'}")
    print(f"\t\tDuration Remaining: {glob_task2.duration if glob_task2 else '-'}")

def increment_time_unit():
    global timeunit
    timeunit += 1

start_barrier = threading.Barrier(2, increment_time_unit)
finish_barrier = threading.Barrier(2, print_output)

ready_queue = Queue()

R_lock = threading.Lock()

queue_lock = threading.Lock()

update_queue_var = 0
update_queue_lock = threading.Lock()

def core(index, resources: List[Resource_]):
    global ready_queue, update_queue_var, glob_R1, glob_R2, glob_task1, glob_task2, timeunit

    while True:
        if timeunit == 40:
            return
        try:
            start_barrier.wait()
            
            update_queue_lock.acquire()
            if update_queue_var == 0:
                update_queue_var = 1
            update_queue_lock.release()
            # while True:
            #     if update_queue_var == 0:
            #         break
            for _ in range(10000000):
                pass

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
            
        except Exception as e:
            print(e)
            pass

def subSystem2(resources: List[Resource_], tasks: List[Task]):
    # return
    global ready_queue, update_queue_var, timeunit
    
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
        
    local_time_unit = 0
    while True:
        if timeunit == 40:
            break
        if update_queue_var == 1 and local_time_unit == timeunit:
            # print(f"local time unit: {local_time_unit} , global time unit: {timeunit} , update_queue_var: {update_queue_var}")
            local_time_unit = timeunit + 1
            for task in tasks:
                ready_queue.put(task)

            task_list = list(tasks)
            task_list.sort(key=lambda task: task.duration)
            ready_queue = Queue()

            for task in task_list:
                if task.entering_time <= timeunit and task.duration > 0:
                    ready_queue.put(task)
            # print(f"ready queue: {[task.name for task in list(ready_queue.queue)]}")
            update_queue_lock.acquire()
            update_queue_var = 0
            update_queue_lock.release()
        
        
    for t in cores:
        t.join()
