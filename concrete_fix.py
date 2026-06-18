from gpt4all import GPT4All
import os

# Step 1: Find model file
print("Finding your model...\n")

possible_locations = [
    os.path.expanduser(r"~\AppData\Local\nomic.ai\GPT4All"),
    os.path.expanduser(r"~\.cache\gpt4all"),
    r"C:\Users\Admin\AppData\Local\nomic.ai\GPT4All",
    r"C:\Users\Admin\.cache\gpt4all",
]

model_dir = None
model_file = None

for path in possible_locations:
    if os.path.exists(path):
        print(f"Checking: {path}")
        for f in os.listdir(path):
            if f.endswith('.gguf'):
                model_dir = path
                model_file = f
                print(f"✅ Found: {f}\n")
                break

if not model_file:
    print("❌ No model found in standard locations")
    print("Tell me where GPT4All is installed!")
    exit()

# Step 2: Load with explicit path
print(f"Loading: {model_file}")
print(f"From: {model_dir}\n")

model = GPT4All(
    model_name=model_file,
    model_path=model_dir,
    allow_download=False   # Don't download, use local file
)

print("✅ Model loaded!\n")

# Step 3: Test
response = model.generate(
    "What crops grow in Maharashtra?",
    max_tokens=150
)
print(f"Response: {response}")