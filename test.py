import gc

gc.enable()
gc.collect()
print(gc.mem_alloc())
print(gc.mem_free())