import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- 1. KONFIGURACE VZHLEDU ---
st.set_page_config(page_title="MatchMaster EU Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #020617; color: #f8fafc; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; color: #38bdf8 !important; }
    .stMetric, .stDataFrame, .stTextArea, .stButton { border-radius: 15px !important; }
    .stAlert { background-color: #1e293b !important; border: 1px solid #38bdf8 !important; color: #f8fafc !important; }
    .stButton>button { background: linear-gradient(90deg, #38bdf8, #0ea5e9) !important; color: white !important; border: none !important; padding: 10px 24px !important; font-weight: bold !important; width: 100%; }
    section[data-testid="stSidebar"] { background-color: #0f172a !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIKA PRO GENEROVÁNÍ E-MAILŮ ---
def get_professional_emails(item, price, lang):
    templates = {
        "DE": f"Betreff: Anfrage zu {item} - Verfügbarkeit\n\nSehr geehrte Damen und Herren,\n\nIch kontaktiere Sie bezüglich Ihres Inserats auf Maschinensucher. Wir vertreten einen Mandanten, der kurzfristig nach einem {item} sucht. Ist das Gerät noch verfügbar?\n\nMit freundlichen Grüßen,\nMatchMaster Trading EU",
        "EN": f"Subject: Inquiry regarding {item} - Availability\n\nDear Sir/Madam,\n\nWe are interested in your listing for {item}. We have a client ready for an immediate purchase. Please confirm the technical status and current location.\n\nBest regards,\nMatchMaster Trading EU",
        "PL": f"Temat: Zapytanie o {item} - Dostępność\n\nDzień dobry,\n\nKontaktuję się w sprawie ogłoszenia {item}. Mamy klienta zainteresowanego natychmiastowym zakupem. Czy oferta jest nadal aktualna?\n\nZ poważaniem,\nMatchMaster Trading EU"
    }
    return templates.get(lang, templates["EN"])

# --- 3. HLAVNÍ DASHBOARD ---
st.title("🇪🇺 MATCHMASTER AI")
st.write("### Evropský brokering náhradních dílů a strojů")

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png")
    st.header("Nastavení")
    api_key = st.text_input("Zadej Gemini API Key", type="password")
    st.divider()
    target_margin = st.slider("Požadovaná marže (EUR)", 200, 5000, 1000)
    platforms = st.multiselect("Sledované zdroje",
                              ["Machineseeker", "Surplex", "Mascus", "eBay DE", "OLX.pl"],
                              default=["Machineseeker", "Surplex"])

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔥 HORKÉ SHODY (Aukce & Inzerce)")
    deals = [
        {"Zdroj": "Machineseeker", "Předmět": "Bosch Rexroth Pump A10VO", "Cena": "850 €", "Tržní hodnota": "1 400 €", "Lokalita": "Německo"},
        {"Zdroj": "Surplex", "Předmět": "Final Drive JCB 3CX", "Cena": "1 100 €", "Tržní hodnota": "2 000 €", "Lokalita": "Itálie (Aukce)"},
        {"Zdroj": "OLX.pl", "Předmět": "Motor Perkins 1104", "Cena": "2 500 €", "Tržní hodnota": "3 800 €", "Lokalita": "Polsko"}
    ]
    st.table(pd.DataFrame(deals))

with col2:
    st.subheader("🛠️ Akce")
    selected_deal = st.selectbox("Vyber obchod k řešení", [d["Předmět"] for d in deals])
    st.metric("Potenciální zisk", "cca 550 €", delta="24%")
    lang = st.selectbox("Jazyk komunikace", ["DE", "EN", "PL", "CZ"])
    if st.button("GENEROVAT PROFESIONÁLNÍ E-MAILY"):
        emails = get_professional_emails(selected_deal, "X", lang)
        st.success("AI připravila e-maily s vysokou autoritou.")
        st.text_area("Návrh pro prodejce", emails, height=250)
        st.info("💡 Tip: Před odesláním se zeptej na 'Operating hours' a 'Maintenance history'.")

st.divider()
st.subheader("📥 Ruční vložení textu (Scraping z mobilu)")
manual_text = st.text_area("Vlož sem text z webu (třeba z Machineseekeru), který chceš analyzovat...")

if st.button("Analyzovat text pomocí AI"):
    if not api_key:
        st.error("Nejdřív vlož API klíč vlevo do panelu!")
    else:
        st.write("Analyzuji technické parametry a hledám shody napříč EU...")
        # Zde by proběhla magie s Gemini API
