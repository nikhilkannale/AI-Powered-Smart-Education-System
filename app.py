import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import random
import json
import requests
import re
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import hashlib
import time
from typing import List, Dict, Any
import asyncio
import aiohttp

# Page configuration
st.set_page_config(
    page_title="AI-Powered Smart Education Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for professional UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 800;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #1e40af;
        margin-bottom: 1.5rem;
        font-weight: 600;
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 0.5rem;
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .metric-container:hover {
        transform: translateY(-5px);
    }
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #3b82f6;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.15);
    }
    .ai-response-card {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid #0ea5e9;
        margin: 1rem 0;
    }
    .warning-card {
        background: linear-gradient(135deg, #fefce8 0%, #fef3cd 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
    }
    .success-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #10b981;
        margin: 1rem 0;
    }
    .timetable-cell {
        padding: 0.75rem;
        text-align: center;
        border: 1px solid #e2e8f0;
        background: #f8fafc;
        border-radius: 8px;
        margin: 2px;
    }
    .question-card {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid #059669;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #3498db;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
</style>
""", unsafe_allow_html=True)

# Configuration class for API settings
class Config:
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")  # Set in Streamlit secrets
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    MAX_TOKENS = 4096
    TEMPERATURE = 0.7
    MODEL = "llama-3.1-8b-instant"  # Free Groq model

# Enhanced Database initialization with proper indexing and constraints
def init_database():
    conn = sqlite3.connect('education_system.db')
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Users table with enhanced security
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('student', 'teacher', 'admin')),
            email TEXT UNIQUE,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Subjects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            teacher_id INTEGER,
            credits INTEGER DEFAULT 3,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users (id) ON DELETE SET NULL
        )
    ''')
    
    # Enhanced timetable table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS timetable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subject_id INTEGER,
            day_of_week TEXT CHECK(day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
            start_time TEXT,
            end_time TEXT,
            room TEXT,
            semester TEXT DEFAULT 'Current',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
        )
    ''')
    
    # Enhanced question bank with AI metadata
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS question_bank (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            question_text TEXT NOT NULL,
            question_type TEXT NOT NULL CHECK(question_type IN ('mcq', 'short', 'long', 'true_false')),
            options TEXT,
            correct_answer TEXT,
            difficulty TEXT DEFAULT 'medium' CHECK(difficulty IN ('easy', 'medium', 'hard')),
            chapter TEXT,
            topic TEXT,
            bloom_level TEXT CHECK(bloom_level IN ('remember', 'understand', 'apply', 'analyze', 'evaluate', 'create')),
            estimated_time INTEGER DEFAULT 5,
            ai_generated BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
        )
    ''')
    
    # Enhanced student scores with detailed tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject_id INTEGER,
            score REAL,
            max_score REAL,
            percentage REAL GENERATED ALWAYS AS (ROUND((score * 100.0) / max_score, 2)) STORED,
            test_date DATE,
            test_type TEXT,
            test_title TEXT,
            time_taken INTEGER,
            questions_attempted INTEGER,
            questions_correct INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
        )
    ''')
    
    # AI interactions log
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            interaction_type TEXT,
            input_text TEXT,
            output_text TEXT,
            tokens_used INTEGER,
            response_time REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # Study plans table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject_id INTEGER,
            plan_title TEXT,
            plan_content TEXT,
            difficulty_level TEXT,
            estimated_hours INTEGER,
            status TEXT DEFAULT 'active',
            ai_generated BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scores_student ON student_scores(student_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_subject ON question_bank(subject_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_timetable_user ON timetable(user_id)")
    
    conn.commit()
    conn.close()

# AI Service Class for Groq API integration
class AIService:
    def __init__(self):
        self.api_key = Config.GROQ_API_KEY
        self.api_url = Config.GROQ_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, messages: List[Dict], max_tokens: int = Config.MAX_TOKENS) -> Dict:
        """Make API request to Groq"""
        if not self.api_key:
            return {"error": "Groq API key not configured"}
        
        payload = {
            "model": Config.MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": Config.TEMPERATURE
        }
        
        try:
            start_time = time.time()
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "content": data["choices"][0]["message"]["content"],
                    "tokens_used": data["usage"]["total_tokens"],
                    "response_time": response_time
                }
            else:
                return {"error": f"API Error: {response.status_code} - {response.text}"}
        
        except requests.exceptions.Timeout:
            return {"error": "Request timeout. Please try again."}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def generate_questions(self, subject: str, topic: str, difficulty: str, question_type: str, count: int = 5) -> Dict:
        """Generate questions using AI"""
        prompt = f"""Generate {count} {difficulty} level {question_type} questions for {subject} on the topic of {topic}.

        Requirements:
        - Questions should be clear and unambiguous
        - For MCQ: Provide 4 options with one correct answer
        - For short answer: Provide sample answer (50-100 words)
        - For long answer: Provide detailed answer outline
        - Include difficulty justification
        - Specify estimated time to solve

        Format the response as JSON:
        {{
            "questions": [
                {{
                    "question": "Question text",
                    "type": "{question_type}",
                    "difficulty": "{difficulty}",
                    "options": ["A", "B", "C", "D"] (only for MCQ),
                    "correct_answer": "Answer",
                    "explanation": "Why this is correct",
                    "estimated_time": 5,
                    "bloom_level": "understand"
                }}
            ]
        }}"""
        
        messages = [
            {"role": "system", "content": "You are an expert educator who creates high-quality educational content."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages)
    
    def analyze_student_performance(self, student_data: Dict) -> Dict:
        """Analyze student performance and provide insights"""
        prompt = f"""Analyze the following student performance data and provide detailed insights:

        Student Data:
        - Name: {student_data.get('name', 'Student')}
        - Subjects: {student_data.get('subjects', [])}
        - Recent Scores: {student_data.get('scores', [])}
        - Average Performance: {student_data.get('average', 0)}%
        - Weak Areas: {student_data.get('weak_areas', [])}
        - Strong Areas: {student_data.get('strong_areas', [])}
        - Test History: {student_data.get('test_history', [])}

        Please provide:
        1. Overall performance analysis
        2. Subject-wise breakdown
        3. Learning patterns identified
        4. Specific recommendations for improvement
        5. Study plan suggestions
        6. Motivational feedback

        Format as a structured analysis with clear sections."""
        
        messages = [
            {"role": "system", "content": "You are an educational analyst providing personalized learning insights."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=2048)
    
    def create_study_plan(self, student_profile: Dict) -> Dict:
        """Create personalized study plan"""
        prompt = f"""Create a comprehensive study plan for a student with the following profile:

        Student Profile:
        - Current Performance: {student_profile.get('performance', {})}
        - Weak Subjects: {student_profile.get('weak_subjects', [])}
        - Available Study Time: {student_profile.get('study_time', 'Not specified')} hours per day
        - Learning Style: {student_profile.get('learning_style', 'Visual/Auditory/Kinesthetic')}
        - Goals: {student_profile.get('goals', 'Improve overall performance')}
        - Upcoming Exams: {student_profile.get('exams', [])}

        Create a detailed 30-day study plan including:
        1. Daily study schedule
        2. Subject-wise time allocation
        3. Specific topics to focus on
        4. Practice recommendations
        5. Weekly milestones
        6. Progress tracking suggestions
        7. Break and revision schedules

        Format as a structured plan with clear daily/weekly breakdowns."""
        
        messages = [
            {"role": "system", "content": "You are an expert educational planner creating personalized study strategies."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages, max_tokens=3000)
    
    def solve_math_problem(self, problem: str) -> Dict:
        """Solve math problems with step-by-step explanation"""
        prompt = f"""Solve the following math problem step by step:

        Problem: {problem}

        Please provide:
        1. Step-by-step solution
        2. Explanation for each step
        3. Final answer
        4. Alternative methods if applicable
        5. Common mistakes to avoid
        6. Related concepts

        Make the explanation clear for educational purposes."""
        
        messages = [
            {"role": "system", "content": "You are a math tutor providing clear, educational solutions."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages)
    
    def explain_concept(self, subject: str, concept: str, level: str = "intermediate") -> Dict:
        """Explain educational concepts"""
        prompt = f"""Explain the concept of "{concept}" in {subject} for a {level} level student.

        Please provide:
        1. Clear definition
        2. Simple explanation with examples
        3. Real-world applications
        4. Common misconceptions
        5. Related concepts
        6. Practice questions or exercises

        Make it engaging and easy to understand."""
        
        messages = [
            {"role": "system", "content": "You are an expert teacher explaining concepts clearly."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_request(messages)

# Initialize AI service
ai_service = AIService()

# Enhanced session state management
def init_session_state():
    defaults = {
        'logged_in': False,
        'user_role': None,
        'user_id': None,
        'username': None,
        'full_name': None,
        'ai_interactions': [],
        'current_subject': None,
        'study_plan': None,
        'current_page': 'dashboard'
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Enhanced authentication with password hashing
def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed

def create_user(username: str, password: str, role: str, email: str, full_name: str) -> bool:
    """Create new user with hashed password"""
    try:
        conn = sqlite3.connect('education_system.db')
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, email, full_name)
            VALUES (?, ?, ?, ?, ?)
        """, (username, password_hash, role, email, full_name))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(username: str, password: str) -> Dict:
    """Enhanced authentication with proper security"""
    conn = sqlite3.connect('education_system.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, username, role, email, full_name, password_hash, is_active
        FROM users WHERE username = ? AND is_active = 1
    """, (username,))
    
    user = cursor.fetchone()
    conn.close()
    
    if user and verify_password(password, user[5]):
        # Update last login
        conn = sqlite3.connect('education_system.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user[0],))
        conn.commit()
        conn.close()
        
        return {
            'id': user[0],
            'username': user[1],
            'role': user[2],
            'email': user[3],
            'full_name': user[4]
        }
    
    return None

# Enhanced sample data insertion
def insert_sample_data():
    conn = sqlite3.connect('education_system.db')
    cursor = conn.cursor()
    
    # Check if data exists
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # Sample users with hashed passwords
    users = [
        ('admin', hash_password('admin123'), 'admin', 'admin@school.edu', 'System Administrator'),
        ('john_teacher', hash_password('teacher123'), 'teacher', 'john@school.edu', 'Dr. John Smith'),
        ('jane_teacher', hash_password('teacher123'), 'teacher', 'jane@school.edu', 'Prof. Jane Doe'),
        ('alice_student', hash_password('student123'), 'student', 'alice@school.edu', 'Alice Johnson'),
        ('bob_student', hash_password('student123'), 'student', 'bob@school.edu', 'Bob Wilson'),
        ('charlie_student', hash_password('student123'), 'student', 'charlie@school.edu', 'Charlie Brown')
    ]
    
    cursor.executemany("""
        INSERT INTO users (username, password_hash, role, email, full_name) 
        VALUES (?, ?, ?, ?, ?)
    """, users)
    
    # Enhanced subjects with descriptions
    subjects = [
        ('THEORY OF COMPUTATIONS(TOC)', 'BCD503', 2, 4, 'Calculus, Linear Algebra, and Differential Equations'),
        ('SEPM', 'BCD501', 2, 3, 'Mechanics, Thermodynamics, and Electromagnetism'),
        ('CN', 'BCD502', 3, 3, 'Organic compounds, reactions, and mechanisms'),
        ('CV', 'BCD515A', 3, 3, 'DNA, RNA, protein synthesis, and genetics'),
        ('EVS', 'BESK508', 2, 4, 'Arrays, linked lists, trees, and algorithms'),
        ('RM', 'BRMK557', 2, 4, 'Supervised and unsupervised learning algorithms')
    ]
    
    cursor.executemany("""
        INSERT INTO subjects (name, code, teacher_id, credits, description) 
        VALUES (?, ?, ?, ?, ?)
    """, subjects)
    
    # Enhanced questions with metadata
    questions = [
        (1, 'Find the derivative of f(x) = x³ + 2x² - 5x + 3', 'short', None, 
         'f\'(x) = 3x² + 4x - 5', 'medium', 'Calculus', 'Derivatives', 'apply', 10, 0),
        (1, 'What is the integral of ∫(2x + 1)dx?', 'mcq', 
         '["x² + x + C", "2x² + x + C", "x² + 2x + C", "2x² + 2x + C"]', 
         'x² + x + C', 'easy', 'Calculus', 'Integration', 'remember', 5, 0),
        (2, 'A ball is thrown upward with initial velocity 20 m/s. Find the maximum height reached.', 
         'long', None, 'h = v²/(2g) = 400/(2×9.8) = 20.4 m', 'hard', 'Mechanics', 
         'Projectile Motion', 'analyze', 15, 0),
        (3, 'Which functional group is present in alcohols?', 'mcq',
         '["-OH", "-COOH", "-NH₂", "-CHO"]', '-OH', 'easy', 'Functional Groups',
         'Alcohols', 'remember', 3, 0),
        (5, 'Implement a binary search algorithm in pseudocode', 'long', None,
         'Binary search divides array in half repeatedly', 'hard', 'Searching',
         'Binary Search', 'create', 25, 0)
    ]
    
    cursor.executemany("""
        INSERT INTO question_bank 
        (subject_id, question_text, question_type, options, correct_answer, 
         difficulty, chapter, topic, bloom_level, estimated_time, ai_generated) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, questions)
    
    # Generate comprehensive score data
    scores = []
    students = [4, 5, 6]  # Alice, Bob, Charlie
    subjects = list(range(1, 7))
    
    for student_id in students:
        for subject_id in subjects:
            # Generate 8-12 test scores per subject with realistic progression
            num_tests = random.randint(8, 12)
            base_performance = random.randint(65, 85)  # Student's base level
            
            for i in range(num_tests):
                # Simulate learning progression with some randomness
                progress_factor = i * 0.02  # Slight improvement over time
                variation = random.uniform(-0.1, 0.1)  # Random variation
                
                score = base_performance + (progress_factor * 100) + (variation * 20)
                score = max(0, min(100, score))  # Clamp between 0-100
                
                test_date = datetime.now() - timedelta(days=random.randint(1, 90))
                test_types = ['Quiz', 'Assignment', 'Midterm', 'Final', 'Lab Test']
                test_type = random.choice(test_types)
                
                questions_total = random.randint(10, 30)
                questions_correct = int((score / 100) * questions_total)
                time_taken = random.randint(30, 120)  # minutes
                
                scores.append((
                    student_id, subject_id, score, 100, test_date.date(),
                    test_type, f"{test_type} - Week {i+1}", time_taken,
                    questions_total, questions_correct
                ))
    
    cursor.executemany("""
        INSERT INTO student_scores 
        (student_id, subject_id, score, max_score, test_date, test_type, 
         test_title, time_taken, questions_attempted, questions_correct)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, scores)
    
    # Create sample timetable entries
    timetable_entries = []
    for student_id in students:
        for subject_id in subjects:
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            day = random.choice(days)
            start_hour = random.randint(8, 15)
            start_time = f"{start_hour:02d}:00"
            end_time = f"{start_hour + 1:02d}:00"
            room = f"Room {random.randint(100, 300)}"
            
            timetable_entries.append((
                student_id, subject_id, day, start_time, end_time, room
            ))
    
    cursor.executemany("""
        INSERT INTO timetable (user_id, subject_id, day_of_week, start_time, end_time, room)
        VALUES (?, ?, ?, ?, ?, ?)
    """, timetable_entries)
    
    conn.commit()
    conn.close()

# Enhanced login page with registration
def login_page():
    st.markdown('<h1 class="main-header">🤖 AI-Powered Smart Education Management System</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown("### 🔐 Login to Continue")
            
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            if st.button("Login", type="primary", use_container_width=True):
                if username and password:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user['id']
                        st.session_state.username = user['username']
                        st.session_state.user_role = user['role']
                        st.session_state.full_name = user['full_name']
                        st.success(f"Welcome back, {user['full_name']}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid credentials! Please check your username and password.")
                else:
                    st.warning("Please enter both username and password.")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Sample credentials
            with st.expander("Sample Credentials"):
                st.markdown("""
                **Teachers:**
                - Username: `john_teacher` Password: `teacher123`
                - Username: `jane_teacher` Password: `teacher123`
                
                **Students:**
                - Username: `alice_student` Password: `student123`
                - Username: `bob_student` Password: `student123`
                - Username: `charlie_student` Password: `student123`
                
                **Admin:**
                - Username: `admin` Password: `admin123`
                """)
    
    with tab2:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown("### 📝 Create New Account")
            
            new_username = st.text_input("Choose Username", key="reg_username")
            new_password = st.text_input("Choose Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
            new_email = st.text_input("Email Address", key="reg_email")
            new_name = st.text_input("Full Name", key="reg_name")
            new_role = st.selectbox("Role", ["student", "teacher"], key="reg_role")
            
            if st.button("Register", type="primary", use_container_width=True):
                if all([new_username, new_password, confirm_password, new_email, new_name]):
                    if new_password == confirm_password:
                        if len(new_password) >= 6:
                            if create_user(new_username, new_password, new_role, new_email, new_name):
                                st.success("Account created successfully! Please login.")
                            else:
                                st.error("Username or email already exists!")
                        else:
                            st.error("Password must be at least 6 characters long!")
                    else:
                        st.error("Passwords don't match!")
                else:
                    st.warning("Please fill in all fields.")
            
            st.markdown('</div>', unsafe_allow_html=True)

# Enhanced AI-powered question paper generator
def ai_question_paper_generator():
    st.markdown('<h2 class="sub-header">🤖 AI Question Paper Generator</h2>', unsafe_allow_html=True)
    
    if st.session_state.user_role not in ['teacher', 'admin']:
        st.warning("This feature is available only for teachers and administrators.")
        return
    
    tab1, tab2, tab3 = st.tabs(["Generate Paper", "Manage Questions", "AI Question Bank"])
    
    with tab1:
        st.markdown("### Create Custom Question Paper")
        
        conn = sqlite3.connect('education_system.db')
        subjects_df = pd.read_sql_query("""
            SELECT s.id, s.name, s.code, s.description 
            FROM subjects s 
            WHERE s.teacher_id = ? OR ? = (SELECT id FROM users WHERE role = 'admin' AND id = ?)
        """, conn, params=(st.session_state.user_id, st.session_state.user_id, st.session_state.user_id))
        
        if not subjects_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                subject_id = st.selectbox(
                    "Select Subject",
                    subjects_df['id'].tolist(),
                    format_func=lambda x: f"{subjects_df[subjects_df['id']==x]['name'].iloc[0]} ({subjects_df[subjects_df['id']==x]['code'].iloc[0]})"
                )
                
                paper_title = st.text_input("Paper Title", value="Test Paper")
                total_marks = st.number_input("Total Marks", min_value=50, max_value=200, value=100)
                duration = st.number_input("Duration (minutes)", min_value=30, max_value=300, value=120)
                
                mcq_count = st.number_input("MCQ Questions", min_value=0, max_value=30, value=10)
                mcq_marks = st.number_input("Marks per MCQ", min_value=1, max_value=5, value=2)
                
            with col2:
                short_count = st.number_input("Short Answer Questions", min_value=0, max_value=15, value=5)
                short_marks = st.number_input("Marks per Short Answer", min_value=2, max_value=10, value=5)
                
                long_count = st.number_input("Long Answer Questions", min_value=0, max_value=8, value=3)
                long_marks = st.number_input("Marks per Long Answer", min_value=5, max_value=25, value=15)
                
                difficulty = st.selectbox("Overall Difficulty", ["easy", "medium", "hard", "mixed"])
                include_ai = st.checkbox("Include AI-generated questions", value=True)
            
            # Calculate total marks
            calculated_marks = (mcq_count * mcq_marks) + (short_count * short_marks) + (long_count * long_marks)
            
            if calculated_marks != total_marks:
                st.warning(f"Calculated marks ({calculated_marks}) don't match total marks ({total_marks})")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🎲 Generate from Database", type="secondary"):
                    with st.spinner("Generating paper from question bank..."):
                        questions = generate_question_paper_from_db(
                            subject_id, mcq_count, short_count, long_count, difficulty, include_ai
                        )
                        if questions:
                            display_generated_paper(
                                questions, paper_title, subjects_df[subjects_df['id']==subject_id]['name'].iloc[0],
                                duration, mcq_marks, short_marks, long_marks
                            )
                        else:
                            st.error("Not enough questions in database. Try AI generation.")
            
            with col2:
                if st.button("🤖 AI Generate Questions", type="primary"):
                    if not ai_service.api_key:
                        st.error("⚠️ Groq API key not configured. Please set GROQ_API_KEY in secrets.")
                        return
                    
                    with st.spinner("AI is generating questions... This may take a moment."):
                        subject_name = subjects_df[subjects_df['id']==subject_id]['name'].iloc[0]
                        ai_questions = generate_ai_questions(subject_name, mcq_count, short_count, long_count, difficulty)
                        
                        if ai_questions and 'error' not in ai_questions:
                            display_ai_generated_paper(
                                ai_questions, paper_title, subject_name, duration,
                                mcq_marks, short_marks, long_marks, subject_id
                            )
                        else:
                            st.error(f"AI generation failed: {ai_questions.get('error', 'Unknown error')}")
        
        conn.close()
    
    with tab2:
        st.markdown("### Question Bank Management")
        
        conn = sqlite3.connect('education_system.db')
        subjects_df = pd.read_sql_query("""
            SELECT s.id, s.name 
            FROM subjects s 
            WHERE s.teacher_id = ? OR ? = (SELECT id FROM users WHERE role = 'admin' AND id = ?)
        """, conn, params=(st.session_state.user_id, st.session_state.user_id, st.session_state.user_id))
        
        if not subjects_df.empty:
            # Add new question form
            with st.expander("➕ Add New Question"):
                subject_id = st.selectbox(
                    "Subject",
                    subjects_df['id'].tolist(),
                    format_func=lambda x: subjects_df[subjects_df['id']==x]['name'].iloc[0],
                    key="add_question_subject"
                )
                
                question_text = st.text_area("Question Text", height=100)
                question_type = st.selectbox("Question Type", ["mcq", "short", "long", "true_false"])
                
                col1, col2 = st.columns(2)
                with col1:
                    difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"])
                    chapter = st.text_input("Chapter/Unit")
                
                with col2:
                    topic = st.text_input("Topic")
                    bloom_level = st.selectbox("Bloom's Level", 
                        ["remember", "understand", "apply", "analyze", "evaluate", "create"])
                    estimated_time = st.number_input("Estimated Time (minutes)", min_value=1, max_value=60, value=5)
                
                if question_type == "mcq":
                    st.write("**Multiple Choice Options:**")
                    option1 = st.text_input("Option A", key="opt_a")
                    option2 = st.text_input("Option B", key="opt_b")
                    option3 = st.text_input("Option C", key="opt_c")
                    option4 = st.text_input("Option D", key="opt_d")
                    correct_option = st.selectbox("Correct Answer", 
                        [option1, option2, option3, option4] if all([option1, option2, option3, option4]) else ["Select options first"])
                    
                    options_json = json.dumps([option1, option2, option3, option4]) if all([option1, option2, option3, option4]) else None
                
                elif question_type == "true_false":
                    correct_option = st.selectbox("Correct Answer", ["True", "False"])
                    options_json = json.dumps(["True", "False"])
                
                else:
                    options_json = None
                    correct_option = st.text_area("Sample Answer/Key Points", height=80)
                
                if st.button("Add Question to Bank", type="primary"):
                    if question_text and correct_option:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO question_bank 
                            (subject_id, question_text, question_type, options, correct_answer, 
                             difficulty, chapter, topic, bloom_level, estimated_time, ai_generated)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                        """, (subject_id, question_text, question_type, options_json, correct_option,
                              difficulty, chapter, topic, bloom_level, estimated_time))
                        conn.commit()
                        st.success("✅ Question added to bank!")
                    else:
                        st.error("Please fill in question text and answer.")
            
            # View existing questions
            st.markdown("### Existing Questions")
            view_subject = st.selectbox(
                "View questions for subject:",
                subjects_df['id'].tolist(),
                format_func=lambda x: subjects_df[subjects_df['id']==x]['name'].iloc[0],
                key="view_questions_subject"
            )
            
            questions_df = pd.read_sql_query("""
                SELECT id, question_text, question_type, difficulty, chapter, topic, 
                       bloom_level, estimated_time, ai_generated, created_at
                FROM question_bank 
                WHERE subject_id = ?
                ORDER BY created_at DESC
            """, conn, params=(view_subject,))
            
            if not questions_df.empty:
                # Add filters
                col1, col2, col3 = st.columns(3)
                with col1:
                    filter_type = st.selectbox("Filter by type", 
                        ["All"] + list(questions_df['question_type'].unique()))
                with col2:
                    filter_difficulty = st.selectbox("Filter by difficulty",
                        ["All"] + list(questions_df['difficulty'].unique()))
                with col3:
                    filter_ai = st.selectbox("Filter by source", 
                        ["All", "Human-created", "AI-generated"])
                
                # Apply filters
                filtered_df = questions_df.copy()
                if filter_type != "All":
                    filtered_df = filtered_df[filtered_df['question_type'] == filter_type]
                if filter_difficulty != "All":
                    filtered_df = filtered_df[filtered_df['difficulty'] == filter_difficulty]
                if filter_ai == "Human-created":
                    filtered_df = filtered_df[filtered_df['ai_generated'] == 0]
                elif filter_ai == "AI-generated":
                    filtered_df = filtered_df[filtered_df['ai_generated'] == 1]
                
                st.dataframe(
                    filtered_df[['question_text', 'question_type', 'difficulty', 'chapter', 'topic', 'bloom_level']],
                    use_container_width=True
                )
                
                st.info(f"Total questions: {len(filtered_df)}")
            else:
                st.info("No questions found. Add some questions to get started.")
        
        conn.close()
    
    with tab3:
        st.markdown("### 🤖 AI Question Generation")
        
        if not ai_service.api_key:
            st.error("⚠️ Groq API key not configured. Please set GROQ_API_KEY in Streamlit secrets.")
            st.info("To use AI features, add your Groq API key to the secrets configuration.")
            return
        
        conn = sqlite3.connect('education_system.db')
        subjects_df = pd.read_sql_query("""
            SELECT s.id, s.name, s.description 
            FROM subjects s 
            WHERE s.teacher_id = ? OR ? = (SELECT id FROM users WHERE role = 'admin' AND id = ?)
        """, conn, params=(st.session_state.user_id, st.session_state.user_id, st.session_state.user_id))
        
        if not subjects_df.empty:
            subject_id = st.selectbox(
                "Select Subject for AI Generation",
                subjects_df['id'].tolist(),
                format_func=lambda x: subjects_df[subjects_df['id']==x]['name'].iloc[0],
                key="ai_gen_subject"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                topic = st.text_input("Specific Topic", placeholder="e.g., Linear Equations, Cell Division")
                question_type = st.selectbox("Question Type", ["mcq", 'short', 'long', 'mixed'])
                difficulty = st.selectbox("Difficulty Level", ["easy", "medium", "hard", "mixed"])
            
            with col2:
                count = st.number_input("Number of Questions", min_value=1, max_value=20, value=5)
                auto_save = st.checkbox("Save to Question Bank", value=True)
            
            if st.button("🚀 Generate AI Questions", type="primary"):
                if topic:
                    with st.spinner("AI is generating questions... Please wait."):
                        subject_name = subjects_df[subjects_df['id']==subject_id]['name'].iloc[0]
                        
                        start_time = time.time()
                        result = ai_service.generate_questions(subject_name, topic, difficulty, question_type, count)
                        response_time = time.time() - start_time
                        
                        if 'error' not in result:
                            try:
                                # Parse AI response
                                content = result['content']
                                
                                # Extract JSON from response
                                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                                if json_match:
                                    questions_data = json.loads(json_match.group())
                                    questions = questions_data.get('questions', [])
                                    
                                    if questions:
                                        st.success(f"✅ Generated {len(questions)} questions in {response_time:.2f} seconds")
                                        
                                        # Log AI interaction
                                        log_ai_interaction(
                                            st.session_state.user_id,
                                            "question_generation",
                                            f"Generate {count} {question_type} questions on {topic}",
                                            content,
                                            result.get('tokens_used', 0),
                                            response_time
                                        )
                                        
                                        # Display generated questions
                                        for i, q in enumerate(questions, 1):
                                            with st.expander(f"Question {i}: {q.get('type', 'Unknown').upper()}"):
                                                st.markdown(f"**Question:** {q.get('question', 'N/A')}")
                                                
                                                if q.get('options'):
                                                    st.markdown("**Options:**")
                                                    for j, opt in enumerate(q['options'], 1):
                                                        st.write(f"{chr(64+j)}. {opt}")
                                                
                                                st.markdown(f"**Answer:** {q.get('correct_answer', 'N/A')}")
                                                st.markdown(f"**Explanation:** {q.get('explanation', 'N/A')}")
                                                
                                                col1, col2, col3 = st.columns(3)
                                                with col1:
                                                    st.write(f"**Difficulty:** {q.get('difficulty', 'N/A')}")
                                                with col2:
                                                    st.write(f"**Time:** {q.get('estimated_time', 'N/A')} min")
                                                with col3:
                                                    st.write(f"**Bloom's:** {q.get('bloom_level', 'N/A')}")
                                        
                                        # Save to database if requested
                                        if auto_save:
                                            cursor = conn.cursor()
                                            saved_count = 0
                                            
                                            for q in questions:
                                                try:
                                                    options_json = json.dumps(q.get('options', [])) if q.get('options') else None
                                                    
                                                    cursor.execute("""
                                                        INSERT INTO question_bank 
                                                        (subject_id, question_text, question_type, options, correct_answer,
                                                         difficulty, chapter, topic, bloom_level, estimated_time, ai_generated)
                                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                                                    """, (
                                                        subject_id,
                                                        q.get('question', ''),
                                                        q.get('type', question_type),
                                                        options_json,
                                                        q.get('correct_answer', ''),
                                                        q.get('difficulty', difficulty),
                                                        'AI Generated',
                                                        topic,
                                                        q.get('bloom_level', 'understand'),
                                                        q.get('estimated_time', 5)
                                                    ))
                                                    saved_count += 1
                                                except Exception as e:
                                                    st.warning(f"Could not save question {saved_count + 1}: {str(e)}")
                                            
                                            conn.commit()
                                            if saved_count > 0:
                                                st.success(f"💾 Saved {saved_count} questions to the question bank!")
                                    else:
                                        st.error("No questions were generated. Please try again.")
                                else:
                                    st.error("Could not parse AI response. Please try again.")
                                    
                            except json.JSONDecodeError:
                                st.error("AI response was not in valid JSON format.")
                                st.text("Raw AI Response:")
                                st.text(result.get('content', 'No content'))
                        else:
                            st.error(f"AI Generation Error: {result['error']}")
                else:
                    st.warning("Please specify a topic for question generation.")
        
        conn.close()

def generate_question_paper_from_db(subject_id: int, mcq_count: int, short_count: int, long_count: int, difficulty: str, include_ai: bool):
    """Generate question paper from existing database questions"""
    conn = sqlite3.connect('education_system.db')
    
    questions = []
    
    # Build query based on parameters
    base_query = "SELECT * FROM question_bank WHERE subject_id = ?"
    params = [subject_id]
    
    if difficulty != "mixed":
        base_query += " AND difficulty = ?"
        params.append(difficulty)
    
    if not include_ai:
        base_query += " AND ai_generated = 0"
    
    # Get MCQ questions
    if mcq_count > 0:
        mcq_query = base_query + " AND question_type = 'mcq' ORDER BY RANDOM() LIMIT ?"
        mcq_df = pd.read_sql_query(mcq_query, conn, params=params + [mcq_count])
        questions.extend(mcq_df.values.tolist())
    
    # Get short answer questions
    if short_count > 0:
        short_query = base_query + " AND question_type = 'short' ORDER BY RANDOM() LIMIT ?"
        short_df = pd.read_sql_query(short_query, conn, params=params + [short_count])
        questions.extend(short_df.values.tolist())
    
    # Get long answer questions
    if long_count > 0:
        long_query = base_query + " AND question_type = 'long' ORDER BY RANDOM() LIMIT ?"
        long_df = pd.read_sql_query(long_query, conn, params=params + [long_count])
        questions.extend(long_df.values.tolist())
    
    conn.close()
    
    return questions if len(questions) >= (mcq_count + short_count + long_count) else None

def display_generated_paper(questions, title, subject, duration, mcq_marks, short_marks, long_marks):
    """Display generated question paper"""
    st.markdown("---")
    st.markdown(f"# 📄 {title}")
    st.markdown(f"**Subject:** {subject}")
    st.markdown(f"**Duration:** {duration} minutes")
    st.markdown(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")
    st.markdown("---")
    
    question_num = 1
    
    # Group questions by type
    mcq_questions = [q for q in questions if q[3] == 'mcq']  # question_type is at index 3
    short_questions = [q for q in questions if q[3] == 'short']
    long_questions = [q for q in questions if q[3] == 'long']
    
    # MCQ Section
    if mcq_questions:
        st.markdown(f"### Section A: Multiple Choice Questions ({len(mcq_questions)} × {mcq_marks} = {len(mcq_questions) * mcq_marks} marks)")
        st.markdown("*Choose the correct answer for each question.*")
        
        for q in mcq_questions:
            st.markdown(f'<div class="question-card">', unsafe_allow_html=True)
            st.markdown(f"**Q{question_num}.** {q[2]} **[{mcq_marks} mark{'s' if mcq_marks > 1 else ''}]**")  # question_text is at index 2
            if q[4]:  # options at index 4
                try:
                    options = json.loads(q[4])
                    for i, option in enumerate(options, 1):
                        st.write(f"   {chr(96+i)}) {option}")
                except:
                    st.write("   Options not available")
            st.markdown('</div>', unsafe_allow_html=True)
            question_num += 1
    
    # Short Answer Section
    if short_questions:
        st.markdown(f"### Section B: Short Answer Questions ({len(short_questions)} × {short_marks} = {len(short_questions) * short_marks} marks)")
        st.markdown("*Answer in 50-100 words.*")
        
        for q in short_questions:
            st.markdown(f'<div class="question-card">', unsafe_allow_html=True)
            st.markdown(f"**Q{question_num}.** {q[2]} **[{short_marks} mark{'s' if short_marks > 1 else ''}]**")
            st.markdown('</div>', unsafe_allow_html=True)
            question_num += 1
    
    # Long Answer Section
    if long_questions:
        st.markdown(f"### Section C: Long Answer Questions ({len(long_questions)} × {long_marks} = {len(long_questions) * long_marks} marks)")
        st.markdown("*Answer in detail with explanations and examples.*")
        
        for q in long_questions:
            st.markdown(f'<div class="question-card">', unsafe_allow_html=True)
            st.markdown(f"**Q{question_num}.** {q[2]} **[{long_marks} mark{'s' if long_marks > 1 else ''}]**")
            st.markdown('</div>', unsafe_allow_html=True)
            question_num += 1
    
    # Summary
    total_questions = len(mcq_questions) + len(short_questions) + len(long_questions)
    total_marks = (len(mcq_questions) * mcq_marks) + (len(short_questions) * short_marks) + (len(long_questions) * long_marks)
    
    st.markdown("---")
    st.markdown(f"**Total Questions:** {total_questions} | **Total Marks:** {total_marks}")

def generate_ai_questions(subject: str, mcq_count: int, short_count: int, long_count: int, difficulty: str):
    """Generate questions using AI for different types"""
    all_questions = []
    
    # Generate different types of questions
    types_to_generate = []
    if mcq_count > 0:
        types_to_generate.append(('mcq', mcq_count))
    if short_count > 0:
        types_to_generate.append(('short', short_count))  
    if long_count > 0:
        types_to_generate.append(('long', long_count))
    
    for question_type, count in types_to_generate:
        result = ai_service.generate_questions(subject, "general concepts", difficulty, question_type, count)
        
        if 'error' not in result:
            try:
                content = result['content']
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    questions_data = json.loads(json_match.group())
                    questions = questions_data.get('questions', [])
                    all_questions.extend(questions)
            except:
                continue
    
    return {'questions': all_questions} if all_questions else {'error': 'No questions generated'}

def display_ai_generated_paper(ai_result, title, subject, duration, mcq_marks, short_marks, long_marks, subject_id):
    """Display AI-generated question paper"""
    if 'questions' in ai_result:
        questions = ai_result['questions']
        
        st.markdown("---")
        st.markdown(f"# 🤖 {title}")
        st.markdown(f"**Subject:** {subject}")
        st.markdown(f"**Duration:** {duration} minutes")
        st.markdown(f"**Generated by AI:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.markdown("---")
        
        question_num = 1
        
        # Group by type
        mcq_questions = [q for q in questions if q.get('type') == 'mcq']
        short_questions = [q for q in questions if q.get('type') == 'short']
        long_questions = [q for q in questions if q.get('type') == 'long']
        
        # Display sections
        for section_name, qs, marks in [
            ("Multiple Choice Questions", mcq_questions, mcq_marks),
            ("Short Answer Questions", short_questions, short_marks), 
            ("Long Answer Questions", long_questions, long_marks)
        ]:
            if qs:
                st.markdown(f"### Section: {section_name} ({len(qs)} × {marks} = {len(qs) * marks} marks)")
                
                for q in qs:
                    st.markdown(f'<div class="question-card">', unsafe_allow_html=True)
                    st.markdown(f"**Q{question_num}.** {q.get('question', '')} **[{marks} marks]**")
                    
                    if q.get('options') and section_name.startswith("Multiple"):
                        for i, option in enumerate(q['options'], 1):
                            st.write(f"   {chr(96+i)}) {option}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    question_num += 1
        
        # Save option
        if st.button("💾 Save AI Questions to Database"):
            save_ai_questions_to_db(questions, subject_id)
            st.success("Questions saved to database!")

def save_ai_questions_to_db(questions, subject_id):
    """Save AI-generated questions to database"""
    conn = sqlite3.connect('education_system.db')
    cursor = conn.cursor()
    
    for q in questions:
        try:
            options_json = json.dumps(q.get('options', [])) if q.get('options') else None
            
            cursor.execute("""
                INSERT INTO question_bank 
                (subject_id, question_text, question_type, options, correct_answer,
                 difficulty, chapter, topic, bloom_level, estimated_time, ai_generated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                subject_id,
                q.get('question', ''),
                q.get('type', 'short'),
                options_json,
                q.get('correct_answer', ''),
                q.get('difficulty', 'medium'),
                'AI Generated',
                'General',
                q.get('bloom_level', 'understand'),
                q.get('estimated_time', 5)
            ))
        except Exception as e:
            st.error(f"Error saving question: {str(e)}")
    
    conn.commit()
    conn.close()

def log_ai_interaction(user_id, interaction_type, input_text, output_text, tokens_used, response_time):
    """Log AI interactions for analytics"""
    conn = sqlite3.connect('education_system.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO ai_interactions 
        (user_id, interaction_type, input_text, output_text, tokens_used, response_time)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, interaction_type, input_text, output_text, tokens_used, response_time))
    
    conn.commit()
    conn.close()

# Enhanced AI-powered learning analytics
def ai_learning_analytics():
    st.markdown('<h2 class="sub-header">🧠 AI-Powered Learning Analytics</h2>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('education_system.db')
    
    if st.session_state.user_role == 'student':
        # Student Analytics
        st.markdown("### 📊 Your Performance Dashboard")
        
        # Get comprehensive student data
        scores_df = pd.read_sql_query("""
            SELECT ss.*, s.name as subject_name, s.code as subject_code
            FROM student_scores ss
            JOIN subjects s ON ss.subject_id = s.id
            WHERE ss.student_id = ?
            ORDER BY ss.test_date DESC
        """, conn, params=(st.session_state.user_id,))
        
        if not scores_df.empty:
            # Enhanced metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                avg_score = scores_df['score'].mean()
                st.markdown(f'<div class="metric-container"><h3>{avg_score:.1f}%</h3><p>Average Score</p></div>', unsafe_allow_html=True)
            
            with col2:
                total_tests = len(scores_df)
                st.markdown(f'<div class="metric-container"><h3>{total_tests}</h3><p>Total Tests</p></div>', unsafe_allow_html=True)
            
            with col3:
                best_score = scores_df['score'].max()
                st.markdown(f'<div class="metric-container"><h3>{best_score:.1f}%</h3><p>Best Score</p></div>', unsafe_allow_html=True)
            
            with col4:
                improvement = calculate_improvement(scores_df)
                color = "green" if improvement >= 0 else "red"
                st.markdown(f'<div class="metric-container"><h3 style="color:{color};">{improvement:+.1f}%</h3><p>Trend</p></div>', unsafe_allow_html=True)
            
            with col5:
                subjects_count = scores_df['subject_id'].nunique()
                st.markdown(f'<div class="metric-container"><h3>{subjects_count}</h3><p>Subjects</p></div>', unsafe_allow_html=True)
            
            # Advanced Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📈 Performance Timeline")
                scores_df['test_date'] = pd.to_datetime(scores_df['test_date'])
                scores_df = scores_df.sort_values('test_date')
                
                # Create a rolling average for better trend visualization
                scores_df['rolling_avg'] = scores_df['score'].rolling(window=5, min_periods=1).mean()
                
                fig = px.line(scores_df, x='test_date', y=['score', 'rolling_avg'], 
                             title='Score Trend Over Time',
                             labels={'value': 'Score (%)', 'test_date': 'Date'},
                             color_discrete_map={'score': 'lightblue', 'rolling_avg': 'darkblue'})
                fig.update_layout(showlegend=True, legend_title_text='Metric')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 📊 Subject-wise Performance")
                subject_avg = scores_df.groupby('subject_name')['score'].agg(['mean', 'count']).reset_index()
                subject_avg = subject_avg.sort_values('mean', ascending=False)
                
                fig = px.bar(subject_avg, x='subject_name', y='mean',
                            title='Average Score by Subject',
                            labels={'mean': 'Average Score (%)', 'subject_name': 'Subject'},
                            color='mean', color_continuous_scale='Viridis')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            # AI Performance Analysis
            st.markdown("### 🤖 AI Performance Analysis")
            
            # Prepare data for AI analysis
            student_data = {
                'name': st.session_state.full_name,
                'subjects': scores_df['subject_name'].unique().tolist(),
                'scores': scores_df[['subject_name', 'score', 'test_date']].to_dict('records'),
                'average': avg_score,
                'weak_areas': identify_weak_areas(scores_df),
                'strong_areas': identify_strong_areas(scores_df),
                'test_history': total_tests
            }
            
            if st.button("🔍 Get AI Performance Insights", type="primary"):
                if not ai_service.api_key:
                    st.error("⚠️ Groq API key not configured. Please set GROQ_API_KEY in secrets.")
                    return
                
                with st.spinner("AI is analyzing your performance... This may take a moment."):
                    result = ai_service.analyze_student_performance(student_data)
                    
                    if 'error' not in result:
                        st.markdown('<div class="ai-response-card">', unsafe_allow_html=True)
                        st.markdown("### 📋 AI Performance Report")
                        st.markdown(result['content'])
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Log interaction
                        log_ai_interaction(
                            st.session_state.user_id,
                            "performance_analysis",
                            f"Analyze performance for {st.session_state.full_name}",
                            result['content'],
                            result.get('tokens_used', 0),
                            result.get('response_time', 0)
                        )
                    else:
                        st.error(f"AI Analysis Error: {result['error']}")
            
            # Study Plan Recommendation
            st.markdown("### 📚 Personalized Study Plan")
            
            if st.button("🎯 Generate AI Study Plan", type="secondary"):
                if not ai_service.api_key:
                    st.error("⚠️ Groq API key not configured.")
                    return
                
                # Create student profile for study planning
                study_time = st.slider("Available study hours per day", 1, 8, 3, key="study_hours")
                learning_style = st.selectbox("Preferred learning style", 
                                            ["Visual", "Auditory", "Kinesthetic", "Mixed"], 
                                            key="learning_style")
                
                student_profile = {
                    'performance': {row['subject_name']: row['mean'] for _, row in subject_avg.iterrows()},
                    'weak_subjects': identify_weak_areas(scores_df),
                    'study_time': study_time,
                    'learning_style': learning_style,
                    'goals': "Improve overall academic performance",
                    'exams': ["Final Exams - Next 30 days"]
                }
                
                with st.spinner("AI is creating your personalized study plan..."):
                    result = ai_service.create_study_plan(student_profile)
                    
                    if 'error' not in result:
                        st.markdown('<div class="ai-response-card">', unsafe_allow_html=True)
                        st.markdown("### 📅 AI-Generated Study Plan")
                        st.markdown(result['content'])
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Save study plan to database
                        save_study_plan(student_profile, result['content'])
                        
                        # Log interaction
                        log_ai_interaction(
                            st.session_state.user_id,
                            "study_plan",
                            f"Create study plan for {st.session_state.full_name}",
                            result['content'],
                            result.get('tokens_used', 0),
                            result.get('response_time', 0)
                        )
                    else:
                        st.error(f"Study Plan Error: {result['error']}")
        
        else:
            st.info("No test scores available yet. Complete some assessments to see your analytics.")
    
    elif st.session_state.user_role in ['teacher', 'admin']:
        # Teacher/Admin Analytics
        st.markdown("### 👥 Class Performance Analytics")
        
        # Get all students' data - FIXED QUERY WITH subject_id
        students_df = pd.read_sql_query("""
            SELECT u.id, u.full_name, u.username, s.name as subject_name, 
                   ss.score, ss.test_date, ss.test_type, ss.subject_id
            FROM users u
            JOIN student_scores ss ON u.id = ss.student_id
            JOIN subjects s ON ss.subject_id = s.id
            WHERE u.role = 'student'
            ORDER BY u.full_name, ss.test_date DESC
        """, conn)
        
        if not students_df.empty:
            # Teacher can only see their own students if not admin
            if st.session_state.user_role == 'teacher':
                teacher_subjects_df = pd.read_sql_query("""
                    SELECT id FROM subjects WHERE teacher_id = ?
                """, conn, params=(st.session_state.user_id,))
                
                if not teacher_subjects_df.empty:
                    teacher_subject_ids = teacher_subjects_df['id'].tolist()
                    students_df = students_df[students_df['subject_id'].isin(teacher_subject_ids)]
            
            # Class overview metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_class_score = students_df['score'].mean()
                st.markdown(f'<div class="metric-container"><h3>{avg_class_score:.1f}%</h3><p>Class Average</p></div>', unsafe_allow_html=True)
            
            with col2:
                total_students = students_df['id'].nunique()
                st.markdown(f'<div class="metric-container"><h3>{total_students}</h3><p>Students</p></div>', unsafe_allow_html=True)
            
            with col3:
                pass_rate = (students_df[students_df['score'] >= 60]['id'].nunique() / total_students * 100) if total_students > 0 else 0
                st.markdown(f'<div class="metric-container"><h3>{pass_rate:.1f}%</h3><p>Pass Rate</p></div>', unsafe_allow_html=True)
            
            with col4:
                tests_per_student = len(students_df) / total_students if total_students > 0 else 0
                st.markdown(f'<div class="metric-container"><h3>{tests_per_student:.1f}</h3><p>Avg Tests/Student</p></div>', unsafe_allow_html=True)
            
            # Advanced class analytics
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 Performance Distribution")
                fig = px.histogram(students_df, x='score', nbins=20, 
                                  title='Score Distribution Across Class',
                                  labels={'score': 'Score (%)', 'count': 'Number of Students'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 📈 Subject Comparison")
                subject_avg = students_df.groupby('subject_name')['score'].mean().reset_index()
                subject_avg = subject_avg.sort_values('score', ascending=False)
                
                fig = px.bar(subject_avg, x='subject_name', y='score',
                            title='Average Score by Subject',
                            labels={'score': 'Average Score (%)', 'subject_name': 'Subject'},
                            color='score', color_continuous_scale='Plasma')
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            # Student ranking
            st.markdown("### 🏆 Student Rankings")
            student_avg = students_df.groupby(['id', 'full_name'])['score'].mean().reset_index()
            student_avg = student_avg.sort_values('score', ascending=False)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.dataframe(
                    student_avg[['full_name', 'score']].rename(
                        columns={'full_name': 'Student Name', 'score': 'Average Score (%)'}
                    ).head(10),
                    use_container_width=True
                )
            
            # Identify struggling students
            st.markdown("### ⚠️ Students Needing Attention")
            struggling_threshold = st.slider("Struggling threshold (%)", 40, 70, 60)
            
            struggling_students = student_avg[student_avg['score'] < struggling_threshold]
            if not struggling_students.empty:
                for _, student in struggling_students.iterrows():
                    st.markdown(f'<div class="warning-card">', unsafe_allow_html=True)
                    st.markdown(f"**{student['full_name']}** - Average: {student['score']:.1f}%")
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.success("No students are currently below the struggling threshold!")
        
        else:
            st.info("No student data available yet.")
    
    conn.close()

def calculate_improvement(scores_df):
    """Calculate performance improvement over time"""
    if len(scores_df) < 2:
        return 0
    
    scores_df = scores_df.sort_values('test_date')
    recent_scores = scores_df.tail(5)['score'].mean()
    older_scores = scores_df.head(5)['score'].mean()
    
    return recent_scores - older_scores

def identify_weak_areas(scores_df):
    """Identify weak areas based on performance"""
    if scores_df.empty:
        return []
    
    subject_avg = scores_df.groupby('subject_name')['score'].mean().reset_index()
    weak_threshold = subject_avg['score'].mean() - 10  # 10% below average
    
    weak_areas = subject_avg[subject_avg['score'] < weak_threshold]['subject_name'].tolist()
    return weak_areas

def identify_strong_areas(scores_df):
    """Identify strong areas based on performance"""
    if scores_df.empty:
        return []
    
    subject_avg = scores_df.groupby('subject_name')['score'].mean().reset_index()
    strong_threshold = subject_avg['score'].mean() + 10  # 10% above average
    
    strong_areas = subject_avg[subject_avg['score'] > strong_threshold]['subject_name'].tolist()
    return strong_areas

def save_study_plan(student_profile, plan_content):
    """Save study plan to database"""
    conn = sqlite3.connect('education_system.db')
    cursor = conn.cursor()
    
    # For each weak subject, create a study plan entry
    for subject in student_profile.get('weak_subjects', []):
        # Get subject ID
        cursor.execute("SELECT id FROM subjects WHERE name = ?", (subject,))
        subject_result = cursor.fetchone()
        
        if subject_result:
            subject_id = subject_result[0]
            
            cursor.execute("""
                INSERT INTO study_plans 
                (student_id, subject_id, plan_title, plan_content, difficulty_level, 
                 estimated_hours, status, ai_generated)
                VALUES (?, ?, ?, ?, ?, ?, 'active', 1)
            """, (
                st.session_state.user_id,
                subject_id,
                f"AI Study Plan for {subject}",
                plan_content,
                "medium",
                student_profile.get('study_time', 3) * 30  # Estimate monthly hours
            ))
    
    conn.commit()
    conn.close()

# Enhanced AI tutor functionality
def ai_tutor_assistant():
    st.markdown('<h2 class="sub-header">🧑‍🏫 AI Tutor Assistant</h2>', unsafe_allow_html=True)
    
    if not ai_service.api_key:
        st.error("⚠️ Groq API key not configured. Please set GROQ_API_KEY in secrets.")
        st.info("To use AI tutor features, add your Groq API key to the secrets configuration.")
        return
    
    tab1, tab2, tab3 = st.tabs(["Ask Questions", "Math Solver", "Concept Explainer"])
    
    with tab1:
        st.markdown("### 💬 Ask Academic Questions")
        
        subject = st.selectbox("Select Subject", [
            "Mathematics", "Physics", "Chemistry", "Biology", 
            "Computer Science", "History", "English", "Other"
        ], key="tutor_subject")
        
        question = st.text_area("Your Question", height=100, 
                               placeholder="Ask any academic question here...")
        
        if st.button("🤖 Get AI Answer", type="primary") and question:
            with st.spinner("AI tutor is thinking..."):
                messages = [
                    {"role": "system", "content": f"You are an expert {subject} tutor. Provide clear, educational answers."},
                    {"role": "user", "content": question}
                ]
                
                result = ai_service._make_request(messages)
                
                if 'error' not in result:
                    st.markdown('<div class="ai-response-card">', unsafe_allow_html=True)
                    st.markdown("### 🎓 AI Tutor Response")
                    st.markdown(result['content'])
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Log interaction
                    log_ai_interaction(
                        st.session_state.user_id,
                        "tutor_question",
                        question,
                        result['content'],
                        result.get('tokens_used', 0),
                        result.get('response_time', 0)
                    )
                else:
                    st.error(f"Tutor Error: {result['error']}")
    
    with tab2:
        st.markdown("### ➗ Math Problem Solver")
        
        math_problem = st.text_area("Enter Math Problem", height=80,
                                  placeholder="Enter any math problem (algebra, calculus, geometry, etc.)")
        
        if st.button("🧮 Solve Math Problem", type="primary") and math_problem:
            with st.spinner("Solving problem step by step..."):
                result = ai_service.solve_math_problem(math_problem)
                
                if 'error' not in result:
                    st.markdown('<div class="ai-response-card">', unsafe_allow_html=True)
                    st.markdown("### 📝 Math Solution")
                    st.markdown(result['content'])
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Log interaction
                    log_ai_interaction(
                        st.session_state.user_id,
                        "math_solver",
                        math_problem,
                        result['content'],
                        result.get('tokens_used', 0),
                        result.get('response_time', 0)
                    )
                else:
                    st.error(f"Math Solver Error: {result['error']}")
    
    with tab3:
        st.markdown("### 📖 Concept Explainer")
        
        col1, col2 = st.columns(2)
        
        with col1:
            explain_subject = st.selectbox("Subject", [
                "Mathematics", "Physics", "Chemistry", "Biology", 
                "Computer Science", "History", "English", "Other"
            ], key="explain_subject")
            
            concept_level = st.selectbox("Explanation Level", 
                                       ["beginner", "intermediate", "advanced"],
                                       key="concept_level")
        
        with col2:
            concept_name = st.text_input("Concept to Explain",
                                       placeholder="e.g., Photosynthesis, Quadratic Equations, Newton's Laws")
        
        if st.button("🔍 Explain Concept", type="primary") and concept_name:
            with st.spinner("Creating explanation..."):
                result = ai_service.explain_concept(explain_subject, concept_name, concept_level)
                
                if 'error' not in result:
                    st.markdown('<div class="ai-response-card">', unsafe_allow_html=True)
                    st.markdown(f"### 📚 Explanation: {concept_name}")
                    st.markdown(result['content'])
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Log interaction
                    log_ai_interaction(
                        st.session_state.user_id,
                        "concept_explanation",
                        f"Explain {concept_name} in {explain_subject} at {concept_level} level",
                        result['content'],
                        result.get('tokens_used', 0),
                        result.get('response_time', 0)
                    )
                else:
                    st.error(f"Concept Explanation Error: {result['error']}")

# Enhanced timetable management
def timetable_management():
    st.markdown('<h2 class="sub-header">📅 Timetable Management</h2>', unsafe_allow_html=True)
    
    conn = sqlite3.connect('education_system.db')
    
    if st.session_state.user_role == 'student':
        # Student view
        st.markdown("### 🗓️ Your Weekly Schedule")
        
        # Get student's timetable
        timetable_df = pd.read_sql_query("""
            SELECT t.*, s.name as subject_name, s.code as subject_code, u.full_name as teacher_name
            FROM timetable t
            JOIN subjects s ON t.subject_id = s.id
            JOIN users u ON s.teacher_id = u.id
            WHERE t.user_id = ?
            ORDER BY 
                CASE t.day_of_week 
                    WHEN 'Monday' THEN 1
                    WHEN 'Tuesday' THEN 2
                    WHEN 'Wednesday' THEN 3
                    WHEN 'Thursday' THEN 4
                    WHEN 'Friday' THEN 5
                    WHEN 'Saturday' THEN 6
                    WHEN 'Sunday' THEN 7
                END,
                t.start_time
        """, conn, params=(st.session_state.user_id,))
        
        if not timetable_df.empty:
            # Display timetable as a grid
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            time_slots = sorted(set(f"{row['start_time']}-{row['end_time']}" for _, row in timetable_df.iterrows()))
            
            # Create timetable grid
            timetable_grid = {day: {slot: [] for slot in time_slots} for day in days}
            
            for _, row in timetable_df.iterrows():
                time_slot = f"{row['start_time']}-{row['end_time']}"
                timetable_grid[row['day_of_week']][time_slot].append(
                    f"{row['subject_name']} ({row['room']}) - {row['teacher_name']}"
                )
            
            # Display timetable
            st.markdown("### Weekly Schedule")
            
            # Create header
            cols = st.columns(len(days) + 1)
            with cols[0]:
                st.write("**Time**")
            for i, day in enumerate(days, 1):
                with cols[i]:
                    st.write(f"**{day}**")
            
            # Create rows for each time slot
            for time_slot in time_slots:
                cols = st.columns(len(days) + 1)
                with cols[0]:
                    st.write(f"**{time_slot}**")
                
                for i, day in enumerate(days, 1):
                    with cols[i]:
                        classes = timetable_grid[day][time_slot]
                        if classes:
                            for class_info in classes:
                                st.markdown(f'<div class="timetable-cell">{class_info}</div>', unsafe_allow_html=True)
                        else:
                            st.write("—")
        
        else:
            st.info("No timetable entries found. Your schedule will appear here once configured.")
    
    elif st.session_state.user_role in ['teacher', 'admin']:
        # Teacher/Admin view
        st.markdown("### 👨‍🏫 Manage Class Schedules")
        
        tab1, tab2 = st.tabs(["View Schedules", "Add/Edit Schedule"])
        
        with tab1:
            # View all schedules
            if st.session_state.user_role == 'teacher':
                # Teacher can only see their subjects
                teacher_subjects_df = pd.read_sql_query("""
                    SELECT id, name FROM subjects WHERE teacher_id = ?
                """, conn, params=(st.session_state.user_id,))
                
                if not teacher_subjects_df.empty:
                    subject_ids = teacher_subjects_df['id'].tolist()
                    timetable_df = pd.read_sql_query(f"""
                        SELECT t.*, s.name as subject_name, u.full_name as student_name
                        FROM timetable t
                        JOIN subjects s ON t.subject_id = s.id
                        JOIN users u ON t.user_id = u.id
                        WHERE t.subject_id IN ({','.join('?' * len(subject_ids))})
                        ORDER BY u.full_name, t.day_of_week, t.start_time
                    """, conn, params=subject_ids)
                    
                    if not timetable_df.empty:
                        st.dataframe(
                            timetable_df[['student_name', 'subject_name', 'day_of_week', 'start_time', 'end_time', 'room']],
                            use_container_width=True
                        )
                    else:
                        st.info("No schedule entries found for your subjects.")
                else:
                    st.info("You are not assigned to any subjects yet.")
            
            else:  # Admin view
                timetable_df = pd.read_sql_query("""
                    SELECT t.*, s.name as subject_name, u.full_name as user_name, u.role
                    FROM timetable t
                    JOIN subjects s ON t.subject_id = s.id
                    JOIN users u ON t.user_id = u.id
                    ORDER BY u.role, u.full_name, t.day_of_week, t.start_time
                """, conn)
                
                if not timetable_df.empty:
                    st.dataframe(
                        timetable_df[['user_name', 'role', 'subject_name', 'day_of_week', 'start_time', 'end_time', 'room']],
                        use_container_width=True
                    )
                else:
                    st.info("No timetable entries found in the system.")
        
        with tab2:
            # Add/edit schedule
            st.markdown("### 📝 Add New Schedule Entry")
            
            # Get available users based on role
            if st.session_state.user_role == 'admin':
                users_df = pd.read_sql_query("SELECT id, full_name, role FROM users WHERE role IN ('student', 'teacher')", conn)
            else:
                # Teacher can only assign to students
                users_df = pd.read_sql_query("SELECT id, full_name FROM users WHERE role = 'student'", conn)
            
            # Get available subjects
            if st.session_state.user_role == 'admin':
                subjects_df = pd.read_sql_query("SELECT id, name FROM subjects", conn)
            else:
                subjects_df = pd.read_sql_query("SELECT id, name FROM subjects WHERE teacher_id = ?", conn, 
                                              params=(st.session_state.user_id,))
            
            if not users_df.empty and not subjects_df.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    user_id = st.selectbox(
                        "User",
                        users_df['id'].tolist(),
                        format_func=lambda x: users_df[users_df['id'] == x]['full_name'].iloc[0]
                    )
                    
                    subject_id = st.selectbox(
                        "Subject",
                        subjects_df['id'].tolist(),
                        format_func=lambda x: subjects_df[subjects_df['id'] == x]['name'].iloc[0]
                    )
                    
                    day_of_week = st.selectbox(
                        "Day of Week",
                        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                    )
                
                with col2:
                    col3, col4 = st.columns(2)
                    with col3:
                        start_time = st.time_input("Start Time", value=datetime.strptime("09:00", "%H:%M"))
                    with col4:
                        end_time = st.time_input("End Time", value=datetime.strptime("10:00", "%H:%M"))
                    
                    room = st.text_input("Room Number", placeholder="e.g., Room 101")
                
                if st.button("➕ Add to Schedule", type="primary"):
                    # Check for time conflicts
                    conflict_check = pd.read_sql_query("""
                        SELECT * FROM timetable 
                        WHERE user_id = ? AND day_of_week = ? AND (
                            (start_time <= ? AND end_time >= ?) OR
                            (start_time <= ? AND end_time >= ?) OR
                            (start_time >= ? AND end_time <= ?)
                        )
                    """, conn, params=(
                        user_id, day_of_week, 
                        start_time.strftime("%H:%M"), start_time.strftime("%H:%M"),
                        end_time.strftime("%H:%M"), end_time.strftime("%H:%M"),
                        start_time.strftime("%H:%M"), end_time.strftime("%H:%M")
                    ))
                    
                    if conflict_check.empty:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO timetable (user_id, subject_id, day_of_week, start_time, end_time, room)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (user_id, subject_id, day_of_week, start_time.strftime("%H:%M"), 
                             end_time.strftime("%H:%M"), room))
                        
                        conn.commit()
                        st.success("✅ Schedule entry added successfully!")
                    else:
                        st.error("❌ Time conflict detected! This user already has a class scheduled at this time.")
            
            else:
                st.info("No users or subjects available for scheduling.")
    
    conn.close()

# Enhanced main application dashboard
def main_dashboard():
    st.markdown('<h1 class="main-header">🎓 AI-Powered Education Dashboard</h1>', unsafe_allow_html=True)
    
    # Welcome message with user info
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### 👋 Welcome back, {st.session_state.full_name}!")
        st.markdown(f"**Role:** {st.session_state.user_role.capitalize()} | **Username:** {st.session_state.username}")
    
    with col3:
        if st.button("🚪 Logout", type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Role-based dashboard
    if st.session_state.user_role == 'student':
        student_dashboard()
    elif st.session_state.user_role == 'teacher':
        teacher_dashboard()
    elif st.session_state.user_role == 'admin':
        admin_dashboard()

def student_dashboard():
    """Student-specific dashboard"""
    conn = sqlite3.connect('education_system.db')
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Today's classes
        today = datetime.now().strftime("%A")
        today_classes = pd.read_sql_query("""
            SELECT COUNT(*) FROM timetable t
            JOIN subjects s ON t.subject_id = s.id
            WHERE t.user_id = ? AND t.day_of_week = ?
        """, conn, params=(st.session_state.user_id, today))
        
        st.markdown(f'<div class="metric-container"><h3>{today_classes.iloc[0,0]}</h3><p>Today\'s Classes</p></div>', unsafe_allow_html=True)
    
    with col2:
        # Recent scores
        recent_score = pd.read_sql_query("""
            SELECT score FROM student_scores 
            WHERE student_id = ? 
            ORDER BY test_date DESC LIMIT 1
        """, conn, params=(st.session_state.user_id,))
        
        score = recent_score.iloc[0,0] if not recent_score.empty else "N/A"
        st.markdown(f'<div class="metric-container"><h3>{score}</h3><p>Latest Score</p></div>', unsafe_allow_html=True)
    
    with col3:
        # Pending assignments (simplified)
        pending_assignments = random.randint(0, 5)
        st.markdown(f'<div class="metric-container"><h3>{pending_assignments}</h3><p>Pending Assignments</p></div>', unsafe_allow_html=True)
    
    with col4:
        # Overall average
        overall_avg = pd.read_sql_query("""
            SELECT AVG(score) FROM student_scores WHERE student_id = ?
        """, conn, params=(st.session_state.user_id,))
        
        avg = f"{overall_avg.iloc[0,0]:.1f}" if overall_avg.iloc[0,0] is not None else "N/A"
        st.markdown(f'<div class="metric-container"><h3>{avg}</h3><p>Overall Average</p></div>', unsafe_allow_html=True)
    
    # Navigation
    st.markdown("### 🚀 Quick Access")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 View My Analytics", use_container_width=True):
            st.session_state.current_page = "analytics"
            st.rerun()
    
    with col2:
        if st.button("📅 My Timetable", use_container_width=True):
            st.session_state.current_page = "timetable"
            st.rerun()
    
    with col3:
        if st.button("🧑‍🏫 AI Tutor", use_container_width=True):
            st.session_state.current_page = "tutor"
            st.rerun()
    
    # Recent activity
    st.markdown("### 📈 Recent Performance")
    
    scores_df = pd.read_sql_query("""
        SELECT ss.*, s.name as subject_name 
        FROM student_scores ss
        JOIN subjects s ON ss.subject_id = s.id
        WHERE ss.student_id = ?
        ORDER BY ss.test_date DESC
        LIMIT 10
    """, conn, params=(st.session_state.user_id,))
    
    if not scores_df.empty:
        fig = px.line(scores_df, x='test_date', y='score', color='subject_name',
                     title='Recent Test Scores', labels={'score': 'Score (%)', 'test_date': 'Date'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No test scores available yet. Complete some assessments to see your progress.")
    
    conn.close()

def teacher_dashboard():
    """Teacher-specific dashboard"""
    conn = sqlite3.connect('education_system.db')
    
    # Teacher stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Number of subjects
        subject_count = pd.read_sql_query("""
            SELECT COUNT(*) FROM subjects WHERE teacher_id = ?
        """, conn, params=(st.session_state.user_id,))
        
        st.markdown(f'<div class="metric-container"><h3>{subject_count.iloc[0,0]}</h3><p>Subjects</p></div>', unsafe_allow_html=True)
    
    with col2:
        # Total students
        student_count = pd.read_sql_query("""
            SELECT COUNT(DISTINCT t.user_id) 
            FROM timetable t
            JOIN subjects s ON t.subject_id = s.id
            WHERE s.teacher_id = ?
        """, conn, params=(st.session_state.user_id,))
        
        st.markdown(f'<div class="metric-container"><h3>{student_count.iloc[0,0]}</h3><p>Students</p></div>', unsafe_allow_html=True)
    
    with col3:
        # Questions in bank
        question_count = pd.read_sql_query("""
            SELECT COUNT(*) FROM question_bank qb
            JOIN subjects s ON qb.subject_id = s.id
            WHERE s.teacher_id = ?
        """, conn, params=(st.session_state.user_id,))
        
        st.markdown(f'<div class="metric-container"><h3>{question_count.iloc[0,0]}</h3><p>Questions</p></div>', unsafe_allow_html=True)
    
    with col4:
        # Average class performance
        class_avg = pd.read_sql_query("""
            SELECT AVG(ss.score) 
            FROM student_scores ss
            JOIN subjects s ON ss.subject_id = s.id
            WHERE s.teacher_id = ?
        """, conn, params=(st.session_state.user_id,))
        
        avg = f"{class_avg.iloc[0,0]:.1f}" if class_avg.iloc[0,0] is not None else "N/A"
        st.markdown(f'<div class="metric-container"><h3>{avg}</h3><p>Class Average</p></div>', unsafe_allow_html=True)
    
    # Navigation
    st.markdown("### 🚀 Quick Access")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Question Generator", use_container_width=True):
            st.session_state.current_page = "question_generator"
            st.rerun()
    
    with col2:
        if st.button("📊 Class Analytics", use_container_width=True):
            st.session_state.current_page = "analytics"
            st.rerun()
    
    with col3:
        if st.button("📅 Manage Schedule", use_container_width=True):
            st.session_state.current_page = "timetable"
            st.rerun()
    
    # Recent student performance
    st.markdown("### 📊 Student Performance Overview")
    
    performance_df = pd.read_sql_query("""
        SELECT u.full_name, s.name as subject_name, AVG(ss.score) as avg_score
        FROM student_scores ss
        JOIN subjects s ON ss.subject_id = s.id
        JOIN users u ON ss.student_id = u.id
        WHERE s.teacher_id = ?
        GROUP BY u.full_name, s.name
        ORDER BY avg_score DESC
        LIMIT 10
    """, conn, params=(st.session_state.user_id,))
    
    if not performance_df.empty:
        fig = px.bar(performance_df, x='full_name', y='avg_score', color='subject_name',
                    title='Top Performing Students', labels={'avg_score': 'Average Score (%)', 'full_name': 'Student'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No student performance data available yet.")
    
    conn.close()

def admin_dashboard():
    """Admin-specific dashboard"""
    conn = sqlite3.connect('education_system.db')
    
    # System stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Total users
        user_count = pd.read_sql_query("SELECT COUNT(*) FROM users", conn)
        st.markdown(f'<div class="metric-container"><h3>{user_count.iloc[0,0]}</h3><p>Total Users</p></div>', unsafe_allow_html=True)
    
    with col2:
        # Active students
        student_count = pd.read_sql_query("SELECT COUNT(*) FROM users WHERE role = 'student'", conn)
        st.markdown(f'<div class="metric-container"><h3>{student_count.iloc[0,0]}</h3><p>Students</p></div>', unsafe_allow_html=True)
    
    with col3:
        # Teachers
        teacher_count = pd.read_sql_query("SELECT COUNT(*) FROM users WHERE role = 'teacher'", conn)
        st.markdown(f'<div class="metric-container"><h3>{teacher_count.iloc[0,0]}</h3><p>Teachers</p></div>', unsafe_allow_html=True)
    
    with col4:
        # Questions in system
        question_count = pd.read_sql_query("SELECT COUNT(*) FROM question_bank", conn)
        st.markdown(f'<div class="metric-container"><h3>{question_count.iloc[0,0]}</h3><p>Questions</p></div>', unsafe_allow_html=True)
    
    # System overview
    st.markdown("### 📈 System Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # User distribution
        role_dist = pd.read_sql_query("SELECT role, COUNT(*) as count FROM users GROUP BY role", conn)
        fig = px.pie(role_dist, values='count', names='role', title='User Distribution by Role')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Question distribution
        question_dist = pd.read_sql_query("""
            SELECT s.name as subject, COUNT(*) as count 
            FROM question_bank qb
            JOIN subjects s ON qb.subject_id = s.id
            GROUP BY s.name
        """, conn)
        
        if not question_dist.empty:
            fig = px.bar(question_dist, x='subject', y='count', title='Questions by Subject')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No questions in the system yet.")
    
    # AI usage statistics
    st.markdown("### 🤖 AI Usage Analytics")
    
    ai_stats = pd.read_sql_query("""
        SELECT interaction_type, COUNT(*) as count, 
               SUM(tokens_used) as total_tokens,
               AVG(response_time) as avg_response_time
        FROM ai_interactions
        GROUP BY interaction_type
    """, conn)
    
    if not ai_stats.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total AI Interactions", ai_stats['count'].sum())
        
        with col2:
            st.metric("Total Tokens Used", f"{ai_stats['total_tokens'].sum():,}")
        
        with col3:
            st.metric("Avg Response Time", f"{ai_stats['avg_response_time'].mean():.2f}s")
        
        # AI interaction types
        fig = px.bar(ai_stats, x='interaction_type', y='count', title='AI Interactions by Type')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No AI interactions recorded yet.")
    
    conn.close()

# Main application flow
def main():
    # Initialize database and session state
    init_database()
    insert_sample_data()
    init_session_state()
    
    # Page navigation
    if not st.session_state.logged_in:
        login_page()
    else:
        # Sidebar navigation
        with st.sidebar:
            st.markdown(f"### 👤 {st.session_state.full_name}")
            st.markdown(f"*{st.session_state.user_role.capitalize()}*")
            st.markdown("---")
            
            # Role-based navigation
            if st.session_state.user_role == 'student':
                nav_options = {
                    "Dashboard": "dashboard",
                    "Learning Analytics": "analytics",
                    "Timetable": "timetable",
                    "AI Tutor": "tutor"
                }
            elif st.session_state.user_role == 'teacher':
                nav_options = {
                    "Dashboard": "dashboard",
                    "Question Generator": "question_generator",
                    "Class Analytics": "analytics",
                    "Timetable": "timetable",
                    "AI Tutor": "tutor"
                }
            else:  # admin
                nav_options = {
                    "Dashboard": "dashboard",
                    "Question Generator": "question_generator",
                    "System Analytics": "analytics",
                    "Timetable Management": "timetable",
                    "AI Tutor": "tutor"
                }
            
            # Navigation selection
            selected_nav = st.radio("Navigation", list(nav_options.keys()))
            st.session_state.current_page = nav_options[selected_nav]
            
            st.markdown("---")
            st.markdown("### ⚙️ Settings")
            
            # API key status
            if ai_service.api_key:
                st.success("✅ Groq API Configured")
            else:
                st.warning("⚠️ Groq API Not Configured")
            
            if st.button("🚪 Logout"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        # Page content
        if st.session_state.current_page == "dashboard":
            main_dashboard()
        elif st.session_state.current_page == "question_generator":
            ai_question_paper_generator()
        elif st.session_state.current_page == "analytics":
            ai_learning_analytics()
        elif st.session_state.current_page == "timetable":
            timetable_management()
        elif st.session_state.current_page == "tutor":
            ai_tutor_assistant()

if __name__ == "__main__":
    main()
