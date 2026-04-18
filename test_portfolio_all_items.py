"""Quick test to verify all portfolio items are being fetched and returned."""
import io
import asyncio
from PIL import Image, ImageDraw
import random
from fastapi import UploadFile
from app.services.platform_service import create_artisan, upload_portfolio, list_portfolio


def create_test_image(seed):
    """Create a simple test image."""
    random.seed(seed)
    img = Image.new('RGB', (256, 256), color=(255, 255, 255))
    draw = ImageDraw.Draw(img, 'RGBA')
    
    for i in range(50):
        x, y = random.randint(0, 256), random.randint(0, 256)
        draw.rectangle([x, y, x+20, y+20], fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


async def test_portfolio():
    print("\n=== Portfolio Multiple Items Test ===\n")
    
    # Create artisan
    artisan = create_artisan({
        'name': 'Test Artisan',
        'email': 'test@example.com',
        'region': 'India',
        'craft_tradition': 'Weaving'
    })
    print(f"✓ Created artisan: {artisan['name']} (ID: {artisan['id']})")
    
    # Upload 3 different artworks
    for i in range(3):
        img_bytes = create_test_image(i)
        
        # Create a mock UploadFile
        file = UploadFile(
            file=io.BytesIO(img_bytes),
            filename=f'artwork_{i}.png',
            size=len(img_bytes)
        )
        
        portfolio_item = await upload_portfolio(
            artisan['id'],
            file,
            title=f'Artwork #{i+1}',
            description=f'Test artwork {i+1}'
        )
        print(f"✓ Uploaded artwork {i+1}: {portfolio_item['title']}")
    
    # List portfolio
    portfolio = list_portfolio(artisan['id'])
    print(f"\n📊 Portfolio Summary:")
    print(f"  Total items: {len(portfolio)}")
    for item in portfolio:
        print(f"  - {item['title']}: {len(item.get('detected_techniques', []))} techniques")
    
    if len(portfolio) == 3:
        print("\n✅ SUCCESS: All 3 artworks are being stored and retrieved!")
    else:
        print(f"\n❌ ERROR: Expected 3 artworks, got {len(portfolio)}")


if __name__ == '__main__':
    asyncio.run(test_portfolio())
