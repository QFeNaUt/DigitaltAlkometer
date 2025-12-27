import streamlit as st
from datetime import datetime, timedelta

# --- OPPSETT AV SIDEN ---
st.set_page_config(page_title="Promillekalkulator", page_icon="🍺")
st.title("🍺 Promillekalkulator")

# --- SESSION STATE (Hukommelse) ---
# 1. Huske drikkeliste
if 'drikke_liste' not in st.session_state:
    st.session_state.drikke_liste = []

# 2. Huske starttidspunkt (NY FIKS)
# Vi setter starttid kun én gang (første gang appen åpnes)
if 'lagret_start_tid' not in st.session_state:
    # Setter standard til nå, men runder av sekundene
    naa = datetime.now().replace(second=0, microsecond=0)
    st.session_state['lagret_start_tid'] = naa.time()

# --- FUNKSJONER ---
def legg_til_drikke(navn, volum_cl, prosent):
    st.session_state.drikke_liste.append({
        'navn': navn, 
        'volum_cl': volum_cl, 
        'prosent': prosent
    })

def nullstill():
    st.session_state.drikke_liste = []

# --- INNDATA (Input) ---
col1, col2 = st.columns(2)
with col1:
    vekt = st.number_input("Vekt (kg)", value=80)
with col2:
    kjonn = st.radio("Kjønn", ["Mann", "Kvinne"])

# HER ER ENDRINGEN:
# Vi bruker key='lagret_start_tid'. Da kobles input-feltet direkte til hukommelsen.
# Streamlit vil nå prioritere det du velger, fremfor standardverdien.
start_tid = st.time_input("Startet å drikke", key='lagret_start_tid')

# --- KNAPPER FOR DRIKKE ---
st.subheader("Hva drikker du?")
col_a, col_b = st.columns(2)

with col_a:
    if st.button("🍺 Øl 0.33 (4.7%)"):
        legg_til_drikke("Øl 0.33", 33, 4.75)
    if st.button("🍺 Øl 0.50 (4.7%)"):
        legg_til_drikke("Øl 0.50", 50, 4.75)
    if st.button("🍷 Vin 0.12 (12.5%)"):
        legg_til_drikke("Vin", 12, 12.5)

with col_b:
    if st.button("🥃 Sprit 4cl (40%)"):
        legg_til_drikke("Sprit 40%", 4, 40)
    if st.button("🔥 Sprit 4cl (60%)"):
        legg_til_drikke("Sprit 60%", 4, 60)
    
    if st.button("❌ Nullstill", type="primary"):
        nullstill()

# --- VISNING AV LISTE ---
if st.session_state.drikke_liste:
    antall = len(st.session_state.drikke_liste)
    st.info(f"Du har lagt til {antall} enheter.")

# --- BEREGNING ---
if st.button("🚀 BEREGN NÅR DU ER KLAR", use_container_width=True):
    if not st.session_state.drikke_liste:
        st.error("Legg til drikke først!")
    else:
        # 1. Total alkohol i gram
        total_alkohol_gram = 0
        for drikke in st.session_state.drikke_liste:
            gram = (drikke['volum_cl'] * 10) * (drikke['prosent'] / 100) * 0.8
            total_alkohol_gram += gram

        # 2. Widmarks faktor
        r = 0.70 if kjonn == "Mann" else 0.60

        # 3. Beregn promille
        maks_promille = total_alkohol_gram / (vekt * r)

        # 4. Tid til 0.15
        grense = 0.15
        forbrenning_per_time = 0.15
        
        if maks_promille <= grense:
            timer_til_edru = 0
        else:
            timer_til_edru = (maks_promille - grense) / forbrenning_per_time

        # 5. Klokkeslett
        naa = datetime.now()
        start_dato_tid = datetime.combine(naa.date(), start_tid)
        
        # Håndtering av dato hvis man fester over midnatt
        # Hvis start_tid er mye høyere enn nå-tid, antar vi kanskje at det var i går? 
        # Men for enkelhets skyld antar vi her at datoen er "i dag" når festen starter.
        
        slutt_tid = start_dato_tid + timedelta(hours=timer_til_edru)
        
        # Hvis slutt-tid er før start-tid (f.eks. over midnatt), legg til en dag
        if slutt_tid < start_dato_tid:
             slutt_tid += timedelta(days=1)

        # --- RESULTAT ---
        st.success(f"Topp-promille: {maks_promille:.2f}")
        st.markdown(f"### Du er kjørbar (under 0.15):")
        
        # Hvis det går over midnatt, vis dato tydeligere
        dag_format = "%H:%M"
        if slutt_tid.day != start_dato_tid.day:
            st.warning("Merk: Dette er neste dag!")
            dag_format = "%H:%M (Dato: %d.%m)"
            
        st.markdown(f"# Kl. {slutt_tid.strftime(dag_format)}")
