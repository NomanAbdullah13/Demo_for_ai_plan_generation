import streamlit as st
from openai import OpenAI
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Demo For Just Plan Generation",
    page_icon="🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #ff6b6b;
        margin-bottom: 2rem;
    }
    
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #4ecdc4;
        margin: 1rem 0;
    }
    
    .fitness-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
    }
    
    .goal-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .plan-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize OpenAI client
@st.cache_resource
def init_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("⚠️ OpenAI API key not found! Please set OPENAI_API_KEY in your .env file")
        st.stop()
    return OpenAI(api_key=api_key)

# Helper function for rerun compatibility
def safe_rerun():
    """Compatible rerun function for different Streamlit versions"""
    try:
        st.rerun()
    except AttributeError:
        try:
            st.experimental_rerun()
        except AttributeError:
            st.warning("Please refresh the page manually")

openai_client = init_openai_client()

# Language settings
LANGUAGES = {
    "English 🇺🇸": "english",
    "Español 🇪🇸": "spanish"
}

CONTENT = {
    'english': {
        'welcome': "Please check spanish is correct or not and which questions you need add or modify",
        'subtitle': "Your AI-Powered Personal Fitness Coach",
        'description': "Get a personalized fitness and nutrition plan tailored just for you!",
        'form_title': "📋 Personal Information",
        'generating': "🔄 Generating your personalized fitness plan...",
        'plan_ready': "🎉 Your Personalized Fitness Plan is Ready!",
        'questions': {
            'weight': "Current Weight (kg or lbs)",
            'height': "Height (e.g., 5'8\" or 175cm)",
            'age': "Age",
            'gender': "Gender",
            'activity_level': "Current Activity Level",
            'goal': "Primary Fitness Goal",
            'diet_restrictions': "Dietary Restrictions/Allergies",
            'training_days': "Training Days per Week",
            'workout_pref': "Workout Preference"
        },
        'activity_levels': {
            'Sedentary': 'Sedentary (little to no exercise)',
            'Lightly active': 'Lightly active (light exercise 1-3 days/week)',
            'Moderately active': 'Moderately active (moderate exercise 3-5 days/week)',
            'Very active': 'Very active (hard exercise 6-7 days/week)',
            'Extremely active': 'Extremely active (very hard exercise, physical job)'
        },
        'goals': {
            'Lose weight': 'Lose weight 📉',
            'Gain muscle': 'Gain muscle 💪',
            'Maintain weight': 'Maintain weight ⚖️',
            'Improve endurance': 'Improve endurance 🏃‍♂️',
            'General fitness': 'General fitness 🌟'
        },
        'workout_prefs': {
            'Gym access': 'Gym access 🏋️‍♂️',
            'Home workouts only': 'Home workouts only 🏠',
            'Both': 'Both gym and home 🔄'
        },
        'motivational_messages': [
            "💪 Remember: Progress, not perfection! Every small step counts.",
            "🔥 Consistency is the key to achieving your fitness dreams.",
            "⭐ Your future self will thank you for the effort you put in today.",
            "🏆 Every workout is a victory! Keep pushing toward your goals.",
            "💯 Believe in yourself! You're stronger than you think."
        ]
    },
    'spanish': {
        'welcome': "¡Bienvenido a FitBot! 🏋️‍♂️",
        'subtitle': "Tu Entrenador Personal con IA",
        'description': "¡Obtén un plan de fitness y nutrición personalizado hecho para ti!",
        'form_title': "📋 Información Personal",
        'generating': "🔄 Generando tu plan de fitness personalizado...",
        'plan_ready': "🎉 ¡Tu Plan de Fitness Personalizado está Listo!",
        'questions': {
            'weight': "Peso Actual (kg o libras)",
            'height': "Altura (ej: 1.75m o 5'8\")",
            'age': "Edad",
            'gender': "Género",
            'activity_level': "Nivel de Actividad Actual",
            'goal': "Objetivo Principal de Fitness",
            'diet_restrictions': "Restricciones Dietéticas/Alergias",
            'training_days': "Días de Entrenamiento por Semana",
            'workout_pref': "Preferencia de Entrenamiento"
        },
        'activity_levels': {
            'Sedentary': 'Sedentario (poco o nada de ejercicio)',
            'Lightly active': 'Ligeramente activo (ejercicio ligero 1-3 días/semana)',
            'Moderately active': 'Moderadamente activo (ejercicio moderado 3-5 días/semana)',
            'Very active': 'Muy activo (ejercicio intenso 6-7 días/semana)',
            'Extremely active': 'Extremadamente activo (ejercicio muy intenso, trabajo físico)'
        },
        'goals': {
            'Lose weight': 'Perder peso 📉',
            'Gain muscle': 'Ganar músculo 💪',
            'Maintain weight': 'Mantener peso ⚖️',
            'Improve endurance': 'Mejorar resistencia 🏃‍♂️',
            'General fitness': 'Fitness general 🌟'
        },
        'workout_prefs': {
            'Gym access': 'Acceso a gimnasio 🏋️‍♂️',
            'Home workouts only': 'Solo entrenamientos en casa 🏠',
            'Both': 'Ambos gimnasio y casa 🔄'
        },
        'motivational_messages': [
            "💪 Recuerda: ¡Progreso, no perfección! Cada pequeño paso cuenta.",
            "🔥 La consistencia es la clave para lograr tus sueños de fitness.",
            "⭐ Tu yo futuro te agradecerá el esfuerzo que pongas hoy.",
            "🏆 ¡Cada entrenamiento es una victoria! Sigue empujando hacia tus objetivos.",
            "💯 ¡Cree en ti mismo! Eres más fuerte de lo que piensas."
        ]
    }
}

