"""
EthicPrivAI API Server Launcher
================================
Starts the FastAPI backend server using Uvicorn.
"""

import uvicorn

if __name__ == "__main__":
    print("Starting EthicPrivAI API Server at http://localhost:8000 ...")
    uvicorn.run("ethicprivai.api.app:app", host="0.0.0.0", port=8000, reload=True)
