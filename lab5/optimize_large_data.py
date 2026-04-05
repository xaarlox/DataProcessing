import time
import multiprocessing
import numpy as np


# 1. NON-OPTIMIZED APPROACH
def simple_approach(data):
    result = []
    for x in data:
        result.append(x ** 2)
    return sum(result)


# 2. PARALLEL COMPUTING
def chunk_worker(chunk):
    return sum(x ** 2 for x in chunk)


def parallel_approach(data, num_processes):
    chunk_size = len(data) // num_processes
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(chunk_worker, chunks)
    return sum(results)


# 3. OPTIMIZED ALGORITHM (NumPy)
def optimized_approach(data_array):
    return np.sum(np.square(data_array.astype(np.float64)))


def run_benchmark(func, data, name, iterations=10, **kwargs):
    """Runs a function multiple times and calculates average time."""
    times = []
    last_res = None
    print(f"Running benchmark for: {name}...")

    for i in range(iterations):
        start = time.time()
        last_res = func(data, **kwargs) if kwargs else func(data)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  Iteration {i + 1}: {elapsed:.4f} sec")

    avg_time = sum(times) / iterations
    print(f">> Average {name}: {avg_time:.4f} sec\n")
    return avg_time, last_res


if __name__ == "__main__":
    n = 10_000_000
    iterations = 10

    print(f"--- Generating data for {n} elements ---")
    data_list = list(range(n))
    data_array = np.array(data_list)
    cpus = multiprocessing.cpu_count()

    print(f"--- Starting Benchmarks ({iterations} iterations each) ---\n")
    avg_simple, res_simple = run_benchmark(simple_approach, data_list, "Simple Loop", iterations)
    avg_parallel, res_parallel = run_benchmark(parallel_approach, data_list, "Multiprocessing", iterations,
                                               num_processes=cpus)
    avg_numpy, res_numpy = run_benchmark(optimized_approach, data_array, "NumPy Vectorization", iterations)

    is_valid = np.isclose(float(res_simple), float(res_parallel), rtol=1e-12) and \
               np.isclose(float(res_simple), float(res_numpy), rtol=1e-12)

    if is_valid:
        print("Success: All methods returned consistent results.")
        print("\n--- Final Performance Comparison (Average) ---")
        print(f"Simple Loop:      {avg_simple:.4f} sec")
        print(f"Multiprocessing:  {avg_parallel:.4f} sec")
        print(f"NumPy:            {avg_numpy:.4f} sec")
    else:
        print("Error: Results differ too much!")
        print(f"DEBUG: Simple={res_simple}\nDEBUG: NumPy={res_numpy}")