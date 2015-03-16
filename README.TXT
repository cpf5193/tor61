Name: Jacob Gile
Student Number: 1065240
UW Email Address: jjgile@uw.edu

Name: Christon Fukuhara
Student Number: 1126856
UW Email Address: cpf5193@uw.edu

ISSUES:
----------------------
Unfortunately, we were unable to get the whole project up and running. We had difficulties with the semantics of python sockets and distinguishing
which end was which, and their use in the routing tables. This caused us to get a routing loop when forwarding the EXTEND messages through the circuits.
We also were unable to get CONNECT requests to receive a response from the server, but all non-CONNECT requests are able to work fine (tested with netcat and firefox).
We did work long and hard on this project, but just ran out of time being stuck on our larger bugs.


NOTES:
----------------------
We created a logging utility for use with our project. It can be turned on in Log61.py by changing "logger.setLevel(logging.ERROR)" to "logger.setLevel(logging.INFO)"

Nothing is beautiful and everything hurts :(
