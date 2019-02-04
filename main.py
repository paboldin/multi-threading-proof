#!/usr/bin/python3

# TODO(pboldin) add locking that yields when lock is taken
# like:
# yield from state.lock.take()
# if scheduler sees that `take` was successful -- immediately restore to the
# yield, otherwise continue until it is there

import itertools

class Lock(object):
    taken = 0
    def take(self):
        if self.taken:
            raise StopIteration()
        self.taken = 1
    def release(self):
        self.taken = 0

class State(object):
    INIT_STATE = {}
    def __init__(self):
        self._state = []
        for k, v in self.INIT_STATE.items():
            if v is Lock:
                v = v()
            else:
                self._state.append(k)
            setattr(self, k, v)
        self._state = tuple(self._state)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__ 

    def __hash__(self):
        return hash(tuple(getattr(self, x) for x in self._state))

    def __repr__(self):
        d = {}
        for s in self._state + ('path',):
            d[s] = getattr(self, s)
        return repr(d)

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

            followed_through = True

            for step in path:
                idx = step

                if generators[idx] is None:
                    followed_through = False
                    break

                try:
                    next(generators[idx])
                except StopIteration:
                    generators[idx] = None

            if not followed_through:
                continue
            state.path = path
            states.append(state)

        return states

    def check(self):
        states = self.run()
        states = sorted(states, key=hash)
        grouped_by = itertools.groupby(states, key=hash)

        states = dict((key, list(values)) for key, values in grouped_by)

        if len(states) != 1:
            print("Incorrect {} different states".format(len(states)))
            for state in states.values():
                print(state)

        return states

class MyState(State):
    INIT_STATE = {
        'value': 0,
        'lock': Lock
    }

def init_func():
    return MyState()

def somecode(state):
    state.lock.take()
    state.value = 1
    yield
    state.value += 1
    state.lock.release()

def someothercode(state):
    val = state.value
    yield
    state.value = val + 1


def main():
    combinator = Combinator(init_func, [somecode, someothercode])
    combinator.check()

if __name__ == '__main__':
    main()
