import urllib.parse
import random

def generate_image_url(prompt: str):
    """
    Converts a text prompt into a high-quality image URL.
    Optimized for faster loading and better compatibility.
    """
    if not prompt:
        return None

    # 1. Clean and Encode the prompt
    # Stripping extra spaces and making it URL-safe
    clean_prompt = prompt.strip().replace(" ", "-")
    encoded_prompt = urllib.parse.quote(clean_prompt)
    
    # 2. Random Seed for uniqueness
    seed = random.randint(1, 1000000)
    
    # 3. Enhanced URL Structure
    # Pollinations works best with /prompt/ rather than /p/ in some cases
    # We use a slightly smaller default size (768) for faster initial rendering
    # nologo=true is great for a clean UI
    image_url = (
        f"https://pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1024"
        f"&height=1024"
        f"&seed={seed}"
        f"&nologo=true"
        f"&model=flux"  # Adding Flux model for high quality
    )
    
    return image_url

# Example usage for your backend:
# prompt = "A futuristic Cybertruck at Islamia University Bahawalpur"
# url = generate_image_url(prompt)
# print(url)