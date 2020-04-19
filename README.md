# bytetrace

**This is just a POC currently.**

A tool for tracing bytecode execution.

Note that this tool currently works on <span style="color:red;">CPython >= 3.7 only</span>, because it relies on a new event `PyTrace_OPCODE`, which is added in CPython 3.7, dispatched inside the [bytecode evaluation loop][ceval_evalframedefault] (known as `ceval.c::PyEval_EvalFrame`).


## Install
```bash
$ pip install git+https://github.com/naleraphael/bytetrace.git
```


## Usage
It's simple, just like you are using `pdb`.

```python
import bytetrace

# ... your code
bytetrace.set_trace()
# ... your code
```

### Commands
- q(uit)
    Enter this command twice to quit from debugger.

- pfl (print_f_locals)
    Print `f_locals` of current frame. (equivalent to `inspect.currentframe().f_locals`)

[ceval_evalframedefault]: https://github.com/python/cpython/blob/3.7/Python/ceval.c#L551
