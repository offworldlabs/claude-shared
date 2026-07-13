# Contracts

Cross-service interface definitions for Offworld Labs.

The files in this directory are the **source of truth** for interfaces shared
between services: API schemas, event/message formats, shared data structures,
and versioning expectations. When two services communicate, the contract lives
here — not duplicated in each repo.

**Consuming repos should point to these files from their `CLAUDE.md`** rather
than copying contract definitions locally. Duplicated contracts drift; a single
referenced source does not.

> Stub — add one file per cross-service contract.
