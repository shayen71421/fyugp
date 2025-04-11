
# 📚 EDUSYNC – AI-Enhanced Academic Guidance System

🚀 Developed for **Techathlon 2024-25** hosted by **ICT Academy of Kerala**

---

## 🏆 About the Event

**Techathlon 2024-25** is a prestigious competition designed to spark innovation among budding technologists. This year's focus was on **FYUGP (Four-Year Undergraduate Programme)** and **Generative AI**, and EDUSYNC was our response to that challenge.

---

## 💡 Project Overview

**EDUSYNC** is a smart academic recommendation and psychological assessment platform tailored for **FYUGP students**. By blending curriculum intelligence, performance tracking, and AI-powered interactions, EDUSYNC provides a personalized, empathetic academic roadmap for every learner.

---

## 🎯 Key Features

### 🧠 AI-Powered Academic Advisor
- Personalized course recommendations based on:
  - Past performance
  - Career goals
  - Discipline and semester
  - Psychometric evaluations
- Uses **Groq API (Gemma-2 9B)** to generate intelligent and concise feedback

### 📊 Skill & Grade Prediction
- Predicts performance in upcoming semesters
- Generates required skill level comparisons for goal alignment
- Visualizes current vs required skill growth using JSON charts

### 🧑‍🏫 Psychological Evaluation
- Custom psychometric questions generated using AI
- Scores user responses on key traits like:
  - Analytical Thinking
  - Motivation
  - Emotional Resilience
  - Collaboration, etc.

### 📚 Course Explorer
- Search courses by discipline and semester
- AI-generated course summaries under 80 characters

### 🤖 Chat with AI Mentor
- Context-aware chatbot that understands user’s:
  - Academic records
  - Psychological profile
  - Goals and strengths
- Offers support, constructive feedback, and motivation

---

## 🏗️ Tech Stack

- **Python + Flask** – Backend & API server
- **Pandas** – Data handling and filtering
- **HTML/CSS + JS (Flask Templates)** – Frontend
- **Groq API (Gemma-2 9B)** – Generative AI engine
- **CSV-based DB** – Lightweight user, course & history storage

---

## 📂 Project Structure

```
├── app.py                  # Main Flask application
├── templates/
│   └── dashboard.html      # UI templates
├── static/                 # Assets (optional for CSS/JS/images)
├── courses.csv             # Master list of courses
├── users.csv               # Registered users
├── history.csv             # Academic records
├── recommendations.csv     # AI-generated course suggestions
├── skillcharts.csv         # Skill progress data
├── psych_eval.csv          # Psychometric scores
```

---

## ⚙️ Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/shayen71421/fyugp.git
   cd fyugp
   ```

2. Install dependencies:
   ```bash
   pip install flask pandas requests
   ```

3. Configure your Groq API Key in `app.py`:
   ```python
   groq_api_key = "your_actual_key_here"
   ```

4. Run the app:
   ```bash
   python app.py
   ```

5. Open your browser and navigate to:
   ```
   http://localhost:5000/
   ```

---

## 🧠 FYUGP + GenAI = Future of Education

EDUSYNC proves that **AI can empower students** to make **data-driven academic decisions**, improve mental well-being, and **thrive in a personalized learning ecosystem** — aligning perfectly with the vision of **FYUGP and NEP 2020**.

---

## 👥 Authors & Contributors

Developed by the students of **Sahrdaya College of Engineering and Technology** for **Techathlon 2024-25** by ICT Academy of Kerala under the guidance of faculty.

### 🔧 Core Team

- [**shayen71421**](https://github.com/shayen71421-backend) – Backend Developer, AI Integration, Data Handling  
- [**mishalshanavas**](https://github.com/mishalshanavas) – Database Management & Data Collection  
- [**mathewgeejo**](https://github.com/mathewgeejo) – Frontend Design & UI/UX

---

## 📝 License

MIT License. Feel free to fork, contribute, and enhance 🚀
