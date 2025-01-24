import threading
from core import Core
from resource_ import Resource_
from typing import List

time_unit = -1

breaking_point = 40

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
