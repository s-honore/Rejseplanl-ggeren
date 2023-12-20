from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import ChatMessage
from langchain.schema.messages import SystemMessage
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='key.env')


def img_to_html(image_path):
    return f'<img src="{image_path}" alt="Image">'

# Streamlit config
st.set_page_config(page_title="Smedens Rejsebureau", page_icon="island2.png", initial_sidebar_state='expanded') 
hide_menu_style = """ <style> #MainMenu {visibility: hidden;} </style> """
#st.markdown(hide_menu_style, unsafe_allow_html=True) 
st.markdown( f"<div style='position: fixed; bottom: {16}px; right: 20px; font-size: {16}px;'> <b>Powered by</b> ISmeden islandrejser </div>", unsafe_allow_html=True) 
st.image("island2.png")

openai_api_key = os.getenv('OPENAI_API_KEY')

def set_northern_lights_background():
    st.markdown("""
    <style>
    .stApp {
        background-image: url('https://your-image-url.jpg');  # Erstat med URL til det genererede nordlys billede
        background-repeat: no-repeat;
        background-size: cover;
    }
    </style>
    """, unsafe_allow_html=True)

# Kald funktionen i starten af din app
set_northern_lights_background()

st.markdown("""
    <style>
    .intro-text {
        font-size:20px;
        color: #4a4a4a;  # You can change this color to fit your theme
    }
    </style>
    <p class='intro-text'>Ho ho ho... velkommen til ISmedens Islandsrejser. Du og Bizman Bizz skal til Island i uge 4. Du får nu nogle valgmuligheder for rejsen og dernæst laver vi et rejseprogram. </p>
    """, unsafe_allow_html=True)

# Add a slider for vacation duration
vacation_duration = st.slider("Hvor mange dage vil du afsted?", 1, 7, 7)

st.write("Hvad kunne du tænke dig at opleve?")
# Add checkboxes for activities or sights
activity_options = {
    "Silfra Snorkling": st.checkbox("Silfra Snorkling - Dyk i krystalklare vande mellem to kontinenter"),
    "Søpapegøjer": st.checkbox("Iagttag de bedårende 'søpapegøjer' i deres naturlige habitat"),
    "Hvalsafari": st.checkbox("Hvalsafari"),
    "Den Blå Lagune": st.checkbox("Den Blå Lagune - Slap af i det geotermiske spa med mineralrige vande"),
    "Den Gyldne Cirkel": st.checkbox("Den Gyldne Cirkel - Udforsk Þingvellir Nationalpark, Gullfoss-vandfaldet og Geysir-geotermiske område"),
    "Nordlys": st.checkbox("Nordlys - Jagt på det magiske nordlys"),
    "Hesteridning": st.checkbox("Hesteridning - Oplev landskabet på ryggen af en islandsk hest"),
    "Besøg Vandfald": st.checkbox("Besøg Vandfald som Seljalandsfoss og Skógafoss")
}
# Generate a prompt based on the selected options
selected_activities = [activity for activity, selected in activity_options.items() if selected]
activities_str = ", ".join(selected_activities)
prompt_base = f"planlæg en {vacation_duration}-dags rejse til Island, der inkluderer følgende aktiviteter {activities_str}. Husk at tage højde for antallet af aktiviteter er realistisk i forhold til rejselængden. Du skal skrive som om det er mig, Sebastian, der skriver til min kæreste Cecilie. Kom med forslag til hvilket tøj der skal pakkes. Der er en bil til rådighed alle dagene. Det er vigtigt at du tager højde for at, der er en baby, Walther, på 6 måneder med på rejsen. Det betyder at du skal angive et tidsestimat på køretid og foreslå eventuelle stop undervejs. Du skal også komme med eksempler på overnatningssteder, hvor mange nætter vi skal være på hvert hotel og et link til booking. Dan et kort over ruten. "


class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

if "messages" not in st.session_state:
    st.session_state["messages"] = [ChatMessage(role="assistant", content="Når du har valgt aktiviteter og dage så skriv: Lav en rejseplan. Du kan også spørge ind til oplevelserne")]

for msg in st.session_state.messages:
    if msg.role != "system":
        st.chat_message(msg.role).write(msg.content)

st.session_state.messages.append(ChatMessage(role="system", content=prompt_base))

if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    st.session_state.messages.append(ChatMessage(role="user", content=(prompt)))
    
    with st.chat_message("assistant"):
        stream_handler = StreamHandler(st.empty())
        llm = ChatOpenAI(model_name="gpt-4-1106-preview"
                         , openai_api_key=openai_api_key
                         , streaming=True
                         , callbacks=[stream_handler])
        response = llm(st.session_state.messages)
        
        st.session_state.messages.append(ChatMessage(role="assistant", content=response.content))
        
if st.button("Double-click to clear message history"):
    st.session_state["messages"].clear()
    st.session_state["messages"] = [ChatMessage(role="assistant", content="Paste your code below")]
