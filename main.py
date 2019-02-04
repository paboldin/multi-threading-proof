#!/usr/bin/python3

# TODO(pboldin) add locking that yields when lock is taken
# like:
# yield from state.lock.take()
# if scheduler sees that `take` was successful -- immediately restore to the
# yield, otherwise continue until it is there

import itertools

class State(object):
    INIT_STATE = {}
    def __init__(self):
        self.__dict__.update(self.INIT_STATE)
        self._state = list(self.INIT_STATE)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__ 

    def __hash__(self):
        return hash(tuple(getattr(self, x) for x in self._state))

    def __repr__(self):
        return repr(self.__dict__)

class TooMuchCombinations(Exception):
    pass

class Combinator(object):
    def __init__(self, init_func, threads, limit=10):
        self.init_func = init_func
        self.threads = threads
        self.limit = limit

    def _generators(self, state):
        return [
            iter(x(state))
            for x in self.threads
        ]

    def get_endpoint(self):
        state = self.init_func()

        power = []
        for generator in self._generators(state):
            this = 1
            for val in generator:
                this += 1
                if this >= self.limit:
                    raise TooMuchCombinations(str(func))
            power.append(this)

        return tuple(power)

    @classmethod
    def combinatioral_iterator(cls, destination):
        if not any(destination):
            yield None, destination

        for idx in range(len(destination)):
            if destination[idx] == 0:
                continue
            this = list(destination)
            this[idx] -= 1
            prev = None
            # TODO(pboldin) convert this to queue/stack so there is no
            # recursion limit
            for tail in cls.combinatioral_iterator(this):
                if prev is None:
                    yield idx, this
                yield tail
                prev = tail[0]

    @classmethod
    def get_all_paths(cls, destination):
        iterator = cls.combinatioral_iterator(destination)

        def until_none(value):
            yield value
            for x in iterator:
                if x[0] is None:
                    raise StopIteration
                yield x

        while True:
            try:
                first = next(iterator)
                yield until_none(first)
            except StopIteration:
                break

    def run(self):
        endpoint = self.get_endpoint()

        states = []

        for path in self.get_all_paths(endpoint):
            state = self.init_func()
            generators = self._generators(state)
            path = [step[0] for step in path]
            for step in path:
                idx = step
                try:
                    next(generators[idx])
                except StopIteration:
                    generators[idx] = None
            state.path = path
            states.append(state)

        return states

    def check(self):
        states = self.run()
        states = sorted(states, key=hash)
        grouped_by = itertools.groupby(states, key=hash)
        for key, values in grouped_by:
            print(key, list(values))


class MyState(State):
    INIT_STATE = {
        'value': 0
    }

def init_func():
    return MyState()

def first_func(state):
    state.value = 1
    yield
    state.value += 1

def second_func(state):
    val = state.value
    yield
    state.value = val + 1




THREADS = [
        first_func,
        second_func
]
def main():
    combinator = Combinator(init_func, THREADS)
    combinator.check()

if __name__ == '__main__':
    main()
