import streamlit as st
import bcrypt
from supabase import create_client
import google.generativeai as genai
import time
from datetime import datetime
import json
from PIL import Image
from gtts import gTTS
import tempfile
import textwrap
import os
import io
import threading
import time

icon_url = "https://i.ibb.co/qLH2c1zC/image.png"

st.set_page_config(
    page_title="Storify! - Just Write It",
    page_icon=icon_url,
    layout="wide",
    initial_sidebar_state="expanded"
)

DEFAULT_CSS = """
<style>
    /* === MAIN LAYOUT ENHANCEMENTS === */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    
    .content-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .sidebar-content {
        background: #f8f9fa !important;
    }
    
    /* === NAVIGATION & LAYOUT COMPONENTS === */
    /* Sidebar Radio Navigation */
    .stSidebar [data-testid="stVerticalBlock"] [data-testid="stRadio"] {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f8f9fa;
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, #667eea, #764ba2) !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    /* Columns Enhancement */
    [data-testid="column"] {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        margin: 0.5rem;
        border-left: 3px solid #667eea;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 8px;
        padding: 1rem;
        font-weight: 600;
        border-left: 4px solid #667eea;
    }
    
    .streamlit-expanderContent {
        background: white;
        padding: 1.5rem;
        border-radius: 0 0 8px 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* === INPUT COMPONENTS === */
    /* Text Input & Text Area */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 8px;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Radio Buttons & Checkboxes */
    .stRadio [role="radiogroup"], .stCheckbox [data-testid="stCheckbox"] {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Slider Styling */
    .stSlider [data-testid="stThumb"] {
        background: linear-gradient(45deg, #667eea, #764ba2);
    }
    
    .stSlider [data-testid="stTrack"] {
        background: #e9ecef;
    }
    
    /* Number Input */
    .stNumberInput>div>div>input {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 8px;
        padding: 0.75rem;
    }
    
    /* Selectbox & Multiselect */
    .stSelectbox>div>div, .stMultiSelect>div>div {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stSelectbox>div>div:hover, .stMultiSelect>div>div:hover {
        border-color: #667eea;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Form Submit Button */
    .stFormSubmitButton>button {
        background: linear-gradient(45deg, #28a745, #20c997) !important;
    }
    
    /* === DISPLAY COMPONENTS === */
    /* Headers and Subheaders */
    .stHeader, .stSubheader, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #2d3748;
        margin-bottom: 1rem;
    }
    
    /* Caption Styling */
    .stCaption {
        color: #718096;
        font-style: italic;
    }
    
    /* Alert Messages */
    .stAlert {
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #bee3f8, #ebf8ff);
        border-left: 4px solid #3182ce;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fefcbf, #fffaf0);
        border-left: 4px solid #d69e2e;
    }
    
    .stError {
        background: linear-gradient(135deg, #fed7d7, #fff5f5);
        border-left: 4px solid #e53e3e;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, #c6f6d5, #f0fff4);
        border-left: 4px solid #38a169;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background: linear-gradient(45deg, #667eea, #764ba2);
        border-radius: 4px;
    }
    
    /* Metric Display */
    [data-testid="metric-container"] {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
    }
    
    /* Spinner */
    .stSpinner > div {
        border: 3px solid #f3f3f3;
        border-top: 3px solid #667eea;
        border-radius: 50%;
    }
    
    /* === FORM COMPONENTS === */
    .stForm {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    /* === CUSTOM CONTAINER STYLING === */
    .stContainer {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    /* === BALLOONS ANIMATION ENHANCEMENT === */
    .balloons-container {
        position: relative;
        z-index: 9999;
    }
</style>
"""
# Apply default beautiful styling
st.markdown(DEFAULT_CSS, unsafe_allow_html=True)

def build_prompt_for_chapter(story_info, chapter_idx, words_per_chapter):
    chapter = story_info["chapters"][chapter_idx]
    characters_text = ""
    for char in story_info["characters"]:
        characters_text += f"- {char['name']} ({char['role']}), Age: {char['age']}, Traits: {', '.join(char['traits'])}, Goal: {char['goal']}, Problem: {char['problem']}, Backstory: {char['backstory']}\n"
    previous_chapters_text = ""
    for i in range(chapter_idx):
        previous_chapters_text += f"Chapter {i + 1}: {story_info['chapters'][i].get('generated_text', '')}\n\n"

    outlines_text = "\n".join(chapter.get("outlines", []))

    prompt = f"""
Hello, you are a world-class story writer.

Here is all the background information for the story:

Title: {story_info['title']}
Type: {story_info['type']}
Summary / Background: {story_info['summary']}

Characters:
{characters_text}

Previously in the story (all previous chapters):
{previous_chapters_text}

Now, write Chapter {chapter_idx + 1} titled "{chapter['title']}" using the following outlines:
{outlines_text}

Instructions:
- Follow the story continuity from previous chapters.
- Maintain character personalities, goals, and backstories.
- Write in engaging, flowing narrative with dialogues where appropriate.
- Ensure the chapter logically fits into the story.
- Keep it creative, coherent, and suitable for the intended audience.
- Please do not add any information such as 'Of course' or 'Yes', give me only the chapter. 
- The chapter should have at least {words_per_chapter} words per chapter
Please generate only the text for this chapter.
"""
    return prompt

def generate_full_story(story_info, words_per_chapter=500):
    try:
        APIkey = st.secrets["gemini"]["api_key"]
        genai.configure(api_key=APIkey)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
    except Exception as e:
        st.error(f"Gemini configuration error: {e}")
        return None

    full_story_text = ""

    for chapter_idx, chapter in enumerate(story_info["chapters"]):
        if not chapter.get("outlines"):
            st.warning(f"Chapter {chapter_idx + 1} has no outlines, skipping...")
            continue
            
        prompt = build_prompt_for_chapter(story_info, chapter_idx, words_per_chapter)

        try:
            response = model.generate_content(prompt)
            if not response.text:
                st.error(f"No response for chapter {chapter_idx + 1}")
                continue
                
            generated_text = response.text
            story_info["chapters"][chapter_idx]["generated_text"] = generated_text
            full_story_text += f"# Chapter {chapter_idx + 1}: {chapter['title']}\n\n{generated_text}\n\n"

        except Exception as e:
            st.error(f"Error generating chapter {chapter_idx + 1}: {e}")
            full_story_text += f"# Chapter {chapter_idx + 1}: {chapter['title']}\n\n[Error generating this chapter]\n\n"

    return full_story_text

