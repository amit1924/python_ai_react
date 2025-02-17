from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
import sqlite3
import google.generativeai as genai
import os
from fastapi.middleware.cors import CORSMiddleware
import re
from PIL import Image
import io

# Load Gemini API Key
GEMINI_API_KEY = "AIzaSyDsdvYPIRx0taU2zrCZ_RUeNK7OPQGeLFQ"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize FastAPI app
app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello World"}


# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DB_NAME = "chat_memory.db"
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

# Create tables for chat history and user info (dynamic)
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    bot TEXT
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS user_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    attribute TEXT,
    value TEXT
)
"""
)

conn.commit()


# Request model
class ChatRequest(BaseModel):
    message: str


# Function to store chat messages
def store_chat(user_message, bot_response):
    cursor.execute(
        "INSERT INTO chat_history (user, bot) VALUES (?, ?)",
        (user_message, bot_response),
    )
    conn.commit()


# Function to store dynamic user info (e.g., name, favorite color, hobbies, etc.)
def store_user_info(attribute, value):
    cursor.execute(
        "INSERT INTO user_info (user, attribute, value) VALUES (?, ?, ?)",
        ("current_user", attribute, value),
    )
    conn.commit()


# Function to get user info
def get_user_info(attribute):
    cursor.execute(
        "SELECT value FROM user_info WHERE user='current_user' AND attribute=?",
        (attribute,),
    )
    result = cursor.fetchone()
    return result[0] if result else None


# Function to get chat history
def get_chat_history():
    cursor.execute("SELECT * FROM chat_history")
    return cursor.fetchall()


# Chat API
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Check if the user has any dynamic information stored (e.g., name, color, hobbies)
        chat_history = get_chat_history()
        conversation = "\n".join(
            [f"User: {entry[1]}\nBot: {entry[2]}" for entry in chat_history]
        )

        # Add context to the conversation
        context = conversation + f"\nUser: {request.message}\nBot:"

        # Check for previously stored information before asking the user again
        if (
            "favorite color" in request.message.lower()
            or "colour" in request.message.lower()
        ):
            favorite_color = get_user_info("favorite_color")
            if favorite_color:
                response_text = f"Your favorite color is {favorite_color}!"
            else:
                response_text = (
                    "I don't know your favorite color yet. Can you tell me what it is?"
                )

        # Search for common patterns (e.g., "My name is", "I like", "My favorite color is")
        elif "my name is" in request.message.lower():
            name = request.message.split("my name is")[-1].strip()
            store_user_info("name", name)
            response_text = f"Got it, your name is {name}!"
        elif "my favorite color is" in request.message.lower():
            color = request.message.split("my favorite color is")[-1].strip()
            store_user_info("favorite_color", color)
            response_text = f"Got it, your favorite color is {color}!"
        elif "i like" in request.message.lower():
            hobby = request.message.split("i like")[-1].strip()
            store_user_info("hobby", hobby)
            response_text = f"Nice! You like {hobby}."
        else:
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(context)
            response_text = response.text

        # Store the chat
        store_chat(request.message, response_text)

        return {"response": response_text}
    except Exception as e:
        print(f"Error in chat API: {e}")  # Log the error to the console
        raise HTTPException(status_code=500, detail="Error generating bot response")


# Endpoint to process the image and generate a response
@app.post("/image")
async def process_image(file: UploadFile = File(...)):
    try:
        # Read the uploaded image
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))

        # Process the image with the Gemini API using the correct model
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(contents=["What is this image?", image])

        # Return the response text
        return {"response": response.text}
    except Exception as e:
        print(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail="Error processing the image")


# Fetch chat history
@app.get("/history")
async def history():
    return {"history": get_chat_history()}


# Run server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


# from fastapi import FastAPI, HTTPException, File, UploadFile
# from pydantic import BaseModel
# import sqlite3
# import google.generativeai as genai
# import os
# from fastapi.middleware.cors import CORSMiddleware
# import re
# from PIL import Image
# import io

# # Load Gemini API Key
# GEMINI_API_KEY = "AIzaSyDsdvYPIRx0taU2zrCZ_RUeNK7OPQGeLFQ"
# genai.configure(api_key=GEMINI_API_KEY)

# # Initialize FastAPI app
# app = FastAPI()


# # Enable CORS for frontend connection
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Database setup
# DB_NAME = "chat_memory.db"
# conn = sqlite3.connect(DB_NAME, check_same_thread=False)
# cursor = conn.cursor()

# # Create tables for chat history and user info (dynamic)
# cursor.execute(
#     """
# CREATE TABLE IF NOT EXISTS chat_history (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     user TEXT,
#     bot TEXT
# )
# """
# )

