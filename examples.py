#! /usr/bin/python
# -*- coding: utf-8 -*-

"""enigmake.examples"""

import enigmake

target1 = enigmake.Parameter(3.0, title = "target1") # The basis to build the dependent targets upon

print target1()

target2 = target1**4 # Operators are implemented for targets and numbers. Use numbers instead of targets if you are sure that the number won't change.

target3 = target1 + target2 # Operators are implemented for targets and other targets.
print target3()

print target1 in target3.dependencies, target2 in target3.dependencies # The + operator automagically detected the dependcies of target3 on target1 and target2.

some_parameter = enigmake.Parameter(1)
divisor = some_parameter * 2
answer = target3/divisor
print "and the answer is...", answer()

def decide_if_target3_is_large_enough():
	return target3() > 100
target4 = enigmake.Target(decide_if_target3_is_large_enough, dependencies = [target3]) # Define a target this way if the function to calculate the data cannot be written with the implemented operators.
print target4() # target1 to 3 won't be recalculated

target1.data = 5
print "and the new answer is...", answer() # This automagically determines which parts of the data have to be recalculated, namely target1 to 3 and answer, but not divisor.

target5 = enigmake.Target(enigmake.not_available, title="target5 (will be done later)") # Do this if you want to implement the target later but define it already now.
target6 = target5 + 7 # Raises no error. You can construct all dependencies upon target5...
try:
	print target6() # ...unless you call any target that depends upon target5. This raises a NotAvailableError.
except enigmake.NotAvailableError:
	print "A target needed for calculation is not yet available."

def some_idea():
	return 1000
# One day later, the implementation of target5 now comes to your mind. No problem! Just replace enigmake.not_available in the definition of target5 with some_idea.
# Or the calculation method of target5 is known only at runtime. In this case, do late binding...
target5.calc_data = some_idea
print "Now available:", target6() # ...and target6 can be calculated!


import enigmake.files

some_answer = enigmake.files.PickleRuntimeConstant(42, 'some_answer.pickle')
some_other_stuff = enigmake.files.PickleFileTarget(some_answer, [some_answer], 'some_other_stuff.pickle')
print some_other_stuff() # Will refresh some_answer only if some_answer.pickle doesn't exist or the value 42 is changed.
even_other_stuff = enigmake.files.PickleFileTarget(some_answer/42.0*23, [some_answer], 'even_other_stuff.pickle') # Will create internals Targets some_answer/42.0 and some_answer/42.0*23 whose dirtynesses aren't tracked since they are left out in the dependency list intentionally. The latter of those targets plays the role of even_other_stuff's calc_data. This way, one can create instances of Target subclasses (here a PickleFileTarget) without having to define calc_data explicitly.
print even_other_stuff()
