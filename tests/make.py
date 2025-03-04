import torch
import pickle
import sys
import traceback
from transformers import AutoTokenizer, AutoModelForCausalLM, logging as transformers_logging

transformers_logging.set_verbosity_error()

# Subclass the model to override prepare_inputs_for_generation for debugging
class DebugModel(AutoModelForCausalLM):
    def prepare_inputs_for_generation(self, input_ids, past_key_values=None, **kwargs):
        print("=== prepare_inputs_for_generation ===")
        print("input_ids shape:", input_ids.shape)
        if past_key_values is not None:
            # Print some details about the first element of past_key_values
            try:
                first_layer = past_key_values[0]
                if isinstance(first_layer, tuple) and len(first_layer) >= 1:
                    print("First past_key tensor shape:", first_layer[0].shape)
                else:
                    print("past_key_values structure:", past_key_values)
            except Exception as e:
                print("Error printing past_key_values:", e)
        else:
            print("No past_key_values provided.")
        # Also print any extra kwargs (like cache_position, if present)
        print("Extra kwargs:", kwargs)
        # Call the original implementation by invoking the super() version
        return super().prepare_inputs_for_generation(input_ids, past_key_values=past_key_values, **kwargs)

def load_kv_cache(cache_file: str):
    try:
        with open(cache_file, "rb") as f:
            kv_cache = pickle.load(f)
        return kv_cache
    except Exception as e:
        print(f"Error loading KV cache from {cache_file}: {e}")
        traceback.print_exc()
        sys.exit(1)

def debug_generate(model_name: str, new_query: str, kv_cache, max_new_tokens: int = 50):
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        # Instead of AutoModelForCausalLM, load our DebugModel
        model = DebugModel.from_pretrained(
            model_name, 
            torch_dtype=torch.float16,
            device_map="auto"
        )
        model.eval()
    except Exception as e:
        print("Error loading model/tokenizer:", e)
        traceback.print_exc()
        sys.exit(1)
    
    try:
        new_input_ids = tokenizer.encode(new_query, return_tensors="pt").to("cuda")
        # For models like GPT-2 or Llama, we might need the input to be (batch_size, 1)
        new_input_ids = new_input_ids[:, -1:]
        print("New input_ids shape:", new_input_ids.shape)
    except Exception as e:
        print("Error encoding new query:", e)
        traceback.print_exc()
        sys.exit(1)
    
    try:
        with torch.no_grad():
            outputs = model.generate(
                new_input_ids,
                past_key_values=kv_cache,
                max_new_tokens=max_new_tokens
                # you can also try adding cache_position here if needed: cache_position=<tensor>
            )
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text
    except Exception as e:
        print("Error during generation with KV cache:", e)
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
    # This is the prompt used to create the KV cache
    prompt = """[제1편 총칙]
    ├─ [제1관 일반규정]
    │     ├─ [단일장 또는 제1장]
    │           ├─ [제1절 정의]
    │           │      ├─ 제1조 (목적)
    │           │      ├─ 제2조 (정의)
    │           │      └─ 제3조 (적용범위)"""
    
    kv_cache = load_kv_cache("kv_cache.pkl")
    print("KV cache loaded successfully.")
    
    new_query = "이 법의 목적과 주요 수단을 설명해 주세요."
    answer = debug_generate(model_name, new_query, kv_cache, max_new_tokens=50)
    print("Generated Answer:")
    print(answer)
