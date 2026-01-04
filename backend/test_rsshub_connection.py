import httpx
import asyncio
import os

# Print proxy environment variables
print("=== Proxy Environment Variables ===")
print("HTTP_PROXY:", os.environ.get("HTTP_PROXY", "Not set"))
print("HTTPS_PROXY:", os.environ.get("HTTPS_PROXY", "Not set"))
print("http_proxy:", os.environ.get("http_proxy", "Not set"))
print("https_proxy:", os.environ.get("https_proxy", "Not set"))

async def test_with_no_proxy():
    url = "http://127.0.0.1:1200/healthz"
    print(f"\n=== Test (proxy disabled): {url} ===")
    async with httpx.AsyncClient(proxy=None, trust_env=False, timeout=10.0) as client:
        response = await client.get(url)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

async def test_with_default():
    url = "http://127.0.0.1:1200/healthz"
    print(f"\n=== Test (default settings): {url} ===")
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

async def main():
    try:
        await test_with_no_proxy()
    except Exception as e:
        print(f"No-proxy test failed: {e}")
    
    try:
        await test_with_default()
    except Exception as e:
        print(f"Default test failed: {e}")

asyncio.run(main())
