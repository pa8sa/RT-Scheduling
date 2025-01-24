import globals
import threading
from typing import List
from queue import Queue
from task import Task
from resource_ import Resource_
import copy

glob_task1: Task = None
glob_task2: Task = None
glob_task3: Task = None

alive_lock = threading.Lock()
wait_lock = threading.Lock()
comp_lock = threading.Lock()

waiting_queue = Queue()
ready_queue1 = Queue()
ready_queue2 = Queue()
ready_queue3 = Queue()

completed_tasks = []

cores_finished = 0

def wait_for_print():
    while globals.print_turn != 1:
        pass

    print_output()
    
    globals.print_turn_lock.acquire()
    globals.print_turn %= 4
    globals.print_turn += 1
    globals.print_turn_lock.release()

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

def add_to_waiting_queue(task: Task):
    global waiting_queue
    temp_list = []
    while not waiting_queue.empty():
        temp_list.append(waiting_queue.get())

    temp_list.append(task)

    temp_list.sort(key=lambda t: (t.age + t.entering_time))

    for sorted_task in temp_list:
        waiting_queue.put(sorted_task)

def read_from_waiting_queue():
    global waiting_queue, number_of_tasks, is_first
    
    while not waiting_queue.empty():
        task = waiting_queue.get()
        if task.entering_time <= globals.time_unit+1 and task.duration > 0:
            add_task_to_ready_queue(task, is_first < number_of_tasks)
            is_first += 1
        else:
            add_to_waiting_queue(task)

def print_output():
    global glob_task1, glob_task2, glob_task3, ready_queue1, ready_queue2, ready_queue3, waiting_queue, completed_tasks, number_of_tasks
    print("------------------------------------------------- time unit:", globals.time_unit, "-------------------------------------------------")
    print("Sub1:")
    print(f"\tR1: {globals.sub1_resources[0].count if globals.sub1_resources[0] else '-'} R2: {globals.sub1_resources[1].count if globals.sub1_resources[1] else '-'}")
    print(f"\tWaiting Queue: {[task.name if task.entering_time<= globals.time_unit and task.state == 'waiting' else '' for task in list(waiting_queue.queue)]}")
    
    print(f"\tCore1:")
    print(f"\t\tRunning Task: {glob_task1.name  if glob_task1 and glob_task1.state=='running' else 'idle'}")
    print(f"\t\tReady Queue: {[task.name if task.state=='ready' else '' for task in list(ready_queue1.queue)]}")
    
    print(f"\tCore2:")
    print(f"\t\tRunning Task: {glob_task2.name if glob_task2 and glob_task2.state=='running' else 'idle'}")
    print(f"\t\tReady Queue: {[task.name if task.state=='ready' else '' for task in list(ready_queue2.queue)]}")
    
    print(f"\tCore3:")
    print(f"\t\tRunning Task: {glob_task3.name if glob_task3 and glob_task3.state=='running' else 'idle'}")
    print(f"\t\tReady Queue: {[task.name if task.state=='ready' else '' for task in list(ready_queue3.queue)]}")
    print(f"\tCompleted Tasks: \n\t\t{[task.name if task.state=='completed' else '' for task in list(completed_tasks)]}")
    
    read_from_waiting_queue()

finish_barrier = threading.Barrier(3, action=wait_for_print)

index_to_ready_queue = {
    0: ready_queue1,
    1: ready_queue2,
    2: ready_queue3
}

QUANTUM = 1

def get_quantum(task: Task):
    return QUANTUM * task.weight

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
            # print(
            #     f"\n [PUSH MIGRATION] Task {task.name} migrated from core {max_load_core} to core {min_load_core} for load balancing."
            # )

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
        # print(
        #     f"\n [PULL MIGRATION] Task {task.name} migrated from core {max_load_core} to core {core_index} for load balancing."
        # )

