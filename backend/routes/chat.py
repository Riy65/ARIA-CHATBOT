import logging
from bson import ObjectId
from fastapi import APIRouter, Depends
from database import ( messages_collection, conversations_collection)
from schemas import chat_message
from datetime import datetime, timedelta
from ai_client import get_ai_reply, generate_chat_title
from utils.auth import get_current_user
from models.chat import ChatRequest

router = APIRouter()

@router.post("/new")
def create_conversation(current_user=Depends(get_current_user)):

    conversation = {

        "user_id": current_user["email"],

        "title": "New Chat",

        "created_at": datetime.utcnow(),

        "updated_at": datetime.utcnow()

    }

    result = conversations_collection.insert_one(conversation)

    return {

        "conversation_id": str(result.inserted_id),

        "title": "New Chat"

    }

@router.post("/send")
def send_message(request: ChatRequest, current_user = Depends(get_current_user)):
    user_id = current_user["email"]
    conversation_id = request.conversation_id
    user_message = request.message

    # 1 Store user message
    user_msg = chat_message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
        content=user_message
    )
    messages_collection.insert_one(user_msg)

    # 2️ Fetch recent chat history (last 10 messages)
    history = list(
        messages_collection.find(
            {"conversation_id": conversation_id},
            {"_id": 0, "role": 1, "content": 1}
        )
        .sort("timestamp", -1)
        .limit(10)
    )

    history.reverse()  # oldest → newest

    # 3️ Add system prompt
    messages = [
        {
            "role": "system",
            "content": "You are a helpful, polite, and concise chatbot."
        }
    ] + history

    # 4️ Get AI reply (safe fallback if quota not ready)
    try:
        ai_reply = get_ai_reply(messages)
    except Exception as e:
        import logging
        logging.error(f"AI ERROR: {e}")

        ai_reply = "AI service is temporarily unavailable. Please try again shortly."

    # 5️ Store AI reply
    bot_msg = chat_message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="assistant",
        content=ai_reply
    )
    messages_collection.insert_one(bot_msg)
    conversation = conversations_collection.find_one(
    {
        "_id": ObjectId(conversation_id)
    }
)

    if conversation["title"] == "New Chat":

        title = generate_chat_title(
            user_message,
            ai_reply
        )

        conversations_collection.update_one(

            {
                "_id": ObjectId(conversation_id)
            },

            {
                "$set": {
                    "title": title,
                    "updated_at": datetime.utcnow()
                }
            }

        )

    # 6️ Return reply
    return {

    "reply": ai_reply,

    "title": title if conversation["title"] == "New Chat"
            else conversation["title"]

}

@router.get("/history")
def get_chat_history(current_user=Depends(get_current_user)):

    user_id = current_user["email"]

    ten_days_ago = datetime.utcnow() - timedelta(days=10)

    chats = messages_collection.find(
        {
            "user_id": user_id,
            "timestamp": {"$gte": ten_days_ago}
        },
        {"_id": 0}
    )

    return list(chats)

@router.get("/conversations")
def get_conversations(current_user=Depends(get_current_user)):

    conversations = list(
        conversations_collection.find(
            {
                "user_id": current_user["email"]
            },
            {
                "_id": 1,
                "title": 1,
                "updated_at": 1
            }
        ).sort("updated_at", -1)
    )

    for conversation in conversations:

        conversation["conversation_id"] = str(conversation["_id"])

        del conversation["_id"]

    return conversations




@router.get("/messages/{conversation_id}")
def get_messages(
    conversation_id: str,
    current_user=Depends(get_current_user)
):

    messages = list(

        messages_collection.find(

            {
                "conversation_id": conversation_id,
                "user_id": current_user["email"]
            },

            {
                "_id": 0
            }

        ).sort("timestamp", 1)

    )

    return messages


@router.delete("/conversation/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    current_user=Depends(get_current_user)
):

    conversations_collection.delete_one(

        {
            "_id": ObjectId(conversation_id),
            "user_id": current_user["email"]
        }

    )

    messages_collection.delete_many(

        {
            "conversation_id": conversation_id,
            "user_id": current_user["email"]
        }

    )

    return {

        "message":"Conversation deleted"

    }