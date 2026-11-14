# Scientific protocol

## Evidence levels

- `OBSERVED`: directly measured in a named binary, trace, or oracle run.
- `INFERRED`: follows from evidence, but has not yet been independently exercised.
- `HYPOTHESIS`: plausible explanation with a stated falsification experiment.
- `UNMEASURED`: gap, unavailable original or unsupported tooling.

## Layers

- `work/rg/` = immutable primary, automatically produced disassembly and metadata.
- `analysis/` = original human/agent annotations with pointers to primary evidence.
- `reconstruction/` = historical architecture reconstruction, keeping source-historical uncertainties visible.
- `modern/` = independent, testable implementation and design choices.
- `experiments/` = inputs, reproducible scripts, oracle summaries, expected observations (when redistributable).

## Minimum initial experiment panel

1. Hello / PRINT and literal strings.
2. Scalar integer, float, unary operations.
3. Operator precedence, parentheses, comparison.
4. Branch / loop / GOSUB.
5. Arrays and string lifetime.
6. Runtime error paths, including limits.
7. Interpreter vs compiler output differences.

With GFA 1/2/3: compare call shapes and runtime signatures only across genuinely version-matched compilation outputs. Keep compiler-produced executables distinguishable from interpreter/editor binaries.

## Three no-go claims

- 'rg-dis named this library function, so GFA BASIC 1.0 called it.' No: v1 recognition is not established.
- 'The disassembly rebuilds, therefore this is original historical source.' No: source reconstruction is inference.
- 'A compatible modern compiler must reproduce historical bytes.' No: observable semantics is the target unless a specific byte-exact claim is separately motivated.
