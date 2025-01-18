import globals
import threading
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

core1_running_task: Task = None
core2_running_task: Task = None
core3_running_task: Task = None

index_to_ready_queue = {
    0: ready_queue1,
    1: ready_queue2,
    2: ready_queue3
}

QUANTUM = 1

def start_wait(index):
    globals.subsystems_ready_cycle_lock.acquire()
    globals.sys1_ready_threads_lock.acquire()

    pull_migration(index)
    globals.sys1_ready_threads += 1
    if globals.sys1_ready_threads == 3:
        push_migration()
        globals.sys1_finish_threads = 0 + cores_finished
        if globals.subsystems_ready_cycle == 1:
            globals.subsystems_finish_cycle = 0
            globals.time_unit += 1
            print(f"---------------------------------------------------------------------------------------- time unit: {globals.time_unit}")
        globals.subsystems_ready_cycle += 1
            

    globals.sys1_ready_threads_lock.release()
    globals.subsystems_ready_cycle_lock.release()
    
    globals.wait_for_subsystems_start_together()

def finish_wait(R1: Resource_, R2: Resource_, task1: Task, task2: Task, task3: Task):
    globals.subsystems_finish_cycle_lock.acquire()
    globals.sys1_finish_threads_lock.acquire()

    globals.sys1_finish_threads += 1
    if globals.sys1_finish_threads == 3:
        globals.sys1_ready_threads = 0 + cores_finished
        if globals.subsystems_finish_cycle == 1:
            globals.subsystems_ready_cycle = 0
        print_output(R1=R1, R2=R2, task1=task1, task2=task2, task3=task3)
        globals.print_output_turn_lock.acquire()
        globals.print_output_turn = 2
        globals.print_output_turn_lock.release()
        globals.subsystems_finish_cycle += 1

    globals.sys1_finish_threads_lock.release()
    globals.subsystems_finish_cycle_lock.release()

    globals.wait_for_subsystems_finish_together()

def print_output(R1: Resource_, R2: Resource_, task1: Task, task2: Task, task3: Task):
    print("Sub1:")
    print(f"\tR1: {R1.count} R2: {R2.count}")
    print(f"\tWaiting Queue: {[task.name for task in list(waiting_queue.queue)]}")
    print(f"\tCore1:")
    print(f"\t\tRuning Task: {task1.name if task1 else 'idle'}")
    print(f"\t\tReady Queue: {[task.name for task in list(ready_queue1.queue)]}")
    print(f"\tCore2:")
    print(f"\t\tRuning Task: {task2.name if task2 else 'idle'}")
    print(f"\t\tReady Queue: {[task.name for task in list(ready_queue2.queue)]}")
    print(f"\tCore3:")
    print(f"\t\tRuning Task: {task3.name if task3 else 'idle'}")
    print(f"\t\tReady Queue: {[task.name for task in list(ready_queue3.queue)]}")

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

def core(index, resources: List[Resource_]):
    global waiting_queue, alive_tasks, cores_finished, core1_running_task, core2_running_task, core3_running_task
    
    how_many_rounds = -1
    prev_task = None
    
    while True:
        if globals.time_unit == 40:
            return
        ready_queue = index_to_ready_queue[index]
        try:
            start_wait(index)
            #! ============================================================= START ===================================================================
            
            R1 = resources[0]
            R2 = resources[1]
            if ready_queue.empty() and prev_task is None:
                finish_wait(R1=R1, R2=R2, task1=core1_running_task, task2=core2_running_task, task3=core3_running_task)
                continue
            
            if prev_task is None:
                task: Task = ready_queue.get()
                task.state = 'running'
            else:
                task = prev_task
                
            # print (f"\n [RUNNING] Task {task.name} is RUNNING on core {index}")
            with R_lock:
                
                if task.resource1_usage <= R1.count and task.resource2_usage <= R2.count:
                    R1.count -= task.resource1_usage
                    R2.count -= task.resource2_usage
                else:
                    task.state = 'waiting'
                    waiting_queue.put(task)
                    
                    finish_wait(R1=R1, R2=R2, task1=core1_running_task, task2=core2_running_task, task3=core3_running_task)
                    
                    continue
            
            if how_many_rounds < 0:
                how_many_rounds = get_quantum(task)
                prev_task = task
            
                
            exec_time = min(1, task.duration)
            task.duration -= exec_time
            how_many_rounds -= 1
            
            if index == 0:
                core1_running_task = task
            elif index == 1:
                core2_running_task = task
            elif index == 2:
                core3_running_task = task

            with R_lock:
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
                waiting_queue.put(task)
            else:
                prev_task = None
                with alive_lock:
                    alive_tasks -= 1
                task.state = 'completed'
                # print(f"\n [COMPLETED] Task {task.name} COMPLETED on core {index}")
                
                
            finish_wait(R1=R1, R2=R2, task1=core1_running_task, task2=core2_running_task, task3=core3_running_task)
            #! ============================================================= END ===================================================================
            
        except Exception as e:
            cores_finished += 1
            globals.sys1_finish_threads_lock.acquire()
            if globals.sys1_finish_threads == 2:
                globals.sys1_ready_threads = 0 + cores_finished
            globals.sys1_finish_threads += 1
            globals.sys1_finish_threads_lock.release()
            print(f'{index} EXCEPTION:  {e}')
            break
# Arrival time
def subSystem1(resources: List[Resource_], tasks: List[Task]):
    global ready_queue1, ready_queue2, ready_queue3, waiting_queue, alive_tasks
    
    number_of_tasks = len(tasks)
    alive_tasks = len(tasks)
    
    min_duration = min(task.duration for task in tasks)
    for task in tasks:
        task.weight = max(1, task.duration // min_duration)
        # print(f'{task.name} WEIGHT {task.weight} DURATION {task.duration}')
    
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
                # print(f'\n [FINISHED] subsystem 1')
                break
            
        if not waiting_queue.empty():
            task = waiting_queue.get()
            add_task_to_ready_queue(task, is_first < number_of_tasks)
            is_first += 1
            
    for t in cores:
        t.join()
