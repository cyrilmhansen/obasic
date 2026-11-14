# Turbo-BASIC XL reconstruction — upstream references

Author dmsc maintains a published MADS disassembly at <https://github.com/dmsc/turbo-dis>.

The project's `turbo-mads.asm` reconstructs the Turbo-BASIC XL v1.5 interpreter, and the Makefile builds both the original and a version incorporating fixes. It documents self-relocation and multiple historical bugs.

**Method:** read and study it as a third-party source, always note the exact commit, distinguish its reverse-engineered names/comments from verified historical evidence, and do not copy third-party material into this repository without checking reuse terms. No repository license was apparent in the listing inspected 2026-11-14; confirm with the author before redistribution.

For a local checkout (ignored by Git):

```sh
mkdir -p work/references
git clone https://github.com/dmsc/turbo-dis.git work/references/turbo-dis
git -C work/references/turbo-dis rev-parse HEAD
```

Additional archival references: <https://www.atariwiki.org/wiki/Wiki.jsp?page=Turbo-BASIC+XL> (original magazine programs, object lists, MADS source).

Compilers and runtime: **not covered by the interpreter disassembly alone**. Inventory compiler 1.1 and its run-time independently.