def core(index):
    global waiting_queue, alive_tasks, cores_finished, glob_task1, glob_task2, glob_task3
    
    how_many_rounds = -1
    prev_task = None
    
    while True:
        if globals.time_unit == globals.breaking_point:
            return
        ready_queue = index_to_ready_queue[index]
        try:
            globals.global_start_barrier.wait()
            #! ============================================================= START ===================================================================
            
            R1 = globals.sub1_resources[0]
            R2 = globals.sub1_resources[1]

            if ready_queue.empty() and prev_task is None:
                if index == 0:
                    glob_task1 = None
                elif index == 1:
                    glob_task2 = None
                elif index == 2:
                    glob_task3 = None
                
                finish_barrier.wait()
                globals.global_finish_barrier.wait()
                continue
            
            if prev_task is None:
                task: Task = ready_queue.get()
                task.state = 'running'
            else:
                task = prev_task
                task.state = 'running'
            
            # print (f"\n [RUNNING] Task {task.name} is RUNNING on core {index}")
            with globals.sub1_resource_lock:
                if task.resource1_usage <= R1.count and task.resource2_usage <= R2.count:
                    R1.count -= task.resource1_usage
                    R2.count -= task.resource2_usage
                else:
                    task.state = 'waiting'
                    add_to_waiting_queue(task)

                    if index == 0:
                        glob_task1 = None
                    elif index == 1:
                        glob_task2 = None
                    elif index == 2:
                        glob_task3 = None

                    finish_barrier.wait()
                    globals.global_finish_barrier.wait()
                    globals.sub1_resource_lock.release()
                    continue
            
            if how_many_rounds < 0:
                how_many_rounds = get_quantum(task)
                prev_task = task
            
                
            exec_time = min(1, task.duration)
            task.duration -= exec_time
            how_many_rounds -= 1
            
            if index == 0:
                glob_task1 = copy.deepcopy(task)
            elif index == 1:
                glob_task2 = copy.deepcopy(task)
            elif index == 2:
                glob_task3 = copy.deepcopy(task)

            with globals.sub1_resource_lock:
                R1.count += task.resource1_usage
                R2.count += task.resource2_usage
            
            if how_many_rounds == 0 or task.duration <= 0:
                prev_task = None
                how_many_rounds = -1
                
            if prev_task is not None :
                # print(f'\n [NEXT ROUND] TASK {task.name} Went for the Next Round. how_many_rounds: {how_many_rounds} task.duration: {task.duration}')
                pass
            elif task.duration > 0:
                prev_task = None
                task.state = 'waiting'
                # print(f"\n [WAITING QUEUE] Task {task.name} went back to WAITING QUEUE with {task.duration} time remaining")
                add_to_waiting_queue(task)
            else:
                prev_task = None
                with alive_lock:
                    alive_tasks -= 1
                task.state = 'completed'
                with comp_lock:
                    completed_tasks.append(task)
                # print(f"\n [COMPLETED] Task {task.name} COMPLETED on core {index}")
                
                
            finish_barrier.wait()
            globals.global_finish_barrier.wait()
            #! ============================================================= END ===================================================================
            
        except Exception as e:
            cores_finished += 1
            finish_barrier.wait()
            globals.global_finish_barrier.wait()
            print(f'{index} EXCEPTION:  {e}')
            break

def increment_tasks_age():
    global waiting_queue

    temp_list = []
    while not waiting_queue.empty():
        task = waiting_queue.get()
        if(task.entering_time <= globals.time_unit):
            task.age=1
        temp_list.append(task)

    for task in temp_list:
        add_to_waiting_queue(task)

def subSystem1(tasks: List[Task]):
    global ready_queue1, ready_queue2, ready_queue3, waiting_queue, alive_tasks, number_of_tasks, is_first
    
    number_of_tasks = len(tasks)
    alive_tasks = len(tasks)
    
    min_duration = min(task.duration for task in tasks)
    for task in tasks:
        task.age=0
        task.weight = max(1, task.duration // min_duration)
        
    cores = []
    for i in range(3):
        t = threading.Thread(target=core, args=(i,))
        cores.append(t)
        t.start()
    
    for task in tasks:
        waiting_queue.put(task) 
        
    is_first = 0
    
    read_from_waiting_queue()
    
    # while True:
    #     with alive_lock:
    #         if alive_tasks == 0:
    #             # print(f'\n +++++++++++++++++++++++++++ [FINISHED] subsystem 1')
    #             break
            
        # if not waiting_queue.empty():
        #     task:Task = waiting_queue.get()
            
        #     if task.entering_time <= globals.time_unit and task.duration > 0:
        #         add_task_to_ready_queue(task, is_first < number_of_tasks)
        #         is_first += 1
        #     else:
        #         add_to_waiting_queue(task)
            
    for t in cores:
        t.join()
