from flask import Flask, request, jsonify, render_template
import pandas as pd
import random
import os, csv, requests, json

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')

# ---------------------------
# User Persistence Functions
# ---------------------------
def load_users():
    users = {}
    filename = 'users.csv'
    if os.path.exists(filename):
        with open(filename, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                username = row["username"]
                users[username] = row
    return users

def save_user(user_data):
    filename = 'users.csv'
    file_exists = os.path.exists(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['username', 'password', 'name', 'age', 'discipline', 'current_semester', 'career_goal']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(user_data)

# -------------------------------
# Subject History Persistence
# -------------------------------
def save_history(history_record):
    filename = 'history.csv'
    file_exists = os.path.exists(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['username', 'subject_code', 'grade', 'attendance', 'semester']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(history_record)

# -------------------------------
# Recommendation Persistence
# -------------------------------
def save_recommendation(rec):
    filename = 'recommendations.csv'
    file_exists = os.path.exists(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['username', 'semester', 'recommended_courses']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(rec)

# ---------------
# Load Courses
# ---------------
courses = pd.read_csv('courses.csv', comment='/', skipinitialspace=True)
courses['Semester'] = pd.to_numeric(courses['Semester'], errors='coerce')
courses['Credits'] = pd.to_numeric(courses['Credits'], errors='coerce')

def filter_courses(search_term, semester):
    filtered = courses[
        (
            (courses['Discipline'].str.contains(search_term, case=False, na=False)) |
            (courses['Course Title'].str.contains(search_term, case=False, na=False))
        ) &
        (courses['Semester'] == int(semester))
    ]
    return filtered

# -------------------
# Registration Endpoint
# -------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    age = data.get('age')
    discipline = data.get('discipline')
    current_semester = data.get('current_semester')
    career_goal = data.get('career_goal', "")

    if not all([username, password, name, age, discipline, current_semester]):
        return jsonify({"error": "All fields (username, password, name, age, discipline, current_semester) are required."}), 400

    users = load_users()
    if username in users:
        return jsonify({"error": "Username already exists."}), 400

    user_data = {
        "username": username,
        "password": password,
        "name": name,
        "age": age,
        "discipline": discipline,
        "current_semester": current_semester,
        "career_goal": career_goal
    }
    save_user(user_data)
    return jsonify({"message": "Registration successful.", "user": user_data})

# -------------------
# Login Endpoint
# -------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    users = load_users()
    user = users.get(username)
    if not user or user.get("password") != password:
        return jsonify({"error": "Invalid credentials."}), 401

    return jsonify({"message": "Login successful.", "user": user})

# ---------------------------
# Add Academic History Endpoint
# ---------------------------
@app.route('/add_history', methods=['POST'])
def add_history():
    data = request.get_json()
    username = data.get('username')
    subject_data = data.get('subject')
    if not username or not subject_data or not subject_data.get("semester"):
        return jsonify({"error": "Username, subject data and a valid semester are required."}), 400

    users = load_users()
    if username not in users:
        return jsonify({"error": "User not found."}), 404

    try:
        semester_value = int(subject_data.get("semester"))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid semester value."}), 400

    history_record = {
        "username": username,
        "subject_code": subject_data.get("subject_code"),
        "grade": subject_data.get("grade"),
        "attendance": subject_data.get("attendance"),
        "semester": semester_value  # saving the semester
    }
    save_history(history_record)
    return jsonify({"message": "Subject history updated.", "record": history_record})

@app.route('/get_history', methods=['GET'])
def get_history():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username is required."}), 400
    if not os.path.exists("history.csv"):
        return jsonify([])
    
    records = []
    with open('history.csv', 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["username"] == username:
                matching = courses[courses['Course Code'] == row["subject_code"]]
                if not matching.empty:
                    course_info = matching.iloc[0]
                    row["course_title"] = course_info["Course Title"]
                    row["credits"] = course_info["Credits"]
                else:
                    row["course_title"] = "Unknown Course"
                    row["credits"] = "N/A"
                records.append(row)
                
    # Clean records: convert None values to empty strings and numpy types to native types.
    cleaned_records = []
    for record in records:
        cleaned_record = {}
        for key, value in record.items():
            if value is None:
                cleaned_record[str(key)] = ""
            elif hasattr(value, "item"):  # e.g., numpy.int64
                cleaned_record[str(key)] = value.item()
            else:
                cleaned_record[str(key)] = value
        cleaned_records.append(cleaned_record)
        
    return jsonify(cleaned_records)

# -------------------
# Update Profile Endpoint
# -------------------
@app.route('/update_profile', methods=['POST'])
def update_profile():
    data = request.get_json()
    username = data.get('username')
    if not username:
        return jsonify({"error": "Username is required."}), 400

    users = load_users()
    if username not in users:
        return jsonify({"error": "User not found."}), 404

    # Update user info and include new 'career_goal' field
    updated_user = {
        "username": username,
        "password": data.get('password', users[username].get('password')),
        "name": data.get('name', users[username].get('name')),
        "age": data.get('age', users[username].get('age')),
        "discipline": data.get('discipline', users[username].get('discipline')),
        "current_semester": data.get('current_semester', users[username].get('current_semester')),
        "career_goal": data.get('career_goal', users[username].get('career_goal', ""))  # new field
    }
    users[username] = updated_user

    # Write updated users back to CSV. Ensure CSV header now includes 'career_goal'
    filename = 'users.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['username', 'password', 'name', 'age', 'discipline', 'current_semester', 'career_goal']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for user in users.values():
            writer.writerow(user)

    return jsonify({"message": "Profile updated.", "user": updated_user})

# -------------------
# Other Endpoints...
# -------------------
@app.route('/get_courses', methods=['GET'])
def get_courses():
    search_term = request.args.get('discipline', '')
    semester = request.args.get('semester', '')
    if not search_term or not semester:
        return jsonify({"error": "Please provide both search term and semester"}), 400
    filtered = filter_courses(search_term, semester)
    if filtered.empty:
        return jsonify({"response": f"No courses found for '{search_term}' in semester {semester}."})
    
    result = filtered.to_dict(orient='records')
    for record in result:
        # Pass CSV Hardness value as-is.
        if "Hardness" not in record or not record["Hardness"]:
            record["Hardness"] = "N/A"
        
        # Request a concise description (under 80 characters)
        prompt = (
            f"Generate a concise description (under 80 characters) for the course: "
            f"{record['Course Code']} - {record['Course Title']}."
        )
        api_response = get_groq_response(prompt)
        description = api_response.get("response", "").strip()
        if len(description) > 80:
            description = description[:80] + "..."
        # Always assign a description – even if short.
        record["Description"] = description if description else "Description not available."
    return jsonify(result)

@app.route('/recommend_courses', methods=['POST'])
def recommend_courses():
    data = request.get_json()
    username = data.get('username')
    if not username:
        return jsonify({"error": "Username is required."}), 400

    users = load_users()
    if username not in users:
        return jsonify({"error": "User not found."}), 404

    # Fetch user's discipline, career goal and current semester from CSV.
    user = users[username]
    discipline = user.get('discipline', '')
    career_goal = user.get('career_goal', '')
    try:
        current_semester = int(user.get('current_semester', 0))
    except (ValueError, TypeError):
        current_semester = 0

    # Obtain the requested recommendation semester from input.
    input_semester = data.get('semester')
    try:
        input_semester = int(input_semester)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid semester input."}), 400

    # Only generate recommendations for a semester earlier than the current one.
    if input_semester < current_semester-1:
        return jsonify({"error": "Recommendation is only available for semesters prior to the current semester."}), 400

    # Filter courses based on fetched discipline and the requested semester.
    filtered = filter_courses(discipline, input_semester)
    if filtered.empty:
        return jsonify({"response": f"No courses found for {discipline} in semester {input_semester}."})
    
    course_list = []
    courses_info = ""
    for _, row in filtered.iterrows():
        mandatory_label = "Mandatory" if float(row['Mandatory']) == 1.0 else "Optional"
        detail = f"{row['Course Code']} - {row['Course Title']} (Credits: {row['Credits']}, {mandatory_label})"
        course_list.append(detail)
        courses_info += f"{detail}\n"
    
    # Build the recommendation prompt.
    prompt = (
        f"Given the following courses available in semester {input_semester} for {discipline}:\n"
        f"{courses_info}\n"
        f"The student is interested in a career in {career_goal}.\n"
        "Make sure to include all mandatory courses (label them as 'Mandatory') and ensure that the recommended courses total between 20 and 30 credits.\n"
        "Provide a concise one-line recommendation including only the course code, title, and a brief reason, indicating if a course is mandatory.\n"
    )
    # Also include predicted grade if present.
    predicted_grade = data.get('predicted_grade')
    if predicted_grade is not None:
        prompt += f" The student's predicted grade is {predicted_grade}%."
    
    groq_response = get_groq_response(prompt)
    
    # Save only the required fields: username, semester and recommended courses.
    recommendation_record = {
        "username": username,
        "semester": input_semester,
        "recommended_courses": "; ".join(course_list)
    }
    save_recommendation(recommendation_record)
    
    return jsonify({
        "courses": course_list,
        "recommendation_explanation": groq_response.get("response", "No recommendation received.")
    })

@app.route('/predict_grades', methods=['POST'])
def predict_grades():
    data = request.get_json()
    username = data.get('username')
    selected_semester = data.get('semester')
    target_grade = data.get('target_grade')  # expected as percentage, e.g., 85

    if not username or not selected_semester:
        return jsonify({"error": "Username and semester are required."}), 400

    try:
        selected_semester = int(selected_semester)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid semester input."}), 400

    try:
        target_grade = float(target_grade) if target_grade is not None else None
    except (ValueError, TypeError):
        target_grade = None

    # Load all past academic records for the user from history.csv
    history_records = []
    if os.path.exists("history.csv"):
        with open('history.csv', 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["username"] == username:
                    history_records.append(row)
    
    history_summary = ""
    if history_records:
        history_summary += "Past Academic Records:\n"
        for rec in history_records:
            history_summary += f"{rec['subject_code']} - Grade: {rec['grade']} (Semester: {rec['semester']})\n"
    else:
        history_summary += "No past academic records available.\n"
    
    # Get recommended courses for the selected semester from recommendations.csv
    recommended_courses = ""
    if os.path.exists("recommendations.csv"):
        with open('recommendations.csv', 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    rec_sem = int(row["semester"])
                except (ValueError, TypeError):
                    continue
                if row["username"] == username and rec_sem == selected_semester:
                    recommended_courses = row["recommended_courses"]
                    break
    if not recommended_courses:
        recommended_courses = "No recommended courses available for this semester."

    # Build a concise predictive prompt for numeric output.
    prompt = (
        f"Past Academic Records:\n{history_summary}\n"
        f"Recommended Courses for Semester {selected_semester}:\n{recommended_courses}\n"
    )
    if target_grade is not None:
        prompt += f"Target Grade: {target_grade}%.\n"
    prompt += (
        "Return a table with three columns: Course Code, Predicted Grade (%) and Required Grade (%) "
        "with numeric values only, without explanation or additional text."
    )
    
    groq_response = get_groq_response(prompt)
    return jsonify({"predicted_grade_details": groq_response.get("response", "No prediction received.")})

@app.route('/generate_skill_chart', methods=['GET'])
def generate_skill_chart():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username is required."}), 400

    # Check if the skill chart for this user is already saved
    filename = 'skillcharts.csv'
    saved_skills = None
    if os.path.exists(filename):
        with open(filename, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row.get('username') == username:
                    try:
                        saved_skills = json.loads(row.get('skills', '{}'))
                    except Exception:
                        saved_skills = {}
                    break
    if saved_skills:
        # Return saved skills if available (do not re-generate)
        return jsonify(saved_skills)

    # No saved record – generate a new skill chart via Groq API.
    users = load_users()
    if username not in users:
        return jsonify({"error": "User not found."}), 404

    user = users[username]
    # Build a string with user details from users.csv
    user_data = (
        f"Username: {user.get('username')}, "
        f"Name: {user.get('name')}, "
        f"Age: {user.get('age')}, "
        f"Discipline: {user.get('discipline')}, "
        f"Current Semester: {user.get('current_semester')}, "
        f"Career Goal: {user.get('career_goal')}"
    )
    # Updated prompt: instruct AI to output ONLY pure JSON (5 key skills and numeric ratings)
    prompt = (
        f"Based on the following user data: {user_data}. "
        "Considering academic performance and factors for success, list exactly 5 key skills that the user needs to become successful. "
        "For each skill, provide a numeric rating between 0 and 100 indicating the user's current strength in that area. "
        "Return ONLY a JSON object with the skill names as keys and their numeric ratings as values, without any additional text."
    )
    
    groq_response = get_groq_response(prompt)
    response_text = groq_response.get("response", "{}")
    
    # Try to parse the API response as JSON.
    try:
        skills = json.loads(response_text)
    except Exception as e:
        # Attempt to extract a JSON object if extra text is present.
        start = response_text.find('{')
        end = response_text.rfind('}')
        if start != -1 and end != -1:
            try:
                skills = json.loads(response_text[start:end+1])
            except Exception as ex:
                skills = {"error": "Failed to parse JSON", "raw_response": response_text}
        else:
            skills = {"error": "No JSON object found", "raw_response": response_text}
    
    # Save the generated skills in CSV for future use.
    file_exists = os.path.exists(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['username', 'skills']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({"username": username, "skills": json.dumps(skills)})

    return jsonify(skills)

def get_groq_response(user_input, language="english"):
    groq_api_key = "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"#paste api key here
    if not groq_api_key:
        return {"response": "API key not configured."}
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gemma2-9b-it",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.ok:
        json_response = response.json()
        if "choices" in json_response and len(json_response["choices"]) > 0:
            return {"response": json_response["choices"][0]["message"]["content"]}
        else:
            return {"response": "No response received from Groq API."}
    else:
        return {"response": f"Error calling Groq API: {response.status_code}, {response.text}"}

@app.route('/chat_with_ai', methods=['POST'])
def chat_with_ai():
    data = request.get_json()
    user_message = data.get('message', '')
    groq_response = get_groq_response(user_message)
    return jsonify(groq_response)

@app.route('/')
def index():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)