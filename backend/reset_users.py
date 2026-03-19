from app import mongo

def reset_users_collection():
    # WARNING: This will delete all documents in users collection
    result = mongo.db.users.delete_many({})
    print(f"Deleted {result.deleted_count} user(s) from the database.")

if __name__ == "__main__":
    reset_users_collection()