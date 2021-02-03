def find_first_index(lst, cond):
    for i, v in enumerate(lst):
        if cond(v):
            return i
    return None