# cursor.execute(
#     """
# CREATE TABLE IF NOT EXISTS user_info (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     user TEXT,
#     attribute TEXT,
#     value TEXT
# )
# """
# )

# conn.commit()


# # Request model
# class ChatRequest(BaseModel):
#     message: str


# # Function to store chat messages
# def store_chat(user_message, bot_response):
#     cursor.execute(
#         "INSERT INTO chat_history (user, bot) VALUES (?, ?)",
#         (user_message, bot_response),
#     )
#     conn.commit()


# # Function to store dynamic user info (e.g., name, favorite color, hobbies, etc.)
# def store_user_info(attribute, value):
#     cursor.execute(
#         "INSERT INTO user_info (user, attribute, value) VALUES (?, ?, ?)",
#         ("current_user", attribute, value),
#     )
#     conn.commit()


# # Function to get user info
# def get_user_info(attribute):
#     cursor.execute(
#         "SELECT value FROM user_info WHERE user='current_user' AND attribute=?",
#         (attribute,),
#     )
#     result = cursor.fetchone()
#     return result[0] if result else None


# # Function to get chat history
# def get_chat_history():
#     cursor.execute("SELECT * FROM chat_history")
#     return cursor.fetchall()


# # Chat API
# @app.post("/chat")
# async def chat(request: ChatRequest):
#     try:
#         # Check if the user has any dynamic information stored (e.g., name, color, hobbies)
#         chat_history = get_chat_history()
#         conversation = "\n".join(
#             [f"User: {entry[1]}\nBot: {entry[2]}" for entry in chat_history]
#         )

#         # Add context to the conversation
#         context = conversation + f"\nUser: {request.message}\nBot:"

#         # Check for previously stored information before asking the user again
#         if (
#             "favorite color" in request.message.lower()
#             or "colour" in request.message.lower()
#         ):
#             favorite_color = get_user_info("favorite_color")
#             if favorite_color:
#                 response_text = f"Your favorite color is {favorite_color}!"
#             else:
#                 response_text = (
#                     "I don't know your favorite color yet. Can you tell me what it is?"
#                 )

#         # Search for common patterns (e.g., "My name is", "I like", "My favorite color is")
#         elif "my name is" in request.message.lower():
#             name = request.message.split("my name is")[-1].strip()
#             store_user_info("name", name)
#             response_text = f"Got it, your name is {name}!"
#         elif "my favorite color is" in request.message.lower():
#             color = request.message.split("my favorite color is")[-1].strip()
#             store_user_info("favorite_color", color)
#             response_text = f"Got it, your favorite color is {color}!"
#         elif "i like" in request.message.lower():
#             hobby = request.message.split("i like")[-1].strip()
#             store_user_info("hobby", hobby)
#             response_text = f"Nice! You like {hobby}."
#         else:
#             model = genai.GenerativeModel(
#                 "gemini-2.0-flash"
#             )  # Confirm this call is correct
#             response = model.generate_content(context)
#             response_text = response.text

#         # Store the chat
#         store_chat(request.message, response_text)

#         return {"response": response_text}
#     except Exception as e:
#         print(f"Error in chat API: {e}")  # Log the error to the console
#         raise HTTPException(status_code=500, detail="Error generating bot response")


# # Endpoint to process the image and generate a response
# @app.post("/image")
# async def process_image(file: UploadFile = File(...)):
#     try:
#         # Read the uploaded image
#         image_bytes = await file.read()
#         image = Image.open(io.BytesIO(image_bytes))

#         # Process the image with the Gemini API using the correct model
#         model = genai.GenerativeModel(
#             "gemini-2.0-flash"
#         )  # Confirm this call is correct
#         response = model.generate_content(contents=["What is this image?", image])

#         # Return the response text
#         return {"response": response.text}
#     except Exception as e:
#         print(f"Error processing image: {e}")
#         raise HTTPException(status_code=500, detail="Error processing the image")


# # Fetch chat history
# @app.get("/history")
# async def history():
#     return {"history": get_chat_history()}


# @app.get("/home")
# def read_root():
#     return {"message": "Hello World"}


# # Run server
# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="0.0.0.0", port=8000)
