import os
from PIL import Image

from app.agents.market_agent import market_agent
from app.agents.pedagogy_agent import pedagogy_agent

def main():
    print("🚀 Initializing Final Synchronous Agent Tests...\n")
    
    test_img_path = "test_craft.jpg"
    if not os.path.exists(test_img_path):
        img = Image.new('RGB', (512, 512), color='#8B0000')
        img.save(test_img_path)

    print("--------------------------------------------------")
    print("🧪 TEST 1: Economic Intelligence Agent (Market Pivots)")
    try:
        market_results = market_agent.recommend(
            craft_tradition="Ikat Weaving", 
            region="India", 
            techniques=["Handloom"], 
            source_image_path=test_img_path
        )
        print(f"✅ Success! Suggested Product: {market_results[0]['suggested_products'][0]}")
        print(f"🖼️ Generated Mockup URL:\n{market_results[0]['mockup_url']}\n")
    except Exception as e:
        print(f"❌ Market Failed: {e}")

    print("--------------------------------------------------")
    print("🧪 TEST 2: Adaptive Pedagogy Agent (Masterclass)")
    try:
        pedagogy_results = pedagogy_agent.build_learning_path("Ikat Weaving")
        print(f"✅ Success! Course: {pedagogy_results['title']}")
        first_module = pedagogy_results['modules'][0]
        print(f"Step 1: {first_module['title']}")
        print(f"🖼️ Generated Thumbnail URL:\n{first_module['thumbnail_url']}\n")
    except Exception as e:
        print(f"❌ Pedagogy Failed: {e}")

if __name__ == "__main__":
    main()