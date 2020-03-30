# bytetrace

**This is just a POC currently.**

A tool for tracing bytecode execution.


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