def create_story(user_id, title, book_type, summary, chapters, characters, full_story="", rating=None):
    try:
        # Check if story with same title already exists for this user
        existing_story = supabase1.table("stories").select("*").eq("user_id", user_id).eq("title", title).execute()
        
        if existing_story.data:
            # Update existing story instead of creating new one
            story_data = {
                "id": existing_story.data[0]["id"],  # Include the existing ID
                "user_id": user_id,
                "title": title,
                "book_type": book_type,
                "summary": summary,
                "chapters": chapters,
                "characters": characters,
                "full_story": full_story,
                "rating": rating,
                "updated_at": datetime.now().isoformat()
            }
            
            response = supabase1.table("stories").update(story_data).eq("id", existing_story.data[0]["id"]).execute()
        else:
            # Create new story
            story_data = {
                "user_id": user_id,
                "title": title,
                "book_type": book_type,
                "summary": summary,
                "chapters": chapters,
                "characters": characters,
                "full_story": full_story,
                "rating": rating,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            response = supabase1.table("stories").insert(story_data).execute()
        
        if response.data:
            return response.data
        return None
    except Exception as e:
        st.error(f"Create story error: {e}")
        return None

def get_stories(user_id):
    """Fetch all stories for a user"""
    try:
        response = supabase1.table("stories").select("*").eq("user_id", user_id).execute()
        return response.data
    except Exception as e:
        st.error(f"Get stories error: {e}")
        return []

def get_all_stories():
    """Fetch all stories for ranking"""
    try:
        response = supabase1.table("stories").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Get all stories error: {e}")
        return []

def get_story_rankings():
    """Get top 5 stories by rating"""
    try:
        response = supabase1.table("stories").select("*").order("rating", desc=True).limit(5).execute()
        return response.data
    except Exception as e:
        st.error(f"Get rankings error: {e}")
        return []

# ===== GLOBAL VARIABLES =====
traits = [
    "Affectionate", "Ambitious", "Analytical", "Appreciative", "Charismatic",
    "Compassionate", "Confident", "Creative", "Curious", "Determined",
    "Empathetic", "Energetic", "Enthusiastic", "Honest", "Imaginative",
    "Intelligent", "Kind", "Loyal", "Optimistic", "Patient",
    "Perceptive", "Persistent", "Practical", "Rational", "Resourceful",
    "Responsible", "Sensitive", "Sociable", "Spontaneous", "Thoughtful",
    "Adventurous", "Cautious", "Competitive", "Cooperative", "Diplomatic",
    "Disciplined", "Flexible", "Independent", "Introverted", "Meticulous",
    "Observant", "Organized", "Passionate", "Perfectionist", "Philosophical",
    "Playful", "Pragmatic", "Proactive", "Proud", "Reliable",
    "Reserved", "Romantic", "Sarcastic", "Selfless", "Serious",
    "Skeptical", "Strategic", "Stubborn", "Supportive", "Tolerant",
    "Traditional", "Versatile", "Visionary", "Witty", "Zealous"
]

LS_TABS = ["Login", "Sign up"]
MENU = ["Home Page", "Login/Signup", "Dashboard", "Create Story", "Leaderboard", "Explore", "About the creator"]

SUPABASE_URL = "https://omkvbyqtvomjivzokezm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ta3ZieXF0dm9taml2em9rZXptIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTczMzkwMzEsImV4cCI6MjA3MjkxNTAzMX0.nc5fqqM1ueM0nn9YGpYAEB68jj7FC_J-q3xupeIQyE8"
supabase1 = create_client(SUPABASE_URL, SUPABASE_KEY)

# ===== INITIALIZE SESSION STATE =====
if "SIGNED_IN" not in st.session_state:
    st.session_state["SIGNED_IN"] = False
if "chapters" not in st.session_state:
    st.session_state["chapters"] = []
if "generated_story" not in st.session_state:
    st.session_state["generated_story"] = ""
if "story_rating" not in st.session_state:
    st.session_state["story_rating"] = None
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "current_story_id" not in st.session_state:
    st.session_state["current_story_id"] = None
if "stories" not in st.session_state:
    st.session_state["stories"] = []
if "num_characters" not in st.session_state:
    st.session_state["num_characters"] = 5
if "story_type" not in st.session_state:
    st.session_state["story_type"] = "Chapters"
if "rough_plot_saved" not in st.session_state:
    st.session_state["rough_plot_saved"] = False

# ===== HELPER FUNCTIONS =====
def signup(first_name, last_name, username, email, password):
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    try:
        response = supabase1.table("users").insert({
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "email": email,
            "password_hash": hashed
        }).execute()
        if response.data:
            return True
        return False
    except Exception as e:
        st.error(f"Signup error: {e}")
        return False

def login(username, password):
    try:
        response = supabase1.table("users").select("id, password_hash").eq("username", username).execute()
        if not response.data:
            return False
        stored_hash = response.data[0]["password_hash"].encode("utf-8")
        if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
            st.session_state["user_id"] = response.data[0]["id"]
            return True
        return False
    except Exception as e:
        st.error(f"Login error: {e}")
        return False

def rate_story(story_content, title, book_type):
    rating_prompt = f"""
As an expert story critic, please rate the following story on a scale of 1-1000.
Consider these criteria:
1. Creativity and originality (25%)
2. Character development (25%)
3. Plot structure and pacing (25%)
4. Emotional impact (15%)

Story Title: {title}
Type: {book_type}

Story Content:
{story_content}

Please provide ONLY a single number between 1-1000 as your rating. No other text.
Example: 850

You must be extremely harsh, and do not consider vocabulary, focus on the plot, chracter development and emotional impact.
Remember to be very harsh. Nothing even above 920.
Even the best stories you have ever read will be only like 850ish
You do not have to only use uniform number you can use numbers like 738 not just 740
Your only job is to be harsh
"""
    try:
        APIkey = st.secrets["gemini"]["api_key"]
        genai.configure(api_key=APIkey)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        response = model.generate_content(rating_prompt)
        rating_text = response.text.strip()
        rating = float(rating_text)
        return max(1.0, min(1000.0, rating))
    except Exception as e:
        st.error(f"Error rating story: {e}")
        return 500.0

def show_confetti():
    """Show confetti animation"""
    confetti_js = """
    <script>
    const confetti = () => {
        const end = Date.now() + (3 * 1000);
        const colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#00ffff', '#ff00ff'];
        
        (function frame() {
            confetti({
                particleCount: 5,
                angle: 60,
                spread: 55,
                origin: { x: 0 },
                colors: colors
            });
            
            confetti({
                particleCount: 5,
                angle: 120,
                spread: 55,
                origin: { x: 1 },
                colors: colors
            });
            
            if (Date.now() < end) {
                requestAnimationFrame(frame);
            }
        }());
    }
    confetti();
    </script>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.2/dist/confetti.browser.min.js"></script>
    """
    st.components.v1.html(confetti_js, height=200)

def display_rating(rating, rank=None, total_stories=None):
    if rating is None:
        st.info("⭐ Rating: Not yet rated")
        return
        
    try:
        display_rating = float(rating)
    except (ValueError, TypeError):
        st.error("Invalid rating format")
        return
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("⭐ Story Rating")
        star_rating = (display_rating / 1000.0) * 5
        stars_count = int(round(star_rating))
        
        st.markdown(f"### {display_rating:.0f}/1000")
        st.progress(display_rating / 1000.0)
    
    with col2:
        if rank is not None and total_stories is not None:
            st.subheader(" Ranking")
            if rank <= 5:
                st.success(f"## #{rank} out of {total_stories} stories!")
                if rank == 1:
                    st.balloons()
                    show_confetti()
                elif rank <= 3:
                    st.balloons()
                else:
                    show_confetti()
            else:
                st.info(f"## #{rank} out of {total_stories} stories")

def has_valid_chapters(chapters):
    """Check if chapters have outlines"""
    if not chapters:
        return False
    for chapter in chapters:
        if chapter.get("outlines") and any(outline.strip() for outline in chapter["outlines"]):
            return True
    return False

def validate_story_data(title, chapters, story_type):
    """Validate story data before generation"""
    if not title.strip():
        return False, "Please enter a story title first"
    
    if not has_valid_chapters(chapters):
        if story_type == "Short Story":
            return False, "Please enter your rough plot and click 'Save Rough Plot' first"
        else:
            return False, "Please add at least one chapter with outlines"
    
    return True, ""

# ===== MAIN APP =====
st.title(" Storify")
page = st.sidebar.radio("Menu", MENU)

if page == "Login/Signup":
    st.caption("Click on the Sign Up button if you do not have an account")
    FLS_TABS = st.tabs(LS_TABS)
    
    with FLS_TABS[1]:
        with st.form("Signup Form"):
            firstname = st.text_input("First Name")
            lastname = st.text_input("Last Name")
            email = st.text_input("Email")
            username = st.text_input("Username", key='username')
            password = st.text_input("Password", type="password", key='password')
            submitted = st.form_submit_button("Sign Up", key='signup')
            if submitted:
                if firstname is not None and lastname is not None and username is not None and password is not None and email is not None:
                    if signup(firstname, lastname, username, email, password):
                        st.success("Signup Successful")
                    else:
                        st.error("Signup Failed")
                else:
                    st.error("Please enter all information")
    
    with FLS_TABS[0]:
        with st.form("Login Form"):
            username = st.text_input("Username", key='loginusername')
            password = st.text_input("Password", type="password", key='loginpassword')
            submitted = st.form_submit_button("Login", key='login')
            if submitted:
                if login(username, password):
                    st.success("Login Successful")
                    st.session_state["SIGNED_IN"] = True
                else:
                    st.error("Login Failed")

elif page == "Create Story":
    if not st.session_state.get("SIGNED_IN", False):
        st.warning("You are not logged in")
        st.caption("Please login or create an account to access this page")
    else:
        st.title("Create the story")
        flstabs = ["Details", "Characters/Rough Outlining", "Outlining", "Final Story", "Save/Manage"]
        STORYTABS = st.tabs(flstabs)
        
        with STORYTABS[0]:
            title = st.text_input("Write the name of your story", help="Enter the title for your story")
            books_type = ['Fiction', 'Non-fiction']
            book_type = st.radio('Type', books_type, index=0, help="Choose if your book is fiction or non-fiction")
            summarised = st.text_area("Write a background/summary for your story",
                                     help="Give a short one line description of your story.")
        
        with STORYTABS[1]:
            st.subheader("Characters")
            st.caption("Create and develop the important characters of your story")
            use_advanced = st.checkbox("Use this if you have more than 40 characters in your story",
                                      help="Click this if you have more than 40 characters")
            if use_advanced:
                num_characters = st.number_input("Enter number of main characters", min_value=40, value=50, step=1)
            else:
                num_characters = st.slider("Enter number of main characters", min_value=2, max_value=40, value=5, step=1)
            
            st.session_state["num_characters"] = num_characters
            
            for i in range(1, num_characters + 1):
                st.markdown(f"**Character {i}**")
                st.text_input("Name", key=f"char_name_{i}", help='What is the character\'s name?')
                st.text_input("Age", key=f"char_age_{i}", help='How old is the character?')
                st.text_input("Goal", key=f"char_goal_{i}", help='What is the character\'s goal?')
                st.text_input("Problem", key=f"char_problem_{i}", help='What is the character\'s problem?')
                st.text_area("Backstory", key=f"char_backstory_{i}", help='What is the character\'s backstory?')
                
                st.multiselect(
                    "Personality Traits",
                    options=traits,
                    key=f"char_personality_{i}",
                    placeholder="Select traits...",
                    accept_new_options=True
                )
                
                roles = ["Protagonist", "Antagonist", "Sidekick", "Mentor", "Catalyst"]
                st.selectbox("Role", options=roles, key=f"char_role_{i}")
        
        with STORYTABS[2]:
            st.title("Story Outlining")
            story_type = st.segmented_control("Choose Story Type", options=["Chapters", "Short Story"], 
                                            key="story_type_selector")
            
            # Store the story type in session state
            st.session_state["story_type"] = story_type
            
            if story_type == "Chapters":
                st.session_state["rough_plot_saved"] = False
                
                if st.button("Add Chapter"):
                    chapter_id = len(st.session_state["chapters"]) + 1
                    st.session_state["chapters"].append({
                        "title": f"Chapter {chapter_id}",
                        "outlines": []
                    })
                    st.rerun()
                
                for idx, chapter in enumerate(st.session_state["chapters"]):
                    st.subheader(chapter["title"])
                    chapter["title"] = st.text_input("Chapter Title", value=chapter["title"], key=f"title_{idx}")
                    if st.button(f"Add Outline to {chapter['title']}", key=f"add_outline_{idx}"):
                        if "outlines" not in chapter:
                            chapter["outlines"] = []
                        chapter["outlines"].append(f"New Outline {len(chapter['outlines']) + 1}")
                        st.rerun()
                    
                    # Ensure outlines list exists
                    if "outlines" not in chapter:
                        chapter["outlines"] = []
                    
                    for o_idx, outline in enumerate(chapter["outlines"]):
                        cols = st.columns([4, 1])
                        with cols[0]:
                            chapter["outlines"][o_idx] = st.text_input(
                                "Outline", value=outline, key=f"outline_{idx}_{o_idx}"
                            )
                        with cols[1]:
                            if st.button("Delete", key=f"delete_{idx}_{o_idx}"):
                                chapter["outlines"].pop(o_idx)
                                st.rerun()
                
                if st.session_state["chapters"]:
                    st.success(f"✅ You have {len(st.session_state['chapters'])} chapter(s) with outlines ready!")
            
            elif story_type == "Short Story":
                st.header("Please enter the rough plot of your story")
                rough_plot = st.text_area("Rough Plot", key="rough_plot", height=200,
                                         placeholder="Describe your entire story plot here...")
                
                if st.button("Save Rough Plot"):
                    if rough_plot.strip():
                        st.session_state["chapters"] = [{
                            "title": "Short Story",
                            "outlines": [rough_plot.strip()]
                        }]
                        st.session_state["rough_plot_saved"] = True
                        st.success("✅ Rough plot saved! Now click 'Create the story' to generate.")
                        st.info("Your story outline has been saved. Go to the 'Final Story' tab to generate your story.")
                    else:
                        st.error("Please enter some text for your rough plot")
                
                if st.session_state.get("rough_plot_saved"):
                    st.success("✅ Rough plot saved and ready for story generation!")
        
        with STORYTABS[3]:
            st.header("Generation")
            st.write("Use AI to create the story")
            words_per_chapter = st.slider("Enter the amount of words per chapter", 300, 2000, 500)
            
            # Show current chapter status
            if st.session_state["chapters"]:
                st.info(f"📚 You have {len(st.session_state['chapters'])} chapter(s) ready for generation")
                for i, chapter in enumerate(st.session_state["chapters"]):
                    outline_count = len(chapter.get("outlines", []))
                    valid_outlines = sum(1 for outline in chapter.get("outlines", []) if outline.strip())
                    status = "✅" if valid_outlines > 0 else "❌"
                    st.write(f"{status} {chapter['title']}: {valid_outlines} valid outline(s)")
            
            if st.button("Create the story", type="primary"):
                is_valid, error_message = validate_story_data(title, st.session_state["chapters"], st.session_state["story_type"])
                
                if not is_valid:
                    st.error(error_message)
                else:
                    with st.spinner("Please wait... This will take a while..."):
                        story_info = {
                            "title": title,
                            "type": book_type,
                            "summary": summarised,
                            "characters": [
                                {
                                    "name": st.session_state.get(f"char_name_{i}", ""),
                                    "role": st.session_state.get(f"char_role_{i}", ""),
                                    "age": st.session_state.get(f"char_age_{i}", ""),
                                    "traits": st.session_state.get(f"char_personality_{i}", []),
                                    "goal": st.session_state.get(f"char_goal_{i}", ""),
                                    "problem": st.session_state.get(f"char_problem_{i}", ""),
                                    "backstory": st.session_state.get(f"char_backstory_{i}", "")
                                }
                                for i in range(1, st.session_state["num_characters"] + 1)
                            ],
                            "chapters": [
                                {
                                    "title": chapter["title"],
                                    "outlines": chapter.get("outlines", []),
                                    "generated_text": chapter.get("generated_text", "")
                                }
                                for chapter in st.session_state.get("chapters", [])
                            ]
                        }
                        
                        full_story = generate_full_story(story_info, words_per_chapter=words_per_chapter)
                        if full_story:
                            st.session_state["generated_story"] = full_story
                            
                            with st.spinner("Rating your story..."):
                                rating = rate_story(full_story, title, book_type)
                                st.session_state["story_rating"] = rating
                            
                            st.subheader("Generated Story")
                            st.markdown(full_story)
                            st.markdown("---")
                            display_rating(rating)
                            
                            # Add download button
                            st.download_button(
                                label="📥 Download Story",
                                data=full_story,
                                file_name=f"{title.replace(' ', '_')}.txt",
                                mime="text/plain"
                            )
                        else:
                            st.error("Failed to generate story. Please try again.")
        
        with STORYTABS[4]:
            st.header("Save & Manage Your Story")
            
            if st.session_state.get("generated_story"):
                st.success("✅ Your story has been generated and is ready to save!")
                if st.session_state.get("story_rating"):
                    display_rating(st.session_state["story_rating"])
            
            if st.button("💾 Save Story", type="primary"):
                if "user_id" not in st.session_state:
                    st.error("No user ID found. Please log in again.")
                elif not title.strip():
                    st.error("Please enter a title.")
                elif not st.session_state.get("generated_story"):
                    st.error("Please generate your story first in the 'Final Story' tab.")
                else:
                    characters = []
                    for i in range(1, st.session_state["num_characters"] + 1):
                        characters.append({
                            "name": st.session_state.get(f"char_name_{i}", ""),
                            "role": st.session_state.get(f"char_role_{i}", ""),
                            "age": st.session_state.get(f"char_age_{i}", ""),
                            "traits": st.session_state.get(f"char_personality_{i}", []),
                            "goal": st.session_state.get(f"char_goal_{i}", ""),
                            "problem": st.session_state.get(f"char_problem_{i}", ""),
                            "backstory": st.session_state.get(f"char_backstory_{i}", "")
                        })
                    
                    story_data = create_story(
                        st.session_state["user_id"],
                        title,
                        book_type,
                        summarised,
                        st.session_state["chapters"],
                        characters,
                        st.session_state.get("generated_story", ""),
                        st.session_state.get("story_rating")
                    )

                    if story_data:
                        st.success("Story saved successfully!")
                        all_stories = get_all_stories()
                        current_story_id = story_data[0]["id"] if story_data else None
                        rankings = get_story_rankings()
                        
                        if current_story_id and rankings:
                            rank = next((i+1 for i, story in enumerate(rankings) if story["id"] == current_story_id), len(all_stories) + 1)
                            display_rating(st.session_state["story_rating"], rank, len(all_stories))
                        
                        # Reset for new story
                        st.session_state["chapters"] = []
                        st.session_state["generated_story"] = ""
                        st.session_state["story_rating"] = None
                        st.session_state["story_type"] = "Chapters"
                        st.session_state["rough_plot_saved"] = False
                        st.rerun()
                    else:
                        st.error("Failed to save story. Please try again.")

            # Add reset button
            if st.button("🔄 Start New Story"):
                st.session_state["chapters"] = []
                st.session_state["generated_story"] = ""
                st.session_state["story_rating"] = None
                st.session_state["story_type"] = "Chapters"
                st.session_state["rough_plot_saved"] = False
                st.success("Ready to create a new story!")
                st.rerun()

elif page == "Dashboard":
    if not st.session_state.get("SIGNED_IN", False):
        st.warning("You are not logged in")
        st.caption("Please login or create an account to access this page")
    else:
        stories = get_stories(st.session_state["user_id"])
        st.session_state["stories"] = stories
        all_stories = get_all_stories()
        rankings = get_story_rankings()

        editing = st.session_state.get("current_story_id") is not None

        if not editing:
            st.header(" Your Stories")
            
            # Show user's best ranking
            user_stories_with_rank = []
            for story in stories:
                rank = next((i+1 for i, s in enumerate(rankings) if s["id"] == story["id"]), len(all_stories) + 1)
                user_stories_with_rank.append((story, rank))
            
            # Handle None ratings by converting to 0
            user_stories_with_rank.sort(key=lambda x: x[0].get("rating", 0) or 0, reverse=True)
            
            if not stories:
                if not stories:
                    st.info("""
                    🎈 **Welcome to your Dashboard!**
                    
                    It looks like you haven't created any stories yet. Here's how to get started:
                    
                    1. **Click on "Create Story"** in the sidebar
                    2. **Fill in your story details** - title, type, and summary
                    3. **Develop your characters** - give them personalities and goals  
                    4. **Outline your plot** - use chapters or a short story format
                    5. **Generate your story** - let AI bring your creation to life!
                    6. **Save and share** - rate your story and see how it ranks
                    
                    Your first amazing story is just a few clicks away! ✨
                    """)
            else:
                for story, rank in user_stories_with_rank:
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.subheader(story["title"])
                            st.write(f"**Type:** {story['book_type']}")
                            st.write(f"**Summary:** {story['summary']}")
                            
                            if story.get("rating") is not None:
                                display_rating(story["rating"], rank, len(all_stories))
                            else:
                                st.info("⭐ Rating: Not yet rated")
                        
                        with col2:
                            st.caption(f"ID: {story['id']}")
                            st.caption(f"Rank: #{rank}")
                            if story.get('created_at'):
                                st.caption(f"Created: {story.get('created_at')[:10]}")
                            else:
                                st.caption("Created: N/A")
                        
                        # Display full story if available
                        if story.get("full_story"):
                            with st.expander("View Full Story"):
                                st.text_area("Full Story", story["full_story"], height=300, key=f"story_{story['id']}")

                        chapters = story.get("chapters", [])
                        if chapters:
                            with st.expander("View Chapters"):
                                for c_idx, chapter in enumerate(chapters):
                                    st.markdown(f"**Chapter {c_idx+1}: {chapter['title']}**")
                                    outlines = chapter.get("outlines", [])
                                    for o_idx, outline in enumerate(outlines):
                                        st.write(f"- {outline}")
                        
                        # Audio book conversion
                        if st.button("Convert to Audio Book", key=f"audio_{story['id']}"):
                            if story.get("full_story"):
                                title = story.get("title", "Untitled")
                                full_story = story.get("full_story")
                                text = f"{title}. {full_story}"

                                # Split text into chunks (~200 chars)
                                chunks = textwrap.wrap(text, 200)

                                # Combine all chunks into one MP3 in memory
                                combined_audio = io.BytesIO()
                                for chunk in chunks:
                                    tts = gTTS(text=chunk, lang='en')
                                    tmp_audio = io.BytesIO()
                                    tts.write_to_fp(tmp_audio)
                                    tmp_audio.seek(0)
                                    combined_audio.write(tmp_audio.read())

                                combined_audio.seek(0)

                                st.success("✅ Audio book generated successfully!")
                                st.audio(combined_audio, format="audio/mp3")
                                st.download_button(
                                    label="💾 Download Full Audiobook",
                                    data=combined_audio,
                                    file_name=f"{title}-audiobook.mp3",
                                    mime="audio/mp3",
                                    key=f"download_audio_{story['id']}"
                                )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Edit '{story['title']}'", key=f"edit_{story['id']}"):
                                st.session_state["current_story_id"] = story["id"]
                                st.session_state["title"] = story["title"]
                                st.session_state["book_type"] = story["book_type"]
                                st.session_state["summary"] = story["summary"]
                                st.session_state["chapters"] = story.get("chapters", [])
                                st.session_state["generated_story"] = story.get("full_story", "")
                                st.session_state["story_rating"] = story.get("rating")
                                
                                if story.get("characters"):
                                    st.session_state["num_characters"] = len(story["characters"])
                                else:
                                    st.session_state["num_characters"] = 1
                                    
                                st.rerun()
                        with col2:
                            if st.button(f"Delete '{story['title']}'", key=f"delete_{story['id']}"):
                                try:
                                    supabase1.table("stories").delete().eq("id", story["id"]).execute()
                                    st.success(f"Story '{story['title']}' deleted.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting story: {e}")
        else:
            # EDITING MODE - Full Dashboard editing interface
            st.header(f"Editing: {st.session_state.get('title', 'Untitled Story')}")
            flstabs = ["Details", "Characters", "Outlining", "Full Story AI", "Save"]
            STORYTABS = st.tabs(flstabs)
            
            with STORYTABS[0]:
                title = st.text_input("Write the name of your story", 
                                    value=st.session_state.get("title", ""),
                                    help="Enter the title for your story")
                books_type = ['Fiction', 'Non-fiction']
                current_type = st.session_state.get("book_type", "Fiction")
                book_type = st.radio('Type', books_type, 
                                    index=0 if current_type == "Fiction" else 1,
                                    help="Choose if your book is fiction or non-fiction")
                summarised = st.text_area("Write a background/summary for your story",
                                        value=st.session_state.get("summary", ""),
                                        help="Give a short one line description of your story.")
            
            with STORYTABS[1]:
                st.subheader("Characters")
                st.caption("Create and develop the important characters of your story")
                
                if "num_characters" not in st.session_state:
                    st.session_state["num_characters"] = 1
                
                num_characters = st.slider("Enter number of main characters", 
                                        min_value=1, max_value=40, 
                                        value=st.session_state["num_characters"],
                                        key="edit_num_chars")
                
                st.session_state["num_characters"] = num_characters
                
                current_story_id = st.session_state.get("current_story_id")
                story_data = None
                if current_story_id and "stories" in st.session_state:
                    for story in st.session_state["stories"]:
                        if story["id"] == current_story_id:
                            story_data = story
                            break
                
                for i in range(1, num_characters + 1):
                    st.markdown(f"**Character {i}**")
                    
                    char_data = {}
                    if (story_data and 
                        story_data.get("characters") and 
                        isinstance(story_data["characters"], list) and 
                        i <= len(story_data["characters"])):
                        char_data = story_data["characters"][i-1]
                    
                    st.text_input("Name", value=char_data.get("name", ""), key=f"edit_name_{i}")
                    st.text_input("Age", value=char_data.get("age", ""), key=f"edit_age_{i}")
                    st.text_input("Goal", value=char_data.get("goal", ""), key=f"edit_goal_{i}")
                    st.text_input("Problem", value=char_data.get("problem", ""), key=f"edit_problem_{i}")
                    st.text_area("Backstory", value=char_data.get("backstory", ""), key=f"edit_backstory_{i}")
                    
                    existing_traits = char_data.get("traits", [])
                    if not isinstance(existing_traits, list):
                        existing_traits = []
                    
                    valid_defaults = [trait for trait in existing_traits if trait in traits]
                    
                    st.multiselect(
                        "Personality Traits",
                        options=traits,
                        default=valid_defaults,
                        key=f"edit_personality_{i}",
                        accept_new_options=True
                    )
                    
                    role_options = ["Protagonist", "Antagonist", "Sidekick", "Mentor", "Catalyst"]
                    current_role = char_data.get("role", "Sidekick")
                    role_index = role_options.index(current_role) if current_role in role_options else 0
                    
                    st.selectbox(
                        "Role",
                        options=role_options,
                        index=role_index,
                        key=f"edit_role_{i}"
                    )

            with STORYTABS[2]:
                st.title("Story Outlining")
                
                # Initialize edit_story_type if not exists
                if "edit_story_type" not in st.session_state:
                    st.session_state.edit_story_type = "Chapters"
                
                # Use callback approach to handle story type changes
                def update_story_type():
                    st.session_state.edit_story_type = st.session_state.story_type_widget
                
                # Create the widget with callback
                story_type = st.segmented_control(
                    "Choose Story Type", 
                    options=["Chapters", "Short Story"], 
                    key="story_type_widget",
                    default=st.session_state.edit_story_type,
                    on_change=update_story_type
                )
                
                # Use the value from session state
                current_story_type = st.session_state.edit_story_type
                
                if current_story_type == "Chapters":
                    current_story_id = st.session_state.get("current_story_id")
                    if current_story_id and "stories" in st.session_state:
                        for story in st.session_state["stories"]:
                            if story["id"] == current_story_id:
                                if story.get("chapters") and isinstance(story["chapters"], list):
                                    if "chapters" not in st.session_state:
                                        st.session_state["chapters"] = story["chapters"]
                                break
                    
                    if "chapters" not in st.session_state:
                        st.session_state["chapters"] = []
                    
                    if st.button("Add Chapter", key="edit_add_chapter"):
                        chapter_id = len(st.session_state["chapters"]) + 1
                        st.session_state["chapters"].append({
                            "title": f"Chapter {chapter_id}",
                            "outlines": []
                        })
                        st.rerun()
                    
                    for idx, chapter in enumerate(st.session_state["chapters"]):
                        with st.expander(chapter.get("title", f"Chapter {idx + 1}"), expanded=False):
                            new_title = st.text_input(
                                "Chapter Title", 
                                value=chapter.get("title", f"Chapter {idx + 1}"), 
                                key=f"edit_title_{idx}"
                            )
                            if new_title != chapter.get("title"):
                                st.session_state["chapters"][idx]["title"] = new_title
                            
                            st.subheader("Outlines")
                            
                            if st.button("Add Outline", key=f"edit_add_outline_{idx}"):
                                if "outlines" not in st.session_state["chapters"][idx]:
                                    st.session_state["chapters"][idx]["outlines"] = []
                                st.session_state["chapters"][idx]["outlines"].append("")
                                st.rerun()
                            
                            if "outlines" in st.session_state["chapters"][idx]:
                                for o_idx, outline in enumerate(st.session_state["chapters"][idx]["outlines"]):
                                    col1, col2 = st.columns([5, 1])
                                    with col1:
                                        new_outline = st.text_input(
                                            f"Outline {o_idx + 1}",
                                            value=outline,
                                            key=f"edit_outline_{idx}_{o_idx}"
                                        )
                                        st.session_state["chapters"][idx]["outlines"][o_idx] = new_outline
                                    with col2:
                                        if st.button("🗑️", key=f"edit_delete_outline_{idx}_{o_idx}"):
                                            st.session_state["chapters"][idx]["outlines"].pop(o_idx)
                                            st.rerun()
                            
                            if st.button("Delete Chapter", key=f"edit_delete_chapter_{idx}"):
                                st.session_state["chapters"].pop(idx)
                                st.rerun()
                
                elif current_story_type == "Short Story":
                    st.header("Please enter the rough plot of your story")
                    
                    # Pre-fill with existing data if editing a short story
                    existing_plot = ""
                    if st.session_state.get("chapters") and len(st.session_state["chapters"]) == 1:
                        existing_chapter = st.session_state["chapters"][0]
                        if existing_chapter.get("outlines"):
                            existing_plot = existing_chapter["outlines"][0]
                    
                    rough_plot = st.text_area("Rough Plot", value=existing_plot, key="edit_rough_plot", height=200,
                                            placeholder="Describe your story here...")
                    
                    if st.button("Save Rough Plot", key="edit_save_rough_plot"):
                        if rough_plot.strip():
                            st.session_state["chapters"] = [{
                                "title": "Short Story",
                                "outlines": [rough_plot]
                            }]
                            st.success("✅ Rough plot saved! Now click 'Create the story' to generate.")
                        else:
                            st.error("Please enter some text for your rough plot")
            
            with STORYTABS[3]:
                st.header("Generation")
                st.write("Use AI to create the story")
                words_per_chapter = st.slider("Enter the amount of words per chapter", 300, 2000, 500, key="edit_words_slider")
                
                if st.button("Create the story", key="edit_create_story"):
                    if not title.strip():
                        st.error("Please enter a story title first")
                    elif not has_valid_chapters(st.session_state["chapters"]):
                        st.error("Please add at least one chapter with outlines")
                    else:
                        with st.spinner("Please wait... This will take a while..."):
                            story_info = {
                                "title": title,
                                "type": book_type,
                                "summary": summarised,
                                "characters": [
                                    {
                                        "name": st.session_state.get(f"edit_name_{i}", ""),
                                        "role": st.session_state.get(f"edit_role_{i}", ""),
                                        "age": st.session_state.get(f"edit_age_{i}", ""),
                                        "traits": st.session_state.get(f"edit_personality_{i}", []),
                                        "goal": st.session_state.get(f"edit_goal_{i}", ""),
                                        "problem": st.session_state.get(f"edit_problem_{i}", ""),
                                        "backstory": st.session_state.get(f"edit_backstory_{i}", "")
                                    }
                                    for i in range(1, st.session_state["num_characters"] + 1)
                                ],
                                "chapters": [
                                    {
                                        "title": chapter["title"],
                                        "outlines": chapter.get("outlines", []),
                                        "generated_text": chapter.get("generated_text", "")
                                    }
                                    for chapter in st.session_state.get("chapters", [])
                                ]
                            }
                            
                            full_story = generate_full_story(story_info, words_per_chapter=words_per_chapter)
                            
                            if full_story:
                                st.session_state["generated_story"] = full_story
                                st.success("✅ Story generated successfully!")
                                
                                with st.spinner("Rating your story..."):
                                    rating = rate_story(full_story, title, book_type)
                                    st.session_state["story_rating"] = rating
                                
                                st.subheader("📖 Your Generated Story")
                                with st.expander("View Full Story", expanded=True):
                                    st.text_area("Full Story Content", full_story, height=400, key="full_story_display")
                                
                                st.download_button(
                                    label="📥 Download Story as Text File",
                                    data=full_story,
                                    file_name=f"{title.replace(' ', '_')}.txt",
                                    mime="text/plain",
                                    key="edit_download_story"
                                )
                                
                                st.markdown("---")
                                display_rating(rating)
                            else:
                                st.error("❌ Failed to generate story. Please try again.")
            
            with STORYTABS[4]:
                st.header("💾 Save & Manage Your Story")
                if st.button("💾 Save Story to Database", type="primary", key="edit_save_final"):
                    if "user_id" not in st.session_state:
                        st.error("❌ No user ID found. Please log in again.")
                    elif not title.strip():
                        st.error("❌ Please enter a story title.")
                    else:
                        with st.spinner("Saving story..."):
                            characters = []
                            for i in range(1, st.session_state["num_characters"] + 1):
                                characters.append({
                                    "name": st.session_state.get(f"edit_name_{i}", ""),
                                    "role": st.session_state.get(f"edit_role_{i}", ""),
                                    "age": st.session_state.get(f"edit_age_{i}", ""),
                                    "traits": st.session_state.get(f"edit_personality_{i}", []),
                                    "goal": st.session_state.get(f"edit_goal_{i}", ""),
                                    "problem": st.session_state.get(f"edit_problem_{i}", ""),
                                    "backstory": st.session_state.get(f"edit_backstory_{i}", "")
                                })
                            
                            story_data = create_story(
                                st.session_state["user_id"],
                                title,
                                book_type,
                                summarised,
                                st.session_state["chapters"],
                                characters,
                                st.session_state.get("generated_story", ""),
                                st.session_state.get("story_rating")
                            )

                            if story_data:
                                st.success("🎉 Story saved successfully!")
                                all_stories = get_all_stories()
                                current_story_id = story_data[0]["id"] if story_data else None
                                rankings = get_story_rankings()
                                
                                if current_story_id and rankings:
                                    rank = next((i+1 for i, story in enumerate(rankings) if story["id"] == current_story_id), len(all_stories) + 1)
                                    display_rating(st.session_state["story_rating"], rank, len(all_stories))
                                
                                st.session_state["current_story_id"] = None
                                st.session_state["story_rating"] = None
                                # Clear edit-specific session states
                                if "edit_story_type" in st.session_state:
                                    del st.session_state["edit_story_type"]
                                st.rerun()
                            else:
                                st.error("❌ Failed to save story. Please check the console for errors.")
                
                if st.button("← Back to Dashboard", key="edit_back_to_dashboard"):
                    st.session_state["current_story_id"] = None
                    st.session_state["chapters"] = []
                    if "generated_story" in st.session_state:
                        del st.session_state["generated_story"]
                    if "edit_story_type" in st.session_state:
                        del st.session_state["edit_story_type"]
                    st.rerun()

elif page == "Leaderboard":
    st.title(" Story Leaderboard")
    st.subheader("Top 5 Stories by Rating")
    
    rankings = get_story_rankings()
    all_stories = get_all_stories()
    
    # Filter out stories with None ratings
    valid_rankings = [story for story in rankings if story.get("rating") is not None]
    
    if not valid_rankings:
        st.info("No rated stories yet! Create and rate stories to start the leaderboard.")
    else:
        for i, story in enumerate(valid_rankings):
            with st.container(border=True):
                col1, col2, col3 = st.columns([1, 3, 1])
                
                with col1:
                    st.markdown(f"## #{i+1}")
                    if i == 0:
                        st.markdown(" **First Place!**")
                    elif i == 1:
                        st.markdown(" **Second Place!**")
                    elif i == 2:
                        st.markdown(" **Third Place!**")
                
                with col2:
                    st.markdown(f"### {story['title']}")
                    st.write(f"**By User ID:** {story['user_id']}")
                    st.write(f"**Type:** {story['book_type']}")
                    if story.get("rating") is not None:
                        stars = "★" * int(story["rating"]) + "☆" * (10 - int(story["rating"]))
                        st.markdown(f"**Rating:** {story['rating']:.1f}/10")
                        st.markdown(f"**{stars}**")
                
                with col3:
                    if story.get("full_story"):
                        with st.expander("Read"):
                            st.text_area("Story", story["full_story"], height=200, key=f"leader_{story['id']}")
        
        st.markdown("---")
        st.subheader("Your Stories Ranking")
        
        if st.session_state.get("SIGNED_IN") and "user_id" in st.session_state:
            user_stories = get_stories(st.session_state["user_id"])
            rated_user_stories = [s for s in user_stories if s.get("rating") is not None]
            
            if rated_user_stories:
                user_best = max(rated_user_stories, key=lambda x: x.get("rating", 0) or 0)
                user_rank = next((i+1 for i, story in enumerate(valid_rankings) if story["id"] == user_best["id"]), len(all_stories) + 1)
                
                st.metric("Your Best Rating", f"{user_best.get('rating'):.1f}/10")
                st.metric("Your Best Rank", f"#{user_rank} of {len(all_stories)}")
                
                if user_rank <= 5:
                    st.success(" Congratulations! You're in the top 5!")
                    show_confetti()
                else:
                    st.info(f"Keep writing! You're {user_rank - 5} places away from the top 5!")
            else:
                st.info("You haven't created any rated stories yet!")
        else:
            st.warning("Please login to see your personal ranking")

elif page == "Explore":
    st.header("📚 Explore Stories")
    
    col1, col2 = st.columns(2)
    with col1:
        search_term = st.text_input("🔍 Search stories", placeholder="Title or author...")
    with col2:
        sort_by = st.selectbox("Sort by", ["Newest First", "Highest Rated", "Oldest First"])
    
    query = supabase1.table("stories").select(
        "id, title, summary, full_story, rating, created_at, book_type, users(first_name, last_name)"
    )
    
    if search_term:
        query = query.ilike("title", f"%{search_term}%")
    
    if sort_by == "Newest First":
        query = query.order("created_at", desc=True)
    elif sort_by == "Highest Rated":
        query = query.order("rating", desc=True)
    else:
        query = query.order("created_at", desc=False)
    
    try:
        response = query.execute()
        stories = response.data if response.data else []
    except Exception as e:
        st.error("Error loading stories")
        stories = []
    
    if not stories:
        st.info("No stories found")
    
    for story in stories:
        with st.expander(f"📖 {story['title']}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                user = story.get("users", {})
                st.write(f"**Author:** {user.get('first_name', '')} {user.get('last_name', '')}")
                st.write(f"**Type:** {story.get('book_type', 'N/A')}")
            with col2:
                rating = story.get('rating')
                if rating:
                    st.write(f"**Rating:** ⭐ {float(rating):.1f}/10")
                else:
                    st.write("**Rating:** Not rated")
            
            st.write(f"**Summary:** {story.get('summary', 'No summary available')}")
            
            if story.get("full_story"):
                word_count = len(story["full_story"].split())
                read_time = max(1, word_count // 200)
                
                st.write(f"**Length:** {word_count} words ({read_time} min read)")
                
                st.markdown("### 📖 Story Content")
                st.markdown(
                    f'<div style="height: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 15px; border-radius: 5px; background: #f9f9f9;">'
                    f'{story["full_story"]}'
                    f'</div>', 
                    unsafe_allow_html=True
                )
                
                st.download_button(
                    "📥 Download Story",
                    story["full_story"],
                    file_name=f"{story['title']}.txt",
                    mime="text/plain",
                    key=f"download_{story['id']}"
                )
            else:
                st.warning("No story content available")
        
        st.markdown("---")

elif page == "Home Page":
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("Storify! 📖")
            st.markdown("### Craft captivating stories with the click of a button")
            
            st.markdown("""
            Transform your **rough ideas** into **beautiful stories** with AI magic. 
            Whether you're writing fantasy, romance, sci-fi, or anything in between - 
            we help you create amazing stories in seconds.
            """)
            
            col1a, col1b = st.columns(2)
            with col1a:
                if st.button("✨ Start Creating", type="primary", use_container_width=True):
                    st.write("Please login to start creating or click on create story from the sidebar")
            with col1b:
                if st.button("Gallery", type="primary", use_container_width=True):
                    st.write("Click on the sidebar and use the Explore option")
        
        with col2:
            try:
                image = Image.open("image.png")
                st.image(image, width=400)
            except:
                st.info("✨ *Your app screenshot or hero image will appear here*")

    st.markdown("---")
    col1a, col1b = st.columns(2)
    with col1a:
        st.header("Watch this video for a tutorial")
        st.write("Detailed Overview")
        st.video("https://www.youtube.com/watch?v=iLNR4q-OIlg")
    st.markdown("---")
    st.markdown("**🎉 5,000+ stories created this week!**")
    st.markdown("**⭐ Loved by writers and dreamers**")

    st.header("How Storify! Works")
    col3, col4, col5 = st.columns(3)

    with col3:
        st.subheader("1. Inspire")
        st.markdown("💡 **Share your idea** - just a sentence or two is enough!")
        
    with col4:
        st.subheader("2. Create")  
        st.markdown("⚡ **Watch AI work** - generate unique stories in seconds")

    with col5:
        st.subheader("3. Enjoy")
        st.markdown("🎭 **Read, share, love** - your story is ready!")

elif page == "About the creator":
    st.header("About the creator")
    Information = """

**Ruhan Ahuja** - Young Innovator & Application Developer **(11 y/o)**

Specializing in **AI-driven creative tools**, Ruhan developed this story generation platform to **demonstrate the practical applications of natural language processing**. With a focus on user-friendly AI interfaces, this project represents the intersection of creative writing and machine learning technology.

This application is designed to **assist writers in overcoming creative blocks and exploring new narrative possibilities** through using AI to convert **rough ideas** into **beautiful stories**. He was inspired by his mother to create this app
"""
    col1, col2 = st.columns(2)
    with col1:
        st.write(Information)
    with col2:
        try:
            image = Image.open("RuhanAhuja.jpg")
            st.image(image)
        except:
            st.info("Profile image not found")
