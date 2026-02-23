import uvicorn
import sys
import os

# Change to backend directory
os.chdir(r"C:\Users\HP\.openclaw\workspace\ClawForge\backend")

# Add backend to path
sys.path.insert(0, r"C:\Users\HP\.openclaw\workspace\ClawForge\backend")

# Run the server on port 8000
if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=False)
