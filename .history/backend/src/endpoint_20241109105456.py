from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app import App, create_mobility_visualization
from langchain_openai import ChatOpenAI
from utils.agent_tools import GoogleAPIClient
import os
import dotenv
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
dotenv.load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
client = GoogleAPIClient(os.getenv('GOOGLE_API_KEY'))
llm = ChatOpenAI(model_name="gpt-4", temperature=0.7)
workflow = App(llm)

class UserInput(BaseModel):
    user_description: str
    current_day_index: int = 0
    plans: Optional[Any] = None

@app.post("/generate-mobility-trace")
async def generate_mobility_trace(user_input: UserInput):
    try:
        config = {"recursion_limit": 50}
        traces = []
        
        # Process the workflow
        async for event in workflow.setup().astream(user_input.dict(), config=config):
            for k, v in event.items():
                if k != "__end__":
                    traces.append(v)
        
        # Post-process traces
        schedule_df, routes, time, day, travel_mode = workflow.post_process_traces(
            client, traces
        )
        
        return {
            'schedule_df': schedule_df.to_dict(orient='records'),
            'routes': routes,
            'time': time,
            'day': day,
            'travel_mode': travel_mode
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)