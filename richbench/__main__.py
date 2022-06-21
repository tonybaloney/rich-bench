"""
A tiny benchmark tool
"""
import argparse
import timeit
import pathlib
import sys
from types import FunctionType
import pyinstrument
try:
    from statistics import fmean
except ImportError: # Python 3.6-3.7 doesn't have fmean
    from statistics import mean as fmean # YOLO
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.box import Box, HEAVY_HEAD

DEFAULT_REPEAT = 5
DEFAULT_TIMES = 5

MARKDOWN: Box = Box(
    """\
    
| ||
|-||
| ||
|-||
|-||
| ||
    
""",
    ascii=True,
)

def format_delta(a: float, b: float, d: float, perc: bool = False) -> Text:
    if a < b:
        if d < 10:
            col = "medium_spring_green"
        elif 10 <= d < 20:  
            col = "spring_green1"
        elif 20 <= d < 40:
            col = "spring_green2"
        else:
            col = "green1"
        x = b / a
        if perc:
            return Text(f"{a:.3f} ({d:.1f}%)", style=col)
        else:
            return Text(f"{a:.3f} ({x:.1f}x)", style=col)
    else:
        x = a / b
        if perc:
            return Text(f"{a:.3f} (-{d:.1f}%)", style="red")
        else:
            return Text(f"{a:.3f} (-{x:.1f}x)", style="red")


def benchmark_function(func: FunctionType, bench_dir: pathlib.Path, repeat: int, times: int, profile=False):
    if profile:
        profiles_out = bench_dir / '.profiles'
        if not profiles_out.exists():
            profiles_out.mkdir(parents=True)
        profiler = pyinstrument.Profiler()
        profiler.start()

    result = timeit.repeat(func, repeat=repeat, number=times)

    if profile:
        profiler.stop()
        with open(profiles_out / f"{func.__name__}.html", "w", encoding='utf-8') as html:
            html.write(profiler.output_html())
    
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', action='store_true', help='Profile the benchmarks and store in .profiles/')
    parser.add_argument('--percentage', action='store_true', help="Show percentage of improvement instead of multiplier")
    parser.add_argument('--markdown', action='store_true', help="Prints a markdown friendly table")
    parser.add_argument('--benchmark', nargs='?', default=None, help="Run specific benchmark")
    parser.add_argument('--repeat', type=int, default=DEFAULT_REPEAT, help="Repeat benchmark this many times")
    parser.add_argument('--times', type=int, default=DEFAULT_TIMES, help="Run benchmark this many times")
    parser.add_argument('target', nargs="+", type=str)

    args = parser.parse_args()

    box = MARKDOWN if args.markdown else HEAVY_HEAD
    table = Table(title=f"Benchmarks, repeat={args.repeat}, number={args.times}", box=box)

    table.add_column("Benchmark", justify="right", style="cyan", no_wrap=True)
    table.add_column("Min", width=7)
    table.add_column("Max", width=7)
    table.add_column("Mean", width=7)
    table.add_column("Min (+)", style="blue", width=15)
    table.add_column("Max (+)", style="blue", width=15)
    table.add_column("Mean (+)", style="blue", width=15)

    n = 0
    for target in args.target:
        bench_dir = pathlib.Path(target)
        for f in bench_dir.glob("bench_*.py"):
            if args.benchmark and f.stem != f"bench_{args.benchmark}":
                continue
            sys.path.append(str(bench_dir.absolute()))
            i = __import__(f.stem, globals(), locals(), level=0)
            if hasattr(i, "__benchmarks__"):
                for benchmark in i.__benchmarks__:
                    n += 1
                    func1, func2, desc = benchmark
                    
                    without_result = benchmark_function(func1, bench_dir, args.repeat, args.times, args.profile)
                    with_result = benchmark_function(func2, bench_dir, args.repeat, args.times, args.profile)

                    delta_mean = (abs(fmean(with_result) - fmean(without_result)) / fmean(without_result)) * 100.0
                    delta_min = (abs(min(with_result) - min(without_result)) / min(without_result)) * 100.0
                    delta_max = (abs(max(with_result) - max(without_result)) / max(without_result)) * 100.0

                    fdelta_min = format_delta(min(with_result), min(without_result), delta_min)
                    fdelta_max = format_delta(max(with_result), max(without_result), delta_max)
                    fdelta_mean = format_delta(fmean(with_result), fmean(without_result), delta_mean)

                    table.add_row(
                                desc,
                                "{:.3f}".format(min(without_result)),
                                "{:.3f}".format(max(without_result)),
                                "{:.3f}".format(fmean(without_result)),
                                fdelta_min,
                                fdelta_max,
                                fdelta_mean,
                                )

    console = Console(width=150)
    console.print(table)

if __name__ == "__main__":
    main()
