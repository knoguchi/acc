Acc
===

A Python implementation of Accounting Pattern framework by Martin Fowler.
It may not necessarily represent MF's design.

Accounting Pattern
==================

- Essentially it's a movement of money from an `Account` to another.
- Movement of quantity can be expressed as `AccountingEvent` and `Entry`
- Movement is not always single entry. `AccountingTransaction` supports multi-legged entries.
- The movement is governed by `Agreement`s and `PostingRule`s.
- There are 3 patterns of adjustment. A general rule is 
  1. Cancel -- use `ReversalAdjustment` to remove the original transaction.  This is possible when the original transaction (event) has no subsequent events.  It's practical but not GAAP compliant.
  2. Reverse -- use `ReplacementAdjustment` to add entries with negated amount.  This is the most common case.
  3. Adjust difference -- use `DifferenceAdjustment` when the original transaction is already closed, and you need to create a new entry for the adjustment.

Example
=======
  See tests/electricity.py and tests/test_electricity.py

Bugs
====

Difference Adjustment does not work.

TODO
====
 - Remove Java-ism.
 - Remove Money specific code from the framework.
 - Create general purpose accouting mixin that supports any quantifiable.
