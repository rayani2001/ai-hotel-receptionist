# 🚀 Complete Setup Guide - AI Hotel Receptionist

## Step-by-Step Installation for VSCode

### Prerequisites Check
Before starting, ensure you have:
- ✅ Python 3.9 or higher
- ✅ VSCode installed
- ✅ OpenAI API key OR Anthropic API key
- ✅ Internet connection

---

## Step 1: Open Project in VSCode

1. **Open VSCode**
2. **Open Folder**: File → Open Folder
3. **Navigate to** `ai-hotel-receptionist` folder
4. **Click** "Select Folder"

---

## Step 2: Create Virtual Environment

### Option A: Using VSCode Terminal
1. Open Terminal in VSCode: `` Ctrl+` `` (backtick)
2. Run:
```bash
python -m venv venv
```

### Option B: Using Command Palette
1. Press `Ctrl+Shift+P`
2. Type: "Python: Create Environment"
3. Select "Venv"
4. Choose Python 3.9+

---

## Step 3: Activate Virtual Environment

### Windows:
```bash
venv\Scripts\activate
```

### Mac/Linux:
```bash
source venv/bin/activate
```

**You should see `(venv)` at the beginning of your terminal prompt**

---

## Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**This will take 5-10 minutes to install all packages.**

### If you encounter errors:

#### For PyAudio errors (Windows):
```bash
pip install pipwin
pipwin install pyaudio
```

#### For PyAudio errors (Mac):
```bash
brew install portaudio
pip install pyaudio
```

#### For PyAudio errors (Linux):
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

---

## Step 5: Get API Keys

### Option A: OpenAI (Recommended)
1. Go to: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-...`)

### Option B: Anthropic (Alternative)
1. Go to: https://console.anthropic.com/
2. Navigate to API Keys
3. Create new key
4. Copy the key

---

## Step 6: Configure Environment Variables

1. **Copy the example file:**
```bash
cp .env.example .env
```

2. **Open `.env` file in VSCode**

3. **Fill in your API key:**

For OpenAI:
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-actual-key-here
```

For Anthropic:
```env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-anthropic-key-here
```

4. **Optional**: Customize hotel information:
```env
HOTEL_NAME=Your Hotel Name
HOTEL_ADDRESS=Your Address
HOTEL_PHONE=Your Phone
```

5. **Save the file** (`Ctrl+S`)

---

## Step 7: Initialize Database

Run the initialization script:

```bash
python scripts/init_database.py
```

**Expected output:**
```
AI HOTEL RECEPTIONIST - DATABASE INITIALIZATION
Creating database tables...
Database tables created successfully
Creating sample rooms...
Created 29 rooms
Creating sample bookings...
Created sample booking
DATABASE INITIALIZATION COMPLETE!
```

---

## Step 8: Start the Application

```bash
python main.py
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Step 9: Access the Application

### Open in Browser:

1. **Main Page**: http://localhost:8000
2. **Chat Interface**: http://localhost:8000/api/chat-ui
3. **API Documentation**: http://localhost:8000/docs

---

## Step 10: Test the System

### Test 1: Simple Chat
1. Open http://localhost:8000/api/chat-ui
2. Type: "Hello"
3. You should get a greeting response

### Test 2: Room Inquiry
1. Type: "What room types do you have?"
2. You should see room types and prices

### Test 3: Booking Flow
1. Type: "I want to book a room"
2. Follow the conversation flow
3. Provide: name, phone, dates, room type, guest count

### Test 4: Multi-language
1. Type: "नमस्ते" (Hindi)
2. System should detect Hindi and respond accordingly

---

## Troubleshooting

### Problem: Import errors
**Solution:**
```bash
# Make sure virtual environment is activated
# Check if you see (venv) in terminal

# Reinstall requirements
pip install -r requirements.txt
```

### Problem: Database errors
**Solution:**
```bash
# Delete existing database
rm hotel_receptionist.db

# Reinitialize
python scripts/init_database.py
```

### Problem: API key errors
**Solution:**
- Check `.env` file has correct API key
- Make sure no extra spaces
- Verify key is valid on provider website
- Check if AI_PROVIDER matches your key type

### Problem: Port already in use
**Solution:**
```bash
# Change port in main.py
# Find: uvicorn.run(..., port=8000)
# Change to: port=8080

# Or kill existing process:
# Windows: netstat -ano | findstr :8000
# Linux/Mac: lsof -ti:8000 | xargs kill -9
```

### Problem: Module not found errors
**Solution:**
```bash
# Make sure you're in project root directory
cd ai-hotel-receptionist

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows

# Install missing module
pip install <module_name>
```

---

## Verification Checklist

✅ Virtual environment activated
✅ All dependencies installed
✅ `.env` file configured with API key
✅ Database initialized successfully
✅ Server starts without errors
✅ Can access http://localhost:8000
✅ Chat interface works
✅ Bot responds to messages

---

## Next Steps

### 1. Customize Your Hotel
Edit `config/settings.py` to add:
- Your room types and prices
- Dining options
- Party hall configurations

### 2. Test Advanced Features
- Try different languages
- Test booking flow end-to-end
- Check analytics dashboard

### 3. Deploy (Optional)
See DEPLOYMENT.md for production deployment

---

## Quick Commands Reference

```bash
# Activate environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Start server
python main.py

# Initialize database
python scripts/init_database.py

# Run tests (if added)
pytest tests/

# View logs
tail -f logs/app.log  # Mac/Linux
type logs\app.log     # Windows
```

---

## Support

If you encounter issues:

1. Check logs in `logs/app.log`
2. Review error messages carefully
3. Make sure all prerequisites are installed
4. Verify API keys are valid

---

## Development Tips

### VSCode Extensions (Recommended):
- Python (Microsoft)
- Pylance
- Python Docstring Generator
- Better Comments
- Error Lens

### To stop the server:
- Press `Ctrl+C` in terminal

### To restart the server:
- Stop with `Ctrl+C`
- Run `python main.py` again

---

## Success! 🎉

You now have a fully functional AI hotel receptionist system running locally!

**Test it by chatting at:** http://localhost:8000/api/chat-ui
