import base64
import html
import re
import streamlit as st
import datetime
import pandas as pd
from pathlib import Path
import mimetypes
from helpers import *

# 1. PAGE CONFIGURATION & CUSTOM STYLING
st.set_page_config(
    page_title="RarityBarter",
    page_icon="💲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS matching clean UI design with badges and card containers
st.markdown("""
<style>
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"] {
        display: none;
    }
    .main-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding:10px 20px;
        background-color: #f8f9fa;
        border-radius: 10px;
        margin-bottom: 25px;
        border: 1px solid #e9ecef;
    }
    .credit-badge {
        background-color: #28a745;
        color: white;
        padding: 4px 16px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1rem;
        white-space: nowrap;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        line-height: 2;
        transform: translateY(-0.5rem);
    }
    .ai-box {
        background-color: #ffffff !important;
        border-left: 5px solid #007bff;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
    }
    .resource-card {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 18px;
        background-color: #ffffff;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .reward-banner {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 12px 16px;
        margin: 12px 0;
        border: 1px solid #9dd4aa;
        border-left: 5px solid #28a745;
        border-radius: 6px;
        background: #e8f7ed;
        color: #1c6338;
    }
    .reward-banner-label {
        font-size: 0.95rem;
        font-weight: 700;
    }
    .reward-banner-amount {
        font-size: 1.35rem;
        font-weight: 800;
        white-space: nowrap;
    }
    .home-quote {
    max-width: none !important;
    margin: 1.5rem 0 1.75rem !important;
    color: #263f37 !important;
    font-size: 4.5rem !important; /* Force exact large size */
    font-weight: 800 !important;
    line-height: 1.05 !important;
    }

    .home-quote-note {
        margin: -1rem 0 2rem !important;
        color: #68776f !important;
        font-size: 1.4rem !important;
    }
    div.st-key-home_contributor button,
    div.st-key-home_browse button {
        width: 100%;
        min-height: 3.25rem;
        padding: 0.7rem 1rem;
        white-space: normal;
        text-align: center;
        justify-content: center;
        align-items: center;
        line-height: 1.2;
        border-radius: 999px;
        font-weight: 700;
        transition: transform 160ms ease, box-shadow 160ms ease, background-color 160ms ease;
    }
    div.st-key-home_contributor button {
        background: #f1f8f3;
        color: #24563a;
        border: 1px solid #c7ddce;
    }
    div.st-key-home_browse button {
        background: #f2f6fb;
        color: #294c70;
        border: 1px solid #ccd9e7;
    }
    div.st-key-home_contributor button:hover {
        background: #e8f4ec;
        border-color: #9fc7ab;
        color: #1d4930;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(35, 80, 50, 0.12);
    }
    div.st-key-home_browse button:hover {
        background: #e9f0f8;
        border-color: #a9bfd6;
        color: #203f60;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(40, 70, 100, 0.12);
    }
    .home-artwork img {
    display: block;
    
    width: 80% !important;          /* Adjust percentage or px (e.g., 50%, 400px, 100%) */
    max-height: 350px !important;    /* Cap maximum height */
    object-fit: contain !important;  /* Keeps image proportions intact */
    
    /* Center horizontal: margin: 0 auto !important; */
    /* Left align:         margin: 0 auto 0 0 !important; */
    /* Right align:        margin: 0 0 0 auto !important; */
    
    margin: 30px auto 0 auto !important;     
    
    transform: translateY(0px) !important; /* Move up (-20px) or down (20px) */

    border-radius: 16px !important;
    }
    .status-verified {
        color: #28a745;
        font-weight: bold;
    }
    .status-reported {
        color: #dc3545;
        font-weight: bold;
    }
    .chat-bubble-ai {
        background-color: #e9ecef;
        padding: 10px 14px;
        border-radius: 12px;
        margin-bottom: 8px;
        border-bottom-left-radius: 2px;
    }
    .chat-bubble-user {
        background-color: #007bff;
        color: white;
        padding: 10px 14px;
        border-radius: 12px;
        margin-bottom: 8px;
        text-align: right;
        border-bottom-right-radius: 2px;
    }
    .user-chat-row {
        display: flex;
        justify-content: flex-end;
        align-items: flex-end;
        gap: 8px;
        margin: 8px 0;
    }
    .user-chat-row .chat-bubble-user {
        max-width: 78%;
        margin-bottom: 0;
    }
    .user-chat-avatar {
        width: 34px;
        height: 34px;
        flex: 0 0 34px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #dce8f2;
        color: #263c52;
    }
    .brand-title {
        color: #30313d;
        font-size: 2.35rem;
        font-weight: 700;
        line-height: 1;
        white-space: nowrap;
    }
    .brand-lockup {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        width: max-content;
    }
    .brand-logo {
        display: block;
        width: 78px;
        height: 78px;
        object-fit: contain;
    }
    div.st-key-profile_navigation > div {
        display: flex;
        justify-content: flex-end;
        transform: translateX(-2rem);
    }
    div.st-key-profile_navigation button {
        width: 3rem !important;
        min-width: 3rem !important;
        max-width: 3rem !important;
        height: 3rem !important;
        min-height: 3rem !important;
        max-height: 3rem !important;
        padding: 0 !important;
        border-radius: 50% !important;
    }
    div.st-key-contributor_chat_composer {
        position: fixed;
        right: 2rem;
        bottom: 2rem;
        left: auto;
        width: min(360px, calc(100vw - 4rem));
        box-sizing: border-box;
        z-index: 1000;
        padding: 0;
        background: transparent;
    }
    div.st-key-contributor_chat_composer [data-testid="stChatInput"] {
        border: none !important;
        border-radius: 28px;
        background-color: #ffffff !important;
        box-shadow: 0 6px 10px rgba(0, 0, 0, 0.12) !important;
    }
    div.st-key-user_chat_composer_expanded,
    div.st-key-user_chat_composer_collapsed {
        position: fixed;
        right: 9vw;
        bottom: 1rem;
        box-sizing: border-box;
        z-index: 1001;
        padding: 0.35rem 0.65rem;
        border: 1px solid #e1e5e3;
        border-radius: 10px;
        background: #ffffff;
        box-shadow: 0 6px 20px -10px rgba(0, 0, 0, 0.18);
    }
    div.st-key-user_chat_composer_expanded {
        width: 50vw;
    }
    div.st-key-user_chat_composer_collapsed {
        width: 83vw;
    }
    div.st-key-user_chat_composer_expanded [data-testid="stChatInput"],
    div.st-key-user_chat_composer_collapsed [data-testid="stChatInput"] {
        width: 100%;
        box-sizing: border-box;
        border: none !important;
        border-radius: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
    }
    div.st-key-user_chat_composer_expanded [data-testid="stChatInput"] [data-baseweb="textarea"],
    div.st-key-user_chat_composer_collapsed [data-testid="stChatInput"] [data-baseweb="textarea"],
    div.st-key-user_chat_composer_expanded [data-testid="stChatInput"] [data-baseweb="textarea"] > div,
    div.st-key-user_chat_composer_collapsed [data-testid="stChatInput"] [data-baseweb="textarea"] > div,
    div.st-key-user_chat_composer_expanded [data-testid="stChatInput"] textarea,
    div.st-key-user_chat_composer_collapsed [data-testid="stChatInput"] textarea {
        border: none !important;
        border-radius: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
        outline: none !important;
    }
    div.st-key-user_chat_composer_expanded [data-testid="stSelectbox"] > div > div,
    div.st-key-user_chat_composer_collapsed [data-testid="stSelectbox"] > div > div {
        border-color: #e1e5e3 !important;
        border-radius: 20px !important;
        background: #f6f8f7 !important;
        overflow: hidden !important;
    }
    div.st-key-user_chat_composer_expanded [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    div.st-key-user_chat_composer_collapsed [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        border-radius: 20px !important;
        background: #f6f8f7 !important;
    }
    div.st-key-app_header {
        width: calc(100vw - 160px) !important;
        max-width: none !important;
        box-sizing: border-box;
    }
    div.st-key-app_header > div[data-testid="stLayoutWrapper"] > div[data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: minmax(280px, 1fr) auto auto 48px !important;
        gap: 1rem !important;
        align-items: center !important;
    }
    div.st-key-app_header > div[data-testid="stLayoutWrapper"] > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        width: auto !important;
        min-width: 0 !important;
        flex: none !important;
    }
    div[data-testid="stLayoutWrapper"]:has(> div.st-key-resource_feed_items) {
        height: max(80px, calc(100vh - 20rem)) !important;
        flex: 0 0 auto !important;
    }
    div.st-key-resource_feed_items {
        height: 100% !important;
        flex: 1 1 auto !important;
        overflow-y: auto;
    }
    div[data-testid="stLayoutWrapper"]:has(> div.st-key-search_chat_history) {
        height: max(120px, calc(100vh - 28rem)) !important;
        flex: 0 0 auto !important;
    }
    div.st-key-search_chat_history {
        height: 100% !important;
        flex: 1 1 auto !important;
        overflow-y: auto;
    }
    @media (max-width: 768px) {
        div.st-key-user_chat_composer_expanded,
        div.st-key-user_chat_composer_collapsed {
            right: 1rem;
            left: 1rem;
            width: auto;
        }
    }
    @media (max-width: 800px) {
        div.st-key-app_header {
            width: calc(100vw - 2rem) !important;
        }
        div.st-key-app_header > div[data-testid="stLayoutWrapper"] > div[data-testid="stHorizontalBlock"] {
            grid-template-columns: minmax(0, 1fr) auto 48px !important;
            gap: 0.5rem !important;
        }
        div.st-key-app_header > div[data-testid="stLayoutWrapper"] > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) {
            grid-column: 1;
            grid-row: 1;
        }
        div.st-key-app_header > div[data-testid="stLayoutWrapper"] > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) {
            grid-column: 1 / -1;
            grid-row: 2;
            justify-self: end;
        }
        div.st-key-app_header > div[data-testid="stLayoutWrapper"] > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) {
            grid-column: 2;
            grid-row: 1;
        }
        div.st-key-app_header > div[data-testid="stLayoutWrapper"] > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(4) {
            grid-column: 3;
            grid-row: 1;
        }
    }
    div[class*="st-key-answer_button_"] button {
        background-color: #28a745 !important; /* Change background color */
        border-color: #28a745 !important;     /* Change border color */
        color: #ffffff !important;            /* Text color */
    }

    div[class*="st-key-answer_button_"] button:hover {
        background-color: #218838 !important; /* Darker green on hover */
        border-color: #1e7e34 !important;
        color: #ffffff !important;
    }
    div[class*="st-key-page_navigation_"] button {
        background-color: transparent !important;
        color: #343a40 !important;
        border: none !important;
        border-bottom: 3px solid transparent !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        font-size: 1rem !important;
        min-height: 3.25rem !important;
        padding: 0.5rem 0.75rem 0.6rem !important;
    }
    div[class*="st-key-page_navigation_"] button:hover,
    div[class*="st-key-page_navigation_"] button[kind="primary"] {
        background-color: transparent !important;
        color: #6c757d !important;
        border-bottom-color: #6c757d !important;
    }
    div[class*="st-key-contributor_submit"] button[kind="primary"] {
        background-color: #28a745;
        border-color: #28a745;
        color: #ffffff;
    }
    div[class*="st-key-contributor_submit"] button[kind="primary"]:hover {
        background-color: #218838;
        border-color: #1e7e34;
    }
    div[class*="st-key-download_"] button {
        background-color: #0d6efd;
        border-color: #0d6efd;
        color: #ffffff;
    }
    div[class*="st-key-download_"] button:hover {
        background-color: #0b5ed7;
        border-color: #0a58ca;
        color: #ffffff;
    }
    div[class*="st-key-unlock_"] button {
        background-color: #28a745;
        border-color: #28a745;
        color: #ffffff;
    }
    div[class*="st-key-unlock_"] button:hover {
        background-color: #218838;
        border-color: #1e7e34;
        color: #ffffff;
    }
    div[class*="st-key-hide_resource_panel"] button,
    div[class*="st-key-show_resource_panel"] button {
        min-height: 60px;
    }
</style>
""", unsafe_allow_html=True)

# 2. SESSION STATE INITIALIZATION
if "user" not in st.session_state:
    st.session_state.user = {
        "name": "Alex Leung",
        "credits": 110,
        "reputation": 95,
        "contributions_count": 3
    }

if "contributions" not in st.session_state:
    st.session_state.contributions = [

        {
            "id": 101,
            "title": "Family Apple Pudding Recipe",
            "type": "Image",
            "category": "Family Secret Food Recipes",
            "description": (
                "A handwritten family apple pudding recipe preserved as a recipe card. "
                "The recipe contains the family's traditional ingredient proportions and "
                "preparation notes, making it a useful example of niche household cooking knowledge."
            ),
            "cultural": True,
            "credits_cost": 15,
            "estimated_value": 32,
            "contributor_id": "KitchenMemory",
            "contributor_rep": 94,
            "likes": 36,
            "dislikes": 1,
            "status": "Verified",
            "unlocked_by": [],
            "content": "Handwritten family apple pudding recipe card.",
            "download_file": "apple_pudding_recipe.png"
        },
        {
            "id": 102,
            "title": "Grandma Rozie's Pot Roast • Tina Barry",
            "type": "Image",
            "category": "Family Secret Food Recipes",
            "description": (
                "A treasured family pot roast recipe passed from Roz Ehlin to her "
                "daughter Tina Barry and later to the next generation. The recipe is "
                "associated with handwritten family traditions, memories around the "
                "dinner table, and a cooking style based on experience rather than "
                "precise measurements."
            ),
            "cultural": True,
            "credits_cost": 25,
            "estimated_value": 55,
            "contributor_id": "TinaBarry",
            "contributor_rep": 97,
            "likes": 63,
            "dislikes": 1,
            "status": "Verified",
            "unlocked_by": [],
            "content": "Grandma Rozie's Pot Roast family recipe image.",
            "download_file": "Rozie's Pot Roast.webp"
        },
        {
            "id": 103,
            "title": "Chinese Braised Pork Bone Recipe",
            "type": "Image",
            "category": "Family Secret Food Recipes",
            "description": (
                "A clear, neatly handwritten master recipe for Braised Bones (滷大骨). "
                "The recipe records traditional Chinese aromatic spices including "
                "liquorice, star anise, cloves, and dried tangerine peel, together with "
                "precise gram measurements and cooking times."
            ),
            "cultural": True,
            "credits_cost": 22,
            "estimated_value": 48,
            "contributor_id": "OldKitchenArchive",
            "contributor_rep": 95,
            "likes": 47,
            "dislikes": 0,
            "status": "Verified",
            "unlocked_by": [],
            "content": "Chinese braised pork bone recipe image.",
            "download_file": "Pork Bone Recipe.png"
        },

        # FAMILY SECRET FOOD RECIPES
        {
            "id": 104,
            "title": "Grandmother's Kowloon-Style Preserved Plum Chicken",
            "type": "Text",
            "category": "Family Secret Food Recipes",
            "description": (
                "A three-generation family recipe for chicken cooked with preserved "
                "plums, ginger, and a sweet-sour sauce. The contributor documents the "
                "family's preferred balance between salty, sour, and sweet flavours."
            ),
            "cultural": True,
            "credits_cost": 18,
            "estimated_value": 38,
            "contributor_id": "KitchenArchive",
            "contributor_rep": 96,
            "likes": 42,
            "dislikes": 1,
            "status": "Verified",
            "unlocked_by": [],
            "content": (
                "📄 Demo family recipe archive\n\n"
                "Main ingredients: chicken thighs, preserved plum, ginger, "
                "light soy sauce, sugar, rice wine.\n\n"
                "Family technique: crush the preserved plum before adding it "
                "to the sauce and simmer slowly rather than boiling strongly."
            )
        },

        {
            "id": 105,
            "title": "Four-Generation Hakka Yellow Rice Wine Chicken Recipe",
            "type": "Text",
            "category": "Family Secret Food Recipes",
            "description": (
                "A family recipe adapted from a New Territories Hakka household. "
                "The notes explain how yellow rice wine was traditionally used in "
                "home cooking and how the family adjusted the recipe for modern kitchens."
            ),
            "cultural": True,
            "credits_cost": 24,
            "estimated_value": 48,
            "contributor_id": "HakkaKitchen",
            "contributor_rep": 98,
            "likes": 51,
            "dislikes": 0,
            "status": "Verified",
            "unlocked_by": [],
            "content": (
                "📄 Demo Hakka recipe archive\n\n"
                "Traditional ingredients include chicken, ginger, sesame oil, "
                "and homemade yellow rice wine.\n\n"
                "Family note: ginger is fried until fragrant before the chicken "
                "is added, and the wine is added gradually."
            )
        },

        {
            "id": 106,
            "title": "Old Kowloon Family Recipe for Preserved Olive Rice",
            "type": "Image",
            "category": "Family Secret Food Recipes",
            "description": (
                "A scanned handwritten recipe card from a Kowloon household. "
                "The recipe combines preserved olives, rice, minced pork, and "
                "seasonal vegetables. The original card contains handwritten "
                "measurements rather than standardized quantities."
            ),
            "cultural": True,
            "credits_cost": 16,
            "estimated_value": 34,
            "contributor_id": "RecipeMemory",
            "contributor_rep": 93,
            "likes": 29,
            "dislikes": 1,
            "status": "Verified",
            "unlocked_by": [],
            "content": (
                "🖼️ Demo scanned recipe card\n"
                "[Preserved_Olive_Rice_Family_Card.jpg]\n\n"
                "Includes handwritten preparation notes and substitutions."
            )
        },

        {
            "id": 107,
            "title": "Family Recipe for Lunar New Year Poon Choi Sauce",
            "type": "Text",
            "category": "Family Secret Food Recipes",
            "description": (
                "A household version of a festive Poon Choi sauce recorded by "
                "a family that has prepared large communal meals for Lunar New Year "
                "for decades."
            ),
            "cultural": True,
            "credits_cost": 26,
            "estimated_value": 52,
            "contributor_id": "VillageTable",
            "contributor_rep": 97,
            "likes": 45,
            "dislikes": 0,
            "status": "Verified",
            "unlocked_by": [],
            "content": (
                "📄 Demo family cooking notes\n\n"
                "The family version uses fermented bean curd, dried seafood, "
                "mushrooms, and a long simmering process.\n\n"
                "Important family note: the sauce is prepared separately before "
                "the ingredients are layered."
            )
        },

        {
            "id": 108,
            "title": "Three-Generation Cantonese Red Bean Curd Pork Recipe",
            "type": "Image",
            "category": "Family Secret Food Recipes",
            "description": (
                "A photographed recipe notebook documenting a family method for "
                "marinating pork with fermented red bean curd. The notebook includes "
                "notes about marinating time and how the recipe changes during winter."
            ),
            "cultural": True,
            "credits_cost": 20,
            "estimated_value": 41,
            "contributor_id": "OldKitchenHK",
            "contributor_rep": 95,
            "likes": 37,
            "dislikes": 1,
            "status": "Verified",
            "unlocked_by": [],
            "content": (
                "🖼️ Demo recipe notebook\n"
                "[Red_Bean_Curd_Pork_Notebook.jpg]\n\n"
                "Includes handwritten family annotations and cooking photographs."
            )
        },

        # OBSOLETE HARDWARE REPAIR TECHNIQUES
        {
            "id": 109,
            "title": "1980s Cassette Player Belt Replacement Technique",
            "type": "Text",
            "category": "Obsolete Hardware Repair Techniques",
            "description": (
                "A hobbyist's repair notes explaining how to diagnose a slipping "
                "or deteriorated drive belt in an older cassette player, including "
                "symptoms, belt routing, and cleaning steps."
            ),
            "cultural": False,
            "credits_cost": 22,
            "estimated_value": 46,
            "contributor_id": "RetroRepair",
            "contributor_rep": 98,
            "likes": 48,
            "dislikes": 0,
            "status": "Verified",
            "unlocked_by": [],
            "content": (
                "📄 Demo repair manual\n\n"
                "Symptoms:\n"
                "- Slow playback\n"
                "- Tape transport stops\n"
                "- Motor spins but cassette does not move\n\n"
                "Technique:\n"
                "Inspect the old belt, clean degraded rubber residue, "
                "and install the replacement following the original belt path."
            )
        },

        {
            "id": 110,
            "title": "Vintage Cassette Deck Pinch Roller Restoration Notes",
            "type": "Video",
            "category": "Obsolete Hardware Repair Techniques",
            "description": (
                "A restoration video showing how an experienced repair hobbyist "
                "diagnoses hardened, glazed, or uneven pinch rollers in vintage "
                "cassette decks."
            ),
            "cultural": False,
            "credits_cost": 25,
            "estimated_value": 51,
            "contributor_id": "TapeMechanic",
            "contributor_rep": 99,
            "likes": 54,
            "dislikes": 0,
            "status": "Verified",
            "unlocked_by": [],
            "content": (
                "🎥 Demo repair video\n"
                "[Pinch_Roller_Restoration.mp4]\n\n"
                "Shows inspection, cleaning, replacement, and tape-path testing."
            )
        },

        {
            "id": 111,
            "title": "1980s Walkman Sticky Belt and Gear Repair Guide",
            "type": "Text",
            "category": "Obsolete Hardware Repair Techniques",
            "description": (
                "A detailed repair log for an old portable cassette player. "
                "The contributor documents belt deterioration, sticky residue, "
                "gear inspection, and safe disassembly order."
            ),
            "cultural": False,
            "credits_cost": 24,
            "estimated_value": 49,
            "contributor_id": "WalkmanRestorer",
            "contributor_rep": 97,
            "likes": 41,
            "dislikes": 1,
            "status": "Verified",
            "unlocked_by": [],
            "content": (
                "📄 Demo Walkman repair guide\n\n"
                "Common symptoms:\n"
                "- Motor runs but tape does not move\n"
                "- Fast-forward becomes weak\n"
                "- Black sticky residue inside mechanism\n\n"
                "Repair notes include belt routing diagrams and gear inspection."
            )
        },

        {
            "id": 112,
            "title": "Old VCR Tape Transport Cleaning and Idler Repair",
            "type": "Video",
            "category": "Obsolete Hardware Repair Techniques",
            "description": (
                "A restoration guide documenting the cleaning of capstan shafts, "
                "pinch rollers, guide rollers, and idler components in an older VCR."
            ),
            "cultural": False,
            "credits_cost": 27,
            "estimated_value": 54,
            "contributor_id": "AnalogWorkshop",
            "contributor_rep": 96,
            "likes": 39,
            "dislikes": 0,
            "status": "Verified",
            "unlocked_by": [],
            "content": (
                "🎥 Demo VCR restoration video\n"
                "[VCR_Tape_Transport_Repair.mp4]\n\n"
                "Covers tape-path inspection, cleaning, idler inspection, "
                "and replacement of damaged rubber components."
            )
        },

        {
            "id": 113,
            "title": "Vintage Tape Recorder Speed Problem Diagnostic Chart",
            "type": "Image",
            "category": "Obsolete Hardware Repair Techniques",
            "description": (
                "A hand-drawn diagnostic chart created by a retired electronics "
                "hobbyist for identifying slow playback, wow and flutter, tape "
                "dragging, and motor-related problems in older tape recorders."
            ),
            "cultural": False,
            "credits_cost": 21,
            "estimated_value": 44,
            "contributor_id": "AnalogMemory",
            "contributor_rep": 94,
            "likes": 34,
            "dislikes": 0,
            "status": "Verified",
            "unlocked_by": [],
            "content": (
                "🖼️ Demo diagnostic chart\n"
                "[Vintage_Tape_Recorder_Diagnostic_Chart.png]\n\n"
                "Decision tree:\n"
                "Slow playback → inspect belt → inspect capstan → inspect "
                "pinch roller → inspect motor."
            )
        },
        # OLD BUILDINGS & HONG KONG URBAN HERITAGE
        {
            "id": 201,
            "title": "Graham Street Market, Central (嘉咸街街市) — Early 1900s",
            "type": "Image",
            "category": "Old Buildings & Urban Heritage",
            "description": (
                "A historical black-and-white photograph of Graham Street Market in "
                "Central, Hong Kong. The market has more than a century of history and "
                "the surrounding streets preserve memories of traditional shops, "
                "hawker stalls, food vendors, and everyday neighbourhood life."
            ),
            "cultural": True,
            "credits_cost": 20,
            "estimated_value": 45,
            "contributor_id": "HKMemoryArchive",
            "contributor_rep": 97,
            "likes": 52,
            "dislikes": 1,
            "status": "Verified",
            "unlocked_by": [],
            "content": "Graham Street Market historical photograph.",
            "download_file": "Graham Street Market.png"
        },

        {
            "id": 202,
            "title": "Chun Yeung Street Tram Market, North Point — 1969",
            "type": "Image",
            "category": "Old Buildings & Urban Heritage",
            "description": (
                "A vintage photograph showing a Hong Kong tram travelling directly "
                "through the busy Chun Yeung Street market in North Point. The scene "
                "captures the relationship between public transport, street markets, "
                "shopfronts, and everyday neighbourhood life in mid-20th-century Hong Kong."
            ),
            "cultural": True,
            "credits_cost": 22,
            "estimated_value": 49,
            "contributor_id": "NorthPointMemory",
            "contributor_rep": 96,
            "likes": 61,
            "dislikes": 0,
            "status": "Verified",
            "unlocked_by": [],
            "content": "Chun Yeung Street tram market historical photograph.",
            "download_file": "North Point.png"
        },

        {
            "id": 203,
            "title": "Mong Kok Neon Street Corridor (旺角街道與霓虹招牌) — Late 1970s",
            "type": "Image",
            "category": "Old Buildings & Urban Heritage",
            "description": (
                "A vibrant historical street photograph showing Mong Kok during the "
                "golden era of Hong Kong neon. Dense shopfronts, illuminated signs, "
                "pedestrians, and older urban buildings create a visual record of "
                "Hong Kong's late-1970s commercial streetscape."
            ),
            "cultural": True,
            "credits_cost": 24,
            "estimated_value": 53,
            "contributor_id": "NeonMemory",
            "contributor_rep": 98,
            "likes": 73,
            "dislikes": 1,
            "status": "Verified",
            "unlocked_by": [],
            "content": "Mong Kok neon street historical photograph.",
            "download_file": "mongkok.png"
        },

        {
            "id": 204,
            "title": "Old Tong Lau Streetscape, Yau Ma Tei / Mong Kok",
            "type": "Image",
            "category": "Old Buildings & Urban Heritage",
            "description": (
                "A photographic record of traditional Hong Kong tong lau, or Chinese "
                "tenement buildings, showing narrow streets, balconies, shopfronts, "
                "and dense mixed residential-commercial architecture. The resource "
                "documents the architectural character of old Kowloon neighbourhoods."
            ),
            "cultural": True,
            "credits_cost": 19,
            "estimated_value": 43,
            "contributor_id": "TongLauArchive",
            "contributor_rep": 95,
            "likes": 44,
            "dislikes": 1,
            "status": "Verified",
            "unlocked_by": [],
            "content": (
                "🖼️ Demo heritage photograph\n"
                "[old_tong_lau_yau_ma_tei.jpg]"
            )
        },

        {
            "id": 205,
            "title": "Blue House, Wan Chai — Historic Tong Lau",
            "type": "Image",
            "category": "Old Buildings & Urban Heritage",
            "description": (
                "A photographic record of the Blue House, a historic pre-war tong lau "
                "in Wan Chai. Built in 1922, the building represents traditional "
                "tenement architecture and the connection between historic buildings "
                "and community life in Hong Kong."
            ),
            "cultural": True,
            "credits_cost": 23,
            "estimated_value": 50,
            "contributor_id": "HeritageWalk",
            "contributor_rep": 99,
            "likes": 58,
            "dislikes": 0,
            "status": "Verified",
            "unlocked_by": [],
            "content": (
                "🖼️ Demo heritage photograph\n"
                "[blue_house_wan_chai.jpg]"
            )
        },
        # DAILY LIFE HACKS
        {
            "id": 301,
            "title": "The Ice Cube Dryer Steam De-Wrinkler",
            "type": "Text",
            "category": "Daily Life Hacks",
            "description": (
                "A practical laundry trick for reducing light wrinkles without using "
                "an ironing board. A few ice cubes are placed in a tumble dryer with "
                "the wrinkled clothes, creating moisture as they melt."
            ),
            "cultural": False,
            "credits_cost": 12,
            "estimated_value": 28,
            "contributor_id": "EverydayTricks",
            "contributor_rep": 91,
            "likes": 34,
            "dislikes": 2,
            "status": "Verified",
            "unlocked_by": [],
            "content": "Ice cube dryer steam de-wrinkler instructions.",
            "download_file": "ice_cube_dryer_steam_dewrinkler.txt"
        },
        {
            "id": 302,
            "title": "The Wet Paper Towel Cutting Board Stabilizer",
            "type": "Text",
            "category": "Daily Life Hacks",
            "description": (
                "A simple kitchen technique for reducing cutting-board movement on "
                "smooth countertops by placing a slightly damp paper towel or thin "
                "cloth underneath the board."
            ),
            "cultural": False,
            "credits_cost": 10,
            "estimated_value": 24,
            "contributor_id": "KitchenHacks",
            "contributor_rep": 94,
            "likes": 46,
            "dislikes": 1,
            "status": "Verified",
            "unlocked_by": [],
            "content": "Wet paper towel cutting board stabilizer instructions.",
            "download_file": "cutting_board_stabilizer.txt"
        },
        {
            "id": 303,
            "title": "The Baking Soda and Vinegar Sink Odor Trick",
            "type": "Text",
            "category": "Daily Life Hacks",
            "description": (
                "A common household method for dealing with unpleasant sink and drain "
                "odors using baking soda and white vinegar."
            ),
            "cultural": False,
            "credits_cost": 8,
            "estimated_value": 18,
            "contributor_id": "HomeFixer",
            "contributor_rep": 89,
            "likes": 31,
            "dislikes": 3,
            "status": "Community Reviewed",
            "unlocked_by": [],
            "content": (
                "Short tip: baking soda and white vinegar are commonly used together "
                "as a household drain-cleaning experiment. Detailed instructions "
                "available from the contributor."
            )
        },
        {
            "id": 304,
            "title": "The Out-of-Reach Alarm Clock Habit",
            "type": "Text",
            "category": "Daily Life Hacks",
            "description": (
                "A simple morning habit: place your alarm clock or phone far enough "
                "from the bed that you need to stand up and walk over to turn it off."
            ),
            "cultural": False,
            "credits_cost": 7,
            "estimated_value": 16,
            "contributor_id": "MorningRoutine",
            "contributor_rep": 92,
            "likes": 52,
            "dislikes": 2,
            "status": "Community Reviewed",
            "unlocked_by": [],
            "content": (
                "Short tip: place your alarm across the room so turning it off "
                "requires you to get out of bed."
            )
        },
        {
            "id": 305,
            "title": "The Cardboard Tube Cable Organizer",
            "type": "Text",
            "category": "Daily Life Hacks",
            "description": (
                "A low-cost cable organization method using empty cardboard toilet "
                "paper or paper towel tubes to separate and label charging cables, "
                "HDMI cables, and other wires."
            ),
            "cultural": False,
            "credits_cost": 6,
            "estimated_value": 14,
            "contributor_id": "DeskHacker",
            "contributor_rep": 90,
            "likes": 43,
            "dislikes": 1,
            "status": "Community Reviewed",
            "unlocked_by": [],
            "content": (
                "Short tip: place labelled cardboard tubes inside a box or drawer "
                "and store one cable in each tube."
            )
        },

    ]
if "contributor_chat" not in st.session_state:
    st.session_state.contributor_chat = [
        {"sender": "AI", "text": "Welcome to the Contributor AI Assistant! What type of niche resource are you uploading today?"}
    ]

if "user_chat" not in st.session_state:
    st.session_state.user_chat = [
        {"sender": "AI", "text": "Hello! Ask me to help you discover niche datasets, cultural archives, or research materials."}
    ]
if "user_actions" not in st.session_state:
    st.session_state.user_actions = {}
if "browse_filters" not in st.session_state:
    st.session_state.browse_filters = {
        "filter_type": "All",
        "search_query": st.session_state.get("user_search_query", ""),
        "sort_by": "newest"
    }
if "notifications" not in st.session_state:
    st.session_state.notifications = [
        {"icon": "❤️", "message": "A community member liked your Architectural Sketches post.", "time": "Today"},
        {"icon": "👎", "message": "A community member left a dislike on your post.", "time": "Yesterday"},
        {"icon": "🪙", "message": "15 credits used to unlock Architectural Sketches.", "time": "Yesterday"},
    ]
if "credit_history" not in st.session_state:
    st.session_state.credit_history = [
        {"description": "Starting wallet balance", "amount": 110, "time": "Today"}
    ]
if "answered_questions" not in st.session_state:
    st.session_state.answered_questions = []
if "questions" not in st.session_state:
    st.session_state.questions = [
        {
            "title": "What old Cantonese phrase did people use to describe extremely heavy rain?",
            "reward": 25,
            "asker": "HKMemory",
            "time": "8 min ago",
            "answers": 2,
            "responses": [
                {
                    "text": "My grandfather used to say 「落狗屎咁」 (lok gau si gam) when the rain was extremely heavy. He used it jokingly when the rain was coming down nonstop.",
                    "file": None
                },
                {
                    "text": (
                        "In my family we also used 「黃雨都唔夠喉」 as a joke when "
                        "someone complained about rain — basically meaning even "
                        "a yellow rainstorm warning would not describe how bad it was."
                    ),
                    "file": None
                },
            ],
        },
        {
            "title": "Does anyone remember the exact melody played by the old ice-cream vans in Hong Kong?",
            "reward": 30,
            "asker": "NostalgiaHunter",
            "time": "21 min ago",
            "answers": 2,
            "responses": [
                {
                    "text": "The van that came to our estate in the 1990s played a short melody that sounded like 「叮叮—叮叮叮—叮叮—叮」. The final notes were noticeably slower.",
                    "file": None
                },
                {
                    "text": "Our neighbourhood vendor had three quick high notes followed by two lower notes. We could recognise the van before seeing it.",
                    "file": None
                },
            ],
        },
        {
            "title": "What small trick did your family use to make preserved vegetables less salty?",
            "reward": 28,
            "asker": "FamilyRecipe",
            "time": "35 min ago",
            "answers": 2,
            "responses": [
                {
                    "text": "My grandmother rinsed the preserved mustard greens first, then soaked them in warm water for about 10 minutes and changed the water twice. She said this removed excess salt without washing away too much flavour.",
                    "file": None
                },
                {
                    "text": "Our family adds a tiny amount of sugar after rinsing. It does not make the vegetables sweet; it just balances the remaining saltiness.",
                    "file": None
                },
            ],
        },
        {
            "title": "Why does this particular 1980s Sony cassette player make a clicking sound?",
            "reward": 32,
            "asker": "TapeCollector",
            "time": "52 min ago",
            "answers": 2,
            "responses": [
                {
                    "text": "On my Sony cassette player, the clicking was not caused by the belt. A small plastic gear in the tape transport had cracked, causing one tooth to slip every rotation. Replacing the gear fixed it.",
                    "file": None
                },
                {
                    "text": "Another thing to check is the idler wheel. When its rubber becomes hard, the mechanism can repeatedly catch and release, producing a rhythmic clicking sound.",
                    "file": None
                },
            ],
        },
        {
            "title": "What did old Hong Kong shopkeepers use to protect handwritten price cards from humidity?",
            "reward": 27,
            "asker": "StreetArchive",
            "time": "1 hr ago",
            "answers": 2,
            "responses": [
                {
                    "text": "My father used to brush a very thin layer of clear wax over the paper after writing the price. It helped the card last longer in humid weather while keeping the writing visible.",
                    "file": None
                },
                {
                    "text": "Some shops put the handwritten card inside a reused transparent plastic food bag and clipped it to the stall. It looked messy but worked surprisingly well.",
                    "file": None
                },
            ],
        },
        {
            "title": "Does anyone know the old hand signal delivery workers used when they couldn't find the customer?",
            "reward": 35,
            "asker": "LostCustoms",
            "time": "2 hrs ago",
            "answers": 1,
            "responses": [
                {
                    "text": "My uncle worked as a delivery driver in the 1970s. If nobody answered the door, he would raise one hand sideways and make two short waving motions. In their team, this meant 'delivery has arrived but nobody answered.'",
                    "file": None
                },
            ],
        },
        {
            "title": "Why does my grandmother insist that dried tangerine peel goes into soup only near the end?",
            "reward": 20,
            "asker": "KitchenMystery",
            "time": "3 hrs ago",
            "answers": 2,
            "responses": [
                {
                    "text": "My grandmother adds the dried tangerine peel during the last 15–20 minutes. She says long boiling makes the peel's bitter flavour stronger, while adding it late keeps the citrus aroma.",
                    "file": None
                },
                {
                    "text": "Our family removes most of the white inner pith before adding the peel because my grandmother says that part makes the soup more bitter.",
                    "file": None
                },
            ],
        },
        {
            "title": "How can my grandfather tell different types of dried seafood apart without looking at the labels?",
            "reward": 24,
            "asker": "FamilyMystery",
            "time": "4 hrs ago",
            "answers": 2,
            "responses": [
                {
                    "text": "He checks the smell, surface texture, and thickness. For dried scallops, he looks for visible fibres and a concentrated sweet seafood smell rather than a sharp fishy smell.",
                    "file": None
                },
                {
                    "text": "For dried shrimp, my grandmother checks the colour. She prefers naturally uneven orange-pink colouring and avoids pieces that look unnaturally bright and completely uniform.",
                    "file": None
                },
            ],
        },
        {
            "title": "What was the hidden shortcut children used between two old Hong Kong estates before redevelopment?",
            "reward": 34,
            "asker": "UrbanMemory",
            "time": "5 hrs ago",
            "answers": 2,
            "responses": [
                {
                    "text": "There used to be a narrow staircase behind an old grocery shop. You walked past a metal gate, turned left behind the storage area, and found a small concrete staircase leading directly to the upper estate.",
                    "file": None
                },
                {
                    "text": "The shortcut saved around 7–10 minutes. There was also a loose metal railing halfway through, so everyone knew not to lean on it.",
                    "file": None
                },
            ],
        },
        {
            "title": "Why did my grandfather tap the rice cooker three times before opening it?",
            "reward": 22,
            "asker": "FamilyMystery",
            "time": "6 hrs ago",
            "answers": 2,
            "responses": [
                {
                    "text": "My grandfather tapped the lid three times with his knuckle before opening it. He said his mother taught him that the tapping helped loosen rice stuck around the edges of the inner pot, making it easier to serve.",
                    "file": None
                },
                {
                    "text": "In my family the three taps had a different meaning. My great-grandmother believed the habit helped keep the rice from becoming too dry. Nobody in the family knows where the tradition originally came from.",
                    "file": None
                },
            ],
        },
        {
            "title": "Does anyone know what this old HK tool was used for?",
            "reward": 15,
            "asker": "Sarah",
            "time": "2 hours ago",
            "answers": 2,
            "responses": [
                {"text": "It may be a traditional hand plane used to smooth wood.", "file": None},
                {"text": "A photo of the blade and handle could help identify the exact tool.", "file": None},
            ],
        },
        {
            "title": "Looking for pre-1990 Hakka dialect recordings",
            "reward": 25,
            "asker": "David",
            "time": "5 hours ago",
            "answers": 2,
            "responses": [
                {"text": "Try searching oral-history collections using the village name and dialect variant.", "file": None},
                {"text": "Local libraries may have cassette catalogs that are not indexed online.", "file": None},
            ],
        },
        {
            "title": "Does anyone have information about old Hong Kong bus routes?",
            "reward": 20,
            "asker": "Michael",
            "time": "Yesterday",
            "answers": 1,
            "responses": [
                {"text": "Historic route maps and timetable scans are good places to start.", "file": None},
            ],
        },
        
    ]

# 3. HELPER FUNCTIONS
AI_MODEL_OPTIONS = {
    "GPT-4.1 Nano": "gpt-4.1-nano",
    "GPT-4.1 Mini": "gpt-4.1-mini",
    "GPT-4.1": "gpt-4.1",
    "o4-mini": "o4-mini",
    "GPT-5": "gpt-5",
}
OPENROUTER_MODEL_OPTIONS = {
    "DeepSeek V4.1 Flash": "deepseek/deepseek-v4.1-flash",
    "Qwen 3.8 27B (Free)": "qwen/qwen3.8-27b:free",
    "Mistral Medium 3.5": "mistralai/mistral-medium-3-5",
    "Kimi K3": "moonshotai/kimi-k3",
}

@st.dialog("Report resource", width="small")
def report_resource_dialog(item_id):
    st.write("Choose a reason for reporting this resource.")
    report_options = [
        "Incorrect or fabricated content",
        "Duplicate or recycled material",
        "Missing provenance or source attribution",
        "Low quality or corrupted file",
        "Not relevant to niche data / not useful",
        "Other"
    ]
    report_reason = st.radio(
        "Choose a reason",
        report_options,
        index=0,
        key=f"report_reason_{item_id}",
    )
    cancel_col, submit_col = st.columns(2)
    with cancel_col:
        if st.button("Cancel", key=f"cancel_report_{item_id}", use_container_width=True):
            st.rerun()
    with submit_col:
        if st.button("Submit", key=f"submit_report_{item_id}", type="primary", use_container_width=True):
            trigger_report(item_id, report_reason)
            st.rerun()

@st.dialog("Answer community question")
def answer_question_dialog(question_index):
    question = st.session_state.questions[question_index]
    st.write(question["title"])
    answer = st.text_area(
        "Your answer",
        placeholder="Share what you know...",
        key=f"answer_text_{question_index}",
        height=120,
    )
    attachment = st.file_uploader(
        "Attach a file (optional)",
        key=f"answer_file_{question_index}",
    )
    cancel_col, submit_col = st.columns(2)
    with cancel_col:
        if st.button("Cancel", key=f"cancel_answer_{question_index}", use_container_width=True):
            st.session_state.pop("answering_question", None)
            st.rerun()
    with submit_col:
        if st.button("Submit answer", key=f"submit_answer_{question_index}", type="primary", use_container_width=True):
            if not answer.strip() and attachment is None:
                st.warning("Enter an answer or attach a file before submitting.")
            else:
                uploaded_file = None
                if attachment is not None:
                    uploaded_file = {
                        "name": attachment.name,
                        "type": attachment.type,
                        "data": attachment.getvalue(),
                    }
                submitted = datetime.datetime.now().strftime("%b %d, %Y %H:%M")
                question.setdefault("responses", []).append({
                    "text": answer.strip(),
                    "file": uploaded_file,
                })
                question["answers"] += 1
                reward = question["reward"]
                st.session_state.user["credits"] += reward
                st.session_state.answered_questions.insert(0, {
                    "question": question["title"],
                    "answer": answer.strip(),
                    "attachment": attachment.name if attachment else "None",
                    "credits_earned": reward,
                    "submitted": submitted,
                })
                record_credit_change("for answering a community question", reward)
                st.session_state.credit_award = reward
                st.session_state.pop("answering_question", None)
                st.rerun()

# 4. TOP NAVIGATION & ACCOUNT MENU
pages = ["Home", "Contribution", "AI Chatbot"]
if "page" not in st.session_state:
    st.session_state.page = pages[0]

def select_page(page_option):
    st.session_state.page = page_option

with st.container(key="app_header"):
    header_brand, header_navigation, header_col2, header_col3 = st.columns(
        [3.4, 3.5, 1.8, 0.6],
        gap="small",
        vertical_alignment="center",
    )
    with header_brand:
        logo_data = base64.b64encode(
            Path(__file__).with_name("RarityBarter-Photoroom.png").read_bytes()
        ).decode("ascii")
        st.markdown(
            f'<div class="brand-lockup"><img class="brand-logo" src="data:image/png;base64,{logo_data}" alt="RarityBarter logo"><span class="brand-title">RarityBarter</span></div>',
            unsafe_allow_html=True,
        )
    with header_navigation:
        with st.container(horizontal=True, gap=None, wrap=False):
            for index, page_option in enumerate(pages):
                st.button(
                    page_option,
                    key=f"page_navigation_{index}",
                    type="primary" if st.session_state.page == page_option else "secondary",
                    width="content",
                    on_click=select_page,
                    args=(page_option,)
                )
    with header_col2:
        credit_display_col, notification_col = st.columns(
            [1, 0.2],
            gap="small",
            vertical_alignment="center",
        )
        with credit_display_col:
            st.markdown(
                f"""
                <div style="text-align: right; padding-top: 0px;">
                    <span class="credit-badge">🪙 {st.session_state.user['credits']} Credits</span>
                </div>
                """,
                unsafe_allow_html=True
            )
    with header_col3:
        if st.button(
            "",
            icon=":material/account_circle:",
            help="My Profile",
            key="profile_navigation",
        ):
            st.session_state.page = "👤 My Profile"
            st.rerun()

page = st.session_state.page

# PAGE 1: HOME
if page == "Home":
    # SECTION 1: Headline, Action Buttons, and Main Showcase Picture
    home_actions, home_showcase = st.columns([1.2, 1], gap="large")
    with home_actions:
        st.markdown(
            '<p class="home-quote">“Exchange your data for credit.”</p>'
            '<p class="home-quote-note">Discover, contribute, and keep meaningful resources in circulation.</p>',
            unsafe_allow_html=True,
        )
        action_buttons = st.columns(2, gap="small")
        with action_buttons[0]:
            st.button(
                "Contribute",
                key="home_contributor",
                icon=":material/upload_file:",
                use_container_width=True,
                on_click=select_page,
                args=("Contribution",),
            )
        with action_buttons[1]:
            st.button(
                "Browse resources",
                key="home_browse",
                icon=":material/search:",
                use_container_width=True,
                on_click=select_page,
                args=("AI Chatbot",),
            )

    with home_showcase:
        homepage_image_data = base64.b64encode(
            Path(__file__).with_name("RarityBarter-HomePage.jpg").read_bytes()
        ).decode("ascii")
        st.markdown(
            f'<div class="home-artwork"><img src="data:image/jpeg;base64,{homepage_image_data}" alt="RarityBarter mascot showcasing shared digital resources"></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

     # SECTION 2: Earn Bonus Credits (Horizontal Scroll Only)
    st.markdown("## 🪙 Earn Bonus Credits!")
    st.caption("Help answer community questions and earn credits.")

    # CSS: make ONLY the question cards horizontally scrollable
    st.markdown("""
        <style>
        /* The question section itself */
        div[data-testid="stHorizontalBlock"]:has(
            div[class*="st-key-question_card_"]
        ) {
            display: flex !important;
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            overflow-y: hidden !important;
            gap: 1rem !important;
            padding: 0.5rem 0 1rem 0 !important;
            width: 100% !important;
            max-width: 100% !important;
        }

        /* Each question card has a fixed width */
        div[data-testid="stHorizontalBlock"]:has(
            div[class*="st-key-question_card_"]
        ) > div {
            flex: 0 0 380px !important;
            min-width: 380px !important;
            max-width: 380px !important;
        }

        /* Prevent the cards themselves from causing page overflow */
        div[class*="st-key-question_card_"] {
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
        }

        /* Hide scrollbar visually but keep scrolling */
        div[data-testid="stHorizontalBlock"]:has(
            div[class*="st-key-question_card_"]
        )::-webkit-scrollbar {
            height: 8px;
        }

        div[data-testid="stHorizontalBlock"]:has(
            div[class*="st-key-question_card_"]
        )::-webkit-scrollbar-thumb {
            background: #c7c7c7;
            border-radius: 10px;
        }

        div[data-testid="stHorizontalBlock"]:has(
            div[class*="st-key-question_card_"]
        )::-webkit-scrollbar-track {
            background: transparent;
        }
        </style>
    """, unsafe_allow_html=True)

    # Question cards
    if "questions" in st.session_state and st.session_state.questions:

        # IMPORTANT:
        # Do NOT wrap this in st.markdown("<div>...</div>").
        # Instead, identify each card with a Streamlit key.
        card_cols = st.columns(len(st.session_state.questions), gap="medium")

        for question_index, question in enumerate(st.session_state.questions):

            with card_cols[question_index]:

                # Unique key lets the CSS identify these cards
                with st.container(
                    border=True,
                    key=f"question_card_{question_index}"
                ):

                    st.markdown(f"#### {question['title']}")

                    st.caption(
                        f"Asked by {question['asker']} · {question['time']}"
                    )

                    st.markdown(
                        f'''
                        <div class="reward-banner">
                            <span class="reward-banner-label">
                                🪙 Credits reward
                            </span>
                            <span class="reward-banner-amount">
                                +{question["reward"]}
                            </span>
                        </div>
                        ''',
                        unsafe_allow_html=True,
                    )

                    # Existing answers
                    for response_index, response in enumerate(
                        question.get("responses", [])
                    ):

                        if response["text"]:
                            st.markdown(
                                f"> {response['text']}"
                            )

                        response_file = response.get("file")

                        if response_file:
                            st.download_button(
                                f"Download {response_file['name']}",
                                data=response_file["data"],
                                file_name=response_file["name"],
                                mime=response_file["type"],
                                key=(
                                    f"question_attachment_"
                                    f"{question_index}_{response_index}"
                                ),
                            )

                    st.caption(
                        f"{question['answers']} answers"
                    )

                    if st.button(
                        "Answer →",
                        key=f"answer_button_{question_index}",
                        use_container_width=True,
                        type="primary",
                    ):
                        st.session_state.answering_question = question_index
                        st.rerun()

    if "answering_question" in st.session_state:
        answer_question_dialog(
            st.session_state.answering_question
        )

# PAGE 2: Contribution
elif page == "Contribution":
    st.header("Exchange your rare data for AI credits!")

    draft_defaults = {
        "type": "Image",
        "title": "",
        "description": "",
        "file_names": [],
        "additional_details": [],
        "value_score": None,
        "assessment": "",
        "estimated_credits": None,
        "estimate_count": 0
    }
    if "contributor_draft" not in st.session_state:
        st.session_state.contributor_draft = draft_defaults.copy()
    if st.session_state.pop("reset_contributor_draft", False):
        st.session_state.contributor_draft = draft_defaults.copy()
        for field_key in (
            "contrib_type_input",
            "contrib_title_input",
            "contrib_description_input",
            "contrib_file_input",
            "contrib_more_details_input",
            "contrib_more_files_input",
            "contrib_type",
            "contrib_title",
            "contrib_description",
            "contrib_file"
        ):
            st.session_state.pop(field_key, None)
    draft = st.session_state.contributor_draft
    if "file_names" not in draft:
        old_file_name = draft.pop("file_name", "")
        draft["file_names"] = [old_file_name] if old_file_name else []
    draft.setdefault("additional_details", [])
    draft.setdefault("assessment", "")
    draft.setdefault("estimated_credits", None)
    draft.setdefault("estimate_count", 0)
    if "contributor_flow_step" not in st.session_state:
        st.session_state.contributor_flow_step = "asset_type"
    elif st.session_state.contributor_flow_step == "confirmation":
        st.session_state.contributor_flow_step = "estimate"

    flow_step = st.session_state.contributor_flow_step
    if flow_step == "estimate" and draft["estimated_credits"] is None:
        estimate_contribution(draft)
        draft["estimate_count"] = max(draft["estimate_count"], 1)
    selected_type = draft["type"]
    value_score = draft["value_score"]
    estimated_credits = draft["estimated_credits"]
    flow_prompts = {
        "asset_type": "Hi! What type of asset would you like to contribute?",
        "details": f"Great, a {selected_type}. What should I call it, and what makes it useful or unique?",
        "file": "Attach any files that support the resource. You can skip this step if you do not have them ready.",
        "estimate": "",
        "complete": ""
    }
    current_prompt = flow_prompts[flow_step]

    def record_contributor_answer(answer, next_step, assistant_reply=None):
        if current_prompt:
            st.session_state.contributor_chat.append({"sender": "AI", "text": current_prompt})
        st.session_state.contributor_chat.append({"sender": "User", "text": answer})
        if assistant_reply:
            st.session_state.contributor_chat.append({"sender": "AI", "text": assistant_reply})
        st.session_state.contributor_flow_step = next_step

    with st.container(height=640, border=False):
        for message in st.session_state.contributor_chat:
            if message["sender"] == "AI":
                with st.chat_message("assistant"):
                    st.markdown(message["text"])
            else:
                safe_text = html.escape(str(message["text"])).replace("\n", "<br>")
                st.markdown(
                    f'<div class="user-chat-row"><div class="chat-bubble-user">{safe_text}</div><div class="user-chat-avatar">👤</div></div>',
                    unsafe_allow_html=True
                )

        with st.chat_message("assistant"):
            if current_prompt:
                st.markdown(current_prompt)

            if flow_step == "asset_type":
                if "contrib_type_input" not in st.session_state:
                    st.session_state.contrib_type_input = draft["type"]
                st.selectbox(
                    "Asset type",
                    ["Image", "Video", "Audio", "Text", "Other"],
                    key="contrib_type_input"
                )
                if st.button("Send", key="contrib_send_type"):
                    draft["type"] = st.session_state.contrib_type_input
                    record_contributor_answer(draft["type"], "details")
                    st.rerun()

            elif flow_step == "details":
                if "contrib_title_input" not in st.session_state:
                    st.session_state.contrib_title_input = draft["title"]
                if "contrib_description_input" not in st.session_state:
                    st.session_state.contrib_description_input = draft["description"]
                title = st.text_input(
                    "Resource title",
                    placeholder="e.g. 1970s Hong Kong Railway Timetables & Scans",
                    key="contrib_title_input"
                )
                description = st.text_area(
                    "Description and provenance",
                    placeholder="Add dates, location, source, and historical context...",
                    key="contrib_description_input"
                )
                if st.button("Send", key="contrib_send_details"):
                    if title.strip():
                        draft["title"] = title.strip()
                        draft["description"] = description.strip()
                        answer = f"{title.strip()} - {description.strip()}" if description.strip() else title.strip()
                        record_contributor_answer(answer, "file")
                        st.rerun()
                    else:
                        st.warning("Please enter a title so I can identify this resource.")

            elif flow_step == "file":
                uploaded_files = st.file_uploader(
                    "Upload or drag and drop a file",
                    type=["png", "jpg", "jpeg", "mp4", "mov", "mp3", "wav", "txt", "pdf", "csv"],
                    accept_multiple_files=True,
                    key="contrib_file_input"
                )
                if draft["file_names"]:
                    st.caption(f"Already attached: {', '.join(draft['file_names'])}")
                if st.button("Continue", key="contrib_send_file"):
                    if uploaded_files and not isinstance(uploaded_files, list):
                        uploaded_files = [uploaded_files]
                    added_names = [uploaded_file.name for uploaded_file in (uploaded_files or [])]
                    draft["file_names"] = list(dict.fromkeys(draft["file_names"] + added_names))
                    value_score, assessment, estimated_credits = estimate_contribution(draft)
                    draft["estimate_count"] = 1
                    answer = f"Attached {', '.join(added_names)}" if added_names else "I'll continue without attaching a file for now"
                    record_contributor_answer(
                        answer,
                        "estimate",
                        f"Estimated credits: 🪙 {estimated_credits}. Add details or files to update the estimate, or submit when you are satisfied."
                    )
                    st.rerun()

            elif flow_step == "estimate":
                with st.form("contrib_refine_estimate_form", clear_on_submit=True):
                    additional_details = st.text_area(
                        "Add more details for the AI",
                        placeholder="Add exact dates, location, source, provenance, or other context...",
                        key="contrib_more_details_input"
                    )
                    additional_files = st.file_uploader(
                        "Attach more files",
                        type=["png", "jpg", "jpeg", "mp4", "mov", "mp3", "wav", "txt", "pdf", "csv"],
                        accept_multiple_files=True,
                        key="contrib_more_files_input"
                    )
                    estimate_again = st.form_submit_button("Estimate again")

                if estimate_again:
                    added_details = additional_details.strip()
                    new_files = additional_files or []
                    added_names = [uploaded_file.name for uploaded_file in new_files]
                    if not added_details and not added_names:
                        st.warning("Add some details or attach a file before asking for another estimate.")
                    else:
                        if added_details:
                            draft["additional_details"].append(added_details)
                        draft["file_names"] = list(dict.fromkeys(draft["file_names"] + added_names))
                        value_score, assessment, estimated_credits = estimate_contribution(draft)
                        draft["estimate_count"] += 1
                        answer_parts = []
                        if added_details:
                            answer_parts.append(f"Additional details: {added_details}")
                        if added_names:
                            answer_parts.append(f"Additional files: {', '.join(added_names)}")
                        record_contributor_answer(
                            "; ".join(answer_parts),
                            "estimate",
                            f"Updated estimate: 🪙 {estimated_credits}. Add details or files to update it again, or submit when satisfied."
                        )
                        st.rerun()

                submit_contribution = st.button(
                    "Submit contribution",
                    type="primary",
                    use_container_width=True,
                    key="contributor_submit"
                )
                if submit_contribution:
                    file_detail = f" Files: {', '.join(draft['file_names'])}." if draft["file_names"] else ""
                    new_entry = {
                        "id": len(st.session_state.contributions) + 101,
                        "title": draft["title"],
                        "type": selected_type,
                        "description": draft["description"],
                        "value_score": value_score,
                        "credits_cost": int(estimated_credits * 0.6),
                        "estimated_value": estimated_credits,
                        "contributor_id": st.session_state.user["name"],
                        "contributor_rep": st.session_state.user["reputation"],
                        "likes": 0,
                        "dislikes": 0,
                        "status": "Verified",
                        "unlocked_by": [st.session_state.user["name"]],
                        "content": f"📁 Uploaded content for '{draft['title']}' successfully decoded.{file_detail}"
                    }
                    st.session_state.contributions.append(new_entry)
                    st.session_state.user["credits"] += estimated_credits
                    st.session_state.user["contributions_count"] += 1
                    record_credit_change(f"for contributing {draft['title']}", estimated_credits)
                    record_contributor_answer(
                        "Submit contribution",
                        "complete",
                        f"Thanks for your contribution!\n\n## 🪙 {estimated_credits} credits added successfully!"
                    )
                    st.balloons()
                    st.rerun()

            elif flow_step == "complete":
                st.balloons()
                if st.button("Start another contribution", key="contrib_start_another"):
                    st.session_state.contributor_chat.append({
                        "sender": "User",
                        "text": "Start another contribution"
                    })
                    st.session_state.contributor_flow_step = "asset_type"
                    st.session_state.reset_contributor_draft = True
                    st.rerun()

            previous_step = {
                "details": "asset_type",
                "file": "details",
                "estimate": "file"
            }.get(flow_step)
            if previous_step and st.button("← Back", key=f"contrib_back_{flow_step}"):
                st.session_state.contributor_flow_step = previous_step
                st.rerun()

    with st.container(key="contributor_chat_composer"):
        chat_input = st.chat_input(
            "Ask the assistant about your contribution",
            key="contributor_chat_input",
            accept_file=True,
            accept_audio=True,
            height=70,
        )
    if chat_input:
        message_parts = []
        if chat_input.text.strip():
            message_parts.append(chat_input.text.strip())
        if chat_input.files:
            message_parts.append(f"Attached files: {', '.join(file.name for file in chat_input.files)}")
        if chat_input.audio:
            message_parts.append(f"Audio recorded: {chat_input.audio.name}")
        if message_parts:
            st.session_state.contributor_chat.append({"sender": "User", "text": "\n".join(message_parts)})
            st.session_state.contributor_chat.append({
                "sender": "AI",
                "text": f"To assess that, include specific dates, locations, and provenance. We can continue with your {flow_step.replace('_', ' ')} step when you're ready."
            })
            st.rerun()

# PAGE 3: AI Chatbot
elif page == "AI Chatbot":
    st.header("Ask anything here and discover niche resources!")

    if "browse_panel_visible" not in st.session_state:
        st.session_state.browse_panel_visible = False

    def render_resource_feed():

        active_filters = st.session_state.browse_filters
        user_search_query = active_filters["search_query"]
        filter_types = ["All", "Audio", "Image", "Video", "Text", "Other"]
        s_col1, s_col2 = st.columns([1, 1.5])
        with s_col1:
            filter_type = st.selectbox(
                "Type",
                filter_types,
                index=filter_types.index(active_filters["filter_type"]),
                key="browse_filter_type"
            )
        with s_col2:
            sort_options = {
                "Newest": "newest",
                "Most favorited": "most_favorited",
                "Most accessed": "most_accessed"
            }
            sort_label = st.selectbox(
                "Sort by",
                list(sort_options),
                index=list(sort_options.values()).index(active_filters["sort_by"]),
                key="browse_sort_by"
            )

        active_filters["filter_type"] = filter_type
        active_filters["sort_by"] = sort_options[sort_label]


        # 1. Retrieve search results or all contributions
        filtered_list = (
            search_contributions(user_search_query, st.session_state.contributions)
            if user_search_query
            else st.session_state.contributions
        )

        # 2. Filter out reported posts for the current user
        filtered_list = [
            x for x in filtered_list 
            if not get_user_action(x["id"])["reported"]
        ]

        # 3. Filter by asset type
        if active_filters["filter_type"] != "All":
            filtered_list = [x for x in filtered_list if x["type"] == active_filters["filter_type"]]

        prioritized_categories = prioritized_download_categories(user_search_query)

        if active_filters["sort_by"] == "most_favorited":
            filtered_list = sorted(
                filtered_list,
                key=lambda x: (
                    x.get("category") in prioritized_categories
                    and bool(x.get("download_file")),
                    x["likes"],
                    len(x.get("unlocked_by", [])),
                ),
                reverse=True,
            )
        elif active_filters["sort_by"] == "most_accessed":
            filtered_list = sorted(
                filtered_list,
                key=lambda x: (
                    x.get("category") in prioritized_categories
                    and bool(x.get("download_file")),
                    len(x.get("unlocked_by", [])),
                ),
                reverse=True,
            )
        else:
            filtered_list = sorted(
                filtered_list,
                key=lambda x: (
                    x.get("category") in prioritized_categories
                    and bool(x.get("download_file")),
                    x["id"],
                ),
                reverse=True,
            )

        with st.container(height=600, border=False, key="resource_feed_items"):
            if not filtered_list:
                st.info("No resources match your current filters.")

            for item in filtered_list:
                is_unlocked = st.session_state.user["name"] in item["unlocked_by"]
                action = get_user_action(item["id"])

                with st.container(border=True):
                    post_header_cols = st.columns([4, 1.6], gap="small")
                    with post_header_cols[0]:
                        st.markdown(f"#### {item['title']}")
                    with post_header_cols[1]:
                        if is_unlocked:
                            control_cols = st.columns(2, gap="small")
                            unlock_col = control_cols[0]
                            download_col = control_cols[1]
                        else:
                            unlock_col = st.container()
                            download_col = None

                        if not is_unlocked:
                            with unlock_col:
                                st.button(
                                    "Unlock",
                                    key=f"unlock_{item['id']}",
                                    use_container_width=True,
                                    on_click=unlock_resource,
                                    args=(item["id"], item["credits_cost"]),
                                )
                        if download_col:
                            payload = get_download_payload(item)
                            with download_col:
                                st.download_button(
                                    label="",
                                    help=(
                                        "Download resource file"
                                        if item.get("download_file")
                                        else "Download resource summary"
                                    ),
                                    data=payload["data"],
                                    file_name=payload["file_name"],
                                    mime=payload["mime"],
                                    icon=":material/download:",
                                    key=f"download_{item['id']}",
                                )
                        if not is_unlocked:
                            st.caption(f"Cost: {item['credits_cost']} credits")
                    st.write(item["description"])
                    st.caption(
                        f"{item.get('category', 'Uncategorized')} · Type: {item['type']} · "
                        f"{'Cultural' if item.get('cultural') else 'Non-cultural'} · "
                        f"Value: {item.get('estimated_value', '—')} credits · "
                        f"Contributor: {item['contributor_id']} "
                        f"(Rep: {item['contributor_rep']}) · Status: {item['status']}"
                    )

                    with st.container(horizontal=True, gap="small"):
                        like_label = f"❤️ {item['likes']}" + (" • You" if action["liked"] else "")
                        if st.button(like_label, key=f"like_{item['id']}"):
                            trigger_like(item['id'])
                            st.rerun()
                        dislike_label = f"👎 {item['dislikes']}" + (" • You" if action["disliked"] else "")
                        if st.button(dislike_label, key=f"dislike_{item['id']}"):
                            trigger_dislike(item['id'])
                            st.rerun()
                        if action["reported"]:
                            st.caption(f"Reported: {action['report_reason']}")
                        elif st.button("🚩 Report", key=f"report_{item['id']}"):
                            report_resource_dialog(item["id"])

                    if is_unlocked:
                        st.info(f"**Unlocked Content:** {item['content']}")
                        if item.get("download_file"):
                            file_path = Path(__file__).resolve().parent / item["download_file"]
                            mime_type, _ = mimetypes.guess_type(file_path.name)
                            if mime_type and mime_type.startswith("image/"):
                                st.image(file_path, caption=item["title"], width="stretch")

    def render_search_assistant(panel_visible):
        api_configured = bool(get_ai_api_key())
        model_options = get_ai_models() if api_configured else {}
        if api_configured:
            st.caption("Resource descriptions and content you have unlocked may be sent to the selected model provider.")
        else:
            st.caption("Local resource chat · searches shared post details without an external AI connection.")

        with st.container(height=600, border=False, key="search_chat_history"):
            for message_index, msg in enumerate(st.session_state.user_chat):
                if msg["sender"] == "AI":
                    if msg["text"].startswith("Found 2 matching archives for "):
                        continue
                    with st.chat_message("assistant"):
                        st.markdown(msg["text"])
                        source_ids = msg.get("source_ids", [])
                        if source_ids and st.button(
                            "View resources",
                            key=f"view_sources_{message_index}",
                            icon=":material/source:",
                        ):
                            st.session_state.resource_source_ids = source_ids
                            st.session_state.browse_panel_visible = True
                            st.rerun()
                else:
                    safe_text = html.escape(str(msg["text"])).replace("\n", "<br>")
                    st.markdown(
                        f'<div class="user-chat-row"><div class="chat-bubble-user">{safe_text}</div><div class="user-chat-avatar">👤</div></div>',
                        unsafe_allow_html=True
                    )

        composer_key = "user_chat_composer_expanded" if panel_visible else "user_chat_composer_collapsed"
        with st.container(key=composer_key):
            if api_configured:
                model_col, input_col = st.columns([1.6, 3.4], gap="small", vertical_alignment="center")
                with model_col:
                    model_label = st.selectbox(
                        "Select AI model",
                        list(model_options),
                        key="user_chat_model",
                        label_visibility="collapsed",
                    )
                with input_col:
                    u_chat_input = st.chat_input("Ask AI to find specific resources:", key="user_chat_input")
            else:
                u_chat_input = st.chat_input(
                    "Ask about a topic, place, time period, or resource type:",
                    key="user_chat_input",
                )
        if u_chat_input:
            query = u_chat_input.strip()
            if query:
                research_cost = 1
                if st.session_state.user["credits"] < research_cost:
                    st.warning("AI Research requires 1 credit. Contribute resources to earn more.")
                else:
                    st.session_state.user["credits"] -= research_cost
                    record_credit_change("for AI Research", -research_cost)
                    previous_messages = list(st.session_state.user_chat)
                    matched_resources = search_contributions(query, st.session_state.contributions)
                    follow_up = re.search(
                        r"\b(it|they|them|those|these|that|more|details|compare|which one)\b",
                        query.lower(),
                    )
                    if not matched_resources and follow_up:
                        previous_source_ids = next(
                            (msg.get("source_ids", []) for msg in reversed(previous_messages) if msg["sender"] == "AI"),
                            [],
                        )
                        matched_resources = [
                            item for item in st.session_state.contributions
                            if item["id"] in previous_source_ids
                        ]
                    st.session_state.user_search_query = query
                    st.session_state.browse_filters["search_query"] = query
                    st.session_state.resource_source_ids = []
                    st.session_state.user_chat.append({"sender": "User", "text": query})
                    ai_response = generate_ai_response(
                        query,
                        model_options[model_label] if api_configured else "",
                        previous_messages,
                        matched_resources,
                        st.session_state.user["name"],
                    )
                    st.session_state.user_chat.append({
                        "sender": "AI",
                        "text": ai_response,
                        "source_ids": get_cited_resource_ids(
                            ai_response,
                            matched_resources,
                        ),
                    })
                    st.rerun()

    if st.session_state.browse_panel_visible:
        col_main, toggle_col, chat_gutter, col_side = st.columns(
            [2, 0.2, 0.1, 3.5],
            gap=None,
        )
        with col_main:
            with st.container(border=True):
                render_resource_feed()
        with toggle_col:
            st.markdown(
                """
                <style>
                div.st-key-hide_resource_panel > div {
                    display: flex;
                    justify-content: flex-start;
                }
                div.st-key-hide_resource_panel button {
                    transform: translateX(3.5px);
                    border-top-left-radius: 0 !important;
                    border-bottom-left-radius: 0 !important;
                    margin-left: 0 !important;
                    width: 3rem !important;
                    min-width: 3rem !important;
                    max-width: 3rem !important;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )
            if st.button(">", key="hide_resource_panel", help="Hide resource panel", use_container_width=True):
                st.session_state.browse_panel_visible = False
                st.rerun()
        with chat_gutter:
            st.empty()
        with col_side:
            render_search_assistant(panel_visible=True)
    else:
        toggle_col, col_side = st.columns([0.0000001, 5], gap="small")
        with toggle_col:
            st.markdown(
                """
                <style>
                div.st-key-show_resource_panel button {
                    transform: translateX(-50px);
                    border-top-left-radius: 0 !important;
                    border-bottom-left-radius: 0 !important;
                    width: 3rem !important;
                    min-width: 3rem !important;
                    max-width: 3rem !important;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )
            if st.button(">", key="show_resource_panel", help="Show resource panel"):
                st.session_state.browse_panel_visible = True
                st.rerun()
        with col_side:
            render_search_assistant(panel_visible=False)

# PAGE 4: User Profile
elif page == "👤 My Profile":
    my_uploads = [
        item for item in st.session_state.contributions
        if item["contributor_id"] == st.session_state.user["name"]
    ]
    
    p_col1, p_col2 = st.columns([1.2, 1], gap="large")
    with p_col1:
        st.markdown(f"## :material/account_circle: {st.session_state.user['name']}")
        st.markdown(f"##### **Credit :** `{st.session_state.user['credits']}`")
        st.markdown(f"##### **Reputation Score :** `{st.session_state.user['reputation']} / 100`")
        st.markdown(
            "<span style='display:inline-block; padding:7px 14px; margin-right:8px; "
            "border-radius:999px; background:rgba(46, 160, 67, 0.14); "
            "border:1px solid rgba(46, 160, 67, 0.28); color:#1f6b35; "
            "font-size:1rem; font-weight:600;'> · Trusted Contributor</span>"
            "<span style='display:inline-block; padding:7px 14px; "
            "border-radius:999px; background:rgba(240, 145, 40, 0.16); "
            "border:1px solid #C66700; color:#C66700; "
            "font-size:1rem; font-weight:600;'> · High Influence</span>",
            unsafe_allow_html=True,
        )

    with p_col2:
        with st.container(border=True):
            st.subheader("🪙 Credit History")
            for transaction in st.session_state.credit_history:
                amount = transaction["amount"]
                color = "#218838" if amount >= 0 else "#b42318"
                signed_amount = f"+{amount}" if amount > 0 else str(amount)
                st.markdown(
                    f"**{transaction['description']}**  "
                    f"<span style='color:{color}; font-weight:700;'>"
                    f"{signed_amount} credits</span>",
                    unsafe_allow_html=True,
                )
                st.caption(transaction["time"])

    st.markdown("---")
    st.write(f"### **📂 My Contributions:** `{len(my_uploads)}`")
    
    if my_uploads:
        upload_rows = [
            {
                "Title": item["title"],
                "Type": item["type"],
                "Estimated Value": item.get("estimated_value", "—"),
                "Likes": item.get("likes", 0),
                "Dislikes": item.get("dislikes", 0),
                "Status": item.get("status", "Unknown"),
            }
            for item in my_uploads
        ]
        st.dataframe(pd.DataFrame(upload_rows), use_container_width=True, hide_index=True)
    else:
        st.info("You haven't uploaded any resources yet.")

    st.markdown("---")
    st.write(f"### **📝 Questions Answered:** `{len(st.session_state.answered_questions)}`")

    if st.session_state.answered_questions:
        df_answers = pd.DataFrame(st.session_state.answered_questions)[
            ["question", "answer", "attachment", "credits_earned", "submitted"]
        ]
        st.dataframe(df_answers, use_container_width=True)
    else:
        st.info("You haven't answered any community questions yet.")