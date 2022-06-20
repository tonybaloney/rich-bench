# tinybench

A little Python benchmarking tool.

## Usage

```console
$ tinybench my_benchmarks/
```

## Writing benchmarks

Benchmarks should be in a directory and must have the filename `bench_{name}.py`.

The last statement in the benchmark file should be a list, called `__benchmarks__` with a list of tuples containing:

1. function a
1. function b
1. the name of the benchmark


```python
def sort_seven():
    """Sort a list of seven items"""
    for _ in range(10_000):
        sorted([3,2,4,5,1,5,3])

def sort_three():
    """Sort a list of three items"""
    for _ in range(10_000):
        sorted([3,2,4])

__benchmarks__ = [
    (sort_seven, sort_three, "Sorting 3 items instead of 7")
]
```

## Profiling

By adding the `--profile` flag to the command line, it will generate a subdirectory `.profiles` with HTML profile data of your target functions.

