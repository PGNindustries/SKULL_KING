import streamlit as st
import streamlit.components.v1 as components
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    layout="wide",
    page_title="Skull King Pirata",
    page_icon="🏴‍☠️"
)

# Ocultar la UI de Streamlit para pantalla completa
hide_st_style = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding: 0rem !important;
        max-width: 100% !important;
    }
    [data-testid="stAppViewContainer"] {
        padding: 0 !important;
    }
    iframe {
        border: none !important;
        display: block !important;
    }
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# =====================================================================
# CONFIGURACIÓN DE FIREBASE
# =====================================================================
try:
    FIREBASE_API_KEY        = st.secrets["firebase"]["apiKey"]
    FIREBASE_AUTH_DOMAIN    = st.secrets["firebase"]["authDomain"]
    FIREBASE_PROJECT_ID     = st.secrets["firebase"]["projectId"]
    FIREBASE_STORAGE_BUCKET = st.secrets["firebase"]["storageBucket"]
    FIREBASE_MESSAGING_ID   = st.secrets["firebase"]["messagingSenderId"]
    FIREBASE_APP_ID         = st.secrets["firebase"]["appId"]
except Exception:
    FIREBASE_API_KEY        = os.environ.get("FIREBASE_API_KEY", "TU_API_KEY")
    FIREBASE_AUTH_DOMAIN    = os.environ.get("FIREBASE_AUTH_DOMAIN", "tu-proyecto.firebaseapp.com")
    FIREBASE_PROJECT_ID     = os.environ.get("FIREBASE_PROJECT_ID", "tu-proyecto")
    FIREBASE_STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET", "tu-proyecto.appspot.com")
    FIREBASE_MESSAGING_ID   = os.environ.get("FIREBASE_MESSAGING_ID", "000000000000")
    FIREBASE_APP_ID         = os.environ.get("FIREBASE_APP_ID", "1:000000000000:web:abc123")

firebase_configured = FIREBASE_API_KEY not in ("TU_API_KEY", "", None)

if not firebase_configured:
    st.error("""
    ⚠️ **Firebase no está configurado.**
    
    Para jugar online necesitas configurar Firebase.  
    Sigue las instrucciones del archivo **README.md** incluido en este proyecto.
    """)
    st.stop()