def generate_fitness_plan(user_data: Dict[str, Any], language: str) -> str:
    """Generate personalized fitness plan using OpenAI"""
    
    language_instruction = "English" if language == 'english' else "Spanish"
    
    prompt = f"""
    Create a comprehensive, personalized fitness and nutrition plan in {language_instruction} for someone with these characteristics:
    
    Personal Information:
    - Weight: {user_data.get('weight', 'Not specified')}
    - Height: {user_data.get('height', 'Not specified')}
    - Age: {user_data.get('age', 'Not specified')}
    - Gender: {user_data.get('gender', 'Not specified')}
    - Activity Level: {user_data.get('activity_level', 'Not specified')}
    - Primary Goal: {user_data.get('goal', 'Not specified')}
    - Dietary Restrictions: {user_data.get('diet_restrictions', 'None')}
    - Available Training Days: {user_data.get('training_days', 'Not specified')} days per week
    - Workout Preference: {user_data.get('workout_pref', 'Not specified')}
    
    Please provide a comprehensive plan with the following sections:
    
    1. 📊 PERSONAL ASSESSMENT
    - BMI calculation and assessment
    - Fitness level evaluation
    - Goal feasibility and timeline
    
    2. 🏋️‍♂️ WEEKLY WORKOUT SCHEDULE
    - Detailed day-by-day workout plan
    - Specific exercises with sets and reps
    - Progressive difficulty recommendations
    
    3. 🥗 NUTRITION PLAN
    - Daily calorie target
    - Macronutrient breakdown
    - Meal timing suggestions
    - Sample meal ideas
    
    4. 📈 PROGRESS TRACKING
    - Key metrics to monitor
    - Timeline for expected results
    - Milestone checkpoints
    
    5. 💡 SUCCESS TIPS
    - Motivation strategies
    - Common pitfalls to avoid
    - Lifestyle integration tips
    
    Make it practical, motivating, and achievable. Use emojis and clear formatting.
    Ensure the advice is safe and encourages consulting healthcare professionals when appropriate.
    """
    
    try:
        with st.spinner("🤖 AI is creating your personalized fitness plan..."):
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional fitness and nutrition coach with expertise in creating personalized, safe, and effective fitness plans. Always prioritize user safety and encourage professional consultation when needed."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
    except Exception as e:
        error_msg = f"❌ Error generating fitness plan: {str(e)}"
        st.error(error_msg)
        return error_msg

