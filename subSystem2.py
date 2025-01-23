import globals
import threading
from typing import List
from queue import Queue
from task import Task
from resource_ import Resource_

glob_task1: Task = None
glob_task2: Task = None

ready_queue = Queue()

queue_lock = threading.Lock()

update_queue_var = 0
update_queue_lock = threading.Lock()

def wait_for_print():
    while globals.print_turn != 2:
        pass

    print_output()
    
    globals.print_turn_lock.acquire()
    globals.print_turn %= 4
    globals.print_turn += 1
    globals.print_turn_lock.release()

def print_output():
    global glob_task1, glob_task2, ready_queue
    print("Sub2:")
    print(f"\tR1: {globals.sub2_resources[0].count if globals.sub2_resources[0] else '-'} R2: {globals.sub2_resources[1].count if globals.sub2_resources[1] else '-'}")
    print(f"\tReady Queue: {[task.name for task in list(ready_queue.queue)]}")
    print(f"\tEach Durations: {[task.duration for task in list(ready_queue.queue)]}")
    print(f"\tCore1:")
    print(f"\t\tRunning Task: {glob_task1.name if glob_task1 else 'idle'}")
    print(f"\t\tDuration Remaining: {glob_task1.duration if glob_task1 else '-'}")
    print(f"\tCore2:")
    print(f"\t\tRunning Task: {glob_task2.name if glob_task2 else 'idle'}")
    print(f"\t\tDuration Remaining: {glob_task2.duration if glob_task2 else '-'}")

finish_barrier = threading.Barrier(2, action=wait_for_print)

def core(index):
    global ready_queue, update_queue_var, glob_task1, glob_task2

    while True:
        if globals.time_unit == globals.breaking_point:
            return
        try:
            globals.global_start_barrier.wait()
            
            update_queue_lock.acquire()
            if update_queue_var == 0:
                update_queue_var = 1
            update_queue_lock.release()
            # while True:
            #     if update_queue_var == 0:
            #         break
            for _ in range(10000000):
                pass

            R1 = globals.sub2_resources[0]
            R2 = globals.sub2_resources[1]

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
            
            globals.sub2_resource_lock.acquire()
            if task.resource1_usage <= R1.count and task.resource2_usage <= R2.count:
                R1.count -= task.resource1_usage
                R2.count -= task.resource2_usage
            else:
                while True:
                    if task.resource1_usage <= R1.count and task.resource2_usage <= R2.count:
                        R1.count -= task.resource1_usage
                        R2.count -= task.resource2_usage
                        break
            globals.sub2_resource_lock.release()

            task.duration -= 1
            # print(f"\nTask {task.name} on core {index} with {task.duration} time remaining")

            if index == 0:
                glob_task1 = task
            elif index == 1:
                glob_task2 = task
            
            globals.sub2_resource_lock.acquire()
            R1.count += task.resource1_usage
            R2.count += task.resource2_usage
            globals.sub2_resource_lock.release()

            if task.duration == 0:
                task.state = 'completed'
                # print(f"\n[COMPLETED] Task {task.name} on core {index}")
                # print(f"\nTask {task.name} COMPLETED on core {index}")
            
            finish_barrier.wait()
            globals.global_finish_barrier.wait()
            
        except Exception as e:
            print(e)
            pass

def subSystem2(tasks: List[Task]):
    global ready_queue, update_queue_var
    
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
        t = threading.Thread(target=core, args=(i, ))
        cores.append(t)
        t.start()
        
    local_time_unit = 0
    while True:
        if globals.time_unit == globals.breaking_point:
            break
        if update_queue_var == 1 and local_time_unit == globals.time_unit:
            # print(f"local time unit: {local_time_unit} , global time unit: {timeunit} , update_queue_var: {update_queue_var}")
            local_time_unit = globals.time_unit + 1
            for task in tasks:
                ready_queue.put(task)

            task_list = list(tasks)
            task_list.sort(key=lambda task: task.duration)
            ready_queue = Queue()

            for task in task_list:
                if task.entering_time <= globals.time_unit and task.duration > 0:
                    ready_queue.put(task)
            # print(f"ready queue: {[task.name for task in list(ready_queue.queue)]}")
            update_queue_lock.acquire()
            update_queue_var = 0
            update_queue_lock.release()
        
        
    for t in cores:
        t.join()