# --- CÓDIGO HTML DEL JUEGO (con Firebase inyectado) ---
html_code = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Skull King</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700;900&family=Cinzel:wght@400;600;700;900&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <style>
        .custom-scrollbar::-webkit-scrollbar {{ width: 6px; }}
        .custom-scrollbar::-webkit-scrollbar-track {{ background: #1e293b; }}
        .custom-scrollbar::-webkit-scrollbar-thumb {{ background: #c5a059; border-radius: 4px; }}
        .hide-scrollbar::-webkit-scrollbar {{ display: none; }}
        .hide-scrollbar {{ -ms-overflow-style: none; scrollbar-width: none; }}
        body {{ margin: 0; overflow: hidden; background-color: #0f172a; height: 100vh; }}
        #root {{ height: 100vh; overflow: hidden; }}
        @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(10px); }} to {{ opacity:1; transform:translateY(0); }} }}
        @keyframes scaleIn {{ from {{ opacity:0; transform:scale(0.9); }} to {{ opacity:1; transform:scale(1); }} }}
        @keyframes countdown {{ from {{ stroke-dashoffset: 0; }} to {{ stroke-dashoffset: 283; }} }}
        .animate-fadeIn {{ animation: fadeIn 0.3s ease-out; }}
        .animate-scaleIn {{ animation: scaleIn 0.3s ease-out; }}
        .countdown-ring {{ animation: countdown 3s linear forwards; }}
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel" data-presets="react" data-type="module">
        import React, {{ useState, useEffect, useMemo, useRef }} from 'https://esm.sh/react@18';
        import {{ createRoot }} from 'https://esm.sh/react-dom@18/client';
        import {{ initializeApp }} from 'https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js';
        import {{ getAuth, signInAnonymously, onAuthStateChanged }} from 'https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js';
        import {{ getFirestore, doc, setDoc, onSnapshot, updateDoc, runTransaction, serverTimestamp }} from 'https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js';
        import {{ Skull, Anchor, Map, Trees, Coins, XCircle, Flag, Trophy, Users, PlayCircle, LogIn, Crown, Swords, Ghost, HelpCircle, Copy, Check, Loader, AlertCircle, ArrowUp, ArrowDown, Handshake, RefreshCw, Eye, Gavel, ListOrdered, X, Compass, Ship, Home, ChevronDown, ChevronUp }} from 'https://esm.sh/lucide-react@0.358.0';

        // =====================================================================
        // CONFIGURACIÓN DE FIREBASE
        // =====================================================================
        const firebaseConfig = {{
            apiKey:            "{FIREBASE_API_KEY}",
            authDomain:        "{FIREBASE_AUTH_DOMAIN}",
            projectId:         "{FIREBASE_PROJECT_ID}",
            storageBucket:     "{FIREBASE_STORAGE_BUCKET}",
            messagingSenderId: "{FIREBASE_MESSAGING_ID}",
            appId:             "{FIREBASE_APP_ID}"
        }};

        const app = initializeApp(firebaseConfig);
        const auth = getAuth(app);
        const db = getFirestore(app);
        const ROOM_COLLECTION = 'skull_king_rooms';

        // =====================================================================
        // UTILIDADES Y CONSTANTES
        // =====================================================================
        const SUITS = {{
            PARROT: {{ color: 'bg-emerald-700', text: 'text-emerald-100', border: 'border-emerald-900', icon: Trees,  label: 'Loro',        bonus: 10 }},
            MAP:    {{ color: 'bg-indigo-700',  text: 'text-indigo-100',  border: 'border-indigo-900',  icon: Map,    label: 'Mapa',        bonus: 10 }},
            CHEST:  {{ color: 'bg-amber-600',   text: 'text-amber-100',   border: 'border-amber-900',   icon: Coins,  label: 'Cofre',       bonus: 10 }},
            TRUMP:  {{ color: 'bg-gray-900',    text: 'text-gray-100',    border: 'border-black',       icon: Skull,  label: 'Jolly Roger', bonus: 20 }}
        }};

        const CARD_TYPES = {{
            SUIT: 'suit', ESCAPE: 'escape', PIRATE: 'pirate', SKULLKING: 'skullking',
            MERMAID: 'mermaid', TIGRESS: 'tigress', KRAKEN: 'kraken', WHALE: 'whale', COINS: 'coins'
        }};

        const PIRATE_NAMES = {{
            PEDRO:  {{ name: 'Capitán Pedro',        desc: 'Modifica tu apuesta (-1, 0, +1)' }},
            ELIAS:  {{ name: 'Contramaestre Elías',  desc: 'Apuesta secundaria (0, 10, 20)' }},
            JAVI:   {{ name: 'Vigía Javi',           desc: 'Siguiente ronda gana la carta más baja' }},
            SERGIO: {{ name: 'Timonel Sergio',       desc: 'Elige quién empieza la siguiente' }},
            TORRI:  {{ name: 'Corsario Torri',       desc: 'Intercambia mano con otro jugador' }}
        }};

        const generateRoomId = () => {{
            const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
            let result = '';
            for (let i = 0; i < 5; i++) result += chars.charAt(Math.floor(Math.random() * chars.length));
            return result;
        }};

        const generateDeck = () => {{
            let deck = [];
            let id = 0;
            ['PARROT','MAP','CHEST'].forEach(s => {{
                for (let i = 1; i <= 14; i++)
                    deck.push({{ id:`c-${{id++}}`, type:CARD_TYPES.SUIT, suit:s, value:i, rank:i, bonus: i===14?10:0 }});
            }});
            for (let i = 1; i <= 14; i++)
                deck.push({{ id:`c-${{id++}}`, type:CARD_TYPES.SUIT, suit:'TRUMP', value:i, rank:20+i, bonus:i===14?20:0 }});
            for (let i = 0; i < 5; i++)
                deck.push({{ id:`c-${{id++}}`, type:CARD_TYPES.ESCAPE, value:0, label:'Huida' }});
            Object.keys(PIRATE_NAMES).forEach(k =>
                deck.push({{ id:`c-${{id++}}`, type:CARD_TYPES.PIRATE, value:50, label:'Pirata', pirateId:k }})
            );
            deck.push({{ id:`c-${{id++}}`, type:CARD_TYPES.TIGRESS,  value:55, label:'Tigresa' }});
            deck.push({{ id:`c-${{id++}}`, type:CARD_TYPES.SKULLKING, value:60, label:'Skull King' }});
            deck.push({{ id:`c-${{id++}}`, type:CARD_TYPES.MERMAID,  value:45, label:'Sirena 1' }});
            deck.push({{ id:`c-${{id++}}`, type:CARD_TYPES.MERMAID,  value:45, label:'Sirena 2' }});
            deck.push({{ id:`c-${{id++}}`, type:CARD_TYPES.KRAKEN,   value:0,  label:'Kraken' }});
            deck.push({{ id:`c-${{id++}}`, type:CARD_TYPES.WHALE,    value:0,  label:'Ballena' }});
            deck.push({{ id:`c-${{id++}}`, type:CARD_TYPES.COINS,    value:0,  label:'Monedas' }});
            // Barajar
            for (let i = deck.length - 1; i > 0; i--) {{
                const j = Math.floor(Math.random() * (i + 1));
                [deck[i], deck[j]] = [deck[j], deck[i]];
            }}
            return deck;
        }};

        const determineTrickWinner = (playedCards, isLowCardMode = false) => {{
            if (!playedCards || playedCards.length === 0) return null;
            const sorted = [...playedCards].sort((a,b) => a.order - b.order);

            if (sorted.some(p => p.card.type === CARD_TYPES.KRAKEN)) return 'KRAKEN';

            if (isLowCardMode) {{
                const nums = sorted.filter(p => p.card.type === CARD_TYPES.SUIT);
                if (nums.length > 0) return nums.sort((a,b) => a.card.value - b.card.value)[0].playerId;
                return sorted[0].playerId;
            }}

            if (sorted.some(p => p.card.type === CARD_TYPES.WHALE)) {{
                const nums = sorted.filter(p => p.card.type === CARD_TYPES.SUIT);
                if (nums.length > 0) return nums.sort((a,b) => b.card.value - a.card.value)[0].playerId;
                const first = sorted.find(p => p.card.type !== CARD_TYPES.WHALE);
                return first ? first.playerId : sorted[0].playerId;
            }}

            const hasSK  = sorted.some(p => p.card.type === CARD_TYPES.SKULLKING);
            const hasMer = sorted.some(p => p.card.type === CARD_TYPES.MERMAID);
            const hasPir = sorted.some(p => p.card.type === CARD_TYPES.PIRATE || (p.card.type === CARD_TYPES.TIGRESS && p.card.playedAs === 'pirate'));

            if (hasSK) {{
                if (hasMer) {{
                    const sk  = sorted.find(p => p.card.type === CARD_TYPES.SKULLKING);
                    const mer = sorted.find(p => p.card.type === CARD_TYPES.MERMAID);
                    return (mer.order > sk.order) ? mer.playerId : sk.playerId;
                }}
                return sorted.find(p => p.card.type === CARD_TYPES.SKULLKING).playerId;
            }}
            if (hasPir) return sorted.find(p => p.card.type === CARD_TYPES.PIRATE || (p.card.type === CARD_TYPES.TIGRESS && p.card.playedAs === 'pirate')).playerId;
            if (hasMer) return sorted.find(p => p.card.type === CARD_TYPES.MERMAID).playerId;

            const active = sorted.filter(p =>
                p.card.type !== CARD_TYPES.ESCAPE &&
                p.card.type !== CARD_TYPES.COINS &&
                !(p.card.type === CARD_TYPES.TIGRESS && p.card.playedAs === 'escape')
            );
            if (active.length === 0) return sorted[0].playerId;

            const leadSuit = active[0].card.type === CARD_TYPES.SUIT ? active[0].card.suit : null;
            let best = active[0];
            for (let i = 1; i < active.length; i++) {{
                const c = active[i].card, w = best.card;
                if (c.suit === 'TRUMP' && w.suit !== 'TRUMP') {{ best = active[i]; continue; }}
                if (c.suit === 'TRUMP' && w.suit === 'TRUMP') {{ if (c.value > w.value) best = active[i]; continue; }}
                if (w.suit !== 'TRUMP') {{
                    if (c.suit === leadSuit && w.suit === leadSuit) {{ if (c.value > w.value) best = active[i]; }}
                    else if (c.suit === leadSuit && w.suit !== leadSuit) best = active[i];
                }}
            }}
            return best.playerId;
        }};

        // =====================================================================
        // COMPONENTES UI (Cartas y Modal de Ayuda)
        // =====================================================================
        const Waves = ({{size}}) => (
            <svg width={{size}} height={{size}} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/>
                <path d="M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/>
                <path d="M2 18c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/>
            </svg>
        );

        // =====================================================================
        // CARD COMPONENT — Diseño ilustrado estilo Skull King original
        // =====================================================================
        const CARD_ART = {{
            // Palos — gradientes temáticos + emoji ilustración central
            SUIT_PARROT:  {{ bg: 'linear-gradient(160deg,#134e2a 0%,#1a6b36 40%,#0d3d1f 100%)', frame: '#4ade80', shine: '#86efac', emoji: '🦜', accent: '#bbf7d0' }},
            SUIT_MAP:     {{ bg: 'linear-gradient(160deg,#1e1b5e 0%,#3730a3 40%,#0f0e3a 100%)', frame: '#818cf8', shine: '#c7d2fe', emoji: '🗺️', accent: '#e0e7ff' }},
            SUIT_CHEST:   {{ bg: 'linear-gradient(160deg,#78350f 0%,#b45309 40%,#451a03 100%)', frame: '#fbbf24', shine: '#fde68a', emoji: '💰', accent: '#fef3c7' }},
            SUIT_TRUMP:   {{ bg: 'linear-gradient(160deg,#0a0a0a 0%,#1c1917 40%,#000000 100%)', frame: '#ffd700', shine: '#fffbeb', emoji: '💀', accent: '#fef9c3' }},
            // Especiales
            ESCAPE:       {{ bg: 'linear-gradient(160deg,#0c4a6e 0%,#0369a1 40%,#082f49 100%)', frame: '#7dd3fc', shine: '#e0f2fe', emoji: '🏳️', accent: '#bae6fd' }},
            SKULLKING:    {{ bg: 'linear-gradient(160deg,#1a0a00 0%,#3d1a00 30%,#000000 100%)', frame: '#ffd700', shine: '#fef08a', emoji: '👑', accent: '#fef9c3' }},
            MERMAID:      {{ bg: 'linear-gradient(160deg,#0a3d52 0%,#0e7490 40%,#052e3d 100%)', frame: '#22d3ee', shine: '#a5f3fc', emoji: '🧜', accent: '#cffafe' }},
            TIGRESS:      {{ bg: 'linear-gradient(160deg,#431407 0%,#9a3412 40%,#1c0701 100%)', frame: '#fb923c', shine: '#fed7aa', emoji: '🐅', accent: '#ffedd5' }},
            KRAKEN:       {{ bg: 'linear-gradient(160deg,#022c22 0%,#065f46 40%,#011916 100%)', frame: '#34d399', shine: '#6ee7b7', emoji: '🐙', accent: '#d1fae5' }},
            WHALE:        {{ bg: 'linear-gradient(160deg,#0c1445 0%,#1d3461 40%,#060a1f 100%)', frame: '#60a5fa', shine: '#bfdbfe', emoji: '🐋', accent: '#dbeafe' }},
            COINS:        {{ bg: 'linear-gradient(160deg,#422006 0%,#854d0e 40%,#1c0a00 100%)', frame: '#facc15', shine: '#fef08a', emoji: '🤝', accent: '#fefce8' }},
            PIRATE:       {{ bg: 'linear-gradient(160deg,#3b0014 0%,#7f1d1d 40%,#1a000a 100%)', frame: '#f87171', shine: '#fecaca', emoji: '⚔️', accent: '#fee2e2' }},
        }};

        const CardSVGDefs = () => (
            <svg width="0" height="0" style={{{{position:'absolute'}}}}>
                <defs>
                    <filter id="card-glow-gold">
                        <feGaussianBlur stdDeviation="3" result="blur"/>
                        <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                    </filter>
                    <filter id="card-inner-shadow">
                        <feOffset dx="0" dy="1"/>
                        <feGaussianBlur stdDeviation="2"/>
                        <feComposite operator="out" in="SourceGraphic"/>
                    </filter>
                </defs>
            </svg>
        );

        const Card = ({{ card, onClick, playable = false, size = 'normal', hidden = false }}) => {{
            const sm = size === 'small';

            // Carta oculta (dorso)
            if (hidden) return (
                <div style={{{{
                    width: sm?'40px':'96px', height: sm?'56px':'144px',
                    background: 'linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%)',
                    borderRadius: sm?'5px':'10px',
                    border: '2px solid #c5a059',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.1)',
                    display:'flex', alignItems:'center', justifyContent:'center',
                    flexShrink:0, position:'relative', overflow:'hidden'
                }}}}>
                    {{/* Patrón de fondo del dorso */}}
                    <div style={{{{
                        position:'absolute', inset:0, opacity:0.15,
                        backgroundImage: `repeating-linear-gradient(45deg, #c5a059 0px, #c5a059 1px, transparent 1px, transparent 8px),
                                         repeating-linear-gradient(-45deg, #c5a059 0px, #c5a059 1px, transparent 1px, transparent 8px)`
                    }}}}/>
                    <Skull style={{{{color:'#c5a059', opacity:0.5}}}} size={{sm?14:28}}/>
                </div>
            );

            // Determinar arte según tipo
            const isSuit = card.type === CARD_TYPES.SUIT;
            let art, label, subLabel, Icon, numValue;

            if (isSuit) {{
                const artKey = `SUIT_${{card.suit}}`;
                art = CARD_ART[artKey];
                numValue = card.value;
                label = SUITS[card.suit].label;
                Icon = SUITS[card.suit].icon;
                subLabel = null;
            }} else {{
                switch(card.type) {{
                    case CARD_TYPES.ESCAPE:    art=CARD_ART.ESCAPE;    label='Huida';    subLabel=null;                                  Icon=Flag;      numValue=null; break;
                    case CARD_TYPES.PIRATE:    art=CARD_ART.PIRATE;    label=PIRATE_NAMES[card.pirateId]?.name||'Pirata'; subLabel='Pirata'; Icon=Swords;  numValue=null; break;
                    case CARD_TYPES.SKULLKING: art=CARD_ART.SKULLKING; label='Skull King'; subLabel=null;                                Icon=Crown;     numValue=null; break;
                    case CARD_TYPES.MERMAID:   art=CARD_ART.MERMAID;   label='Sirena';   subLabel=null;                                  Icon=Anchor;    numValue=null; break;
                    case CARD_TYPES.TIGRESS:   art=CARD_ART.TIGRESS;   label='Tigresa';  subLabel=null;                                  Icon=Ghost;     numValue=null; break;
                    case CARD_TYPES.KRAKEN:    art=CARD_ART.KRAKEN;    label='Kraken';   subLabel=null;                                  Icon=XCircle;   numValue=null; break;
                    case CARD_TYPES.WHALE:     art=CARD_ART.WHALE;     label='Ballena';  subLabel=null;                                  Icon=Waves;     numValue=null; break;
                    case CARD_TYPES.COINS:     art=CARD_ART.COINS;     label='Alianza';  subLabel=null;                                  Icon=Handshake; numValue=null; break;
                    default:                   art=CARD_ART.PIRATE;    label='?';        subLabel=null;                                  Icon=HelpCircle;numValue=null;
                }}
            }}

            const W = sm ? 48 : 96;
            const H = sm ? 68 : 144;
            const R = sm ? 5 : 9;

            // Truncar nombre de pirata para cartas pequeñas
            const displayLabel = sm && label.length > 8 ? label.split(' ').pop() : label;

            return (
                <div
                    onClick={{onClick}}
                    style={{{{
                        width:`${{W}}px`, height:`${{H}}px`,
                        background: art.bg,
                        borderRadius:`${{R}}px`,
                        border: `${{sm?'1.5':'2'}}px solid ${{art.frame}}`,
                        boxShadow: playable
                            ? `0 0 0 2px #ffd700, 0 0 12px rgba(255,215,0,0.5), 0 6px 20px rgba(0,0,0,0.7), inset 0 1px 0 rgba(255,255,255,0.15)`
                            : `0 4px 14px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.08)`,
                        cursor: playable ? 'pointer' : 'not-allowed',
                        opacity: playable ? 1 : 0.72,
                        filter: playable ? 'none' : 'brightness(0.8)',
                        flexShrink: 0,
                        position: 'relative',
                        overflow: 'hidden',
                        transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                        userSelect: 'none',
                        fontFamily: "'Cinzel', 'Georgia', serif",
                    }}}}
                    className={{sm ? '' : 'hover:-translate-y-4 hover:z-10'}}
                >
                    {{/* Brillo diagonal superior */}}
                    <div style={{{{
                        position:'absolute', top:0, left:0, right:0, height:`${{H*0.45}}px`,
                        background:`linear-gradient(180deg, ${{art.shine}}18 0%, transparent 100%)`,
                        borderRadius:`${{R}}px ${{R}}px 0 0`, pointerEvents:'none', zIndex:1
                    }}}}/>

                    {{/* Marco interior ornamentado */}}
                    <div style={{{{
                        position:'absolute',
                        inset: sm?'2px':'4px',
                        borderRadius:`${{R-2}}px`,
                        border:`1px solid ${{art.frame}}44`,
                        pointerEvents:'none', zIndex:2
                    }}}}/>

                    {{/* Esquinas decorativas (solo tamaño normal) */}}
                    {{!sm && <>
                        {{[{{t:'2px',l:'2px'}},{{t:'2px',r:'2px'}},{{b:'2px',l:'2px'}},{{b:'2px',r:'2px'}}].map((pos,i)=>(
                            <div key={{i}} style={{{{
                                position:'absolute', width:'10px', height:'10px',
                                borderTop: i<2?`1.5px solid ${{art.frame}}`:undefined,
                                borderBottom: i>=2?`1.5px solid ${{art.frame}}`:undefined,
                                borderLeft: (i===0||i===2)?`1.5px solid ${{art.frame}}`:undefined,
                                borderRight: (i===1||i===3)?`1.5px solid ${{art.frame}}`:undefined,
                                ...pos, zIndex:3, pointerEvents:'none'
                            }}}}/>
                        ))}}
                    </>}}

                    {{/* Número (esquina superior izquierda) */}}
                    {{numValue !== null && (
                        <div style={{{{
                            position:'absolute',
                            top: sm?'2px':'5px', left: sm?'3px':'6px',
                            zIndex:4, lineHeight:1,
                            display:'flex', flexDirection:'column', alignItems:'center',
                        }}}}>
                            <span style={{{{
                                fontSize: sm?'11px':'18px',
                                fontWeight:'900',
                                color: art.shine,
                                textShadow:`0 1px 3px rgba(0,0,0,0.8), 0 0 8px ${{art.frame}}88`,
                                letterSpacing:'-0.5px'
                            }}}}>{{numValue}}</span>
                            {{!sm && <Icon size={{9}} style={{{{color:art.accent, marginTop:'1px'}}}}/>}}
                        </div>
                    )}}

                    {{/* Número espejo (esquina inferior derecha) */}}
                    {{numValue !== null && !sm && (
                        <div style={{{{
                            position:'absolute', bottom:'5px', right:'6px',
                            zIndex:4, transform:'rotate(180deg)', lineHeight:1,
                            display:'flex', flexDirection:'column', alignItems:'center',
                        }}}}>
                            <span style={{{{
                                fontSize:'18px', fontWeight:'900',
                                color: art.shine,
                                textShadow:`0 1px 3px rgba(0,0,0,0.8), 0 0 8px ${{art.frame}}88`,
                                letterSpacing:'-0.5px'
                            }}}}>{{numValue}}</span>
                            <Icon size={{9}} style={{{{color:art.accent, marginTop:'1px'}}}}/>
                        </div>
                    )}}

                    {{/* Ilustración central — emoji grande + resplandor */}}
                    <div style={{{{
                        position:'absolute',
                        top: sm?'50%':'50%',
                        left:'50%',
                        transform: numValue!==null && !sm
                            ? 'translate(-50%, -44%)'
                            : 'translate(-50%, -50%)',
                        zIndex:3,
                        display:'flex', flexDirection:'column', alignItems:'center', gap:'2px'
                    }}}}>
                        {{/* Halo detrás del emoji */}}
                        <div style={{{{
                            position:'absolute',
                            width: sm?'28px':'56px', height: sm?'28px':'56px',
                            borderRadius:'50%',
                            background:`radial-gradient(circle, ${{art.frame}}30 0%, transparent 70%)`,
                            transform:'translate(-50%,-50%)', top:'50%', left:'50%',
                            pointerEvents:'none'
                        }}}}/>
                        <span style={{{{
                            fontSize: sm?'20px':'40px',
                            lineHeight:1,
                            filter:`drop-shadow(0 2px 6px ${{art.frame}}88)`,
                            position:'relative', zIndex:1
                        }}}}>{{art.emoji}}</span>
                        {{/* Nombre de la carta bajo el emoji (tamaño normal, no número) */}}
                        {{!sm && numValue === null && (
                            <span style={{{{
                                fontSize:'9px', fontWeight:'800',
                                color: art.shine,
                                textTransform:'uppercase', letterSpacing:'0.08em',
                                textShadow:`0 1px 4px rgba(0,0,0,0.9)`,
                                textAlign:'center', maxWidth:`${{W-12}}px`,
                                lineHeight:1.1, marginTop:'2px'
                            }}}}>{{label}}</span>
                        )}}
                    </div>

                    {{/* Banda inferior con nombre del palo (solo cartas de palo, tamaño normal) */}}
                    {{!sm && isSuit && (
                        <div style={{{{
                            position:'absolute', bottom:0, left:0, right:0,
                            background:`linear-gradient(0deg, rgba(0,0,0,0.85) 0%, transparent 100%)`,
                            padding:'10px 6px 5px', zIndex:4, textAlign:'center'
                        }}}}>
                            <span style={{{{
                                fontSize:'8px', fontWeight:'700',
                                color: art.accent, textTransform:'uppercase',
                                letterSpacing:'0.12em',
                                textShadow:'0 1px 3px rgba(0,0,0,0.9)'
                            }}}}>{{label}}</span>
                        </div>
                    )}}

                    {{/* Badge bonus */}}
                    {{card.bonus > 0 && (
                        <div style={{{{
                            position:'absolute', top: sm?'-3px':'-4px', right: sm?'-3px':'-4px',
                            background:'linear-gradient(135deg,#fbbf24,#f59e0b)',
                            color:'#1a0a00', fontSize: sm?'7px':'8px',
                            fontWeight:'900', padding: sm?'1px 3px':'2px 4px',
                            borderRadius:'999px',
                            border:'1.5px solid #fef08a',
                            boxShadow:'0 2px 6px rgba(245,158,11,0.6)',
                            zIndex:10, lineHeight:1
                        }}}}>+{{card.bonus}}</div>
                    )}}

                    {{/* Overlay playedAs (Tigresa) */}}
                    {{card.playedAs && (
                        <div style={{{{
                            position:'absolute', inset:0, display:'flex',
                            alignItems:'center', justifyContent:'center',
                            background:'rgba(0,0,0,0.65)', borderRadius:`${{R}}px`, zIndex:20
                        }}}}>
                            <span style={{{{
                                fontSize:'9px', fontWeight:'800', color:'#ffd700',
                                background:'rgba(0,0,0,0.85)', padding:'3px 7px',
                                borderRadius:'4px', border:'1px solid #ffd700',
                                textTransform:'uppercase', letterSpacing:'0.1em'
                            }}}}>{{card.playedAs}}</span>
                        </div>
                    )}}
                </div>
            );
        }};

        // BANNER GANADOR — aparece ENCIMA de la zona de oponentes, no tapa las cartas
        const WinnerBanner = ({{ players, winnerId }}) => {{
            const [count, setCount] = useState(3);
            const circumference = 2 * Math.PI * 18;

            useEffect(() => {{
                setCount(3);
                const interval = setInterval(() => {{
                    setCount(prev => (prev <= 1 ? 1 : prev - 1));
                }}, 1000);
                return () => clearInterval(interval);
            }}, [winnerId]);

            const winnerName = winnerId === 'KRAKEN'
                ? '💀 Kraken — Nadie gana'
                : (players.find(p => p.uid === winnerId)?.name || '?');

            return (
                <div className="flex items-center gap-3 bg-[#1e1a0e] border-2 border-[#ffd700] rounded-2xl px-5 py-2 shadow-[0_0_24px_rgba(255,215,0,0.4)] animate-scaleIn pointer-events-none select-none">
                    <Trophy className="text-[#ffd700] flex-shrink-0" size={{20}} />
                    <div className="text-center leading-tight">
                        <div className="text-[9px] text-slate-400 uppercase tracking-widest">Gana la baza</div>
                        <div className="text-lg font-bold text-[#ffd700]">{{winnerName}}</div>
                    </div>
                    <div className="relative w-10 h-10 flex-shrink-0 flex items-center justify-center">
                        <svg className="absolute inset-0 w-full h-full -rotate-90" viewBox="0 0 44 44">
                            <circle cx="22" cy="22" r="18" fill="none" stroke="#334155" strokeWidth="3.5"/>
                            <circle cx="22" cy="22" r="18" fill="none" stroke="#ffd700" strokeWidth="3.5"
                                strokeDasharray={{circumference}}
                                strokeDashoffset={{circumference - (count / 3) * circumference}}
                                strokeLinecap="round"
                                style={{{{ transition: 'stroke-dashoffset 0.9s linear' }}}}
                            />
                        </svg>
                        <span className="text-base font-bold text-white relative z-10">{{count}}</span>
                    </div>
                </div>
            );
        }};

        // MODAL DE AYUDA — rediseñado con tabs y visual claro
        const HelpModal = ({{ onClose }}) => {{
            const [tab, setTab] = useState('reglas');
            const TabBtn = ({{id, label}}) => (
                <button onClick={{()=>setTab(id)}} className={{`px-4 py-2 rounded-lg text-sm font-bold transition-all ${{tab===id?'bg-[#c5a059] text-black':'bg-[#334155] text-slate-300 hover:bg-[#475569]'}}`}}>
                    {{label}}
                </button>
            );
            return (
                <div className="fixed inset-0 bg-black/90 z-[100] flex items-center justify-center p-3 backdrop-blur-sm animate-fadeIn">
                    <div className="bg-[#1e293b] rounded-2xl border-2 border-[#c5a059] shadow-2xl w-full max-w-2xl max-h-[92vh] overflow-hidden flex flex-col relative text-[#e2d2ac]">
                        <button onClick={{onClose}} className="absolute top-3 right-3 text-slate-400 hover:text-white bg-slate-800 rounded-full p-1.5 transition-colors z-10"><X size={{20}}/></button>
                        {{/* Header */}}
                        <div className="p-5 pb-3 border-b border-[#334155] flex-shrink-0">
                            <h2 className="text-2xl font-bold text-[#ffd700] flex items-center gap-2 mb-3">
                                <HelpCircle size={{28}}/> Manual del Pirata
                            </h2>
                            <div className="flex gap-2 flex-wrap">
                                <TabBtn id="reglas" label="🏴‍☠️ Reglas"/>
                                <TabBtn id="jerarquia" label="👑 Cartas"/>
                                <TabBtn id="puntos" label="💰 Puntos"/>
                                <TabBtn id="piratas" label="⚔️ Piratas"/>
                            </div>
                        </div>
                        {{/* Content */}}
                        <div className="overflow-y-auto flex-1 p-5 custom-scrollbar text-sm">

                            {{tab === 'reglas' && (
                                <div className="space-y-4">
                                    <div className="bg-[#0f172a] rounded-xl p-4 border border-[#334155]">
                                        <h3 className="font-bold text-white mb-2 text-base">📋 Estructura</h3>
                                        <div className="grid grid-cols-2 gap-2">
                                            <div className="bg-[#1e293b] rounded-lg p-3 text-center"><div className="text-2xl font-bold text-[#ffd700]">10</div><div className="text-xs text-slate-400">Rondas</div></div>
                                            <div className="bg-[#1e293b] rounded-lg p-3 text-center"><div className="text-2xl font-bold text-[#ffd700]">1→10</div><div className="text-xs text-slate-400">Cartas por ronda</div></div>
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        {{[
                                            {{step:'1', icon:'👀', title:'Ver y apostar', desc:'Mira tu mano y apuesta cuántas bazas ganarás esta ronda (puede ser 0).'}},
                                            {{step:'2', icon:'🃏', title:'Tirar cartas', desc:'El primero tira una carta marcando el palo. Los demás deben seguir ese palo si lo tienen (Loro/Mapa/Cofre). Si alguien ha tirado un negro (Jolly Roger), ya no hay obligación de seguir palo.'}},
                                            {{step:'3', icon:'🏆', title:'Ganar la baza', desc:'La carta más alta del palo liderador gana, o el Jolly Roger más alto. Los especiales tienen reglas propias. El ganador empieza la siguiente baza.'}},
                                            {{step:'4', icon:'🔄', title:'Nueva ronda', desc:'El que ganó la última baza empieza la siguiente ronda. Las cartas repartidas aumentan en 1 cada ronda.'}},
                                        ].map(s => (
                                            <div key={{s.step}} className="bg-[#0f172a] rounded-xl p-3 flex gap-3 items-start border border-[#334155]">
                                                <div className="w-7 h-7 rounded-full bg-[#c5a059] text-black font-bold flex items-center justify-center flex-shrink-0 text-xs">{{s.step}}</div>
                                                <div>
                                                    <div className="font-bold text-white">{{s.icon}} {{s.title}}</div>
                                                    <div className="text-slate-400 text-xs mt-0.5">{{s.desc}}</div>
                                                </div>
                                            </div>
                                        ))}}
                                    </div>
                                </div>
                            )}}

                            {{tab === 'jerarquia' && (
                                <div className="space-y-2">
                                    <p className="text-slate-400 text-xs mb-3">De mayor a menor fuerza:</p>
                                    {{[
                                        {{rank:'1', color:'bg-yellow-500', label:'👑 Skull King', desc:'Gana a todo… ¡excepto a la Sirena que juega después!', extra:''}},
                                        {{rank:'2', color:'bg-cyan-600',   label:'🧜 Sirena',     desc:'Gana al Skull King si se jugó después. Pierde contra Piratas.', extra:''}},
                                        {{rank:'3', color:'bg-red-700',    label:'⚔️ Pirata / Tigresa (Pirata)', desc:'Gana a Sirenas y a todos los palos.', extra:''}},
                                        {{rank:'4', color:'bg-gray-700',   label:'💀 Jolly Roger (Negro)', desc:'Triunfo numerado (1-14). Gana a cualquier palo normal.', extra:'Si hay un negro en mesa, los demás pueden tirar lo que quieran.'}},
                                        {{rank:'5', color:'bg-emerald-700',label:'🦜 Loro · 🗺️ Mapa · 💰 Cofre', desc:'Palos normales. Gana el número más alto del palo que salió primero.', extra:''}},
                                        {{rank:'6', color:'bg-sky-800',    label:'🏳️ Huida / Tigresa (Huida)', desc:'Siempre pierde.', extra:''}},
                                        {{rank:'—', color:'bg-emerald-900',label:'🐙 Kraken', desc:'Nadie gana la baza. Quien lo jugó elige quién empieza la siguiente.', extra:''}},
                                        {{rank:'—', color:'bg-blue-900',   label:'🐋 Ballena', desc:'Anula todos los palos especiales. Gana la carta numérica más alta (incluso no negra).', extra:''}},
                                        {{rank:'—', color:'bg-yellow-600', label:'🤝 Alianza (Monedas)', desc:'Si alguien la juega en una baza que ganas, ambos os lleváis +20 pts bonus.', extra:''}},
                                    ].map((r,i) => (
                                        <div key={{i}} className="flex gap-3 items-start bg-[#0f172a] rounded-xl p-3 border border-[#334155]">
                                            <div className={{`w-6 h-6 rounded-full ${{r.color}} flex items-center justify-center flex-shrink-0 text-[10px] font-bold text-white`}}>{{r.rank}}</div>
                                            <div>
                                                <div className="font-bold text-white text-sm">{{r.label}}</div>
                                                <div className="text-slate-400 text-xs mt-0.5">{{r.desc}}</div>
                                                {{r.extra && <div className="text-[#c5a059] text-xs mt-0.5 italic">{{r.extra}}</div>}}
                                            </div>
                                        </div>
                                    ))}}
                                </div>
                            )}}

                            {{tab === 'puntos' && (
                                <div className="space-y-3">
                                    <div className="grid grid-cols-1 gap-2">
                                        <div className="bg-green-900/30 border border-green-700 rounded-xl p-4">
                                            <div className="font-bold text-green-400 mb-2">✅ Apuesta acertada (1-10)</div>
                                            <div className="text-2xl font-bold text-white">Apuesta × 20 pts</div>
                                            <div className="text-xs text-slate-400 mt-1">+ bonus si aplican (ver abajo)</div>
                                        </div>
                                        <div className="bg-green-900/30 border border-green-700 rounded-xl p-4">
                                            <div className="font-bold text-green-400 mb-2">✅ Apuesta acertada (0)</div>
                                            <div className="text-2xl font-bold text-white">Ronda × 10 pts</div>
                                            <div className="text-xs text-slate-400 mt-1">Ej. Ronda 7 → +70 pts si ganas 0 bazas</div>
                                        </div>
                                        <div className="bg-red-900/30 border border-red-700 rounded-xl p-4">
                                            <div className="font-bold text-red-400 mb-2">❌ Apuesta fallada (1-10)</div>
                                            <div className="text-2xl font-bold text-white">Diferencia × -10 pts</div>
                                            <div className="text-xs text-slate-400 mt-1">Sin bonus. Ej. apostaste 3, ganaste 1 → -20 pts</div>
                                        </div>
                                        <div className="bg-red-900/30 border border-red-700 rounded-xl p-4">
                                            <div className="font-bold text-red-400 mb-2">❌ Apuesta fallada (0)</div>
                                            <div className="text-2xl font-bold text-white">Ronda × -10 pts</div>
                                            <div className="text-xs text-slate-400 mt-1">Ej. apostaste 0 pero ganaste bazas → Ronda 7 = -70 pts</div>
                                        </div>
                                    </div>
                                    <div className="bg-[#1a1a0a] border border-[#c5a059] rounded-xl p-4">
                                        <div className="font-bold text-[#ffd700] mb-2">⭐ Bonus (solo si aciertas)</div>
                                        <div className="space-y-1.5">
                                            {{[
                                                {{label:'14 de palo normal', pts:'+10'}},
                                                {{label:'14 negro (Jolly Roger)', pts:'+20'}},
                                                {{label:'Pirata captura Sirena', pts:'+20'}},
                                                {{label:'Skull King captura Pirata', pts:'+30 c/u'}},
                                                {{label:'Sirena captura Skull King', pts:'+40'}},
                                                {{label:'Alianza (Monedas) mutua', pts:'+20 a ambos'}},
                                            ].map((b,i) => (
                                                <div key={{i}} className="flex justify-between items-center text-sm">
                                                    <span className="text-slate-300">{{b.label}}</span>
                                                    <span className="font-bold text-[#ffd700] bg-[#2a2000] px-2 py-0.5 rounded">{{b.pts}}</span>
                                                </div>
                                            ))}}
                                        </div>
                                    </div>
                                </div>
                            )}}

                            {{tab === 'piratas' && (
                                <div className="space-y-3">
                                    <p className="text-slate-400 text-xs">Al ganar una baza con estos piratas, se activa su poder:</p>
                                    {{[
                                        {{color:'border-red-500',    emoji:'🎯', name:'Capitán Pedro',       desc:'Modifica tu apuesta actual: -1, mantener, o +1. Muy útil si te has pasado o quedado corto.'}},
                                        {{color:'border-blue-500',   emoji:'💰', name:'Contramaestre Elías', desc:'Apuesta secundaria secreta: 0, +10 o +20 pts. Se suma si aciertas, se resta si fallas.'}},
                                        {{color:'border-purple-500', emoji:'⬇️', name:'Vigía Javi',          desc:'En la SIGUIENTE baza, gana la carta más BAJA en lugar de la más alta. ¡Invierte las reglas!'}},
                                        {{color:'border-emerald-500',emoji:'🧭', name:'Timonel Sergio',      desc:'Elige quién empieza la siguiente baza (tú u otro jugador).'}},
                                        {{color:'border-orange-500', emoji:'🔀', name:'Corsario Torri',      desc:'Intercambia todas tus cartas restantes con las de otro jugador que elijas.'}},
                                    ].map((p,i) => (
                                        <div key={{i}} className={{`bg-[#0f172a] p-4 rounded-xl border-l-4 ${{p.color}} border border-[#1e293b]`}}>
                                            <div className="font-bold text-white text-base flex items-center gap-2">
                                                <span>{{p.emoji}}</span> {{p.name}}
                                            </div>
                                            <div className="text-slate-300 text-sm mt-1">{{p.desc}}</div>
                                        </div>
                                    ))}}
                                </div>
                            )}}
                        </div>
                        <div className="p-4 border-t border-[#334155] flex-shrink-0">
                            <button onClick={{onClose}} className="w-full bg-[#c5a059] hover:bg-[#ffd700] text-black py-3 rounded-xl font-bold text-base transition-colors shadow-lg">¡Entendido, al abordaje!</button>
                        </div>
                    </div>
                </div>
            );
        }};

        // =====================================================================
        // COMPONENTE PRINCIPAL
        // =====================================================================
        function SkullKingApp() {{
            const [user,            setUser]            = useState(null);
            const [activeRoomId,    setActiveRoomId]    = useState('');
            const [inputRoomId,     setInputRoomId]     = useState('');
            const [playerName,      setPlayerName]      = useState('');
            const [gameState,       setGameState]       = useState(null);
            const [error,           setError]           = useState('');
            const [copied,          setCopied]          = useState(false);
            const [toast,           setToast]           = useState(null);
            const [showLeaderboard, setShowLeaderboard] = useState(false);
            const [showHelp,        setShowHelp]        = useState(false);
            const [tigressModal,    setTigressModal]    = useState(null);
            const [isHandMinimized, setIsHandMinimized] = useState(false);
            // Estado local para la cuenta atrás (sólo visual, no en Firebase)
            const [trickWinnerId,   setTrickWinnerId]   = useState(null);
            const [currentWinnerId, setCurrentWinnerId] = useState(null); // ganador parcial mientras se juega
            const [roundStartMsg,   setRoundStartMsg]   = useState(null); // anuncio inicio de ronda
            const [showRoomCode,    setShowRoomCode]    = useState(false);
            const resolvingTrickRef = useRef(false);
            const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

            useEffect(() => {{
                const fn = () => setIsMobile(window.innerWidth < 768);
                window.addEventListener('resize', fn);
                return () => window.removeEventListener('resize', fn);
            }}, []);

            const showToast = msg => {{ setToast(msg); setTimeout(() => setToast(null), 3500); }};

            // Auth anónima
            useEffect(() => {{
                signInAnonymously(auth).catch(e => setError("Error conectando. Revisa tu configuración de Firebase. " + e.message));
                return onAuthStateChanged(auth, u => setUser(u));
            }}, []);

            // Listener de sala
            useEffect(() => {{
                if (!user || !activeRoomId) return;
                return onSnapshot(
                    doc(db, ROOM_COLLECTION, `sk_room_${{activeRoomId}}`),
                    snap => {{
                        if (snap.exists()) {{ setGameState(snap.data()); setError(''); }}
                        else {{ setError("La sala no existe."); setActiveRoomId(''); setGameState(null); }}
                    }},
                    err => setError("Error de conexión: " + err.message)
                );
            }}, [user, activeRoomId]);

            // Auto-minimizar mano en fases especiales
            useEffect(() => {{
                if (!gameState) return;
                setIsHandMinimized(gameState.phase === 'PIRATE_ACTION' || !!tigressModal);
            }}, [gameState?.phase, tigressModal]);

            // Ganador parcial mientras se juegan cartas (actualizar en tiempo real)
            useEffect(() => {{
                if (!gameState || gameState.phase !== 'PLAYING') {{ setCurrentWinnerId(null); return; }}
                if (gameState.trickCards.length === 0) {{ setCurrentWinnerId(null); return; }}
                const partial = determineTrickWinner(gameState.trickCards, gameState.nextTrickLowWins);
                setCurrentWinnerId(partial || null);
            }}, [gameState?.trickCards?.length, gameState?.phase]);

            // Anuncios globales (Ballena/Kraken en tiempo real, efectos Piratas confirmados)
            useEffect(() => {{
                if (!gameState) return;
                
                // Efectos Kraken/Ballena al jugarlos a la mesa
                if (gameState.trickCards && gameState.trickCards.length > 0) {{
                    const lastCard = gameState.trickCards[gameState.trickCards.length - 1].card;
                    if (lastCard.type === CARD_TYPES.KRAKEN) {{
                        setRoundStartMsg('🐙 ¡El Kraken destruye la baza!');
                        const t = setTimeout(() => setRoundStartMsg(null), 2000);
                        return () => clearTimeout(t);
                    }} else if (lastCard.type === CARD_TYPES.WHALE) {{
                        setRoundStartMsg('🐋 ¡La Ballena se come los palos especiales!');
                        const t = setTimeout(() => setRoundStartMsg(null), 2000);
                        return () => clearTimeout(t);
                    }}
                }}
            }}, [gameState?.trickCards?.length]);

            useEffect(() => {{
                if (gameState?.actionBroadcast?.ts) {{
                    // Evitar que salte si es muy viejo (ej. recargó página tras 10s)
                    if (Date.now() - gameState.actionBroadcast.ts < 10000) {{
                        setRoundStartMsg(gameState.actionBroadcast.msg);
                        const t = setTimeout(() => setRoundStartMsg(null), 2000);
                        return () => clearTimeout(t);
                    }}
                }}
            }}, [gameState?.actionBroadcast?.ts]);

            // ── LÓGICA DE CUENTA ATRÁS ──────────────────────────────────────
            // El host detecta mesa llena en PLAYING y pone TRICK_RESOLVING.
            // Todos ven las cartas + banner 3s. Luego el host llama resolveTrick.
            useEffect(() => {{
                if (!gameState || !user) return;
                if (gameState.hostId !== user.uid) return;
                if (
                    gameState.phase === 'PLAYING' &&
                    gameState.trickCards.length > 0 &&
                    gameState.trickCards.length >= gameState.players.length
                ) {{
                    updateDoc(doc(db, ROOM_COLLECTION, `sk_room_${{activeRoomId}}`), {{
                        phase: 'TRICK_RESOLVING'
                    }}).catch(e => console.error('TRICK_RESOLVING update failed', e));
                }}
            }}, [gameState?.trickCards?.length, gameState?.phase]);

            useEffect(() => {{
                if (!gameState || !user) return;
                if (gameState.phase === 'TRICK_RESOLVING') {{
                    const winnerId = determineTrickWinner(gameState.trickCards, gameState.nextTrickLowWins)
                        || gameState.trickCards[0]?.playerId;
                    setTrickWinnerId(winnerId || null);
                    // Solo el host resuelve, tras 3 segundos
                    if (gameState.hostId === user.uid) {{
                        const timer = setTimeout(() => {{
                            resolveTrick(gameState.trickCards);
                        }}, 3000);
                        return () => clearTimeout(timer);
                    }}
                }} else {{
                    setTrickWinnerId(null);
                }}
            }}, [gameState?.phase]);

            const roomRef = () => doc(db, ROOM_COLLECTION, `sk_room_${{activeRoomId}}`);

            const newPlayer = (uid, name) => ({{ uid, name, score:0, hand:[], bid:null, tricksWon:0, lastRoundScore:0, bonusPoints:0, eliasBet:null }});

            const createRoom = async () => {{
                if (!playerName.trim()) return setError("Escribe tu nombre primero");
                const id = generateRoomId();
                const data = {{
                    roomId: id, hostId: user.uid, phase: 'LOBBY', round: 1,
                    turnIndex: 0, dealerIndex: 0,
                    players: [newPlayer(user.uid, playerName.trim())],
                    trickCards: [], nextTrickLowWins: false, nextTrickStarter: null,
                    alliances: [], pendingPirateAction: null, createdAt: serverTimestamp()
                }};
                await setDoc(doc(db, ROOM_COLLECTION, `sk_room_${{id}}`), data);
                setActiveRoomId(id);
            }};

            const joinRoom = async () => {{
                if (!playerName.trim() || !inputRoomId.trim()) return setError("Faltan datos");
                const target = inputRoomId.trim().toUpperCase().replace(/[^A-Z0-9]/g,'');
                const ref = doc(db, ROOM_COLLECTION, `sk_room_${{target}}`);
                try {{
                    await runTransaction(db, async t => {{
                        const snap = await t.get(ref);
                        if (!snap.exists()) throw new Error("Sala no encontrada");
                        const d = snap.data();
                        if (!d.players.some(p => p.uid === user.uid)) {{
                            if (d.phase !== 'LOBBY') throw new Error("La partida ya empezó");
                            if (d.players.length >= 8) throw new Error("Sala llena (máx 8)");
                            t.update(ref, {{ players: [...d.players, newPlayer(user.uid, playerName.trim())] }});
                        }}
                    }});
                    setActiveRoomId(target);
                }} catch(e) {{ setError(e.message); }}
            }};

            const resetToLobby = async () => {{
                const resetPlayers = gameState.players.map(p => newPlayer(p.uid, p.name));
                await updateDoc(roomRef(), {{
                    phase:'LOBBY', round:1, turnIndex:0, dealerIndex:0,
                    players:resetPlayers, trickCards:[], nextTrickLowWins:false,
                    nextTrickStarter:null, alliances:[], pendingPirateAction:null,
                    createdAt: serverTimestamp()
                }});
            }};

            const startRound = async (roundNum) => {{
                const deck = generateDeck();
                const players = JSON.parse(JSON.stringify(gameState.players));
                players.forEach(p => {{
                    p.hand = deck.splice(0, roundNum);
                    p.bid = null; p.tricksWon = 0; p.bonusPoints = 0; p.eliasBet = null;
                }});
                // El que ganó la última baza de la ronda anterior empieza
                let startTurnIndex = (gameState.dealerIndex + 1) % players.length;
                if (gameState.lastRoundWinnerId) {{
                    const wi = players.findIndex(p => p.uid === gameState.lastRoundWinnerId);
                    if (wi !== -1) startTurnIndex = wi;
                }}
                await updateDoc(roomRef(), {{
                    phase:'BIDDING', round:roundNum, players,
                    trickCards:[], turnIndex:startTurnIndex,
                    nextTrickLowWins:false, nextTrickStarter:null,
                    alliances:[], pendingPirateAction:null, lastRoundWinnerId:null
                }});
            }};

            const submitBid = async amount => {{
                const players = [...gameState.players];
                players.find(p => p.uid === user.uid).bid = amount;
                const allBid = players.every(p => p.bid !== null);
                await updateDoc(roomRef(), {{ players, phase: allBid ? 'PLAYING' : 'BIDDING' }});
            }};

            const canPlayCard = card => {{
                if (gameState.trickCards.length >= gameState.players.length) return false;
                if (gameState.trickCards.length === 0) return true;
                // Especiales (huidas, piratas, SK, sirenas, kraken, ballena...) siempre jugables
                if (card.type !== CARD_TYPES.SUIT) return true;
                // Buscar la primera carta de palo NORMAL (Loro/Mapa/Cofre) que marcó el palo
                const sorted = [...gameState.trickCards].sort((a,b) => a.order - b.order);
                // Si hay un negro (TRUMP) en mesa, no hay obligación de seguir palo
                const trumpPlayed = sorted.some(p => p.card.type === CARD_TYPES.SUIT && p.card.suit === 'TRUMP');
                if (trumpPlayed) return true;
                // Buscar palo normal líder
                const leadPlay = sorted.find(p => p.card.type === CARD_TYPES.SUIT && p.card.suit !== 'TRUMP');
                if (!leadPlay) return true; // No hay palo normal liderando -> libre
                const leadSuit = leadPlay.card.suit;
                const myHand = gameState.players.find(p => p.uid === user.uid).hand;
                const hasLead = myHand.some(c => c.type === CARD_TYPES.SUIT && c.suit === leadSuit);
                if (!hasLead) return true; // No tenemos el palo -> libre
                // Tenemos el palo: obligatorio tirarlo (o tirar negro)
                return card.suit === leadSuit || card.suit === 'TRUMP';
            }};

            const handleCardClick = card => {{
                if (gameState.phase !== 'PLAYING') return;
                if (gameState.trickCards.length >= gameState.players.length) return showToast("Esperando resolución...");
                if (gameState.players[gameState.turnIndex].uid !== user.uid) return showToast("No es tu turno");
                if (!canPlayCard(card)) return showToast("Debes seguir el palo");
                if (card.type === CARD_TYPES.TIGRESS && !card.playedAs) return setTigressModal(card);
                playCard(card);
            }};

            const playCard = async (card, extra={{}}) => {{
                const players = JSON.parse(JSON.stringify(gameState.players));
                const me = players.find(p => p.uid === user.uid);
                me.hand = me.hand.filter(c => c.id !== card.id);
                const trickCards = [...gameState.trickCards, {{
                    playerId: user.uid, playerName: me.name,
                    card: {{ ...card, ...extra }},
                    order: gameState.trickCards.length
                }}];
                await updateDoc(roomRef(), {{
                    players, trickCards,
                    turnIndex: (gameState.turnIndex + 1) % players.length
                }});
                setTigressModal(null);
            }};

            const resolveTrick = async cards => {{
                try {{
                    let winnerId = determineTrickWinner(cards, gameState.nextTrickLowWins);
                    if (!winnerId) winnerId = cards[0].playerId;
                    const players = JSON.parse(JSON.stringify(gameState.players));

                    let pirateAction = null;
                    if (winnerId !== 'KRAKEN') {{
                        const wp = cards.find(p => p.playerId === winnerId);
                        if (wp?.card.type === CARD_TYPES.PIRATE && PIRATE_NAMES[wp.card.pirateId]) {{
                            const roundOver = players[0].hand.length === 0;
                            if (!roundOver || ['PEDRO','ELIAS'].includes(wp.card.pirateId))
                                pirateAction = {{ pirateId: wp.card.pirateId, winnerId }};
                        }}
                    }}

                    if (pirateAction) {{
                        players.find(p => p.uid === winnerId).tricksWon += 1;
                        cards.forEach(play => {{
                            if (play.card.bonus) players.find(p => p.uid === winnerId).bonusPoints += play.card.bonus;
                        }});
                        await updateDoc(roomRef(), {{ phase:'PIRATE_ACTION', pendingPirateAction:pirateAction, players }});
                        return;
                    }}
                    await finishTrickResolution(winnerId, cards, players);
                }} catch(e) {{ console.error(e); }}
            }};

            const executePirateAction = async payload => {{
                const action = gameState.pendingPirateAction;
                if (!action || gameState.phase !== 'PIRATE_ACTION') return;
                const players = JSON.parse(JSON.stringify(gameState.players));
                const me = players.find(p => p.uid === user.uid);
                let nextLowWins = false, nextStarterOverride = null;

                let bCast = "";
                if      (action.pirateId === 'PEDRO')  {{ me.bid = Math.max(0, me.bid + payload.mod); bCast = `🎯 El Capitán Pedro ha modificado la apuesta de ${{me.name}}`; }}
                else if (action.pirateId === 'ELIAS')  {{ me.eliasBet = payload.bet; bCast = `💰 El Contramaestre Elías ha hecho un pacto secreto...`; }}
                else if (action.pirateId === 'TORRI' && payload.targetId) {{
                    const ti = players.findIndex(p => p.uid === payload.targetId);
                    if (ti !== -1) {{ 
                        const h = [...me.hand]; me.hand = [...players[ti].hand]; players[ti].hand = h; 
                        bCast = `🔀 ¡Torri intercambia las cartas de ${{me.name}} y ${{players[ti].name}}!`;
                    }}
                }}
                else if (action.pirateId === 'JAVI')   {{ nextLowWins = true; bCast = `⬇ ¡Vigía Javi impone que la carta MÁS BAJA gane!`; }}
                else if (action.pirateId === 'SERGIO') {{ 
                    nextStarterOverride = payload.targetId; 
                    const tn = players.find(p => p.uid === payload.targetId)?.name;
                    bCast = `🧭 ¡Timonel Sergio elige que ${{tn}} empiece!`; 
                }}

                await finishTrickResolution(user.uid, gameState.trickCards, players, {{ nextLowWins, nextStarterOverride, broadcast: bCast }});
            }};

            const finishTrickResolution = async (winnerId, cards, players, extra={{}}) => {{
                let nextStarterId = winnerId;
                const alliances = [...(gameState.alliances||[])];

                if (winnerId !== 'KRAKEN' && gameState.phase !== 'PIRATE_ACTION') {{
                    const wi = players.findIndex(p => p.uid === winnerId);
                    if (wi !== -1) {{
                        players[wi].tricksWon += 1;
                        cards.forEach(p => {{ if (p.card.bonus) players[wi].bonusPoints += p.card.bonus; }});
                        const wc = cards.find(p => p.playerId === winnerId)?.card;
                        if (wc) {{
                            const isPir = wc.type === CARD_TYPES.PIRATE || (wc.type === CARD_TYPES.TIGRESS && wc.playedAs==='pirate');
                            const isSK  = wc.type === CARD_TYPES.SKULLKING;
                            const isMer = wc.type === CARD_TYPES.MERMAID;
                            if (isPir) cards.forEach(p => {{ if (p.card.type===CARD_TYPES.MERMAID) {{ players[wi].bonusPoints+=20; showToast("¡Pirata captura Sirena! (+20)"); }} }});
                            if (isSK)  cards.forEach(p => {{ if (p.card.type===CARD_TYPES.PIRATE||(p.card.type===CARD_TYPES.TIGRESS&&p.card.playedAs==='pirate')) {{ players[wi].bonusPoints+=30; showToast("¡Skull King captura Pirata! (+30)"); }} }});
                            if (isMer && cards.some(p=>p.card.type===CARD_TYPES.SKULLKING)) {{ players[wi].bonusPoints+=40; showToast("¡Sirena captura Skull King! (+40)"); }}
                        }}
                    }}
                }} else if (winnerId === 'KRAKEN') {{
                    const kr = cards.find(p => p.card.type === CARD_TYPES.KRAKEN);
                    nextStarterId = kr ? kr.playerId : cards[0].playerId;
                }}

                // Alianzas (monedas)
                cards.filter(p=>p.card.type===CARD_TYPES.COINS).forEach(cp => {{
                    if (cp.playerId !== winnerId && winnerId !== 'KRAKEN') alliances.push({{p1:cp.playerId, p2:winnerId}});
                }});

                let nextTurn = extra.nextStarterOverride
                    ? players.findIndex(p => p.uid === extra.nextStarterOverride)
                    : players.findIndex(p => p.uid === nextStarterId);
                if (nextTurn === -1) nextTurn = 0;

                const roundOver = players[0].hand.length === 0;

                if (roundOver) {{
                    players.forEach(p => {{
                        const diff = Math.abs(p.bid - p.tricksWon);
                        let pts;
                        if (diff === 0) {{
                            // Apuesta acertada: base + bonus + elias
                            const base = p.bid === 0 ? gameState.round * 10 : p.bid * 20;
                            pts = base + p.bonusPoints + (p.eliasBet || 0);
                        }} else {{
                            // Apuesta fallada: penalización, sin bonus. Apuesta 0 falla -> -10*ronda
                            const pen = p.bid === 0 ? gameState.round * -10 : diff * -10;
                            pts = pen - (p.eliasBet || 0);
                        }}
                        alliances.forEach(al => {{
                            const partnerId = al.p1===p.uid?al.p2:al.p2===p.uid?al.p1:null;
                            if (partnerId) {{
                                const partner = players.find(pl=>pl.uid===partnerId);
                                if (partner && partner.bid===partner.tricksWon && p.bid===p.tricksWon) pts+=20;
                            }}
                        }});
                        p.score += pts;
                        p.lastRoundScore = pts;
                    }});
                    // Guardar quién ganó la última baza para que empiece la siguiente ronda
                    await updateDoc(roomRef(), {{
                        players, phase: gameState.round>=10?'GAME_END':'ROUND_END',
                        trickCards:[], pendingPirateAction:null, alliances,
                        lastRoundWinnerId: winnerId !== 'KRAKEN' ? winnerId : (cards[0]?.playerId || null),
                        actionBroadcast: extra.broadcast ? {{ msg: extra.broadcast, ts: Date.now() }} : null
                    }});
                }} else {{
                    await updateDoc(roomRef(), {{
                        players, trickCards:[], turnIndex:nextTurn, phase:'PLAYING',
                        nextTrickLowWins: extra.nextLowWins||false,
                        nextTrickStarter:null, pendingPirateAction:null, alliances,
                        actionBroadcast: extra.broadcast ? {{ msg: extra.broadcast, ts: Date.now() }} : null
                    }});
                }}
            }};

            // =====================================================================
            // LÓGICA DE RENDERIZADO PRINCIPAL
            // =====================================================================
            const renderMainContent = () => {{
                
                if (!user) return (
                    <div className="min-h-screen bg-[#0f172a] flex items-center justify-center text-[#e2d2ac] font-serif">
                        <Loader className="animate-spin text-[#c5a059]" size={{48}} />
                        <h2 className="text-xl font-bold ml-4">Conectando con la red pirata...</h2>
                    </div>
                );

                // ── LOBBY DE ENTRADA ──────────────────────────────────────────────
                if (!activeRoomId) return (
                    <div className="bg-[#0f172a] min-h-screen text-[#e2d2ac] font-serif p-6 flex flex-col items-center justify-center relative">
                        <div className="text-center mb-8">
                            <div className="flex justify-center mb-4"><Skull className="text-[#c5a059]" size={{80}} /></div>
                            <h1 className="text-5xl text-[#ffd700] font-bold drop-shadow-[0_2px_2px_rgba(0,0,0,0.8)] tracking-wider">SKULL KING</h1>
                            <p className="text-slate-400 mt-2 text-sm">El juego de cartas pirata definitivo</p>
                        </div>
                        <div className="space-y-6 w-full max-w-sm bg-[#1e293b] p-8 rounded-2xl border-4 border-[#c5a059] shadow-2xl relative">
                            <div className="space-y-2">
                                <label className="text-xs uppercase font-bold text-[#c5a059] tracking-widest">Tu Nombre de Pirata</label>
                                <input
                                    className="w-full p-4 rounded-lg bg-[#0f172a] border-2 border-[#334155] text-white focus:border-[#ffd700] outline-none transition-colors"
                                    placeholder="Ej. Barbanegra"
                                    value={{playerName}}
                                    onChange={{e=>setPlayerName(e.target.value)}}
                                    onKeyDown={{e=>e.key==='Enter'&&createRoom()}}
                                />
                            </div>
                            <button onClick={{createRoom}} className="w-full bg-gradient-to-r from-[#ca8a04] to-[#eab308] hover:from-[#a16207] hover:to-[#ca8a04] text-[#2c1810] py-4 rounded-lg font-bold text-lg shadow-[0_4px_0_#713f12] active:shadow-none active:translate-y-1 transition-all flex items-center justify-center gap-2">
                                <Ship size={{24}}/> CREAR SALA
                            </button>
                            <div className="relative flex items-center py-2">
                                <div className="flex-grow border-t border-[#334155]"></div>
                                <span className="flex-shrink-0 mx-4 text-slate-500 text-xs uppercase tracking-widest">O únete</span>
                                <div className="flex-grow border-t border-[#334155]"></div>
                            </div>
                            <div className="flex gap-2">
                                <input
                                    className="flex-1 p-4 rounded-lg bg-[#0f172a] border-2 border-[#334155] text-white focus:border-[#ffd700] outline-none uppercase font-mono tracking-widest text-center"
                                    placeholder="CÓDIGO"
                                    value={{inputRoomId}}
                                    onChange={{e=>setInputRoomId(e.target.value)}}
                                    onKeyDown={{e=>e.key==='Enter'&&joinRoom()}}
                                />
                                <button onClick={{joinRoom}} className="bg-[#334155] hover:bg-[#475569] text-white px-6 rounded-lg font-bold shadow-[0_4px_0_#1e293b] active:shadow-none active:translate-y-1 transition-all">
                                    <LogIn size={{24}}/>
                                </button>
                            </div>
                            {{error && <p className="text-red-400 text-center text-sm font-bold bg-red-900/20 p-2 rounded border border-red-900/50">{{error}}</p>}}
                            
                            {{/* BOTÓN DE AYUDA EN EL MENU */}}
                            <button onClick={{()=>setShowHelp(true)}} className="w-full mt-4 bg-slate-800 hover:bg-slate-700 text-[#c5a059] py-3 rounded-lg font-bold border border-slate-600 shadow-md transition-all flex justify-center items-center gap-2">
                                <HelpCircle size={{20}}/> Cómo Jugar y Reglas
                            </button>
                        </div>
                    </div>
                );

                if (!gameState) return (
                    <div className="min-h-screen bg-[#0f172a] flex flex-col items-center justify-center text-[#e2d2ac] font-serif">
                        <Loader className="animate-spin text-[#c5a059] mb-4" size={{48}}/>
                        <h2 className="text-xl font-bold">Buscando la sala...</h2>
                        <button onClick={{()=>setActiveRoomId('')}} className="mt-4 text-slate-400 underline hover:text-white">Cancelar</button>
                    </div>
                );

                const me = gameState.players.find(p => p.uid === user.uid);
                if (!me) return (
                    <div className="min-h-screen bg-[#0f172a] flex flex-col items-center justify-center text-[#e2d2ac] font-serif">
                        <Loader className="animate-spin text-[#c5a059] mb-4" size={{48}}/>
                        <h2 className="text-xl font-bold">Sincronizando...</h2>
                        <button onClick={{()=>setActiveRoomId('')}} className="mt-4 text-slate-400 underline hover:text-white">Cancelar</button>
                    </div>
                );

                // ── LOBBY DE SALA ─────────────────────────────────────────────────
                if (gameState.phase === 'LOBBY') return (
                    <div className="bg-[#0f172a] min-h-screen text-[#e2d2ac] font-serif p-6 flex flex-col items-center justify-center">
                        <div className="w-full max-w-md bg-[#1e293b] p-6 rounded-2xl border-2 border-[#c5a059] shadow-2xl">
                            <h2 className="text-2xl font-bold text-[#ffd700] text-center mb-6 flex items-center justify-center gap-2"><Anchor/> Sala de Espera</h2>
                            <div
                                className="bg-[#0f172a] p-4 rounded-xl mb-6 text-center border border-[#334155] cursor-pointer hover:border-[#c5a059] transition-colors"
                                onClick={{()=>{{ navigator.clipboard.writeText(activeRoomId); setCopied(true); setTimeout(()=>setCopied(false),2000); }}}}
                            >
                                <div className="text-xs text-slate-400 uppercase tracking-widest mb-1">Código de Sala — toca para copiar</div>
                                <div className="text-5xl font-mono tracking-widest text-[#ffd700] font-bold">{{activeRoomId}}</div>
                                <div className="text-xs text-slate-500 mt-1">{{copied?'¡Copiado! ✓':'Comparte este código con tus amigos'}}</div>
                            </div>
                            <div className="mb-6">
                                <h3 className="text-sm font-bold text-[#c5a059] uppercase mb-3 flex items-center gap-2"><Users size={{16}}/> Tripulación ({{gameState.players.length}}/8)</h3>
                                <div className="space-y-2 max-h-60 overflow-y-auto custom-scrollbar">
                                    {{gameState.players.map(p=>(
                                        <div key={{p.uid}} className="bg-[#334155] p-3 rounded-lg flex justify-between items-center border border-[#475569]">
                                            <span className="font-bold text-white">{{p.name}}</span>
                                            {{p.uid===gameState.hostId && <span className="text-xs bg-[#ffd700] text-black px-2 py-1 rounded font-bold flex items-center gap-1"><Crown size={{12}}/> CAPITÁN</span>}}
                                        </div>
                                    ))}}
                                </div>
                            </div>
                            {{gameState.hostId===user.uid ? (
                                <button
                                    onClick={{()=>startRound(1)}}
                                    disabled={{gameState.players.length < 2}}
                                    className="w-full bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 disabled:opacity-40 disabled:cursor-not-allowed text-white py-4 rounded-xl font-bold text-lg shadow-[0_4px_0_#064e3b] active:shadow-none active:translate-y-1 transition-all uppercase tracking-wider flex justify-center items-center gap-2"
                                >
                                    <Ship/> Zarpar {{gameState.players.length<2?'(mín. 2 jugadores)':''}}
                                </button>
                            ) : (
                                <div className="bg-[#0f172a] p-4 rounded-xl border border-[#334155] text-center animate-pulse">
                                    <p className="text-slate-400 text-sm">El Capitán está reuniendo a la tripulación...</p>
                                </div>
                            )}}
                            
                            <div className="mt-4 flex gap-2">
                                <button onClick={{()=>setShowHelp(true)}} className="flex-1 bg-slate-800 hover:bg-slate-700 text-[#c5a059] py-2 rounded-lg font-bold border border-slate-600 transition-all flex justify-center items-center gap-2 text-sm">
                                    <HelpCircle size={{16}}/> Reglas
                                </button>
                                <button onClick={{()=>setActiveRoomId('')}} className="flex-1 py-2 text-slate-500 hover:text-slate-300 text-sm underline transition-colors">
                                    Abandonar sala
                                </button>
                            </div>
                        </div>
                    </div>
                );

                // ── JUEGO PRINCIPAL ───────────────────────────────────────────────
                const myIndex   = gameState.players.findIndex(p => p.uid === user.uid);
                const opponents = [...gameState.players.slice(myIndex+1), ...gameState.players.slice(0, myIndex)];
                const isTableFull = gameState.trickCards.length >= gameState.players.length;
                const isPAPhase   = gameState.phase === 'PIRATE_ACTION';
                const isResolvingPhase = gameState.phase === 'TRICK_RESOLVING';
                const myPAId      = isPAPhase && gameState.pendingPirateAction?.winnerId === user.uid ? gameState.pendingPirateAction.pirateId : null;
                const rx = isMobile ? 50 : 80, ry = isMobile ? 40 : 60;

                return (
                    <div className="bg-[#0f172a] h-screen overflow-hidden flex flex-col text-[#e2d2ac] font-serif relative">

                        {{/* ── HEADER ── */}}
                        <div className="bg-[#1e293b] p-2 flex justify-between items-center shadow-lg z-20 border-b border-[#334155] flex-shrink-0">
                            <div className="flex items-center gap-2">
                                {{/* Ronda */}}
                                <div className="bg-[#0f172a] px-3 py-1 rounded-full border border-[#c5a059] flex items-center gap-1.5">
                                    <span className="text-slate-400 text-xs uppercase">R</span>
                                    <span className="text-[#ffd700] font-bold text-lg leading-none">{{gameState.round}}</span>
                                    <span className="text-slate-600 text-xs">/10</span>
                                </div>
                                {{/* Código de sala — siempre visible en el header */}}
                                <button
                                    onClick={{()=>{{ navigator.clipboard.writeText(activeRoomId); showToast('¡Código copiado: ' + activeRoomId + '!'); }}}}
                                    className="bg-[#0f172a] px-2 py-1 rounded-full border border-[#334155] hover:border-[#c5a059] transition-colors flex items-center gap-1 group"
                                    title="Código de sala — toca para copiar"
                                >
                                    <span className="text-[10px] text-slate-500 uppercase">Sala</span>
                                    <span className="text-xs font-mono font-bold text-[#c5a059] tracking-widest group-hover:text-[#ffd700] transition-colors">{{activeRoomId}}</span>
                                </button>
                                {{gameState.nextTrickLowWins && <span className="bg-purple-900 text-purple-300 text-[10px] px-2 py-0.5 rounded border border-purple-600 font-bold">⬇ BAJA</span>}}
                            </div>
                            
                            <div className="flex gap-1.5 items-center">
                                {{/* Abandonar partida */}}
                                <button
                                    onClick={{()=>{{ if(confirm('¿Abandonar la partida? El código es ' + activeRoomId + ' para volver.')) setActiveRoomId(''); }}}}
                                    className="bg-[#334155] p-2 rounded text-slate-400 hover:text-red-400 hover:bg-red-900/30 transition-colors shadow-sm"
                                    title="Abandonar partida"
                                >
                                    <Home size={{16}}/>
                                </button>
                                <button onClick={{()=>setShowHelp(true)}} className="bg-[#334155] p-2 rounded text-[#c5a059] hover:text-[#ffd700] hover:bg-[#475569] transition-colors shadow-sm" title="Reglas">
                                    <HelpCircle size={{18}}/>
                                </button>
                                <button onClick={{()=>setShowLeaderboard(!showLeaderboard)}} className="bg-[#334155] p-2 rounded text-white hover:bg-[#475569] transition-colors shadow-sm" title="Clasificación">
                                    <ListOrdered size={{18}}/>
                                </button>
                            </div>
                        </div>

                        {{/* ── CLASIFICACIÓN LATERAL ── */}}
                        <div className={{`absolute right-0 top-[56px] bottom-0 w-60 bg-[#1e293b]/95 border-l border-[#c5a059] p-4 z-40 transition-transform duration-300 ${{showLeaderboard?'translate-x-0':'translate-x-full'}} backdrop-blur-md shadow-2xl`}}>
                            <div className="flex justify-between items-center mb-4 border-b border-[#334155] pb-2">
                                <span className="text-xs font-bold text-[#c5a059] uppercase tracking-widest">Clasificación</span>
                                <button onClick={{()=>setShowLeaderboard(false)}} className="text-slate-500 hover:text-white"><X size={{16}}/></button>
                            </div>
                            <div className="space-y-2">
                                {{[...gameState.players].sort((a,b)=>b.score-a.score).map((p,i)=>(
                                    <div key={{p.uid}} className={{`p-3 rounded-lg flex justify-between items-center ${{p.uid===user.uid?'bg-[#c5a059] text-[#2c1810] font-bold':'bg-[#0f172a] text-slate-300 border border-[#334155]'}}`}}>
                                        <div className="flex items-center gap-2">
                                            <span className={{`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${{i===0?'bg-yellow-500 text-black':i===1?'bg-gray-400 text-black':i===2?'bg-orange-700 text-white':'bg-slate-700 text-slate-300'}}`}}>{{i+1}}</span>
                                            <span className="truncate max-w-[90px] text-sm">{{p.name}}</span>
                                        </div>
                                        <span className="font-mono font-bold">{{p.score}}</span>
                                    </div>
                                ))}}
                            </div>
                        </div>

                        {{/* ── TOAST ── */}}
                        {{toast && (
                            <div className="absolute top-20 left-1/2 -translate-x-1/2 bg-[#7f1d1d] text-white px-6 py-3 rounded-xl font-bold shadow-2xl z-50 border-2 border-red-500 text-center w-max max-w-[90vw]">
                                {{toast}}
                            </div>
                        )}}

                        {{/* ── ANUNCIO INICIO DE BAZA (Javi: baja gana) ── */}}
                        {{roundStartMsg && (
                            <div className="absolute inset-0 z-[60] flex items-center justify-center pointer-events-none">
                                <div className="bg-purple-950/95 border-2 border-purple-400 rounded-2xl px-10 py-6 shadow-2xl animate-scaleIn text-center">
                                    <div className="text-3xl font-bold text-purple-200">{{roundStartMsg}}</div>
                                </div>
                            </div>
                        )}}

                        {{/* ── BANNER GANADOR (encima de oponentes) ── */}}
                        {{isResolvingPhase && trickWinnerId && (
                            <div className="flex justify-center py-2 flex-shrink-0" style={{{{marginRight: showLeaderboard?'240px':'0', transition:'margin 0.3s'}}}}>
                                <WinnerBanner players={{gameState.players}} winnerId={{trickWinnerId}} />
                            </div>
                        )}}

                        {{/* ── OPONENTES ── */}}
                        <div className="flex justify-start md:justify-center gap-3 p-3 overflow-x-auto flex-shrink-0" style={{{{marginRight: showLeaderboard?'240px':'0', transition:'margin 0.3s'}}}}>
                            {{opponents.map(p => {{
                                const isActive = gameState.players[gameState.turnIndex]?.uid === p.uid;
                                // Durante TRICK_RESOLVING, destacamos al ganador
                                const isWinner = isResolvingPhase && trickWinnerId === p.uid;
                                return (
                                    <div key={{p.uid}} className={{`relative flex flex-col items-center min-w-[80px] transition-all duration-300 ${{isActive&&!isResolvingPhase?'scale-110 z-10':isWinner?'scale-125 z-10':'opacity-70'}}`}}>
                                        {{isActive && !isResolvingPhase && <div className="absolute -top-6 text-[#ffd700] animate-bounce"><Swords size={{18}}/></div>}}
                                        {{isWinner && <div className="absolute -top-6 text-[#ffd700] animate-bounce"><Trophy size={{18}}/></div>}}
                                        <div className={{`bg-[#1e293b] p-2 rounded-xl border-2 ${{isWinner?'border-[#ffd700] shadow-[0_0_20px_rgba(255,215,0,0.5)]':isActive&&!isResolvingPhase?'border-[#ffd700] shadow-[0_0_15px_rgba(255,215,0,0.3)]':'border-[#334155]'}}`}}>
                                            <div className="font-bold truncate w-full text-center text-xs mb-1 text-white">{{p.name}}</div>
                                            <div className="text-xs text-[#c5a059] font-mono bg-[#0f172a] rounded px-2 py-0.5 text-center mb-1">
                                                {{p.tricksWon}} / {{(gameState.phase==='BIDDING' && p.uid!==user.uid) ? (p.bid===null?'?':'✔️') : (p.bid===null?'?':p.bid)}}
                                            </div>
                                            <div className="flex justify-center" style={{{{gap:'1px'}}}}>
                                                {{Array(Math.min(p.hand.length,4)).fill(0).map((_,i)=>(
                                                    <div key={{i}} style={{{{
                                                        width:'8px', height:'11px',
                                                        background:'linear-gradient(135deg,#1a1a2e,#0f3460)',
                                                        borderRadius:'2px',
                                                        border:'1px solid #c5a059',
                                                        opacity: 1 - i*0.15
                                                    }}}}/>
                                                ))}}
                                                {{p.hand.length>4 && <span className="text-[7px] text-[#c5a059] ml-0.5 font-bold">+{{p.hand.length-4}}</span>}}
                                            </div>
                                        </div>
                                    </div>
                                );
                            }})}}
                        </div>

                        {{/* ── MESA ── */}}
                        <div className="flex-1 relative flex items-center justify-center overflow-hidden" style={{{{marginRight: showLeaderboard?'240px':'0', transition:'margin 0.3s'}}}}>
                            {{/* Tapete */}}
                            <div className="absolute inset-2 rounded-[2rem] border-[12px] border-[#3e2723] overflow-hidden pointer-events-none">
                                <div className="absolute inset-0 bg-[#0f3d3e]"></div>
                                <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_30%,rgba(0,0,0,0.6)_100%)]"></div>
                                <div className="absolute inset-0 flex items-center justify-center opacity-10 text-[#c5a059]">
                                    <Skull size={{200}} strokeWidth={{1}}/>
                                </div>
                            </div>

                            {{/* Fase de apuestas */}}
                            {{gameState.phase === 'BIDDING' && (
                                <div className="absolute inset-0 z-30 bg-black/80 backdrop-blur-sm flex flex-col items-center justify-center p-6 animate-fadeIn overflow-y-auto">
                                    <h2 className="text-3xl font-bold mb-2 text-[#ffd700]">¿Cuántas bazas ganarás?</h2>
                                    <p className="text-slate-400 text-sm mb-6">Ronda {{gameState.round}} — {{gameState.round}} carta{{gameState.round>1?'s':''}}</p>
                                    {{me.bid !== null ? (
                                        <div className="text-center text-emerald-400 font-bold text-xl animate-pulse flex items-center gap-2"><Check size={{24}}/> Apuesta enviada: {{me.bid}}</div>
                                    ) : (
                                        <div className="grid grid-cols-4 gap-3 max-w-md w-full">
                                            <button onClick={{()=>submitBid(0)}} className="col-span-4 bg-blue-700 hover:bg-blue-600 py-4 rounded-xl font-bold text-2xl border-2 border-blue-400 transition-all hover:scale-[1.02]">0</button>
                                            {{Array.from({{length:gameState.round}},(_,i)=>i+1).map(n=>(
                                                <button key={{n}} onClick={{()=>submitBid(n)}} className="bg-[#334155] hover:bg-[#475569] aspect-square rounded-xl font-bold text-lg border border-[#64748b] text-white transition-all hover:scale-110 flex items-center justify-center">{{n}}</button>
                                            ))}}
                                        </div>
                                    )}}
                                    <div className="mt-6 flex gap-4 text-xs text-slate-500">
                                        {{gameState.players.map(p=>(
                                            <div key={{p.uid}} className={{`flex items-center gap-1 ${{p.bid!==null?'text-emerald-400':''}}`}}>
                                                {{p.bid!==null?<Check size={{12}}/>:<Loader className="animate-spin" size={{12}}/>}} {{p.name}}
                                            </div>
                                        ))}}
                                    </div>
                                </div>
                            )}}

                            {{/* Fase de acción pirata */}}
                            {{isPAPhase && (
                                <div className="absolute inset-0 z-30 bg-black/70 backdrop-blur-md flex items-center justify-center p-4">
                                    {{!myPAId ? (
                                        <div className="bg-[#1e293b] p-6 rounded-2xl border-2 border-[#c5a059] text-center">
                                            <h3 className="text-xl font-bold text-[#ffd700] mb-2 flex items-center justify-center gap-2"><Gavel/> Decisión del Capitán</h3>
                                            <p className="text-slate-400 text-sm mb-4">{{gameState.pendingPirateAction && PIRATE_NAMES[gameState.pendingPirateAction.pirateId]?.name}} está decidiendo...</p>
                                            <Loader className="animate-spin mx-auto text-[#c5a059]" size={{32}}/>
                                        </div>
                                    ) : (
                                        <div className="bg-[#1e293b] p-6 rounded-2xl border-2 border-[#ffd700] shadow-[0_0_40px_rgba(255,215,0,0.2)] max-w-sm w-full animate-scaleIn">
                                            <div className="text-center mb-6">
                                                <Swords className="mx-auto text-[#c5a059] mb-2" size={{32}}/>
                                                <h3 className="text-2xl font-bold text-[#ffd700]">{{PIRATE_NAMES[myPAId]?.name}}</h3>
                                                <p className="text-sm text-slate-400 italic mt-1">{{PIRATE_NAMES[myPAId]?.desc}}</p>
                                            </div>
                                            {{myPAId==='PEDRO' && (
                                                <div className="flex gap-3">
                                                    <button onClick={{()=>executePirateAction({{mod:-1}})}} className="flex-1 bg-red-900 hover:bg-red-800 text-red-100 p-4 rounded-xl font-bold border border-red-500 text-xl">-1</button>
                                                    <button onClick={{()=>executePirateAction({{mod:0}})}}  className="flex-1 bg-slate-700 hover:bg-slate-600 p-4 rounded-xl font-bold border border-slate-500 text-sm">Mantener</button>
                                                    <button onClick={{()=>executePirateAction({{mod:+1}})}} className="flex-1 bg-green-800 hover:bg-green-700 text-green-100 p-4 rounded-xl font-bold border border-green-500 text-xl">+1</button>
                                                </div>
                                            )}}
                                            {{myPAId==='ELIAS' && (
                                                <div className="flex gap-3">
                                                    {{[0,10,20].map(v=><button key={{v}} onClick={{()=>executePirateAction({{bet:v}})}} className="flex-1 bg-blue-800 hover:bg-blue-700 p-4 rounded-xl font-bold border border-blue-500 text-xl">{{v}}</button>)}}
                                                </div>
                                            )}}
                                            {{myPAId==='JAVI' && (
                                                <button onClick={{()=>executePirateAction({{}})}} className="w-full bg-red-700 hover:bg-red-600 p-4 rounded-xl font-bold border border-red-500 flex items-center justify-center gap-2 text-lg">
                                                    <ArrowDown size={{24}}/> ¡La más baja gana!
                                                </button>
                                            )}}
                                            {{myPAId==='SERGIO' && (
                                                <div className="grid grid-cols-2 gap-2">
                                                    {{gameState.players.map(p=>(
                                                        <button key={{p.uid}} onClick={{()=>executePirateAction({{targetId:p.uid}})}} className="bg-slate-700 hover:bg-[#c5a059] hover:text-black p-3 rounded-lg text-sm font-bold border border-slate-600 transition-colors">{{p.name}}</button>
                                                    ))}}
                                                </div>
                                            )}}
                                            {{myPAId==='TORRI' && (
                                                <div className="space-y-2">
                                                    {{gameState.players.filter(p=>p.uid!==user.uid).map(p=>(
                                                        <button key={{p.uid}} onClick={{()=>executePirateAction({{targetId:p.uid}})}} className="w-full bg-red-900/50 hover:bg-red-900 p-3 rounded-lg text-sm border border-red-500/50 hover:border-red-500 transition-all flex justify-between items-center">
                                                            <span className="font-bold">{{p.name}}</span>
                                                            <span className="text-[10px] opacity-70">{{p.hand.length}} cartas</span>
                                                        </button>
                                                    ))}}
                                                    <button onClick={{()=>executePirateAction({{}})}} className="w-full py-2 text-slate-400 hover:text-white text-sm underline">No intercambiar</button>
                                                </div>
                                            )}}
                                        </div>
                                    )}}
                                </div>
                            )}}

                            {{/* Cartas en la mesa */}}
                            {{gameState.trickCards.map((play,i) => {{
                                const isWinnerCard = isResolvingPhase && trickWinnerId && play.playerId === trickWinnerId;
                                const isCurrentWinner = !isResolvingPhase && currentWinnerId && play.playerId === currentWinnerId && gameState.trickCards.length > 0;
                                const isPirate = play.card.type === CARD_TYPES.PIRATE;
                                const pirateName = isPirate ? (PIRATE_NAMES[play.card.pirateId]?.name || 'Pirata') : null;
                                return (
                                    <div key={{i}} className="absolute transition-all duration-500 ease-out z-10" style={{{{
                                        transform: `translate(${{Math.cos(2*Math.PI*i/gameState.trickCards.length)*rx}}px, ${{Math.sin(2*Math.PI*i/gameState.trickCards.length)*ry}}px) rotate(${{(i - gameState.trickCards.length/2)*15}}deg) ${{(isWinnerCard||isCurrentWinner) ? 'scale(1.15)' : ''}}`
                                    }}}}>
                                        <div className="relative">
                                            <Card card={{play.card}} size={{isMobile?'small':'normal'}}/>
                                            {{/* Halo dorado: ganador final */}}
                                            {{isWinnerCard && (
                                                <div className="absolute inset-0 rounded-xl ring-4 ring-[#ffd700] shadow-[0_0_20px_rgba(255,215,0,0.8)] pointer-events-none z-30 animate-pulse"></div>
                                            )}}
                                            {{/* Halo blanco: ganando parcialmente */}}
                                            {{isCurrentWinner && !isWinnerCard && (
                                                <div className="absolute inset-0 rounded-xl ring-2 ring-white/60 shadow-[0_0_12px_rgba(255,255,255,0.4)] pointer-events-none z-30"></div>
                                            )}}
                                            {{/* Etiqueta: nombre del jugador + pirata si aplica — siempre visible */}}
                                            <div className="absolute -bottom-7 left-1/2 -translate-x-1/2 flex flex-col items-center gap-0.5 pointer-events-none" style={{{{zIndex:40}}}}>
                                                <div className="text-[9px] font-bold bg-black/85 text-white px-2 py-0.5 rounded-full whitespace-nowrap border border-white/20">
                                                    {{play.playerName}}
                                                </div>
                                                {{isPirate && (
                                                    <div className="text-[8px] font-bold bg-red-900/90 text-red-200 px-1.5 py-0.5 rounded-full whitespace-nowrap border border-red-500/50">
                                                        {{pirateName}}
                                                    </div>
                                                )}}
                                            </div>
                                        </div>
                                    </div>
                                );
                            }})}}


                        </div>

                        {{/* ── MANO DEL JUGADOR ── */}}
                        <div className="z-20 relative flex-shrink-0" style={{{{marginRight: showLeaderboard?'240px':'0', transition:'margin 0.3s'}}}}>
                            <button
                                onClick={{()=>setIsHandMinimized(!isHandMinimized)}}
                                className="absolute top-[-28px] right-4 bg-[#1e293b] text-[#c5a059] rounded-t-lg px-3 py-1.5 border-t border-l border-r border-[#334155] text-xs font-bold flex items-center gap-1 shadow-lg z-30"
                            >
                                {{isHandMinimized?<ChevronUp size={{14}}/>:<ChevronDown size={{14}}/>}} Mis Cartas ({{me.hand.length}})
                            </button>
                            <div className={{`bg-[#1e293b] shadow-[0_-4px_20px_rgba(0,0,0,0.5)] border-t border-[#334155] transition-all duration-300 overflow-hidden ${{isHandMinimized?'h-14':'h-auto'}}`}}>
                                <div className="flex justify-between items-center px-4 py-2">
                                    <div className="flex items-center gap-3">
                                        <div className="bg-[#0f172a] px-3 py-1.5 rounded-lg border border-[#334155]">
                                            <div className="text-[10px] text-slate-400 uppercase tracking-wider">Bazas</div>
                                            <div className="text-xl font-bold text-[#c5a059] font-mono leading-none">{{me.tricksWon}} <span className="text-slate-600">/</span> {{me.bid===null?'—':me.bid}}</div>
                                        </div>
                                        {{me.bid!==null && me.tricksWon===me.bid && (
                                            <div className="text-green-500 flex items-center gap-1 text-xs font-bold bg-green-900/20 px-2 py-1 rounded border border-green-800/50">
                                                <Check size={{12}}/> ¡EN CAMINO!
                                            </div>
                                        )}}
                                    </div>
                                    {{gameState.phase==='PLAYING' && gameState.players[gameState.turnIndex]?.uid===user.uid && (
                                        <div className="bg-gradient-to-r from-green-600 to-emerald-500 text-white px-5 py-2 rounded-full text-sm font-bold animate-bounce shadow-lg border border-green-400">
                                            ¡TU TURNO!
                                        </div>
                                    )}}
                                </div>
                                <div className={{`w-full overflow-x-auto pb-4 hide-scrollbar transition-opacity duration-200 ${{isHandMinimized?'opacity-0 pointer-events-none':'opacity-100'}}`}}>
                                    <div className="flex justify-start md:justify-center min-w-max px-4 pt-2 gap-2 md:gap-0 md:-space-x-6">
                                        {{me.hand.sort((a,b)=>a.type===b.type?a.value-b.value:a.type.localeCompare(b.type)).map(card=>{{
                                            const isMyTurn = !isTableFull && gameState.phase==='PLAYING' && gameState.players[gameState.turnIndex]?.uid===user.uid;
                                            const valid = canPlayCard(card);
                                            const playable = isMyTurn && valid;
                                            return (
                                                <div key={{card.id}} className={{`transition-all duration-300 md:hover:-translate-y-6 md:hover:z-20 relative flex-shrink-0 ${{playable?'md:hover:scale-105':''}}`}}>
                                                    <Card card={{card}} playable={{playable}} onClick={{()=>handleCardClick(card)}}/>
                                                    {{isMyTurn && !valid && (
                                                        <div className="absolute inset-0 bg-black/60 rounded-xl z-20 flex items-center justify-center backdrop-blur-[1px] border-2 border-red-500/50">
                                                            <XCircle className="text-red-500 opacity-80" size={{24}}/>
                                                        </div>
                                                    )}}
                                                </div>
                                            );
                                        }})}}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {{/* ── MODAL TIGRESA ── */}}
                        {{tigressModal && (
                            <div className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
                                <div className="bg-[#1e293b] p-8 rounded-2xl border-2 border-orange-500 shadow-2xl max-w-xs w-full text-center">
                                    <Ghost className="mx-auto text-orange-400 mb-3" size={{48}}/>
                                    <h3 className="text-2xl font-bold text-orange-400 mb-1">¡La Tigresa!</h3>
                                    <p className="text-slate-400 text-sm mb-6">¿Cómo la juegas?</p>
                                    <div className="flex gap-4">
                                        <button onClick={{()=>playCard(tigressModal,{{playedAs:'pirate'}})}} className="flex-1 bg-red-900 hover:bg-red-800 text-white py-6 rounded-xl font-bold border-2 border-red-600 transition-all hover:scale-105 flex flex-col items-center gap-2">
                                            <Swords size={{28}}/> PIRATA
                                        </button>
                                        <button onClick={{()=>playCard(tigressModal,{{playedAs:'escape'}})}} className="flex-1 bg-sky-900 hover:bg-sky-800 text-white py-6 rounded-xl font-bold border-2 border-sky-600 transition-all hover:scale-105 flex flex-col items-center gap-2">
                                            <Flag size={{28}}/> HUIDA
                                        </button>
                                    </div>
                                    <button onClick={{()=>setTigressModal(null)}} className="mt-4 text-slate-500 hover:text-slate-300 text-sm underline">Cancelar</button>
                                </div>
                            </div>
                        )}}

                        {{/* ── FIN DE RONDA / PARTIDA ── */}}
                        {{(gameState.phase==='ROUND_END'||gameState.phase==='GAME_END') && (
                            <div className="fixed inset-0 bg-black/95 z-50 flex items-center justify-center p-4 backdrop-blur-md">
                                <div className="w-full max-w-lg bg-[#1e293b] p-8 rounded-2xl border-4 border-[#c5a059] shadow-2xl relative overflow-hidden">
                                    <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-transparent via-[#ffd700] to-transparent"></div>
                                    {{gameState.phase==='GAME_END'?<Trophy className="mx-auto text-[#ffd700] mb-4" size={{64}}/>:<Flag className="mx-auto text-[#c5a059] mb-4" size={{48}}/>}}
                                    <h2 className="text-4xl text-[#ffd700] font-bold text-center mb-1 drop-shadow-md">
                                        {{gameState.phase==='GAME_END'?'¡FIN DE LA PARTIDA!':`Ronda ${{gameState.round}} — Resultados`}}
                                    </h2>
                                    <p className="text-center text-[#c5a059] mb-6 uppercase tracking-widest text-xs font-bold">Bitácora del Capitán</p>
                                    <div className="space-y-2 mb-6 max-h-[45vh] overflow-y-auto pr-2 custom-scrollbar">
                                        {{[...gameState.players].sort((a,b)=>b.score-a.score).map((p,i)=>(
                                            <div key={{i}} className={{`flex justify-between items-center p-4 rounded-xl border ${{p.uid===user.uid?'bg-[#334155] border-[#c5a059]':'bg-[#0f172a] border-[#334155]'}}`}}>
                                                <div className="flex items-center gap-3">
                                                    <div className={{`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${{i===0?'bg-yellow-500 text-black':i===1?'bg-gray-400 text-black':i===2?'bg-orange-700 text-white':'bg-slate-700 text-slate-300'}}`}}>{{i+1}}</div>
                                                    <div>
                                                        <div className="font-bold flex items-center gap-2">
                                                            {{p.name}}
                                                            <span className={{`text-xs font-bold px-2 py-0.5 rounded-full ${{p.lastRoundScore>=0?'bg-green-900/50 text-green-400':'bg-red-900/50 text-red-400'}}`}}>
                                                                {{p.lastRoundScore>0?'+':''}}{{p.lastRoundScore}}
                                                            </span>
                                                        </div>
                                                        <div className="text-xs text-slate-400 font-mono">Apuesta: {{p.bid}} | Ganadas: {{p.tricksWon}}</div>
                                                    </div>
                                                </div>
                                                <div className="text-3xl font-bold text-[#ffd700] font-mono">{{p.score}}</div>
                                            </div>
                                        ))}}
                                    </div>
                                    {{gameState.hostId===user.uid && (
                                        <div className="space-y-3">
                                            {{gameState.phase!=='GAME_END' && (
                                                <button
                                                    onClick={{async()=>{{
                                                        const newDealer=(gameState.dealerIndex+1)%gameState.players.length;
                                                        await updateDoc(doc(db,ROOM_COLLECTION,`sk_room_${{activeRoomId}}`),{{dealerIndex:newDealer}});
                                                        startRound(gameState.round+1);
                                                    }}}}
                                                    className="w-full bg-gradient-to-r from-green-600 to-emerald-500 py-4 rounded-xl font-bold text-xl text-white shadow-lg uppercase tracking-wider flex items-center justify-center gap-2 hover:from-green-500 hover:to-emerald-400 transition-all"
                                                >
                                                    Siguiente Ronda <ArrowUp size={{24}}/>
                                                </button>
                                            )}}
                                            {{gameState.phase==='GAME_END' && (
                                                <button onClick={{resetToLobby}} className="w-full bg-[#334155] hover:bg-[#475569] py-4 rounded-xl font-bold text-xl text-[#ffd700] border border-[#c5a059] shadow-lg uppercase tracking-wider flex items-center justify-center gap-2 transition-all">
                                                    <Home size={{24}}/> Nueva Partida
                                                </button>
                                            )}}
                                        </div>
                                    )}}
                                    {{gameState.hostId!==user.uid && (
                                        <div className="bg-[#0f172a] p-4 rounded-xl border border-[#334155] text-center animate-pulse">
                                            <p className="text-slate-400 text-sm">Esperando al Capitán...</p>
                                        </div>
                                    )}}
                                </div>
                            </div>
                        )}}
                    </div>
                );
            }};

            return (
                <>
                    <CardSVGDefs />
                    {{renderMainContent()}}
                    {{showHelp && <HelpModal onClose={{() => setShowHelp(false)}} />}}
                </>
            );
        }}

        createRoot(document.getElementById('root')).render(<SkullKingApp />);
    </script>
</body>
</html>"""

# Renderizar el juego a pantalla completa
screen_height = 900
components.html(html_code, height=screen_height, scrolling=False)
