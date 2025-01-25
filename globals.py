import threading
from core import Core
from resource_ import Resource_
from typing import List

time_unit = -1

breaking_point = 2

def increment_time_unit():
  global time_unit
  time_unit += 1

global_start_barrier = threading.Barrier(8, action=increment_time_unit)
global_finish_barrier = threading.Barrier(8)

print_turn = 1
print_turn_lock = threading.Lock()

sub1_resource_lock = threading.Lock()
sub2_resource_lock = threading.Lock()
sub3_resource_lock = threading.Lock()
sub4_resource_lock = threading.Lock()

sub1_resources: List[Resource_] = []
sub2_resources: List[Resource_] = []
sub3_resources: List[Resource_] = []
sub4_resources: List[Resource_] = []

sub1_core1 = Core('sub1_core1')
sub1_core2 = Core('sub1_core2')
sub1_core3 = Core('sub1_core3')
sub2_core1 = Core('sub2_core1')
sub2_core2 = Core('sub2_core2')
sub3_core1 = Core('sub3_core1')
sub4_core1 = Core('sub4_core1')
sub4_core2 = Core('sub4_core2')

# time_units_data = [{'time': 0, 'subsystems': [{'R1': 2, 'R2': 2, 'waiting_queue': [], 'cores': [{'running_task': 'T11', 'ready_queue': ['T11']}, {'running_task': 'idle', 'ready_queue': []}, {'running_task': 'idle', 'ready_queue': []}], 'completed_tasks': []}, {'R1': 2, 'R2': 2, 'ready_queue': ['T24', 'T21', 'T22'], 'duration': [1, 3, 5], 'cores': [{'running_task': 'idle', 'duration': '-'}, {'running_task': 'T21', 'duration': 3}]}, {'R1': 2, 'R2': 2, 'ready_queue': ['T32'], 'cores': [{'running_task': 'T31'}], 'completed_tasks': ['T31']}, {'R1': 2, 'R2': 2, 'waiting_queue': [], 'ready_queue': ['T46', 'T44'], 'cores': [{'running_task': 'idle', 'duration': [4, 4]}, {'running_task': 'idle', 'duration': [4, 4]}]}]}, {'time': 1, 'subsystems': [{'R1': 2, 'R2': 2, 'waiting_queue': [], 'cores': [{'running_task': 'T11', 'ready_queue': []}, {'running_task': 'idle', 'ready_queue': []}, {'running_task': 'idle', 'ready_queue': []}], 'completed_tasks': ['T11']}, {'R1': 2, 'R2': 2, 'ready_queue': ['T21', 'T23', 'T22'], 'duration': [2, 2, 5], 'cores': [{'running_task': 'T21', 'duration': 2}, {'running_task': 'T24', 'duration': 0}]}, {'R1': 2, 'R2': 2, 'ready_queue': [], 'cores': [{'running_task': 'T32'}], 'completed_tasks': ['T31', 'T32']}, {'R1': 2, 'R2': 2, 'waiting_queue': [], 'ready_queue': ['T46', 'T44'], 'cores': [{'running_task': 'idle', 'duration': [4, 4]}, {'running_task': 'idle', 'duration': [4, 4]}]}]}]
time_units_data = []
current_time_data = {}
