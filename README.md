# Combinatorial proof for multithreading apps

Having your ass covered during kernel kpatch development is a nice thing.

Especially when scheduling, preemptivity and interruption/exception handling
can all happen in any order.

This project aims at providing a simple way to know if your code correctly
passes all the states in all the orders.

Simple Python implementation for now.
