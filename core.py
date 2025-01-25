from typing import List
import globals
from task import Task

class Core:
  def __init__(self, name):
    self.name = name
    self.schedule = []

    self.tasks = 0

    self.total_waiting_time = -1
    self.total_turnaround_time = -1
    self.total_response_time = -1

    self.avg_waiting_time = -1
    self.avg_turnaround_time = -1
    self.avg_response_time = -1

  def append_task(self, task):
    if task and not task.name.startswith("failed"):
      self.tasks += 1
      self.schedule.append(task)
    else:
      self.schedule.append(None)

  def start(self):
    print(f"Core {self.name} started:")
    print("--------------------------------------------------")
    for task in self.schedule:
      if task:
        print(task.name, end="-")
      else:
        print("Idle", end="-")
    print()
    print("--------------------------------------------------\n")

    if self.tasks > 0:
      self.waiting_time()
      self.turnaround_time()
      self.response_time()
    else:
      self.avg_waiting_time = 0
      self.avg_turnaround_time = 0
      self.avg_response_time = 0

  def waiting_time(self):
    seen_tasks = []

    self.total_waiting_time = 0

    for i in range(len(self.schedule)):
      current_task: Task = self.schedule[i]

      if not current_task:
        continue

      if current_task.name not in seen_tasks:
        seen_tasks.append(current_task.name)
        self.total_waiting_time += i - current_task.entering_time
      
      for j in range(i + 1, len(self.schedule)):
        if self.schedule[j] and self.schedule[j].name == current_task.name:
          self.total_waiting_time += (j - i - 1)
          break
        
    self.avg_waiting_time = self.total_waiting_time / len(seen_tasks)
    
  def turnaround_time(self):
    seen_tasks = []

    self.total_turnaround_time = 0

    for i in range(len(self.schedule) - 1, -1, -1):
      current_task: Task = self.schedule[i]

      if not current_task:
        continue

      if current_task.name not in seen_tasks:
        seen_tasks.append(current_task.name)
        self.total_turnaround_time += i + 1 - current_task.entering_time
        
    self.avg_turnaround_time = self.total_turnaround_time / len(seen_tasks)
  
  def response_time(self):
    seen_tasks = []
    
    self.total_response_time = 0
    
    for i in range(len(self.schedule)):
      current_task: Task = self.schedule[i]
      
      if not current_task:
        continue
      
      if current_task.name not in seen_tasks:
        seen_tasks.append(current_task.name)
        self.total_response_time += i - current_task.entering_time
        
    self.avg_response_time = self.total_response_time / len(seen_tasks)

  @staticmethod
  def info_of_each_task(subsystem_number , cores: List['Core'], num_of_tasks: int):
    each_task_info = []
    each_task_last_run = []
    
    for i in range(num_of_tasks):
      task_info = []
      task_name = f"T{subsystem_number}{i + 1}"
      each_task_last_run.append(-1)
      
      for j in range(globals.breaking_point):
        done = 0
        for core in cores:
          if core.schedule[j] and core.schedule[j].name == task_name:
            task_info.append(core.name)
            each_task_last_run[i] = j
            done = 1
            break
        if done == 0:
          task_info.append("Idle")
          
      each_task_info.append(task_info)
      
    for i in range(len(each_task_info)):
      print(f"T{subsystem_number}{i + 1} completed in time_unit {each_task_last_run[i]} ", end=": ")
      for j in range(len(each_task_info[i])):
        print(each_task_info[i][j], end="|")
      print('\n')
