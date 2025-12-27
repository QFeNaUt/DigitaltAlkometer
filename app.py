import streamlit as st
from datetime import datetime, timedelta

# --- OPPSETT AV SIDEN ---
st.title("🍺 Promillekalkulator")

# --- SESSION STATE (Hukommelse) ---
# Nettsider glemmer alt hver gang du trykker på noe. 
# Vi må be den huske drikkelisten.
if 'drikke_liste' not in st.session_state:
    st.session_state.drikke_liste = []

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

start_tid = st.time_input("Startet å drikke", value=datetime.now().time())

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
    
    # Rød knapp for nullstilling
    if st.button("❌ Nullstill", type="primary"):
        nullstill()

# --- VISNING AV LISTE ---
if st.session_state.drikke_liste:
    antall = len(st.session_state.drikke_liste)
    st.info(f"Du har lagt til {antall} enheter.")
    
    # Vis liste over innhold (valgfritt)
    # st.write(st.session_state.drikke_liste)

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
        # Kombiner datoen i dag med klokkeslettet fra input
        start_dato_tid = datetime.combine(naa.date(), start_tid)
        
        # Hvis starttiden er senere på dagen enn "nå" (f.eks du tester kl 14:00 men setter start 18:00),
        # antar vi at det gjelder i dag. Hvis du beregner over midnatt, ordner timedelta biffen.
        
        slutt_tid = start_dato_tid + timedelta(hours=timer_til_edru)

        # --- RESULTAT ---
        st.success(f"Topp-promille: {maks_promille:.2f}")
        st.markdown(f"### Du er kjørbar (under 0.15):")
        st.markdown(f"# Kl. {slutt_tid.strftime('%H:%M')}")
        st.caption(f"(Dato: {slutt_tid.strftime('%d.%m')})")