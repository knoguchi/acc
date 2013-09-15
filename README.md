Acc
===

A Python implementation of Accounting Patterns framework by Martin Fowler.
It may not necessarily represent MF's design.

Accounting Patterns
===================

- Essentially it's a movement of money from an `Account` to another.
- Movement of quantity can be expressed as `AccountingEvent` and `Entry`
- Movement is not always single entry. `AccountingTransaction` supports multi-legged entries.
- The movement is governed by `Agreement`s and `PostingRule`s.
- There are 3 patterns of adjustment. A general rule is 
  1. Cancel(Replace) -- use `ReplaceAdjustment` to remove the original transaction, and add a new one as necessary.  This is possible when the original transaction (event) has no subsequent events.  It's practical but not GAAP compliant.
  2. Reverse -- use `ReversalAdjustment` to add entries with negated amount.  This is the most common case that keeps both of the erratic and correct entries.
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

References
==========
* The main article
  http://martinfowler.com/apsupp/accounting.pdf

* Account
  http://martinfowler.com/eaaDev/Account.html

* Accounting Entry
  http://martinfowler.com/eaaDev/AccountingEntry.html

* Service Agreement and Posting Rule
  http://martinfowler.com/eaaDev/AgreementDispatcher.html

* Reversal Adjustment
  http://martinfowler.com/eaaDev/ReversalAdjustment.html

* Replacement Adjustment
  http://martinfowler.com/eaaDev/ReplacementAdjustment.html

* Difference Adjustment
  http://martinfowler.com/eaaDev/DifferenceAdjustment.html

