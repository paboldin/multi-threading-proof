# Combinatorial proof for multithreading apps

Having your ass covered during kernel kpatch development is a nice thing.

Especially when scheduling, preemptivity and interruption/exception handling
can all happen in any order.

This project aims at providing a simple way to know if your code correctly
passes all the states in all the orders.

Simple Python implementation for now.

## How to use it

First, you should convert your code to the Python. Every thread should be a
different function and use `yield` at every place where scheduling might occur
(which is everywhere!). Variables are stored in the `state` object passed to
every thread as a solely argument:

```c

int value;
spinlock_t lock;

void somecode(void) {
	spin_lock(&lock);
	value = 0;
	value++;
	spin_unlock(&lock);
}

void someothercode(void) {
	int b = value;
	value = b + 1;
}
```

This transfers to:

```python

def somecode(state):
	state.lock.take()
	state.value = 0
	yield
	state.value += 1
	state.lock.release()

def someothercode(state):
	val = state.value
	yield
	state.value = val + 1
```

The function providing initial states must be defined. It is useful
to subclass the `State` class providing `INIT_STATE` dict with the init values:

```python

class MyState(State):
	INIT_STATE = {
		'a': 0,
		'lock': Lock
	}

def init_func():
	return MyState()
```

The initial state and threads-functions should be supplied to the `Combinator`
constructor:

```python
combinator = Combinator(init_func, [somecode, someothercode])
```

Now just run `check()`:

```python
combinator.check()
```

It will run this multithreading code through all the possible ways and check if
the final states are the same. This code, obviously, contains races since lock
is not taken in `someothercode`:

```
Incorrect 3 different states
[{'value': 1, 'path': [1, 0, 0, 1]}]
[{'value': 2, 'path': [0, 1, 0, 1]}, {'value': 2, 'path': [1, 0, 1, 0]}, {'value': 2, 'path': [1, 1, 0, 0]}]
[{'value': 3, 'path': [0, 0, 1, 1]}, {'value': 3, 'path': [0, 1, 1, 0]}]
```

Let's add this lock:

```python
def someothercode(state):
	state.lock.take()
	val = state.value
	yield
	state.value = val + 1
	state.lock.release()
```


This code still races, because `somecode` sets value to zero:

```
Incorrect 2 different states
[{'value': 2, 'path': [1, 1, 0, 0]}]
[{'value': 3, 'path': [0, 0, 1, 1]}]
```

Note that all the paths conflicting with locks are not taken anymore.
