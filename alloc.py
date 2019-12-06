#!/usr/bin/python3

import functools

from mtp import State, Combinator

class MyState(State):
    INIT_STATE = {
        'get': 0,
        'put': 1,
        'N': 1,
        'Np1': 2,
        'indexes': [0, -1],
        'retval': {}
    }

def init_func():
    return MyState()

def alloc(state, i):
    state.retval[i] = -1

    get_raw = state.get
    get = get_raw % state.Np1
    state.get += 1
    yield

    if get == state.put % state.Np1:
        state.get -= 1
    else:
        state.retval[i] = state.indexes[get]
        yield

        if state.retval[i] == -1:
            state.get -= 1
        else:
            #if get_raw == state.Np1:
                #state.get -= state.Np1
            # yield
            state.indexes[get] = -1

def allocn(i):
    return functools.partial(alloc, i=i)

def main():
    combinator = Combinator(init_func, [allocn(0), allocn(1), allocn(2)])
    combinator.check()

if __name__ == '__main__':
    main()
