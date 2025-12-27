# 🇳🇴 Norsk Promillekalkulator

En mobilvennlig webapplikasjon som hjelper deg å loggføre inntak av alkohol og beregne når du teoretisk sett er kjørbar igjen, tilpasset norske forhold.

## 📱 Prøv appen
**[KLIKK HER FOR Å ÅPNE KALKULATOREN](DIN_STREAMLIT_LINK_HER)**


## ✨ Funksjoner
* **Tidsstyring:** Legg inn drikkevarer med nøyaktig klokkeslett (f.eks. hvis du glemte å logge en øl for en time siden).
* **Norsk tid:** Bruker tidssonen `Europe/Oslo` for å sikre at klokkeslettene stemmer.
* **Smart sortering:** Listen sorteres automatisk kronologisk, uavhengig av hvilken rekkefølge du legger inn enhetene.
* **Sikkerhetsmargin:** Beregner tiden til du er nede på **0,15 promille** (under den lovlige grensen på 0,2).

## 🛠️ Hvordan bruke den
1.  Velg type drikke i listen (Øl, Vin, Sprit osv.).
2.  Juster klokkeslettet for når du inntok enheten.
3.  Trykk **"Legg til i listen"**.
4.  Gjenta for alle enheter.
5.  Trykk **"Oppdater beregning"** for å se når du er "grønn".

## ⚙️ Teknisk installasjon (Lokalt)
Hvis du vil kjøre appen på din egen PC i stedet for i skyen:

1.  **Klone prosjektet:**
    ```bash
    git clone [https://github.com/DITT_BRUKERNAVN/promille-kalkulator.git](https://github.com/DITT_BRUKERNAVN/promille-kalkulator.git)
    cd promille-kalkulator
    ```

2.  **Installer avhengigheter:**
    Det er viktig at du har både `streamlit` og `pytz` installert.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Kjør appen:**
    ```bash
    streamlit run app.py
    ```

## 🧮 Logikken bak tallene
* **Widmarks formel:** Brukes for å beregne promille basert på kjønn, vekt og alkoholmengde.
* **Forbrenning:** Appen bruker en konservativ forbrenningsrate på **0.15 promille per time**.
* **Starttid:** Forbrenningen beregnes fra tidspunktet du inntok den *første* enheten i listen.

## ⚠️ Ansvarsfraskrivelse (Disclaimer)
**Dette verktøyet gir kun et teoretisk estimat.**

Faktisk promille påvirkes av mange individuelle faktorer som mat i magen, genetikk, leverfunksjon og generell dagsform.
* Resultatet fra denne appen må **aldri** brukes som en garanti for at du er lovlig skikket til å kjøre bil.
* Er du usikker? La bilen stå.

---
Laget med Python og Streamlit.
