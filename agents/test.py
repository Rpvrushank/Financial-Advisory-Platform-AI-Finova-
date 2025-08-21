import fastacp
print("FastACP contents:", dir(fastacp))

# Try to find the right classes
import inspect
for name, obj in inspect.getmembers(fastacp):
    if inspect.isclass(obj):
        print(f"Class found: {name}")