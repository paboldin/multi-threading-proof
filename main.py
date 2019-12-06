#!/usr/bin/python3

from mtp import *

class MyState(State):
    INIT_STATE = {
        'value': 0,
        'lock': Lock
    }

def init_func():
    return MyState()

def first_func(state):
    state.lock.take()
    state.value = 1
    yield
    state.value += 1
    state.lock.release()

def second_func(state):
    state.lock.take()
    val = state.value
    yield
    state.value = val + 1
    state.lock.release()


def main():
    combinator = Combinator(init_func, [first_func, second_func])
    combinator.check()

if __name__ == '__main__':
    main()
