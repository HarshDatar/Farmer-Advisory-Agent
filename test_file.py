# find_model.py
import os

path = r"C:\Users\Admin\AppData\Local\nomic.ai\GPT4All"

print("Files in GPT4All folder:\n")
for f in os.listdir(path):
    size = os.path.getsize(os.path.join(path, f)) / (1024**3)
    print(f"  '{f}'  ({size:.2f} GB)")