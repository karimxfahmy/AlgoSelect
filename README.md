# AlgoSelect

A small problem-solving assistant that picks the right algorithm for the job.

You feed it a problem (knapsack, MST/routing, sorting, search), tell it how big
the input is and how long you're willing to wait, and it figures out which of
its four algorithm families is the best fit — Dynamic Programming, Greedy,
Divide and Conquer, or plain old Brute Force.

It then runs the chosen one and shows you why it picked it. There's also an
experiment mode that runs every applicable algorithm side by side so you can
compare them on the exact same input.

## Stack

- **Engine**: Python (pure, no heavy deps for the algorithms themselves)
- **API**: FastAPI
- **UI**: React + Tailwind
- **Charts**: Chart.js

## Status

Work in progress — being built up in small, deliberate steps.
