from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://gxbot:GlxBot%40321@GxbotApp01:27017/?authSource=gxbot" 

client = AsyncIOMotorClient(MONGO_URI)
db = client["AutomatedValidator"]  # replace with your DB name
