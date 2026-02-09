"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Basketball": {
        "description": "Learn basketball skills and join our competitive team",
        "schedule": "Monday & Wednesday, 3:30 PM",
        "participants": []
    },
    "Soccer": {
        "description": "Play soccer and develop teamwork skills",
        "schedule": "Tuesday & Thursday, 3:30 PM",
        "participants": []
    },
    "Tennis": {
        "description": "Master tennis techniques and compete in tournaments",
        "schedule": "Monday & Friday, 4:00 PM",
        "participants": []
    },
    "Volleyball": {
        "description": "Join our volleyball team and improve your athletic abilities",
        "schedule": "Wednesday & Saturday, 3:00 PM",
        "participants": []
    },
    "Painting": {
        "description": "Explore painting techniques and create beautiful artworks",
        "schedule": "Tuesday & Thursday, 4:00 PM",
        "participants": []
    },
    "Theater": {
        "description": "Perform in school plays and develop acting skills",
        "schedule": "Monday, Wednesday & Friday, 4:30 PM",
        "participants": []
    },
    "Photography": {
        "description": "Learn photography and capture the world through your lens",
        "schedule": "Saturday, 2:00 PM",
        "participants": []
    },
    "Debate Club": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Tuesday & Thursday, 3:45 PM",
        "participants": []
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts",
        "schedule": "Wednesday, 4:00 PM",
        "participants": []
    },
    "Chess Club": {
        "description": "Master chess strategy and compete with other players",
        "schedule": "Saturday, 1:00 PM",
        "participants": []
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]
   
    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")
    
    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}
