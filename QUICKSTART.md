# 🚀 Quick Start Guide

Get your Background Removal API running in 5 minutes!

## Step 1: Get Your Replicate API Token

1. Go to [replicate.com](https://replicate.com)
2. Sign up or log in
3. Navigate to [API Tokens](https://replicate.com/account/api-tokens)
4. Copy your API token (starts with `r8_`)

## Step 2: Configure Your Environment

Edit the `.env` file and replace `your_replicate_api_token_here` with your actual token:

```bash
REPLICATE_API_TOKEN=r8_your_actual_token_here
```

## Step 3: Install Dependencies

### Option A: Using the startup script (macOS/Linux)

```bash
./run.sh
```

### Option B: Manual installation

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

## Step 4: Test Your API

The API should now be running at `http://localhost:8000`

### View Interactive Documentation

Open your browser and go to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Test with cURL

```bash
curl -X POST "http://localhost:8000/remove-background" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://replicate.delivery/pbxt/MAqakpYnuaS5IxU4WZAh5irkSn92wuYc5bdU1TNV5xzIJ8sM/gzp35qt55t4aatwznmccv2ssgds2.png",
    "format": "png",
    "background_type": "rgba"
  }'
```

### Test with Python Script

In a new terminal:

```bash
# Activate virtual environment if not already active
source venv/bin/activate

# Run the test script
python test_api.py
```

## Step 5: Start Building!

Your API is ready! Here's a simple example:

```python
import requests

response = requests.post(
    "http://localhost:8000/remove-background",
    json={
        "image_url": "https://example.com/your-image.jpg",
        "format": "png",
        "background_type": "rgba"
    }
)

result = response.json()
print(f"Processed image: {result['output_url']}")
```

## 🎯 Next Steps

1. **Customize**: Modify `main.py` to add features like authentication, rate limiting, etc.
2. **Deploy**: Follow the deployment guide in README.md
3. **Monetize**: List your API on RapidAPI Hub
4. **Scale**: Add caching, queue systems, and load balancing

## 🐛 Troubleshooting

### "REPLICATE_API_TOKEN not found"
- Make sure you edited the `.env` file with your actual token
- Restart the server after editing `.env`

### "Connection refused"
- Make sure the server is running (`python main.py`)
- Check if port 8000 is already in use

### "Service unavailable"
- Verify your Replicate API token is valid
- Check your internet connection
- Replicate service might be experiencing issues

## 💡 Tips

- The first request might take longer as the model initializes
- Supported image formats: JPG, PNG, WebP, etc.
- Larger images will take more time to process
- Monitor your Replicate usage at [replicate.com/account](https://replicate.com/account)

## 📚 Resources

- [Full README](README.md)
- [Replicate Documentation](https://replicate.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [RapidAPI Hub](https://rapidapi.com)

---

Need help? Check out the full README.md for detailed documentation!

