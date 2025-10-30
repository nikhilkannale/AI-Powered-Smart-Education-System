# 🎓 AI-Powered Smart Education Management System

A comprehensive, AI-integrated education management platform built with Streamlit that provides intelligent features for students, teachers, and administrators.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [User Roles](#user-roles)
- [Database Schema](#database-schema)
- [AI Integration](#ai-integration)
- [Screenshots](#screenshots)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)
- [License](#license)

## 🌟 Overview

The AI-Powered Smart Education Management System is a modern, feature-rich educational platform that leverages artificial intelligence to enhance teaching and learning experiences. It provides role-based access control, automated question paper generation, personalized learning analytics, and AI-powered tutoring capabilities.

### Key Highlights

- 🤖 **AI-Powered Features**: Question generation, performance analysis, and personalized study plans
- 📊 **Advanced Analytics**: Real-time performance tracking with interactive visualizations
- 📝 **Smart Question Bank**: Automated question paper generation with difficulty levels
- 🎯 **Personalized Learning**: AI-driven insights and recommendations for students
- 📅 **Timetable Management**: Intelligent scheduling with conflict detection
- 🔐 **Secure Authentication**: Role-based access with encrypted passwords

## ✨ Features

### For Students

- **Performance Dashboard**
  - Real-time performance metrics and trends
  - Subject-wise score analysis
  - Interactive charts and visualizations
  
- **AI Learning Analytics**
  - Personalized performance insights
  - Identification of weak and strong areas
  - Learning pattern analysis
  
- **AI Study Planner**
  - Customized 30-day study plans
  - Subject-specific recommendations
  - Time management guidance
  
- **AI Tutor Assistant**
  - Ask academic questions
  - Step-by-step math problem solver
  - Concept explanations with examples
  
- **Timetable View**
  - Weekly schedule visualization
  - Class and teacher information

### For Teachers

- **Question Paper Generator**
  - AI-powered question generation
  - Multiple question types (MCQ, Short, Long answer)
  - Difficulty level customization
  - Bloom's taxonomy integration
  
- **Question Bank Management**
  - Add, edit, and organize questions
  - Filter by type, difficulty, and topic
  - Track AI vs human-created questions
  
- **Class Analytics**
  - Student performance overview
  - Class average tracking
  - Identify struggling students
  - Performance distribution analysis
  
- **Schedule Management**
  - Create and manage class timetables
  - Conflict detection
  - Student assignment

### For Administrators

- **System Overview**
  - Total users, subjects, and questions
  - User distribution analytics
  - System-wide performance metrics
  
- **AI Usage Analytics**
  - Track AI interaction statistics
  - Token usage monitoring
  - Response time analysis
  
- **Complete Access**
  - All teacher features
  - User management capabilities
  - System configuration

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (optional)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/ai-education-system.git
cd ai-education-system
```

Or download and extract the ZIP file.

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Create Requirements File

If `requirements.txt` doesn't exist, create it with:

```txt
streamlit==1.28.0
pandas==2.1.0
numpy==1.24.3
plotly==5.17.0
scikit-learn==1.3.0
requests==2.31.0
```

## ⚙️ Configuration

### 1. Setup Groq API Key

Create a `.streamlit/secrets.toml` file in your project directory:

```bash
mkdir .streamlit
```

Add your Groq API key to `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

### 2. Get Groq API Key

1. Visit [Groq Cloud](https://console.groq.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste it into your secrets.toml file

### 3. Database Initialization

The SQLite database (`education_system.db`) will be created automatically on first run with sample data.

## 💻 Usage

### Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### Default Login Credentials

#### Students
- Username: `alice_student` | Password: `student123`
- Username: `bob_student` | Password: `student123`
- Username: `charlie_student` | Password: `student123`

#### Teachers
- Username: `john_teacher` | Password: `teacher123`
- Username: `jane_teacher` | Password: `teacher123`

#### Administrator
- Username: `admin` | Password: `admin123`

### Creating New Users

1. Click on the "Register" tab on the login page
2. Fill in all required fields
3. Choose role (student or teacher)
4. Submit the form
5. Login with your new credentials

## 👥 User Roles

### Student Role

Students can:
- View personal performance analytics
- Access AI tutor for academic help
- Generate personalized study plans
- View weekly timetable
- Track test scores and progress

### Teacher Role

Teachers can:
- Generate question papers (AI or database)
- Manage question bank
- View class performance analytics
- Create student schedules
- Access AI tutoring features
- Identify struggling students

### Admin Role

Administrators can:
- Access all system features
- View system-wide analytics
- Monitor AI usage
- Manage all users and subjects
- Configure system settings

## 🗄️ Database Schema

### Main Tables

#### users
- `id`: Primary key
- `username`: Unique username
- `password_hash`: SHA-256 hashed password
- `role`: student/teacher/admin
- `email`: User email
- `full_name`: Full name
- `created_at`: Account creation timestamp
- `last_login`: Last login timestamp
- `is_active`: Account status

#### subjects
- `id`: Primary key
- `name`: Subject name
- `code`: Unique subject code
- `teacher_id`: Foreign key to users
- `credits`: Credit hours
- `description`: Subject description

#### question_bank
- `id`: Primary key
- `subject_id`: Foreign key to subjects
- `question_text`: Question content
- `question_type`: mcq/short/long/true_false
- `options`: JSON array of options (for MCQ)
- `correct_answer`: Answer/solution
- `difficulty`: easy/medium/hard
- `chapter`: Chapter/unit name
- `topic`: Specific topic
- `bloom_level`: Bloom's taxonomy level
- `estimated_time`: Time in minutes
- `ai_generated`: Boolean flag

#### student_scores
- `id`: Primary key
- `student_id`: Foreign key to users
- `subject_id`: Foreign key to subjects
- `score`: Obtained score
- `max_score`: Maximum score
- `percentage`: Calculated percentage
- `test_date`: Test date
- `test_type`: Quiz/Assignment/Midterm/Final
- `test_title`: Test name
- `time_taken`: Time in minutes
- `questions_attempted`: Total questions
- `questions_correct`: Correct answers

#### timetable
- `id`: Primary key
- `user_id`: Foreign key to users
- `subject_id`: Foreign key to subjects
- `day_of_week`: Day name
- `start_time`: Class start time
- `end_time`: Class end time
- `room`: Room number/location
- `semester`: Current semester

#### ai_interactions
- `id`: Primary key
- `user_id`: Foreign key to users
- `interaction_type`: Type of AI interaction
- `input_text`: User input
- `output_text`: AI response
- `tokens_used`: API tokens consumed
- `response_time`: Response time in seconds
- `created_at`: Interaction timestamp

#### study_plans
- `id`: Primary key
- `student_id`: Foreign key to users
- `subject_id`: Foreign key to subjects
- `plan_title`: Plan name
- `plan_content`: Full plan text
- `difficulty_level`: easy/medium/hard
- `estimated_hours`: Total hours
- `status`: active/completed/cancelled
- `ai_generated`: Boolean flag

## 🤖 AI Integration

### Groq API

The system uses Groq's fast inference API for AI features:

- **Model**: llama-3.1-8b-instant
- **Provider**: Groq Cloud
- **Features**:
  - Question generation
  - Performance analysis
  - Study plan creation
  - Math problem solving
  - Concept explanations

### AI Functions

#### 1. Question Generation
```python
ai_service.generate_questions(
    subject="Mathematics",
    topic="Calculus",
    difficulty="medium",
    question_type="mcq",
    count=5
)
```

#### 2. Performance Analysis
```python
ai_service.analyze_student_performance(student_data)
```

#### 3. Study Plan Creation
```python
ai_service.create_study_plan(student_profile)
```

#### 4. Math Problem Solver
```python
ai_service.solve_math_problem(problem_text)
```

#### 5. Concept Explainer
```python
ai_service.explain_concept(subject, concept, level)
```

## 📸 Screenshots

### Login Page
Modern, user-friendly authentication with registration option.

### Student Dashboard
- Performance metrics
- Recent test scores
- Quick access to features

### AI Question Generator
- Automatic question creation
- Multiple formats and difficulties
- Save to question bank

### Learning Analytics
- Interactive charts
- Performance trends
- AI-powered insights

### AI Tutor
- Academic question answering
- Math problem solving
- Concept explanations

## 🛠️ Technologies Used

### Backend
- **Python 3.8+**: Core programming language
- **SQLite3**: Embedded database
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations

### Frontend
- **Streamlit**: Web application framework
- **Plotly**: Interactive visualizations
- **HTML/CSS**: Custom styling

### AI/ML
- **Groq API**: Fast LLM inference
- **scikit-learn**: Machine learning utilities
- **LLaMA 3.1**: Language model

### Security
- **hashlib**: Password hashing (SHA-256)
- **SQLite Foreign Keys**: Data integrity

## 📁 Project Structure

```
ai-education-system/
│
├── app.py                      # Main application file
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── .streamlit/
│   └── secrets.toml           # API keys (not in git)
│
├── education_system.db        # SQLite database (auto-generated)
│
└── .gitignore                 # Git ignore file
```

## 🔧 Troubleshooting

### Database Errors
**Issue**: Database locked or permission errors  
**Solution**: Close any SQLite browser tools and restart the app

### API Errors
**Issue**: Groq API key not configured  
**Solution**: Add your API key to `.streamlit/secrets.toml`

### Import Errors
**Issue**: Module not found  
**Solution**: Install all requirements: `pip install -r requirements.txt`

### Performance Issues
**Issue**: Slow loading or timeouts  
**Solution**: 
- Check your internet connection
- Verify Groq API status
- Reduce the number of AI-generated questions

## 🚀 Future Enhancements

- [ ] Real-time collaboration features
- [ ] Video conferencing integration
- [ ] Mobile application
- [ ] Assignment submission system
- [ ] Automated grading
- [ ] Parent portal
- [ ] Multi-language support
- [ ] Advanced reporting
- [ ] Integration with LMS platforms
- [ ] Gamification elements

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards
- Follow PEP 8 style guide
- Add docstrings to functions
- Comment complex logic
- Test new features thoroughly

## 📝 License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2024 AI Education System

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 📞 Support

For issues, questions, or suggestions:

- **Email**: support@aieducationsystem.com
- **GitHub Issues**: [Create an issue](https://github.com/yourusername/ai-education-system/issues)
- **Documentation**: [Wiki](https://github.com/yourusername/ai-education-system/wiki)

## 🙏 Acknowledgments

- **Groq** for providing fast LLM inference
- **Streamlit** for the amazing web framework
- **Plotly** for interactive visualizations
- **Open Source Community** for various libraries used

## 📊 Project Status

- **Version**: 1.0.0
- **Status**: Active Development
- **Last Updated**: October 2024
- **Maintained**: Yes

---

**Made with ❤️ for educators and students worldwide**

⭐ If you find this project helpful, please consider giving it a star on GitHub!


Generate a Abstract according to the Research Level in 200 words