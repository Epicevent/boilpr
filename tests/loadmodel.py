import gc
import psutil
from transformers import AutoTokenizer, AutoModel
from easynmt import EasyNMT
import torch

# Define models to test
model_list = {
    "EasyNMT (opus-mt)": lambda: EasyNMT('opus-mt', device='cuda' if torch.cuda.is_available() else 'cpu'),
    "Helsinki-NLP/opus-mt-ko-en": lambda: (
        AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-ko-en"),
        AutoModel.from_pretrained("Helsinki-NLP/opus-mt-ko-en")
    ),
    "facebook/mbart-large-50-many-to-many-mmt": lambda: (
        AutoTokenizer.from_pretrained("facebook/mbart-large-50-many-to-many-mmt"),
        AutoModel.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
    ),
    "alirezamsh/small100": lambda: (
        AutoTokenizer.from_pretrained("alirezamsh/small100"),
        AutoModel.from_pretrained("alirezamsh/small100")
    )
}

# Measure memory usage
def get_memory_usage(loader_function):
    gc.collect()
    before_memory = psutil.Process().memory_info().rss / (1024 ** 2)  # Memory in MB
    model = loader_function()
    after_memory = psutil.Process().memory_info().rss / (1024 ** 2)  # Memory in MB
    memory_usage = after_memory - before_memory
    del model
    gc.collect()
    return memory_usage

memory_results = {}
for model_name, loader in model_list.items():
    try:
        memory_results[model_name] = get_memory_usage(loader)
    except Exception as e:
        memory_results[model_name] = f"Error: {e}"

print(memory_results)
