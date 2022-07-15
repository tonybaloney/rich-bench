def sort_seven():
    """Sort a list of seven items"""
    for _ in range(10_000):
        sorted([3,2,4,5,1,5,3])

def sort_three():
    """Sort a list of three items"""
    for _ in range(10_000):
        sorted([3,2,4])

__benchmarks__ = [
    (sort_seven, sort_three, "Sorting 3 items instead of 7"),
    # run the same benchmark in reverse to see what a slowdown looks like
    (sort_three, sort_seven, "Sorting 7 items instead of 3"),
]
