from Database.mongo import db

users_db = db["user"]

class UserService:
    @staticmethod
    async def login_user(login_data: dict) -> dict:
        username = login_data.get("username")
        password = login_data.get("password")

        if not username or not password:
            return {
                "status": "fail",
                "message": "Username and password are required",
                "data": {}
            }

        user = await users_db.find_one({"username": username})

        if not user or user.get("password") != password:
            return {
                "status": "fail",
                "message": "Invalid username or password",
                "data": {}
            }

        return {
            "status": "success",
            "message": "Login successful",
            "data": {"username": username, "password": password}
        }
