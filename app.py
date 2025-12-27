import streamlit as st
from datetime import datetime, timedelta
import pytz

# --- KONFIGURASJON ---
st.set_page_config(page_title="Alkokalkulator Norge", page_icon="🇳🇴")
st.title("🇳🇴 Promillekalkulator")

norsk_sone = pytz.timezone('Europe/Oslo')

def hent_norsk_tid():
    return datetime.now(norsk_sone)

# --- SESSION STATE ---
if 'drikke_liste' not in st.session_state:
    st.session_state.drikke_liste = []

# --- FUNKSJONER ---
def legg_til_i_liste(navn, volum, prosent, tidspunkt):
    st.session_state.drikke_liste.append({
        'navn': navn,
        'volum_cl': volum,
        'prosent': prosent,
        'tidspunkt': tidspunkt
    })
    # Sorterer listen kronologisk
    st.session_state.drikke_liste.sort(key=lambda x: x['tidspunkt'])

def nullstill():
    st.session_state.drikke_liste = []

# --- DEFINISJON AV ENHETER ---
meny_valg = {
    "Øl 0.33 (4.7%)":   {"vol": 33, "pros": 4.75},
    "Øl 0.50 (4.7%)":   {"vol": 50, "pros": 4.75},
    "Vin glass (12.5%)": {"vol": 12, "pros": 12.5},
    "Sprit shot (40%)": {"vol": 4,  "pros": 40.0},
    "Sprit shot (60%)": {"vol": 4,  "pros": 60.0},
    "Rusbrus 0.33 (4.5%)": {"vol": 33, "pros": 4.5},
}

# --- GUI: LEGG TIL ENHET ---
st.subheader("Registrer inntak")

with st.form("drikke_skjema", clear_on_submit=False):
    col_a, col_b = st.columns(2)
    with col_a:
        valgt_navn = st.selectbox("Velg enhet", list(meny_valg.keys()))
    with col_b:
        naa_tid = hent_norsk_tid().time().replace(second=0, microsecond=0)
        valgt_tid = st.time_input("Klokkeslett", value=naa_tid)

    submit = st.form_submit_button("Legg til i listen", use_container_width=True)

    if submit:
        info = meny_valg[valgt_navn]
        dato_i_dag = hent_norsk_tid().date()
        full_tid = datetime.combine(dato_i_dag, valgt_tid)
        
        # Enkel sjekk for nattmat (over midnatt)
        if full_tid.hour < 6 and hent_norsk_tid().hour > 18:
             full_tid += timedelta(days=1)
        
        # Konverter til tidssone-aware (så vi kan sammenligne med nå-tid)
        full_tid = norsk_sone.localize(full_tid)

        legg_til_i_liste(valgt_navn, info['vol'], info['pros'], full_tid)
        st.success(f"La til {valgt_navn} kl. {valgt_tid}")

# --- VISNING AV LISTE ---
if st.session_state.drikke_liste:
    st.divider()
    st.markdown("### 📋 Din drikkeliste")
    for enhet in st.session_state.drikke_liste:
        klokke = enhet['tidspunkt'].strftime("%H:%M")
        st.text(f"🕗 {klokke} - {enhet['navn']}")
    
    if st.button("Slett alt", type="primary"):
        nullstill()
        st.rerun()

# --- BEREGNING (SIMULERING) ---
if st.session_state.drikke_liste:
    st.divider()
    st.subheader("📊 Resultat")
    
    col1, col2 = st.columns(2)
    with col1:
        vekt = st.number_input("Din vekt (kg)", value=80, step=1)
    with col2:
        kjonn = st.radio("Kjønn", ["Mann", "Kvinne"], horizontal=True)

    if st.button("Oppdater beregning"):
        # 1. Konstanter
        r = 0.70 if kjonn == "Mann" else 0.60
        forbrenning_per_time = 0.15
        forbrenning_per_minutt = forbrenning_per_time / 60
        grense = 0.15

        # 2. Setup for simulering
        drikke_kopi = list(st.session_state.drikke_liste) # Kopi så vi ikke ødelegger originalen
        
        # Start simulering fra tidspunktet til første drink
        sim_tid = drikke_kopi[0]['tidspunkt']
        # Finn siste drink-tidspunkt for å vite når vi tidligst kan stoppe
        siste_drink_tid = drikke_kopi[-1]['tidspunkt']
        
        current_promille = 0.0
        
        # 3. Løkke: Gå fremover minutt for minutt
        # Vi fortsetter så lenge vi har drinker igjen i listen, 
        # ELLER promillen er for høy, ELLER vi ikke har passert siste drink
        while True:
            # A. Sjekk om det skal drikkes noe NÅ (i dette minuttet)
            # Vi bruker en while-løkke her i tilfelle man tar 2 shots på nøyaktig samme minutt
            while drikke_kopi and drikke_kopi[0]['tidspunkt'] <= sim_tid:
                drink = drikke_kopi.pop(0) # Ta ut drinken fra listen
                
                # Beregn promilleøkning for denne drinken
                alkohol_gram = (drink['volum_cl'] * 10) * (drink['prosent'] / 100) * 0.8
                promille_okning = alkohol_gram / (vekt * r)
                current_promille += promille_okning
            
            # B. Sjekk exit-betingelse
            # Hvis vi er ferdige med alle drinker, har passert siste tidspunkt, OG er under grensa
            if not drikke_kopi and sim_tid >= siste_drink_tid and current_promille <= grense:
                break

            # C. Forbrenning (ett minutt)
            current_promille -= forbrenning_per_minutt
            if current_promille < 0:
                current_promille = 0 # Kan ikke ha negativ promille (her er dødsonen!)

            # D. Gå ett minutt frem i tid
            sim_tid += timedelta(minutes=1)
            
            # Sikkerhetsventil (hvis loopen går amok i mer enn 48 timer)
            if (sim_tid - siste_drink_tid).total_seconds() > 172800:
                st.error("Noe gikk galt. Simuleringen ble stoppet.")
                break

        # --- RESULTAT VISNING ---
        st.success(f"Beregningen tar hensyn til pauser mellom drinker.")
        
        # Vis ferdig tidspunkt
        ferdig_klokke = sim_tid.strftime('%H:%M')
        
        dato_tekst = ""
        # Sjekk dato mot første drink
        start_dato = st.session_state.drikke_liste[0]['tidspunkt'].date()
        if sim_tid.date() > start_dato:
            dato_tekst = "(Neste dag)"
            
        st.markdown(f"## ✅ Kjørbar ca. kl. {ferdig_klokke} {dato_tekst}")
        st.caption(f"Basert på 0.15 promille-grense. Du blir edru mellom drinkene hvis pausen er lang nok.")

else:
    st.info("Legg til enheter for å se beregningen.")
