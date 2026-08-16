import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import math
import random

# ==============================================================================
# KONFIGURATION & STILMALL
# ==============================================================================
st.set_page_config(
    page_title="GeoTrainer - Geodesi & Mätningsteknik",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Anpassad CSS för professionell och ren layout
st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .success-box {
        background-color: #ECFDF5;
        border-left: 5px solid #10B981;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #FEF2F2;
        border-left: 5px solid #EF4444;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
    .info-box {
        background-color: #EFF6FF;
        border-left: 5px solid #3B82F6;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# GEODETISKA HJÄLPFUNKTIONER (400-graderssystemet / Gon)
# ==============================================================================
def gon_to_rad(gon):
    """Konverterar gon (nygrader) till radianer."""
    return gon * (math.pi / 200.0)

def rad_to_gon(rad):
    """Konverterar radianer till gon (0 - 400 gon)."""
    g = rad * (200.0 / math.pi)
    return (g + 400.0) % 400.0

def polar_to_cartesian(n0, e0, h0, hz_gon, v_gon, s_dist, ih, th):
    """
    Beräknar rätvinkliga koordinater (N, E, H) från polära mätdata.
    hz_gon: Horisontell riktning (gon)
    v_gon: Zenitvinkel (gon)
    s_dist: Lutande längd (m)
    ih: Instrumenthöjd (m)
    th: Reflektorhöjd/Prismahöjd (m)
    """
    v_rad = gon_to_rad(v_gon)
    hz_rad = gon_to_rad(hz_gon)
    
    # Horisontell längd (HD) och höjdskillnad (dh)
    hd = s_dist * math.sin(v_rad)
    dh = s_dist * math.cos(v_rad) + ih - th
    
    # Koordinattillskott (Svensk standard: 0 gon = Norr, 100 gon = Öst)
    dn = hd * math.cos(hz_rad)
    de = hd * math.sin(hz_rad)
    
    n = n0 + dn
    e = e0 + de
    h = h0 + dh
    return n, e, h, hd, dh

def coordinate_geometry(n1, e1, n2, e2):
    """Beräknar plan längd och bäring (riktningsvinkel i gon) mellan två punkter."""
    dn = n2 - n1
    de = e2 - e1
    dist = math.sqrt(dn**2 + de**2)
    bearing_rad = math.atan2(de, dn)
    bearing_gon = rad_to_gon(bearing_rad)
    return dist, bearing_gon

# ==============================================================================
# INITIALISERING AV SESSION STATE
# ==============================================================================
if 'math_exercise' not in st.session_state:
    st.session_state.math_exercise = None

if 'sim_scenario' not in st.session_state:
    st.session_state.sim_scenario = None
if 'sim_score' not in st.session_state:
    st.session_state.sim_score = 0
if 'sim_total' not in st.session_state:
    st.session_state.sim_total = 0

# ==============================================================================
# SIDOMENY
# ==============================================================================
st.sidebar.markdown("# 📐 GeoTrainer")
st.sidebar.markdown("**Träningsplattform för mätningstekniker**")
st.sidebar.markdown("---")

app_mode = st.sidebar.radio(
    "Välj utbildningsmodul:",
    [
        "1. Yrkesmatematik & Geodesi",
        "2. Felteori & Felsökningssimulator",
        "3. 3D-Terräng & Mängdberäkning",
        "4. Utsättning & Toleranskontroll (AMA)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Standarder i appen:**\n"
    "- Vinkelenhet: **Gon** ($400^g = 360^\\circ$)\n"
    "- Koordinatsystem: Plan (**N, E**), Höjd (**H**)\n"
    "- Toleransnorm: **AMA Anläggning**"
)

# ==============================================================================
# MODUL 1: YRKESMATEMATIK & GEODESI
# ==============================================================================
if app_mode == "1. Yrkesmatematik & Geodesi":
    st.markdown('<div class="main-title">Modul 1: Yrkesmatematik & Geodetiska Beräkningar</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Träna på standardberäkningar inom totalstationsmätning, trigonometri och ledningsprojektering.</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs([
        "📍 Polär till Rätvinklig (Totalstation)",
        "📐 Fall & Lutningsberäkning (VA/Väg)",
        "🧭 Bäring & Längd (Koordinatgeometri)"
    ])
    
    # --------------------------------------------------------------------------
    # FLIK 1: POLÄR TILL RÄTVINKLIG
    # --------------------------------------------------------------------------
    with tab1:
        st.subheader("Omvandling från Polära till Rätvinkliga Koordinater")
        st.write("Beräkna koordinaterna $(N, E, H)$ för en inmätt punkt baserat på stationens koordinater och mätdata från totalstationen.")
        
        col_gen, col_empty = st.columns([1, 3])
        with col_gen:
            if st.button("🎲 Generera nytt övningstal", key="gen_polar"):
                st.session_state.math_exercise = {
                    "type": "polar",
                    "n0": round(random.uniform(6580000.0, 6585000.0), 3),
                    "e0": round(random.uniform(150000.0, 155000.0), 3),
                    "h0": round(random.uniform(25.0, 85.0), 3),
                    "hz": round(random.uniform(0.0, 399.999), 4),
                    "v": round(random.uniform(85.0, 115.0), 4), # Kring horisontalplanet (100 gon)
                    "s": round(random.uniform(15.0, 250.0), 3),
                    "ih": round(random.uniform(1.50, 1.80), 3),
                    "th": round(random.uniform(1.30, 2.15), 3)
                }
        
        if st.session_state.math_exercise and st.session_state.math_exercise.get("type") == "polar":
            ex = st.session_state.math_exercise
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("##### Stationspunkt ($P_0$)")
                st.write(f"**Norr ($N_0$):** `{ex['n0']:.3f}` m")
                st.write(f"**Öst ($E_0$):** `{ex['e0']:.3f}` m")
                st.write(f"**Höjd ($H_0$):** `{ex['h0']:.3f}` m")
                st.write(f"**Instrumenthöjd ($ih$):** `{ex['ih']:.3f}` m")
            with c2:
                st.markdown("##### Råmätdata från Totalstation")
                st.write(f"**Horisontell riktning ($Hz$):** `{ex['hz']:.4f}` gon")
                st.write(f"**Zenitvinkel ($V$):** `{ex['v']:.4f}` gon")
                st.write(f"**Lutande längd ($S$):** `{ex['s']:.3f}` m")
                st.write(f"**Prismahöjd ($th$):** `{ex['th']:.3f}` m")
            with c3:
                st.markdown("##### Testa ditt svar")
                user_n = st.number_input("Ditt beräknade N (m):", format="%.3f", key="p_n")
                user_e = st.number_input("Ditt beräknade E (m):", format="%.3f", key="p_e")
                user_h = st.number_input("Ditt beräknade H (m):", format="%.3f", key="p_h")
                
                check_btn = st.button("Kontrollera svar", key="check_polar")
            
            # Beräkna facit
            true_n, true_e, true_h, true_hd, true_dh = polar_to_cartesian(
                ex['n0'], ex['e0'], ex['h0'], ex['hz'], ex['v'], ex['s'], ex['ih'], ex['th']
            )
            
            if check_btn:
                tol = 0.005 # 5 mm tolerans för avrundningar
                ok_n = abs(user_n - true_n) <= tol
                ok_e = abs(user_e - true_e) <= tol
                ok_h = abs(user_h - true_h) <= tol
                
                if ok_n and ok_e and ok_h:
                    st.success(f"🎉 Utmärkt! Dina svar stämmer inom toleransen (±5 mm).")
                else:
                    st.error(f"❌ Inte helt rätt ännu. Se steg-för-steg-lösningen nedan.")
                
                with st.expander("📖 Se fullständig steg-för-steg-lösning", expanded=True):
                    st.markdown(f"""
                    **1. Omvandling av vinklar till radianer:**
                    - $V_{{rad}} = {ex['v']:.4f} \\times \\frac{{\\pi}}{{200}} = {gon_to_rad(ex['v']):.6f}\\text{{ rad}}$
                    - $Hz_{{rad}} = {ex['hz']:.4f} \\times \\frac{{\\pi}}{{200}} = {gon_to_rad(ex['hz']):.6f}\\text{{ rad}}$
                    
                    **2. Horisontell längd ($HD$) och höjdskillnad ($\\Delta H$):**
                    - $HD = S \\cdot \\sin(V) = {ex['s']:.3f} \\cdot \\sin({gon_to_rad(ex['v']):.6f}) = {true_hd:.4f}\\text{{ m}}$
                    - $\\Delta H = S \\cdot \\cos(V) + ih - th = {ex['s']:.3f} \\cdot \\cos({gon_to_rad(ex['v']):.6f}) + {ex['ih']:.3f} - {ex['th']:.3f} = {true_dh:.4f}\\text{{ m}}$
                    
                    **3. Koordinattillskott ($\\Delta N, \\Delta E$):**
                    - $\\Delta N = HD \\cdot \\cos(Hz) = {true_hd:.4f} \\cdot \\cos({gon_to_rad(ex['hz']):.6f}) = {true_hd * math.cos(gon_to_rad(ex['hz'])):.4f}\\text{{ m}}$
                    - $\\Delta E = HD \\cdot \\sin(Hz) = {true_hd:.4f} \\cdot \\sin({gon_to_rad(ex['hz']):.6f}) = {true_hd * math.sin(gon_to_rad(ex['hz'])):.4f}\\text{{ m}}$
                    
                    **4. Slutgiltiga koordinater:**
                    - **$N$** $= {ex['n0']:.3f} + ({true_hd * math.cos(gon_to_rad(ex['hz'])):.4f}) =$ **`{true_n:.3f}` m**
                    - **$E$** $= {ex['e0']:.3f} + ({true_hd * math.sin(gon_to_rad(ex['hz'])):.4f}) =$ **`{true_e:.3f}` m**
                    - **$H$** $= {ex['h0']:.3f} + ({true_dh:.4f}) =$ **`{true_h:.3f}` m**
                    """)
        else:
            st.info("Klicka på **'🎲 Generera nytt övningstal'** ovan för att starta en övning.")

    # --------------------------------------------------------------------------
    # FLIK 2: FALL OCH LUTNING
    # --------------------------------------------------------------------------
    with tab2:
        st.subheader("Fall- & Lutningsberäkning (VA-ledningar och vägsektioner)")
        st.write("Beräkna lutning i procent (%), promille (‰) samt erforderlig höjd vid schaktbotten eller rörläggning.")
        
        col_gen2, _ = st.columns([1, 3])
        with col_gen2:
            if st.button("🎲 Slumpa VA-ledningsscenario", key="gen_va"):
                st.session_state.math_exercise = {
                    "type": "va",
                    "h_start": round(random.uniform(32.50, 48.00), 3),
                    "length": round(random.uniform(25.0, 140.0), 2),
                    "fall_promille": round(random.uniform(5.0, 25.0), 1), # ‰
                }
        
        if st.session_state.math_exercise and st.session_state.math_exercise.get("type") == "va":
            va = st.session_state.math_exercise
            req_dh = (va['length'] * va['fall_promille']) / 1000.0
            h_slut_correct = va['h_start'] - req_dh
            lutning_pct = va['fall_promille'] / 10.0
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("##### Projekteringsdata")
                st.write(f"**Startbrunn / Inloppshöjd ($H_1$):** `{va['h_start']:.3f}` m")
                st.write(f"**Ledningssträcka ($L$):** `{va['length']:.2f}` m")
                st.write(f"**Föreskriven lutning:** `{va['fall_promille']:.1f}` ‰ (fall nedåt)")
            with c2:
                st.markdown("##### Dina svar")
                user_pct = st.number_input("Vad motsvarar detta i procent (%)?", format="%.2f", key="va_pct")
                user_h2 = st.number_input("Vad blir slutbrunnens höjd $H_2$ (m)?", format="%.3f", key="va_h2")
                va_check = st.button("Rätta svar", key="check_va")
                
            if va_check:
                if abs(user_pct - lutning_pct) < 0.05 and abs(user_h2 - h_slut_correct) < 0.005:
                    st.success(f"🎉 Helt rätt! Lutningen är {lutning_pct:.2f}% och slutgiltig invändig rörhöjd är {h_slut_correct:.3f} m.")
                else:
                    st.error(f"❌ Något blev fel. Kontrollera formlerna nedan.")
                    
                with st.expander("📖 Lösningsgång & Formler", expanded=True):
                    st.markdown(f"""
                    - **Omvandling Promille till Procent:**
                      $$\\text{{Lutning (\\%)}} = \\frac{{{va['fall_promille']:.1f}\\text{{ ‰}}}}{{10}} = {lutning_pct:.2f}\\%$$
                    - **Total höjdförlust (fall):**
                      $$\\Delta H = L \\cdot \\frac{{\\text{{promille}}}}{{1000}} = {va['length']:.2f} \\cdot \\frac{{{va['fall_promille']:.1f}}}{{1000}} = {req_dh:.3f}\\text{{ m}}$$
                    - **Sluthöjd:**
                      $$H_2 = H_1 - \\Delta H = {va['h_start']:.3f} - {req_dh:.3f} = \\mathbf{{{h_slut_correct:.3f}\\text{{ m}}}}$$
                    """)
        else:
            st.info("Klicka på **'🎲 Slumpa VA-ledningsscenario'** för att starta.")

    # --------------------------------------------------------------------------
    # FLIK 3: KOORDINATGEOMETRI (BÄRING & LÄNGD)
    # --------------------------------------------------------------------------
    with tab3:
        st.subheader("Koordinatgeometri: Tvåpunktsberäkning (Bäring & Avstånd)")
        st.write("Givet två kända stompunkter $P_1(N_1, E_1)$ och $P_2(N_2, E_2)$, beräkna det plana avståndet och bäringen (riktningsvinkeln) från $P_1$ till $P_2$.")
        
        col_gen3, _ = st.columns([1, 3])
        with col_gen3:
            if st.button("🎲 Slumpa två stompunkter", key="gen_cogo"):
                st.session_state.math_exercise = {
                    "type": "cogo",
                    "n1": round(random.uniform(6581000.0, 6582000.0), 3),
                    "e1": round(random.uniform(151000.0, 152000.0), 3),
                    "n2": round(random.uniform(6581000.0, 6582000.0), 3),
                    "e2": round(random.uniform(151000.0, 152000.0), 3),
                }
        
        if st.session_state.math_exercise and st.session_state.math_exercise.get("type") == "cogo":
            cg = st.session_state.math_exercise
            true_dist, true_bearing = coordinate_geometry(cg['n1'], cg['e1'], cg['n2'], cg['e2'])
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("##### Giltiga stompunkter")
                st.write(f"**Punkt 1 ($P_1$):** $N_1 = {cg['n1']:.3f}$, $E_1 = {cg['e1']:.3f}$")
                st.write(f"**Punkt 2 ($P_2$):** $N_2 = {cg['n2']:.3f}$, $E_2 = {cg['e2']:.3f}$")
            with c2:
                st.markdown("##### Dina beräknade värden")
                u_dist = st.number_input("Plan längd $D$ (m):", format="%.3f", key="cg_d")
                u_bear = st.number_input("Bäring $\\phi$ från $P_1$ till $P_2$ (gon):", format="%.4f", key="cg_b")
                cogo_check = st.button("Kontrollera svar", key="check_cogo")
                
            if cogo_check:
                if abs(u_dist - true_dist) < 0.01 and abs(u_bear - true_bearing) < 0.05:
                    st.success(f"🎉 Korrekt! Längd = {true_dist:.3f} m, Bäring = {true_bearing:.4f} gon.")
                else:
                    st.error("❌ Felaktigt resultat. Se förklaringen nedan.")
                    
                with st.expander("📖 Genomgång av formler", expanded=True):
                    dn = cg['n2'] - cg['n1']
                    de = cg['e2'] - cg['e1']
                    st.markdown(f"""
                    - **Koordinatdifferenser:**
                      - $\\Delta N = N_2 - N_1 = {cg['n2']:.3f} - {cg['n1']:.3f} = {dn:.3f}\\text{{ m}}$
                      - $\\Delta E = E_2 - E_1 = {cg['e2']:.3f} - {cg['e1']:.3f} = {de:.3f}\\text{{ m}}$
                    - **Pythagoras sats för plan längd:**
                      $$D = \\sqrt{{\\Delta N^2 + \\Delta E^2}} = \\sqrt{{{dn:.3f}^2 + {de:.3f}^2}} = \\mathbf{{{true_dist:.3f}\\text{{ m}}}}$$
                    - **Riktningsvinkel (Bäring i gon):**
                      $$\\theta = \\text{{atan2}}(\\Delta E, \\Delta N) = \\mathbf{{{true_bearing:.4f}\\text{{ gon}}}}$$
                    """)
        else:
            st.info("Klicka på **'🎲 Slumpa två stompunkter'** för att starta.")

# ==============================================================================
# MODUL 2: FELTEORI & RIMLIGHETSBEDÖMNING I REALTID
# ==============================================================================
elif app_mode == "2. Felteori & Felsökningssimulator":
    st.markdown('<div class="main-title">Modul 2: Geodetisk Felteori & Felsökningssimulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Agera mätningsingenjör i fält. Upptäck systematiska instrumentfel, atmosfäriska störningar och GNSS-avvikelser.</div>', unsafe_allow_html=True)
    
    SCENARIOS = [
        {
            "id": 1,
            "title": "Stomnätsetablering med 2.5 m prismastång i blåst",
            "context": "Du utför precisionsmätning av polygonpunkter med totalstation. Du mäter mot ett 360-gradersprisma på en 2.50 m hög stång. Det blåser kraftiga vindbyar (14 m/s).",
            "observations": "Dubbelmätning (läge 1 och läge 2) ger en differens i plan på 22 mm, medan höjdmätningen repeterar inom 1 mm.",
            "correct_action": "Underkänn",
            "correct_reason": "Prismastång ur lod / svajande stång",
            "explanation": "Vid hög stång och kraftig vind svajar prismat i sidled (planfel upp till flera centimeter), medan den vertikala komponenten förblir nästintill oförändrad. Åtgärd: Använd trefot med optiskt lod eller sänk stången till ett miniprisma."
        },
        {
            "id": 2,
            "title": "Inmätning av detaljpunkter med miniprisma",
            "context": "Du har bytt från standard rundprisma (prismakonstant -30 mm) till ett GMP111 miniprisma (konstant 0 mm), men glömde ändra prismatyp i mätboken.",
            "observations": "Kontrollmätning mot en känd stompunkt på 45 meters avstånd ger en längdavvikelse på exakt +30 mm jämfört med teoretiskt värde.",
            "correct_action": "Underkänn",
            "correct_reason": "Felaktig prismakonstant inställd",
            "explanation": "En felaktigt inställd prismakonstant adderar ett konstant systematiskt fel på alla uppmätta längder, oavsett avstånd till målet. Åtgärd: Korrigera prismakonstanten i fältdatorn innan vidare mätning."
        },
        {
            "id": 3,
            "title": "GNSS-RTK mätning intill hög reflekterande glasfasad",
            "context": "Du mäter in fastighetsgränser intill en 8 våningar hög byggnad med glas- och stålfasad. Fältdatorn visar 'RTK FIX'.",
            "observations": "PDOP = 3.8. Upprepad mätning av samma gränsrör med 10 minuters mellanrum ger en positionsdifferens på 78 mm i plan, trots att mottagaren indikerar 'Fixlösning'.",
            "correct_action": "Underkänn",
            "correct_reason": "GNSS Multipath (flervägsutbredning)",
            "explanation": "Nära reflekterande ytor studsar satellitsignalen innan den når antennen (multipath). Detta kan lura GNSS-mottagarens faslåsningsalgoritm att rapportera falsk 'Fix' med centimeternoggrannhet trots grova fel. Åtgärd: Mät med totalstation istället."
        },
        {
            "id": 4,
            "title": "Långdistansmätning över solvarm asfalterad motorväg",
            "context": "En varm sommardag (+32°C) ska du mäta in en fjärrpunkt på 850 meters avstånd tvärs över en nyasfalterad motorvägssträcka. Synfältet passerar 0.5 m ovanför asfalten.",
            "observations": "Siktesbilden dallrar kraftigt ('värmedaller') och vertikalvinkelmätningen driver med 15 mgon mellan mätserierna.",
            "correct_action": "Underkänn",
            "correct_reason": "Atmosfärisk refraktion & temperaturgradienter",
            "explanation": "Starka temperaturgradienter nära markytan kröker ljusstrålen kraftigt och asymmetriskt (marknära refraktion). Detta omöjliggör tillförlitlig trigonometrisk höjdbestämning. Åtgärd: Mät tidigt på morgonen innan marken värms upp."
        },
        {
            "id": 5,
            "title": "Finutsättning av bultgrupper med trefotsuppställt prisma",
            "context": "Utsättning av bultgrupper för stålpelare med tolerans ±3 mm. Totalstationen är friuppställd mot 4 kända stompunkter. Prismat är monterat i trefot på stativ.",
            "observations": "Standardavvikelse i stationsetableringen: $s_N = 0.8\\text{ mm}, s_E = 0.9\\text{ mm}, s_H = 0.5\\text{ mm}$. Backsight-kontroll visar 1 mm avvikelse.",
            "correct_action": "Godkänn",
            "correct_reason": "Inget fel - mätningen uppfyller kraven",
            "explanation": "Etableringen har utmärkt geometri och låg residual, stabilt fäste utan stångsvaj och kontrollerad backsight. Mätningen uppfyller kraven för finutsättning enligt högsta toleransklass."
        }
    ]
    
    # Skapa eller hämta scenario
    c_btn, c_stat = st.columns([1, 1])
    with c_btn:
        if st.button("🎲 Ladda ett slumpmässigt fältfall", key="gen_sim"):
            st.session_state.sim_scenario = random.choice(SCENARIOS)
            st.session_state.sim_answered = False
    
    with c_stat:
        st.metric("Ditt resultat i simulatorn", f"{st.session_state.sim_score} / {st.session_state.sim_total} godkända bedömningar")
        
    if st.session_state.sim_scenario is None:
        st.session_state.sim_scenario = SCENARIOS[0]
        st.session_state.sim_answered = False
        
    sc = st.session_state.sim_scenario
    
    st.markdown(f"### Scenario: {sc['title']}")
    
    col_sc1, col_sc2 = st.columns([3, 2])
    with col_sc1:
        st.markdown(f"""
        <div class="info-box">
            <b>📋 Förutsättningar i fält:</b><br>{sc['context']}<br><br>
            <b>🔍 Inhämtade mätvärden & observationer:</b><br>{sc['observations']}
        </div>
        """, unsafe_allow_html=True)
    
    with col_sc2:
        st.markdown("#### Din yrkesbedömning:")
        user_decision = st.radio("Vad gör du som ansvarig mätare?", ["Välj åtgärd...", "Godkänn mätning", "Underkänn mätning"])
        
        reason_options = [
            "Välj felorsak vid underkännande...",
            "Prismastång ur lod / svajande stång",
            "Felaktig prismakonstant inställd",
            "GNSS Multipath (flervägsutbredning)",
            "Atmosfärisk refraktion & temperaturgradienter",
            "Inget fel - mätningen uppfyller kraven"
        ]
        user_reason = st.selectbox("Identifierad orsak:", reason_options)
        
        submit_decision = st.button("Skicka in fältbeslut")
        
    if submit_decision:
        if user_decision == "Välj åtgärd...":
            st.warning("Du måste välja om du vill godkänna eller underkänna mätningen.")
        else:
            is_action_correct = (user_decision == f"{sc['correct_action']} mätning")
            is_reason_correct = (user_reason == sc['correct_reason'])
            
            st.session_state.sim_total += 1
            if is_action_correct and is_reason_correct:
                st.session_state.sim_score += 1
                st.markdown(f"""
                <div class="success-box">
                    <h4>✅ KORREKT BESLUT!</h4>
                    <b>Geodetisk förklaring:</b> {sc['explanation']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="error-box">
                    <h4>❌ FELAKTIGT BESLUT</h4>
                    <b>Rätt åtgärd:</b> {sc['correct_action']} mätning.<br>
                    <b>Rätt orsak:</b> {sc['correct_reason']}.<br><br>
                    <b>Förklaring:</b> {sc['explanation']}
                </div>
                """, unsafe_allow_html=True)

# ==============================================================================
# MODUL 3: 3D-TERRÄNGMODELL & MÄNGDBERÄKNING
# ==============================================================================
elif app_mode == "3. 3D-Terräng & Mängdberäkning":
    st.markdown('<div class="main-title">Modul 3: 3D-Terrängmodell & Mängdberäkning</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Interaktiv volymberäkning av schakt och fyllnad med 3D-nät och prismatisk cellmetod.</div>', unsafe_allow_html=True)
    
    col_ctrl, col_plot = st.columns([1, 2.5])
    
    with col_ctrl:
        st.markdown("#### ⚙️ Schakt- & Terrassparametrar")
        form_height = st.slider("Planerad terrassnivå / Schaktbotten (m):", min_value=20.0, max_value=40.0, value=28.5, step=0.25)
        grid_res = st.select_slider("Rutnätsupplösning i beräkning ($dx=dy$):", options=[4, 2, 1], value=2, help="Mindre cellstorlek ger högre precision i volymberäkningen.")
        
        truck_capacity = st.number_input("Lastbilsflakets kapacitet ($m^3$ fast mått):", value=12.0, step=1.0)
        swell_factor = st.slider("Svällningsfaktor schaktmassor (berg/jord):", min_value=1.10, max_value=1.50, value=1.25, step=0.05)
        
        st.markdown("---")
        st.markdown("##### 📌 Förklaring av färgskala:")
        st.markdown("- 🔴 **Schakt (Cut):** Befintlig mark ligger ovanför den planerade nivån.")
        st.markdown("- 🔵 **Fyll (Fill):** Befintlig mark ligger under den planerade nivån.")

    # Generera terrängmatris
    x_coords = np.arange(0, 100 + grid_res, grid_res)
    y_coords = np.arange(0, 100 + grid_res, grid_res)
    X, Y = np.meshgrid(x_coords, y_coords)
    
    # Syntetisk realistisk topografi (kulle och dalgång)
    Z_terrain = 28.0 + 7.0 * np.sin(X / 25.0) * np.cos(Y / 30.0) + 3.0 * np.cos(X / 15.0)
    Z_design = np.full_like(Z_terrain, form_height)
    
    # Volymberäkning per cell
    cell_area = grid_res * grid_res
    diff = Z_terrain - Z_design
    
    cut_matrix = np.where(diff > 0, diff, 0.0)
    fill_matrix = np.where(diff < 0, -diff, 0.0)
    
    vol_cut = float(np.sum(cut_matrix) * cell_area)
    vol_fill = float(np.sum(fill_matrix) * cell_area)
    net_vol = vol_cut - vol_fill
    trucks_needed = math.ceil((vol_cut * swell_factor) / truck_capacity) if vol_cut > 0 else 0
    
    with col_plot:
        # Skapa 3D Plotly Visualisering
        fig = go.Figure()
        
        # 1. Befintlig mark (Surface)
        fig.add_trace(go.Surface(
            z=Z_terrain, x=X, y=Y,
            colorscale="Viridis",
            name="Befintlig terräng",
            opacity=0.85,
            colorbar=dict(title="Markhöjd (m)", x=-0.15)
        ))
        
        # 2. Planerad schaktbotten (Plan)
        fig.add_trace(go.Surface(
            z=Z_design, x=X, y=Y,
            colorscale=[[0, 'rgba(239, 68, 68, 0.5)'], [1, 'rgba(239, 68, 68, 0.5)']],
            showscale=False,
            name="Projekterad nivå",
            opacity=0.6
        ))
        
        fig.update_layout(
            title="3D-visualisering: Terräng mot Projekterad terrass",
            scene=dict(
                xaxis_title="Öst (E) [m]",
                yaxis_title="Norr (N) [m]",
                zaxis_title="Höjd (H) [m]",
                zaxis=dict(range=[15, 45]),
                camera=dict(eye=dict(x=1.5, y=-1.5, z=1.2))
            ),
            margin=dict(l=0, r=0, b=0, t=40),
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Redovisning av massberäkning
    st.markdown("### 📊 Sammanställning av Mängdförteckning")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Schaktvolym (Fast mått)", f"{vol_cut:,.1f} m³".replace(",", " "))
    m2.metric("Fyllnadsvolym (Packat mått)", f"{vol_fill:,.1f} m³".replace(",", " "))
    m3.metric("Nettomassor (Schakt - Fyll)", f"{net_vol:+,.1f} m³".replace(",", " "))
    m4.metric("Beräknad borttransport", f"{trucks_needed} lastbilar", help="Inkluderar svällningsfaktor")
    
    # Detaljerad sektionstabell
    df_vol = pd.DataFrame({
        "Typ av massor": ["Schakt (Berg/Jord)", "Fyllnadsmaterial", "Nettobehov"],
        "Volym (m³ fast)": [round(vol_cut, 1), round(vol_fill, 1), round(net_vol, 1)],
        "Volym (m³ lös / svälld)": [round(vol_cut * swell_factor, 1), round(vol_fill * 1.05, 1), "-"],
        "Enhetskostnad schablon (kr/m³)": [180, 220, "-"],
        "Estimerad kostnad (kr)": [f"{int(vol_cut * 180):,} kr".replace(",", " "), f"{int(vol_fill * 220):,} kr".replace(",", " "), "-"]
    })
    st.table(df_vol)

# ==============================================================================
# MODUL 4: UTSÄTTNING & TOLERANSKONTROLL (AMA-SIMULATOR)
# ==============================================================================
elif app_mode == "4. Utsättning & Toleranskontroll (AMA)":
    st.markdown('<div class="main-title">Modul 4: Utsättning & Toleranskontroll (GeoPad / AMA)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Simulera fältarbete med fältdator: Jämför projekterade koordinater mot faktiskt inmätta lägen och granska mot AMA-krav.</div>', unsafe_allow_html=True)
    
    AMA_CLASSES = {
        "Husgrund / Pelare (Finutsättning)": {"tol_plane": 0.005, "tol_height": 0.005, "desc": "Byggnadsdelar med höga precisionskrav (±5 mm)."},
        "Kantsten & Finplanering": {"tol_plane": 0.010, "tol_height": 0.010, "desc": "Kantadstöd och linjeföring för gatumiljö (±10 mm)."},
        "Självfallsledning VA (Spillvatten)": {"tol_plane": 0.050, "tol_height": 0.010, "desc": "Måttligt plankrav (±50 mm) men extremt strängt höjdkrav (±10 mm) för fall."},
        "Vägkropp / Terrass": {"tol_plane": 0.050, "tol_height": 0.030, "desc": "Underbyggnad för väg och anläggningsytor (Plan: ±50 mm, Höjd: ±30 mm)."},
        "Grovschakt / Rörgrav": {"tol_plane": 0.100, "tol_height": 0.050, "desc": "Allmän grovschaktning (Plan: ±100 mm, Höjd: ±50 mm)."}
    }
    
    c_set1, c_set2 = st.columns([1, 1])
    
    with c_set1:
        st.markdown("#### 1. Välj Typ av Anläggningsarbete")
        work_type = st.selectbox("Anläggningstyp enligt AMA:", list(AMA_CLASSES.keys()))
        selected_tol = AMA_CLASSES[work_type]
        st.info(f"**Toleranskrav:** Plan $\\le \\pm {int(selected_tol['tol_plane']*1000)}$ mm | Höjd $\\le \\pm {int(selected_tol['tol_height']*1000)}$ mm\n\n_{selected_tol['desc']}_")
        
    with c_set2:
        st.markdown("#### 2. Punkthantering")
        sim_mode = st.radio("Metod:", ["Simulera 10 utsatta punkter automatiskt", "Mata in en punkt manuellt"])
        
    if sim_mode == "Simulera 10 utsatta punkter automatiskt":
        # Generera 10 slumpmässiga punkter kring ett tänkt centrum
        np.random.seed(42)
        base_n, base_e, base_h = 6582500.000, 153200.000, 45.000
        
        points_data = []
        for i in range(1, 11):
            p_n = base_n + i * 5.0
            p_e = base_e + (i % 3) * 4.0
            p_h = base_h + i * 0.1
            
            # Lägg till slumpmässig avvikelse (normalfördelat kring millimeternivå)
            err_n = np.random.normal(0, selected_tol['tol_plane'] * 0.7)
            err_e = np.random.normal(0, selected_tol['tol_plane'] * 0.7)
            err_h = np.random.normal(0, selected_tol['tol_height'] * 0.8)
            
            # Introducera något enstaka fel som överskrider toleransen
            if i in [3, 7]:
                err_e += selected_tol['tol_plane'] * 1.5
                err_h -= selected_tol['tol_height'] * 1.6
                
            m_n = p_n + err_n
            m_e = p_e + err_e
            m_h = p_h + err_h
            
            dn = (m_n - p_n) * 1000.0 # mm
            de = (m_e - p_e) * 1000.0 # mm
            dh = (m_h - p_h) * 1000.0 # mm
            dr = math.sqrt(dn**2 + de**2)
            
            plane_ok = (dr <= selected_tol['tol_plane'] * 1000.0)
            height_ok = (abs(dh) <= selected_tol['tol_height'] * 1000.0)
            overall_ok = plane_ok and height_ok
            
            points_data.append({
                "Punkt-ID": f"P{100+i}",
                "N Teo (m)": p_n, "E Teo (m)": p_e, "H Teo (m)": p_h,
                "ΔN (mm)": round(dn, 1),
                "ΔE (mm)": round(de, 1),
                "ΔH (mm)": round(dh, 1),
                "Planavvikelse dr (mm)": round(dr, 1),
                "Status": "✅ Godkänd" if overall_ok else "❌ Ej godkänd"
            })
            
        df_pts = pd.DataFrame(points_data)
        
        # Visa plankarta med Plotly
        fig_map = go.Figure()
        
        # Lägg till punkterna
        for _, row in df_pts.iterrows():
            color = "#10B981" if "Godkänd" in row["Status"] else "#EF4444"
            fig_map.add_trace(go.Scatter(
                x=[row["ΔE (mm)"]], y=[row["ΔN (mm)"]],
                mode="markers+text",
                text=[row["Punkt-ID"]],
                textposition="top center",
                marker=dict(size=12, color=color, line=dict(width=1, color="black")),
                name=row["Punkt-ID"],
                hoverinfo="text",
                hovertext=f"<b>{row['Punkt-ID']}</b><br>ΔE: {row['ΔE (mm)']} mm<br>ΔN: {row['ΔN (mm)']} mm<br>ΔH: {row['ΔH (mm)']} mm<br>Status: {row['Status']}"
            ))
            
        # Lägg till toleranscirkel
        theta = np.linspace(0, 2*np.pi, 100)
        tol_r = selected_tol['tol_plane'] * 1000.0
        fig_map.add_trace(go.Scatter(
            x=tol_r * np.cos(theta), y=tol_r * np.sin(theta),
            mode="lines",
            line=dict(color="rgba(16, 185, 129, 0.6)", dash="dash", width=2),
            name="Plantoleransgräns",
            hoverinfo="skip"
        ))
        
        fig_map.update_layout(
            title="Avvikelsediagram (Skillnad Inmätt - Projekterat) [mm]",
            xaxis_title="Avvikelse Öst ΔE (mm)",
            yaxis_title="Avvikelse Norr ΔN (mm)",
            yaxis=dict(scaleanchor="x", scaleratio=1),
            showlegend=False,
            height=450
        )
        
        c_map, c_res = st.columns([1.5, 1])
        with c_map:
            st.plotly_chart(fig_map, use_container_width=True)
        with c_res:
            st.markdown("#### 📋 Kvalitetskontrollrapport")
            total_pts = len(df_pts)
            passed_pts = len(df_pts[df_pts["Status"] == "✅ Godkänd"])
            st.metric("Godkända punkter", f"{passed_pts} / {total_pts} ({int(passed_pts/total_pts*100)}%)")
            
            if passed_pts == total_pts:
                st.success("Samtliga inmätta punkter ligger inom föreskrivna AMA-krav!")
            else:
                st.error(f"{total_pts - passed_pts} punkt(er) överskrider toleransen och kräver åtgärd i fält.")
                
        st.markdown("##### Detaljerad kontrolltabell")
        st.dataframe(df_pts, use_container_width=True)
        
    else:
        # Manuell inmatning
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            st.markdown("##### Projekterat teoretiskt läge")
            tn = st.number_input("Teoretiskt N (m):", value=6582500.000, format="%.3f")
            te = st.number_input("Teoretiskt E (m):", value=153200.000, format="%.3f")
            th = st.number_input("Teoretiskt H (m):", value=45.000, format="%.3f")
        with c_m2:
            st.markdown("##### Faktiskt inmätt läge i fält")
            mn = st.number_input("Inmätt N (m):", value=6582500.008, format="%.3f")
            me = st.number_input("Inmätt E (m):", value=153200.004, format="%.3f")
            mh = st.number_input("Inmätt H (m):", value=44.992, format="%.3f")
            
        dn = (mn - tn) * 1000.0
        de = (me - te) * 1000.0
        dh = (mh - th) * 1000.0
        dr = math.sqrt(dn**2 + de**2)
        
        ok_plane = dr <= selected_tol['tol_plane'] * 1000.0
        ok_h = abs(dh) <= selected_tol['tol_height'] * 1000.0
        
        st.markdown("---")
        st.markdown("#### Resultat & Fältinstruktion till utsättare:")
        
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("ΔN (Norr)", f"{dn:+.1f} mm")
        r2.metric("ΔE (Öst)", f"{de:+.1f} mm")
        r3.metric("Planavvikelse (dr)", f"{dr:.1f} mm", delta=f"Krav: ≤ {selected_tol['tol_plane']*1000:.0f} mm", delta_color="normal" if ok_plane else "inverse")
        r4.metric("ΔH (Höjd)", f"{dh:+.1f} mm", delta=f"Krav: ≤ {selected_tol['tol_height']*1000:.0f} mm", delta_color="normal" if ok_h else "inverse")
        
        # Fältinstruktion
        dir_n = "SÖDERUT" if dn > 0 else "NORRUT"
        dir_e = "VÄSTERUT" if de > 0 else "ÖSTERUT"
        dir_h = "SÄNK" if dh > 0 else "HÖJ"
        
        st.info(f"""
        🧭 **Fältinstruktion för justering av spik/prisma:**
        - Flytta prismat / markeringen **{abs(dn):.1f} mm {dir_n}**
        - Flytta prismat / markeringen **{abs(de):.1f} mm {dir_e}**
        - **{dir_h}** nivån med **{abs(dh):.1f} mm**
        """)

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("---")
st.markdown(
    "<center style='color: #9CA3AF; font-size: 0.85rem;'>"
    "GeoTrainer v1.0 • Utbildningsapplikation för Mätningstekniker & Geodetiska Ingenjörer • Byggd med Streamlit & Plotly"
    "</center>",
    unsafe_allow_html=True
)