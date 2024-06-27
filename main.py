#Libraries
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.general_use_router import general_use_router 

# Initialize FastAPI app
app = FastAPI()

# Configure CORS settings
origins = [
    "http://localhost",
    "https://track-finder-frontend.vercel.app"  # Add the URL of your Angular frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"]
)

# Additional endpoints can be added as needed
#app.include_router(prefix="/openAI", router=openAI_router)
app.include_router(prefix="/general_use", router=general_use_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8000, reload=True)