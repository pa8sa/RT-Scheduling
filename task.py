from enum import Enum

class Task:
  def __init__(self, sub_system_number = None, name = None, duration = None, resource1_usage = None, resource2_usage = None, entering_time = None, dest_cpu = None, period = None, prerequisite_task_name = None, recursion = None):
    # waiting, running, ready, complete
    self.state = 'waiting'

    self.sub_system_number = sub_system_number
    self.name = name
    self.duration = duration
    self.resource1_usage = resource1_usage
    self.resource2_usage = resource2_usage
    self.entering_time = entering_time
    
    #sub1
    self.dest_cpu = dest_cpu

    #sub3
    self.period = period
    self.recursion = recursion
    
    self.prerequisite_task_name = prerequisite_task_name
    
    self.age = 0
    self.waiting_time = 0