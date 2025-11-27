In `Analysis of Exception Hierarchy and Handling.md`,
you and me we co-authored a report about the shortcomings of the exception handling.
However, we forgot to consider 1 thing, namely:
Please search the codebase if there are occurrences where we log the same error multiple times.
I guess we should avoid catching an error, logging it, re-raising it, and then catch and log it in the caller.
If you find such a thing, please add a short description of the problem as sub-chapter 3.10.
