from time import time


def time_function_execution(label, fnc):
    start_time = time()
    result = fnc()
    end_time = time()
    print(f'{label} took {end_time-start_time} seconds')
    return result
