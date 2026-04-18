"""Verify that the portfolio gallery shows all items correctly."""
import io
import asyncio
import json
from PIL import Image, ImageDraw
import random
from fastapi import UploadFile
from app.services.platform_service import create_artisan, upload_portfolio, unified_workspace


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


async def test_portfolio_gallery():
    print("\n=== Portfolio Gallery Workspace Test ===\n")
    
    # Create artisan
    artisan = create_artisan({
        'name': 'Gallery Test Artisan',
        'email': 'gallery@test.com',
        'region': 'India',
        'craft_tradition': 'Textile Weaving'
    })
    print(f"✓ Created artisan: {artisan['name']} (ID: {artisan['id']})")
    
    # Upload 5 different artworks
    for i in range(5):
        img_bytes = create_test_image(i * 100)
        file = UploadFile(
            file=io.BytesIO(img_bytes),
            filename=f'artwork_{i+1}.png',
            size=len(img_bytes)
        )
        
        item = await upload_portfolio(
            artisan['id'],
            file,
            title=f'Textile Piece #{i+1}',
            description=f'Handwoven textile {i+1}'
        )
        print(f"✓ Uploaded: {item['title']}")
    
    # Get unified workspace (what the frontend sees)
    workspace = unified_workspace(artisan['id'])
    portfolio = workspace['portfolio']
    
    print(f"\n📊 Workspace Portfolio Data:")
    print(f"  Total items: {len(portfolio)}")
    print(f"  Items in workspace.portfolio:")
    for idx, item in enumerate(portfolio, 1):
        techniques = ', '.join(item.get('detected_techniques', [])[:2])
        print(f"    {idx}. {item['title']} | Techniques: {techniques}")
    
    if len(portfolio) >= 5:
        print(f"\n✅ SUCCESS: All {len(portfolio)} artworks are returned in workspace!")
        print("   → Frontend will display all items in the portfolio gallery section")
    else:
        print(f"\n❌ ERROR: Expected at least 5 artworks, got {len(portfolio)}")


if __name__ == '__main__':
    asyncio.run(test_portfolio_gallery())
