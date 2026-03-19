from datetime import datetime
from app import mongo


def create_user(name, email, hashed_password, role="user", is_donor=False, is_requester=False,
                blood_group=None, city=None, longitude=None, latitude=None):
    """
    Creates a user document in the users collection.

    Roles:
      - "user"  → a normal user; can be a donor, a requester, or both.
      - "admin" → platform administrator; no donor/requester flags needed.

    For role="user", at least one of is_donor or is_requester must be True.
    If is_donor=True, blood_group, city, longitude, and latitude are required.
    """

    if role not in ("user", "admin"):
        raise ValueError("role must be 'user' or 'admin'")

    if role == "user" and not (is_donor or is_requester):
        raise ValueError("A user must be at least a donor or a requester")

    user = {
        "name": name,
        "email": email,
        "password": hashed_password,
        "role": role,
        "created_at": datetime.utcnow()
    }

    if role == "user":
        user["is_donor"] = bool(is_donor)
        user["is_requester"] = bool(is_requester)
        user["city"] = city or ""

        if is_donor:
            if not blood_group or longitude is None or latitude is None:
                raise ValueError("Donor must provide blood_group, longitude, and latitude")
            user["blood_group"] = blood_group
            user["location"] = {
                "type": "Point",
                "coordinates": [float(longitude), float(latitude)]
            }

    return mongo.db.users.insert_one(user)