def main():
    # Initialize session state
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}
    if 'fitness_plan' not in st.session_state:
        st.session_state.fitness_plan = ""
    if 'plan_generated' not in st.session_state:
        st.session_state.plan_generated = False
    if 'reset_form' not in st.session_state:
        st.session_state.reset_form = False
    if 'generate_new' not in st.session_state:
        st.session_state.generate_new = False
    
    # Sidebar for language and settings
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        selected_language = st.selectbox(
            "🌐 Choose Language",
            options=list(LANGUAGES.keys()),
            index=0
        )
        language = LANGUAGES[selected_language]
        content = CONTENT[language]
        
        st.markdown("---")
        st.markdown("### 📊 Your Progress")
        if st.session_state.plan_generated:
            st.success("✅ Plan Generated!")
            st.info("📅 Plan created: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
        else:
            st.info("📝 Fill out the form to get started")
        
        st.markdown("---")
        st.markdown("### 🔗 Quick Actions")
        
        # Reset form button
        if st.button("🔄 Reset Form"):
            st.session_state.user_data = {}
            st.session_state.fitness_plan = ""
            st.session_state.plan_generated = False
            st.session_state.reset_form = True
        
        # Generate new plan button
        if st.session_state.plan_generated:
            if st.button("📄 Generate New Plan"):
                st.session_state.fitness_plan = ""
                st.session_state.plan_generated = False
                st.session_state.generate_new = True
        
        # Handle resets without using rerun
        if st.session_state.reset_form:
            st.session_state.reset_form = False
            st.success("✅ Form reset! Please fill it out again.")
        
        if st.session_state.generate_new:
            st.session_state.generate_new = False
            st.info("📝 Please fill out the form to generate a new plan.")
    
    # Main content area
    st.markdown(f'<h1 class="main-header">{content["welcome"]}</h1>', unsafe_allow_html=True)
    st.markdown(f'<h2 style="text-align: center; color: #666;">{content["subtitle"]}</h2>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align: center; font-size: 1.2rem; margin-bottom: 2rem;">{content["description"]}</p>', unsafe_allow_html=True)
    
    # Show motivational message
    import random
    motivational_msg = random.choice(content['motivational_messages'])
    st.markdown(f'<div class="fitness-card">{motivational_msg}</div>', unsafe_allow_html=True)
    
    # Main form
    if not st.session_state.plan_generated:
        st.markdown(f'<h2 class="sub-header">{content["form_title"]}</h2>', unsafe_allow_html=True)
        
        with st.form("fitness_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                weight = st.text_input(content['questions']['weight'], 
                                     placeholder="e.g., 70kg or 154lbs")
                height = st.text_input(content['questions']['height'], 
                                     placeholder="e.g., 175cm or 5'9\"")
                age = st.number_input(content['questions']['age'], 
                                    min_value=13, max_value=100, value=25)
                gender = st.selectbox(content['questions']['gender'], 
                                    ["Male", "Female", "Other"])
                activity_level = st.selectbox(content['questions']['activity_level'], 
                                            list(content['activity_levels'].values()))
            
            with col2:
                goal = st.selectbox(content['questions']['goal'], 
                                  list(content['goals'].values()))
                diet_restrictions = st.text_area(content['questions']['diet_restrictions'], 
                                               placeholder="e.g., vegetarian, lactose intolerant, none")
                training_days = st.number_input(content['questions']['training_days'], 
                                              min_value=1, max_value=7, value=3)
                workout_pref = st.selectbox(content['questions']['workout_pref'], 
                                          list(content['workout_prefs'].values()))
                
                # Add some additional optional fields
                st.markdown("**Optional Information:**")
                experience_level = st.selectbox("Fitness Experience Level", 
                                              ["Beginner", "Intermediate", "Advanced"])
                injuries = st.text_input("Any injuries or physical limitations?", 
                                       placeholder="e.g., knee injury, back problems, none")
            
            submitted = st.form_submit_button("🚀 Generate My Fitness Plan", use_container_width=True)
            
            if submitted:
                # Validate required fields
                if not weight or not height:
                    st.error("⚠️ Please fill in your weight and height!")
                else:
                    # Store user data
                    activity_key = [k for k, v in content['activity_levels'].items() if v == activity_level][0]
                    goal_key = [k for k, v in content['goals'].items() if v == goal][0]
                    workout_key = [k for k, v in content['workout_prefs'].items() if v == workout_pref][0]
                    
                    st.session_state.user_data = {
                        'weight': weight,
                        'height': height,
                        'age': age,
                        'gender': gender,
                        'activity_level': activity_key,
                        'goal': goal_key,
                        'diet_restrictions': diet_restrictions if diet_restrictions else 'None',
                        'training_days': training_days,
                        'workout_pref': workout_key,
                        'experience_level': experience_level,
                        'injuries': injuries if injuries else 'None'
                    }
                    
                    # Generate fitness plan
                    with st.spinner(content['generating']):
                        progress_bar = st.progress(0)
                        for i in range(100):
                            time.sleep(0.01)
                            progress_bar.progress(i + 1)
                        
                        st.session_state.fitness_plan = generate_fitness_plan(
                            st.session_state.user_data, language
                        )
                        st.session_state.plan_generated = True
                        safe_rerun()
    
    # Display fitness plan
    if st.session_state.plan_generated and st.session_state.fitness_plan:
        st.markdown(f'<h2 class="sub-header">{content["plan_ready"]}</h2>', unsafe_allow_html=True)
        
        # Display user summary
        with st.expander("👤 Your Profile Summary", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f'<div class="metric-card"><strong>Weight</strong><br>{st.session_state.user_data["weight"]}</div>', 
                          unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric-card"><strong>Height</strong><br>{st.session_state.user_data["height"]}</div>', 
                          unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="metric-card"><strong>Age</strong><br>{st.session_state.user_data["age"]}</div>', 
                          unsafe_allow_html=True)
            with col4:
                st.markdown(f'<div class="metric-card"><strong>Goal</strong><br>{st.session_state.user_data["goal"]}</div>', 
                          unsafe_allow_html=True)
        
        # Display the fitness plan
        st.markdown('<div class="plan-section">', unsafe_allow_html=True)
        st.markdown(st.session_state.fitness_plan)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 Copy Plan to Clipboard"):
                try:
                    # Try to copy to clipboard (requires pyperclip)
                    import pyperclip
                    pyperclip.copy(st.session_state.fitness_plan)
                    st.success("✅ Plan copied to clipboard!")
                except ImportError:
                    st.info("📋 Copy the plan text manually from above")
        
        with col2:
            if st.button("📊 View Plan Summary"):
                st.info("📈 Plan Summary: Your personalized fitness journey starts here!")
        
        with col3:
            if st.button("💡 Get Tips"):
                tips = [
                    "💧 Stay hydrated - aim for 8 glasses of water daily",
                    "😴 Get 7-9 hours of sleep for optimal recovery",
                    "📱 Track your progress with photos and measurements",
                    "🥗 Prep your meals in advance for consistency",
                    "👥 Find a workout buddy for accountability"
                ]
                tip = random.choice(tips)
                st.success(f"💡 **Tip:** {tip}")
        
        # Show another motivational message
        st.markdown("---")
        final_motivation = random.choice(content['motivational_messages'])
        st.markdown(f'<div class="goal-card">{final_motivation}</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🤖 Powered by AI | 💪 Built for Your Fitness Success</p>
        <p><small>⚠️ Always consult with healthcare professionals before starting any new fitness program.</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":

    main()
