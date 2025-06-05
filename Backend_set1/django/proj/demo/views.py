from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bson import ObjectId
import json
import bcrypt
import jwt
import datetime
import os
from .mongodb import users_collection, products_collection

JWT_SECRET = os.getenv("JWT_SECRET", "your_jwt_secret_here")

# Helper: Encode JWT
def generate_jwt(user):
    payload = {
        "user_id": str(user["_id"]),
        "username": user["username"],
        "role": user["role"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

# Middleware-like JWT decorator
def authenticate(view_func):
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"message": "No token provided"}, status=401)
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.user = payload
            return view_func(request, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return JsonResponse({"message": "Token expired"}, status=403)
        except jwt.InvalidTokenError:
            return JsonResponse({"message": "Invalid token"}, status=403)
    return wrapper

# Admin-only decorator
def admin_only(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.get("role") != "admin":
            return JsonResponse({"message": "Admins only"}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper

@csrf_exempt
def register_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        username = data["username"]
        password = data["password"]
        role = data.get("role", "consumer")

        if users_collection.find_one({"username": username}):
            return JsonResponse({"message": "Username already exists"}, status=400)

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        user = {
            "username": username,
            "password": hashed.decode(),
            "role": role if role == "admin" else "consumer"
        }
        result = users_collection.insert_one(user)
        user["_id"] = str(result.inserted_id)
        return JsonResponse({"message": "Registration successful. You can now login."})
    except Exception as e:
        return JsonResponse({"message": "Registration failed: " + str(e)}, status=500)

@csrf_exempt
def login_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        username = data["username"]
        password = data["password"]

        user = users_collection.find_one({"username": username})
        if not user:
            return JsonResponse({"message": "Login failed. Please try again."}, status=401)

        if not bcrypt.checkpw(password.encode(), user["password"].encode()):
            return JsonResponse({"message": "Login failed. Please try again."}, status=401)

        token = generate_jwt(user)
        return JsonResponse({"token": token, "role": user["role"]})
    except Exception as e:
        return JsonResponse({"message": "Login failed: " + str(e)}, status=500)

@authenticate
def get_products(request):
    try:
        products = list(products_collection.find({}))
        for p in products:
            p["_id"] = str(p["_id"])
        return JsonResponse(products, safe=False)
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)

@csrf_exempt
@authenticate
@admin_only
def update_product(request, id):
    if request.method == "PUT":
        # return JsonResponse({"error": "PUT required"}, status=405)\
        try:
            data = json.loads(request.body)
            result = products_collection.find_one_and_update(
                {"_id": ObjectId(id)},
                {"$set": data},
                return_document=True
            )
            if not result:
                return JsonResponse({"message": "Product not found"}, status=404)
            result["_id"] = str(result["_id"])
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({"message": "Error updating product", "error": str(e)}, status=500)
    elif request.method=='DELETE':
        try:
            result = products_collection.delete_one({"_id": ObjectId(id)})
            if result.deleted_count == 0:
                return JsonResponse({"message": "Product not found"}, status=404)
            return JsonResponse({"message": "Product deleted"})
        except Exception as e:
            return JsonResponse({"message": "Error deleting product", "error": str(e)}, status=500)
    return JsonResponse({"error": "DELETE required"}, status=405)
