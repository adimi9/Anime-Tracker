# 🎥 Anime Tracker REST API  

This is a **REST API** built with **Django REST Framework** using **Test-Driven Development (TDD)**. It allows users to track their anime watch status, manage genres, and more!  

---

## 🚀 Features  

✅ **User Authentication** (Token-based)  
✅ **CRUD Operations** for Anime, Watch Status, and Genres  
✅ **Secure Endpoints** (Only authenticated users can modify data)  
✅ **Test-Driven Development (TDD)** with `unittest`  
✅ **Uses SQLite by default, but supports PostgreSQL**  

---

## 🔧 Installation  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/yourusername/anime-tracker.git
cd anime-tracker
```
### 2️⃣ Create a Virtual Environment & Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```
### 3️⃣ Setup Environment Variables
You must create a .env file inside api/app/ before running the project.
Create the .env file:
```bash
touch api/app/.env
```
Inside .env, add:
```bash
DJANGO_SECRET_KEY=your_secret_key_here
```
🔹 Replace your_secret_key_here with a strong, random key.
🔹 This is required, otherwise Django will throw an error.
### 4️⃣ Run Migrations
```bash
python api/manage.py migrate
```
### 5️⃣ Run the Server
```bash
python api/manage.py runserver
```
Your API will be available at: http://127.0.0.1:8000/ 🎉

---

## 📌 API Endpoints
### 📚 API Endpoints
#### User Authentication
- POST /api/user/create/ - Create a new user.
- POST /api/user/token/ - Generate an authentication token.
#### Anime Management
- GET /api/anime/animes/ - Get a list of all animes (with filters for genres and watch status).
- POST /api/anime/animes/ - Add a new anime to your collection.
- GET /api/anime/animes/{anime_id}/ - Retrieve details for a specific anime.
- PATCH /api/anime/animes/{anime_id}/ - Update an anime's details.
- DELETE /api/anime/animes/{anime_id}/ - Delete a specific anime.
#### Watch Status Management
- GET /api/anime/watch_status/ - Get all watch statuses.
- POST /api/anime/watch_status/ - Add a new watch status.
#### Genre Management
- GET /api/anime/genres/ - Get a list of all genres.
- POST /api/anime/genres/ - Add a new genre.

---

## 📝 Usage
Authentication: After creating a user and generating a token, use the token in the Authorization header for secure access to the endpoints.
``` bash
Authorization: Token your_token_here
```
Filter Animes: You can filter animes by watch status or genres by passing their IDs in the query parameters.
``` bash
GET /api/anime/animes/?watch_status=1&genres=2,3
```

---

## 🧪 Test-Driven Development (TDD)
This API was developed using Test-Driven Development (TDD) principles with Django’s test framework. Here's why:

- Automated Tests: Before writing the actual API code, tests were written to define expected behavior.
- Test Coverage: Every feature, from user authentication to anime CRUD operations, is covered by automated tests.
- Ensures Reliability: TDD ensures that any new features or updates do not break existing functionality.

#### Running Tests
You can run the project's tests using Django's built-in testing framework to verify the integrity of the codebase:

``` bash
python api/manage.py test tests
```
📌 Make sure you are inside the project root (anime-tracker/) before running this command.

#### Writing Tests
The tests are located in the anime/tests/ directory. Each feature has corresponding test files that validate its functionality.

---

## 💡 Future Features
- Add anime ratings and reviews to enrich the anime-tracking experience.
- Implement user-specific anime recommendations based on watch status and genres.
- Add image upload functionality for anime cover art.
