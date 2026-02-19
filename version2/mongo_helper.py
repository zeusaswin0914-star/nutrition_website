
import pymongo
from datetime import datetime, timedelta
from bson.objectid import ObjectId

# Global client
client = None
db = None

def connect_db():
    global client, db
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["nutrition_app_v2"]
        print("Connected to MongoDB")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")

# Ensure connection is established
connect_db()

def save_user(user_data):
    """
    Save user data to 'users' collection.
    Update if email exists.
    """
    if db is None: connect_db()
    users = db.users
    # Check if user exists
    existing = users.find_one({'email': user_data['email']})
    
    # Create copy to avoid mutating original dict with _id if we don't want to
    data_to_save = user_data.copy()
    
    # Remove _id if it's there as string, let mongo handle it or convert to ObjectId if needed
    if '_id' in data_to_save:
         # used for session storage, remove before saving/updating to avoid immutable field error
         del data_to_save['_id']

    if existing:
        users.update_one({'email': user_data['email']}, {'$set': data_to_save})
        # After update, get the ID
        user_id = existing['_id']
    else:
        result = users.insert_one(data_to_save)
        user_id = result.inserted_id
    
    # Return user_data with _id as string for session serialization
    user_data['_id'] = str(user_id)
    return user_data

def get_user_by_email(email):
    if db is None: connect_db()
    users = db.users
    user = users.find_one({'email': email})
    if user:
        user['_id'] = str(user['_id'])
    return user

def get_user(email):
    return get_user_by_email(email)

def save_report(email, report_data):
    """
    Save report to 'reports' collection.
    Link with email.
    """
    if db is None: connect_db()
    reports = db.reports
    
    data_to_save = report_data.copy()
    
    # Add timestamp if not present
    if 'timestamp' not in data_to_save:
        data_to_save['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    # Associate with user email
    data_to_save['user_email'] = email
    
    if '_id' in data_to_save:
        del data_to_save['_id']
        
    result = reports.insert_one(data_to_save)
    report_id = result.inserted_id
    
    # Update with calculated PDF path
    reports.update_one(
        {'_id': report_id}, 
        {'$set': {'pdf_path': f'/download_report/{report_id}'}}
    )
    
    return str(report_id)

def get_reports_for_user(email):
    if db is None: connect_db()
    reports_col = db.reports
    reports = list(reports_col.find({'user_email': email}).sort('timestamp', -1))
    for r in reports:
        r['id'] = str(r['_id']) # App uses 'id'
        r['_id'] = str(r['_id'])
    return reports

def get_user_reports(email):
    return get_reports_for_user(email)

def get_report_by_id(report_id):
    if db is None: connect_db()
    reports_col = db.reports
    try:
        report = reports_col.find_one({'_id': ObjectId(report_id)})
        if report:
            report['id'] = str(report['_id'])
            report['_id'] = str(report['_id'])
        return report
    except:
        return None

def delete_report(report_id):
    if db is None: connect_db()
    reports_col = db.reports
    try:
        result = reports_col.delete_one({'_id': ObjectId(report_id)})
        return result.deleted_count > 0
    except Exception as e:
        return False

def save_otp(email, otp):
    """Save OTP with 5 minute expiration."""
    if db is None: connect_db()
    otp_col = db.otp_verifications
    
    # Expiry time
    now = datetime.utcnow()
    expires_at = now + timedelta(minutes=5)
    
    # Upsert: Replace existing OTP if any
    otp_col.update_one(
        {'email': email},
        {'$set': {
            'otp': otp,
            'expires_at': expires_at,
            'verified': False,
            'created_at': now
        }},
        upsert=True
    )
    return True

def verify_and_delete_otp(email, otp):
    """
    Verify OTP. 
    Returns True if valid and not expired.
    Deletes OTP after successful verification.
    """
    if db is None: connect_db()
    otp_col = db.otp_verifications
    
    record = otp_col.find_one({'email': email})
    
    if not record:
        return False, "No OTP requests found."
        
    if record['expires_at'] < datetime.utcnow():
        return False, "OTP has expired."
        
    if record['otp'] != otp:
        return False, "Invalid OTP."
        
    # Success - Delete record
    otp_col.delete_one({'email': email})
    return True, "Verified"

def update_password(email, password_hash):
    """Update user password hash."""
    if db is None: connect_db()
    users = db.users
    
    result = users.update_one(
        {'email': email},
        {'$set': {'password_hash': password_hash}}
    )
    return result.modified_count > 0
