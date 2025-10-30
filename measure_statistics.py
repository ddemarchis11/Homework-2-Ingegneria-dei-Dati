import os, statistics
from indexer import build_index
from build_dataset import build_dataset

def measure_statistics():
    
    files = os.listdir("to_index_dataset")
    print(f"Evaluating statistics on {len(files)} fiels")
    
    tokens_per_file = build_dataset()
    print(f"Average number of tokens per file: {sum(tokens_per_file)/len(tokens_per_file)}")
    
    times = []
    for i in range(5):
        elapsed = build_index()
        print(f"Run {i+1}: {elapsed:.3f}s")
        times.append(elapsed)

    mean = statistics.mean(times)
    stdev = statistics.stdev(times)
    print(f"Mean: {mean:.3f}s, Standard Deviation {stdev:.3f}s")
    
if __name__ == "__main__": measure_statistics()