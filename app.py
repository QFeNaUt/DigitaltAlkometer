import streamlit as st
from datetime import datetime, timedelta, date
import pytz # Bibliotek for tidssoner

# --- KONFIGURASJON ---
st.set_page_config(page_title="Alkokalkulator Norge", page_icon="🇳🇴")
st.title("🇳🇴 Promillekalkulator")

# --- TIDSSONE (Norge) ---
# Dette sikrer at "nå" er riktig uavhengig av hvor serveren står
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
        'tidspunkt': tidspunkt # Lagrer selve tidsobjektet
    })
    # Sorterer listen kronologisk basert på tidspunkt hver gang vi legger til noe
    st.session_state.drikke_liste.sort(key=lambda x: x['tidspunkt'])

def nullstill():
    st.session_state.drikke_liste = []

# --- DEFINISJON AV ENHETER ---
# Her kan du enkelt legge til flere valg i menyen
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

# Vi bruker st.form for å samle valgene før vi sender det inn
with st.form("drikke_skjema", clear_on_submit=False):
    col_a, col_b = st.columns(2)
    
    with col_a:
        # Nedtrekksmeny for drikke
        valgt_navn = st.selectbox("Velg enhet", list(meny_valg.keys()))
    
    with col_b:
        # Tidsvelger som standard er satt til NÅ (norsk tid)
        # Vi runder av til nærmeste minutt for penere visning
        naa_tid = hent_norsk_tid().time().replace(second=0, microsecond=0)
        valgt_tid = st.time_input("Klokkeslett", value=naa_tid)

    # Knapp for å sende inn
    submit = st.form_submit_button("Legg til i listen", use_container_width=True)

    if submit:
        # Hent data fra ordboken
        info = meny_valg[valgt_navn]
        
        # Vi må koble klokkeslettet til en dato (i dag) for å kunne regne med det
        dato_i_dag = hent_norsk_tid().date()
        full_tid = datetime.combine(dato_i_dag, valgt_tid)
        
        # Håndtering av nattmat: Hvis klokka er 02:00, men festen startet 20:00,
        # antar vi at 02:00 er "neste dag" hvis vi logger det mens det fortsatt er kveld.
        # (Dette er en forenkling, men fungerer greit for de fleste tilfeller).
        
        legg_til_i_liste(valgt_navn, info['vol'], info['pros'], full_tid)
        st.success(f"La til {valgt_navn} kl. {valgt_tid}")

# --- VISNING AV LISTE ---
if st.session_state.drikke_liste:
    st.divider()
    st.markdown("### 📋 Din drikkeliste (kronologisk)")
    
    for enhet in st.session_state.drikke_liste:
        klokke = enhet['tidspunkt'].strftime("%H:%M")
        st.text(f"🕗 {klokke} - {enhet['navn']}")
    
    if st.button("Slett alt", type="primary"):
        nullstill()
        st.rerun()

# --- BEREGNING ---
if st.session_state.drikke_liste:
    st.divider()
    st.subheader("📊 Resultat")
    
    # 1. Input parametere
    col1, col2 = st.columns(2)
    with col1:
        vekt = st.number_input("Din vekt (kg)", value=80, step=1)
    with col2:
        kjonn = st.radio("Kjønn", ["Mann", "Kvinne"], horizontal=True)

    if st.button("Oppdater beregning"):
        # Logikk: 
        # Starttidspunkt = Tiden for den aller FØRSTE enheten i listen.
        # Vi summerer all alkohol og later som forbrenningen starter ved første slurk.
        
        forste_drink = st.session_state.drikke_liste[0]['tidspunkt']
        
        total_alkohol_gram = 0
        for enhet in st.session_state.drikke_liste:
            gram = (enhet['volum_cl'] * 10) * (enhet['prosent'] / 100) * 0.8
            total_alkohol_gram += gram
            
        # Widmarks
        r = 0.70 if kjonn == "Mann" else 0.60
        maks_promille = total_alkohol_gram / (vekt * r)
        
        # Tid
        grense = 0.15
        forbrenning_per_time = 0.15
        
        if maks_promille <= grense:
            timer = 0
        else:
            timer = (maks_promille - grense) / forbrenning_per_time
            
        slutt_tid = forste_drink + timedelta(hours=timer)
        
        # --- GUI OUTPUT ---
        st.info(f"Startet å drikke: {forste_drink.strftime('%H:%M')}")
        st.write(f"Total inntak: {len(st.session_state.drikke_liste)} enheter")
        st.write(f"Teoretisk topp-promille: **{maks_promille:.2f}**")
        
        # Vis ferdig tidspunkt tydelig
        ferdig_klokke = slutt_tid.strftime('%H:%M')
        
        # Sjekk om det er neste dag
        dato_tekst = ""
        if slutt_tid.date() > forste_drink.date():
            dato_tekst = "(Neste dag)"
            
        st.markdown(f"## ✅ Kjørbar ca. kl. {ferdig_klokke} {dato_tekst}")
        st.caption("Basert på 0.15 promille-grense (buffer).")

else:
    st.info("Legg til enheter for å se beregningen.")
