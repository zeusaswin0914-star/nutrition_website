
# Version 2 Backend - MongoDB Integration

This directory contains the backend code for the Nutrition App Version 2, now integrated with MongoDB for data persistence.

## 1. MongoDB Setup

Ensure MongoDB is installed and running locally on port 27017.

**Connection String:** `mongodb://localhost:27017/`
**Database Name:** `nutrition_app_v2`

### Collections
1. **`users`**: Stores user profile information.
2. **`reports`**: Stores generated health reports and diet plans.

## 2. Schema Documentation

### Users Collection (`users`)
Stores user registration details.
```json
{
  "_id": "ObjectId('...')",
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30,
  "gender": 1, // 1 for Male, 0 for Female
  "height": 175.0,
  "weight": 70.0,
  "goal": "Health",
  "diet_type": "Vegetarian",
  "bmi": 22.86
}
```

### Reports Collection (`reports`)
Stores analysis results for each upload. Linked to user by email.
```json
{
  "_id": "ObjectId('...')",
  "user_email": "john@example.com",
  "timestamp": "2023-10-27 10:30:00",
  "user_profile": { ... }, // Snapshot of profile at time of report
  "lab_results": {
    "hemoglobin": 14.5,
    "glucose": 95,
    ...
  },
  "health_status": "Healthy",
  "diet_plan": {
    "Monday": { ... },
    ...
  },
  "macros": {
    "carbs": 50,
    "protein": 30,
    "fat": 20
  },
  "deficiencies": [],
  "assessment": [ ... ],
  "recommendation_table_data": [ ... ],
  "prediction": 2000
}
```

## 3. Integration Details
- **`mongo_helper.py`**: Handles database connections and CRUD operations using `pymongo`.
- **`app.py`**: Imported as `db` module to replace the previous file-based storage.

## 4. Running the App
1. Start MongoDB service.
2. Run data pipeline or verify requirements: `pip install pymongo`
3. Start Flask app:
   ```bash
   python version2/app.py
   ```
