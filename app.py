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

    <script type="text/babel" data-type="module">
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

        const Card = ({{ card, onClick, playable = false, size = 'normal', hidden = false }}) => {{
            if (hidden) return (
                <div className={{`${{size==='small'?'w-10 h-14':'w-24 h-36'}} bg-[#1a1a2e] border-2 border-[#c5a059] rounded-lg shadow-lg flex items-center justify-center flex-shrink-0`}}>
                    <Skull className="text-[#c5a059] opacity-30" size={{32}} />
                </div>
            );

            const isSuit = card.type === CARD_TYPES.SUIT;
            const sc = isSuit ? SUITS[card.suit] : null;
            let bg='bg-slate-700', tc='text-white', bc='border-slate-600', Icon=HelpCircle, label='';

            if (isSuit) {{
                bg=sc.color; tc=sc.text; bc=sc.border; Icon=sc.icon; label=card.value;
            }} else {{
                switch(card.type) {{
                    case CARD_TYPES.ESCAPE:   bg='bg-sky-200';    tc='text-sky-900';    bc='border-sky-400';    Icon=Flag;    label='Huida'; break;
                    case CARD_TYPES.PIRATE:   bg='bg-red-800';    tc='text-red-100';    bc='border-red-950';    Icon=Swords;  label=PIRATE_NAMES[card.pirateId]?.name||'Pirata'; break;
                    case CARD_TYPES.SKULLKING:bg='bg-gray-950';   tc='text-white';      bc='border-yellow-500'; Icon=Crown;   label='King'; break;
                    case CARD_TYPES.MERMAID:  bg='bg-cyan-600';   tc='text-cyan-50';    bc='border-cyan-800';   Icon=Anchor;  label='Sirena'; break;
                    case CARD_TYPES.TIGRESS:  bg='bg-orange-600'; tc='text-orange-100'; bc='border-orange-800'; Icon=Ghost;   label='Tigresa'; break;
                    case CARD_TYPES.KRAKEN:   bg='bg-emerald-950';tc='text-emerald-400';bc='border-emerald-600';Icon=XCircle; label='Kraken'; break;
                    case CARD_TYPES.WHALE:    bg='bg-blue-900';   tc='text-blue-200';   bc='border-blue-950';   Icon=Waves;   label='Ballena'; break;
                    case CARD_TYPES.COINS:    bg='bg-yellow-500'; tc='text-yellow-950'; bc='border-yellow-700'; Icon=Handshake;label='Alianza'; break;
                }}
            }}

            const base = `relative rounded-xl shadow-xl flex flex-col items-center justify-between p-2 select-none transition-all duration-200
                ${{size==='small'?'w-12 h-16 text-[10px]':'w-24 h-36 text-base hover:-translate-y-4 hover:shadow-2xl hover:z-10'}}
                ${{playable?'cursor-pointer ring-2 ring-[#ffd700] ring-offset-2 ring-offset-black':'cursor-not-allowed opacity-80 brightness-75'}}
                ${{bg}} ${{tc}} border-2 ${{bc}} flex-shrink-0 font-serif`;

            return (
                <div className={{base}} onClick={{onClick}}>
                    <div className="absolute inset-0 opacity-10 pointer-events-none mix-blend-multiply bg-white"></div>
                    <div className="self-start font-bold truncate w-full text-center z-10">{{label}}</div>
                    <Icon size={{size==='small'?16:32}} className="z-10 drop-shadow-md" />
                    <div className="self-end font-bold transform rotate-180 w-full text-center z-10">{{label}}</div>
                    {{card.bonus > 0 && <div className="absolute -top-1 -right-1 text-[9px] bg-[#ffd700] text-black px-1.5 py-0.5 rounded-full border border-yellow-700 font-bold z-20 shadow-sm">+{{card.bonus}}</div>}}
                    {{card.playedAs && <div className="absolute inset-0 flex items-center justify-center bg-black/60 rounded-xl z-20"><span className="text-[10px] font-bold text-[#ffd700] bg-black/80 px-2 py-1 rounded border border-[#ffd700] uppercase tracking-wider">{{card.playedAs}}</span></div>}}
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

        // MODAL DE AYUDA / MANUAL DEL PIRATA
        const HelpModal = ({{ onClose }}) => (
            <div className="fixed inset-0 bg-black/90 z-[100] flex items-center justify-center p-4 backdrop-blur-sm animate-fadeIn">
                <div className="bg-[#1e293b] p-6 md:p-8 rounded-2xl border-2 border-[#c5a059] shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto custom-scrollbar relative text-left text-[#e2d2ac]">
                    <button onClick={{onClose}} className="absolute top-4 right-4 text-slate-400 hover:text-white bg-slate-800 rounded-full p-2 transition-colors"><X size={{24}}/></button>
                    <h2 className="text-2xl md:text-4xl font-bold text-[#ffd700] mb-6 flex items-center gap-3 border-b border-[#334155] pb-4">
                        <HelpCircle size={{36}}/> Manual del Pirata
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 text-sm md:text-base">
                        
                        {{/* COLUMNA IZQUIERDA */}}
                        <div className="space-y-6">
                            <section>
                                <h3 className="text-xl font-bold text-white mb-2 pb-1 border-b border-slate-600">🏴‍☠️ Cómo Jugar</h3>
                                <p className="mb-2">El juego consta de <strong>10 rondas</strong>. En la ronda 1 se reparte 1 carta, en la 10 se reparten 10. Al inicio, debes observar tu mano y <strong>apostar cuántas bazas vas a ganar</strong>.</p>
                                <ul className="list-disc pl-5 space-y-1 text-slate-300">
                                    <li>El primer jugador tira una carta y marca el <strong>palo a seguir</strong> (Loro, Mapa o Cofre). Los demás están obligados a seguir ese palo si lo tienen.</li>
                                    <li>Las cartas negras (Jolly Roger) son triunfos: ganan a cualquier palo normal.</li>
                                    <li>Las cartas Especiales (Huidas, Sirenas, Piratas, etc.) se pueden jugar en cualquier momento, <strong>incluso si tienes el palo pedido</strong>.</li>
                                </ul>
                            </section>

                            <section>
                                <h3 className="text-xl font-bold text-white mb-2 pb-1 border-b border-slate-600">👑 Jerarquía de Cartas</h3>
                                <p className="mb-2 text-slate-400 text-xs">De la más fuerte a la más débil:</p>
                                <ol className="list-decimal pl-5 space-y-1 text-slate-300">
                                    <li><strong className="text-yellow-400">Skull King:</strong> Gana a todo... ¡excepto a la Sirena!</li>
                                    <li><strong className="text-cyan-400">Sirena:</strong> Gana al Skull King y palos, pero pierde contra Piratas.</li>
                                    <li><strong className="text-red-400">Pirata / Tigresa (Pirata):</strong> Ganan a Sirenas y palos normales/negros.</li>
                                    <li><strong className="text-gray-400">Jolly Roger (Negras):</strong> Triunfo numerado (1-14). Gana a palos normales.</li>
                                    <li><strong>Palos Normales:</strong> Loro (Verde), Mapa (Morado), Cofre (Amarillo). El mayor número gana.</li>
                                    <li><strong className="text-sky-300">Huida / Tigresa (Huida):</strong> Siempre pierde (valor 0).</li>
                                    <li><strong className="text-emerald-400">Kraken:</strong> Destruye la baza. Nadie la gana. El que lo tiró decide quién empieza la siguiente.</li>
                                    <li><strong className="text-blue-400">Ballena:</strong> Cambia todos los palos y gana la carta numérica más alta (incluso si no es negra).</li>
                                </ol>
                            </section>

                            <section>
                                <h3 className="text-xl font-bold text-white mb-2 pb-1 border-b border-slate-600">💰 Puntuaciones</h3>
                                <ul className="list-disc pl-5 space-y-1 text-slate-300">
                                    <li><strong className="text-green-400">Apuesta Acertada (1 a 10):</strong> +20 pts por cada baza ganada.</li>
                                    <li><strong className="text-green-400">Apuesta 0 Acertada:</strong> +10 pts multiplicados por la ronda actual (ej. Ronda 5 = +50 pts).</li>
                                    <li><strong className="text-red-400">Apuesta Fallada:</strong> -10 pts por cada baza de diferencia entre tu apuesta y lo que ganaste (incluso si apuestas 0).</li>
                                    <li className="pt-2 text-[#ffd700]"><strong>Puntos Extra (Bonus):</strong>
                                        <ul className="pl-5 mt-1 text-slate-300 border-l border-[#c5a059] ml-2 space-y-1">
                                            <li>- Ganar con un 14 normal: +10 pts.</li>
                                            <li>- Ganar con un 14 negro: +20 pts.</li>
                                            <li>- Pirata captura a una Sirena: +20 pts.</li>
                                            <li>- Skull King captura Piratas: +30 pts (c/u).</li>
                                            <li>- Sirena captura al Skull King: +40 pts.</li>
                                        </ul>
                                    </li>
                                </ul>
                            </section>
                        </div>

                        {{/* COLUMNA DERECHA: HABILIDADES PIRATA */}}
                        <div className="bg-[#0f172a] p-5 rounded-xl border-2 border-red-900/50">
                            <h3 className="text-xl font-bold text-[#ffd700] mb-4 pb-2 border-b border-[#c5a059] flex items-center gap-2">
                                <Swords size={{24}}/> Habilidades Pirata
                            </h3>
                            <p className="mb-4 text-sm text-slate-400">
                                Al ganar una baza con uno de estos piratas, se activará su poder especial inmediatamente:
                            </p>
                            <div className="space-y-4">
                                <div className="bg-[#1e293b] p-3 rounded-lg border-l-4 border-red-500">
                                    <span className="font-bold text-white block mb-1">Capitán Pedro</span>
                                    <span className="text-sm text-slate-300">Te permite modificar tu apuesta actual sumando 1, restando 1, o manteniéndola igual. Muy útil si te pasas o te quedas corto.</span>
                                </div>
                                <div className="bg-[#1e293b] p-3 rounded-lg border-l-4 border-blue-500">
                                    <span className="font-bold text-white block mb-1">Contramaestre Elías</span>
                                    <span className="text-sm text-slate-300">Haces una apuesta secundaria secreta. Puedes apostar 0, 10 o 20 pts extras (se sumarán o restarán a tu puntuación dependiendo de si aciertas tu apuesta principal o no).</span>
                                </div>
                                <div className="bg-[#1e293b] p-3 rounded-lg border-l-4 border-emerald-500">
                                    <span className="font-bold text-white block mb-1">Vigía Javi</span>
                                    <span className="text-sm text-slate-300">¡Locura! Obliga a que en la siguiente baza, la carta ganadora sea <strong>la más baja</strong> en lugar de la más alta. Invierte totalmente las reglas.</span>
                                </div>
                                <div className="bg-[#1e293b] p-3 rounded-lg border-l-4 border-purple-500">
                                    <span className="font-bold text-white block mb-1">Timonel Sergio</span>
                                    <span className="text-sm text-slate-300">Toma el timón y elige qué jugador (puedes ser tú u otro) empezará tirando carta en la siguiente baza.</span>
                                </div>
                                <div className="bg-[#1e293b] p-3 rounded-lg border-l-4 border-orange-500">
                                    <span className="font-bold text-white block mb-1">Corsario Torri</span>
                                    <span className="text-sm text-slate-300">El ladrón de manos. Intercambias todas las cartas que te quedan en la mano con las de cualquier otro jugador de la mesa que elijas.</span>
                                </div>
                            </div>
                        </div>

                    </div>
                    <div className="mt-8 text-center">
                        <button onClick={{onClose}} className="bg-[#c5a059] hover:bg-[#ffd700] text-black px-10 py-3 rounded-xl font-bold text-lg transition-colors shadow-lg">¡Entendido, al abordaje!</button>
                    </div>
                </div>
            </div>
        );

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
                await updateDoc(roomRef(), {{
                    phase:'BIDDING', round:roundNum, players,
                    trickCards:[], turnIndex:(gameState.dealerIndex+1)%players.length,
                    nextTrickLowWins:false, nextTrickStarter:null,
                    alliances:[], pendingPirateAction:null
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
                const valid = gameState.trickCards
                    .filter(p => p.card.type !== CARD_TYPES.ESCAPE && p.card.type !== CARD_TYPES.COINS)
                    .sort((a,b) => a.order - b.order);
                const leadSuit = valid.length > 0 && valid[0].card.type === CARD_TYPES.SUIT ? valid[0].card.suit : null;
                if (!leadSuit) return true;
                const myHand = gameState.players.find(p => p.uid === user.uid).hand;
                const hasLead = myHand.some(c => c.type === CARD_TYPES.SUIT && c.suit === leadSuit);
                if (card.type === CARD_TYPES.SUIT) {{
                    if (hasLead) return card.suit === leadSuit || card.suit === 'TRUMP';
                    return true;
                }}
                return true;
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

                if      (action.pirateId === 'PEDRO')  me.bid = Math.max(0, me.bid + payload.mod);
                else if (action.pirateId === 'ELIAS')  me.eliasBet = payload.bet;
                else if (action.pirateId === 'TORRI' && payload.targetId) {{
                    const ti = players.findIndex(p => p.uid === payload.targetId);
                    if (ti !== -1) {{ const h = [...me.hand]; me.hand = [...players[ti].hand]; players[ti].hand = h; }}
                }}
                else if (action.pirateId === 'JAVI')   nextLowWins = true;
                else if (action.pirateId === 'SERGIO') nextStarterOverride = payload.targetId;

                await finishTrickResolution(user.uid, gameState.trickCards, players, {{ nextLowWins, nextStarterOverride }});
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
                        let pts = diff === 0
                            ? (p.bid === 0 ? gameState.round*10 : p.bid*20) + p.bonusPoints + (p.eliasBet||0)
                            : diff * -10 - (p.eliasBet||0);
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
                    await updateDoc(roomRef(), {{
                        players, phase: gameState.round>=10?'GAME_END':'ROUND_END',
                        trickCards:[], pendingPirateAction:null, alliances
                    }});
                }} else {{
                    await updateDoc(roomRef(), {{
                        players, trickCards:[], turnIndex:nextTurn, phase:'PLAYING',
                        nextTrickLowWins: extra.nextLowWins||false,
                        nextTrickStarter:null, pendingPirateAction:null, alliances
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
                        <div className="bg-[#1e293b] p-3 flex justify-between items-center shadow-lg z-20 border-b border-[#334155] flex-shrink-0">
                            <div className="flex items-center gap-3">
                                <div className="bg-[#0f172a] px-4 py-1 rounded-full border border-[#c5a059] flex items-center gap-2">
                                    <span className="text-slate-400 text-xs uppercase">Ronda</span>
                                    <span className="text-[#ffd700] font-bold text-lg">{{gameState.round}}</span>
                                    <span className="text-slate-600 text-xs">/10</span>
                                </div>
                                {{gameState.nextTrickLowWins && <span className="bg-purple-900 text-purple-300 text-xs px-2 py-1 rounded border border-purple-600 font-bold">⬇ BAJA GANA</span>}}
                            </div>
                            
                            {{/* BOTONES DE AYUDA Y LEADERBOARD EN EL HEADER */}}
                            <div className="flex gap-2">
                                <button onClick={{()=>setShowHelp(true)}} className="bg-[#334155] p-2 rounded text-[#c5a059] hover:text-[#ffd700] hover:bg-[#475569] transition-colors shadow-sm" title="Manual del Pirata (Ayuda)">
                                    <HelpCircle size={{20}}/>
                                </button>
                                <button onClick={{()=>setShowLeaderboard(!showLeaderboard)}} className="bg-[#334155] p-2 rounded text-white hover:bg-[#475569] transition-colors shadow-sm" title="Clasificación">
                                    <ListOrdered size={{20}}/>
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

                        {{/* ── BANNER GANADOR (encima de oponentes) ── */}}
                        {{isResolvingPhase && trickWinnerId && (
                            <div className="flex justify-center py-2 flex-shrink-0" style={{{{marginRight: showLeaderboard?'240px':'0', transition:'margin 0.3s'}}}}>
                                <WinnerBanner players={{gameState.players}} winnerId={{trickWinnerId}} />
                            </div>
                        )}}

                        {{/* ── OPONENTES ── */}}
                        <div className="flex justify-center gap-3 p-3 overflow-x-auto flex-shrink-0" style={{{{marginRight: showLeaderboard?'240px':'0', transition:'margin 0.3s'}}}}>
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
                                                {{p.tricksWon}} / {{p.bid===null?'?':p.bid}}
                                            </div>
                                            <div className="flex -space-x-1 justify-center">
                                                {{Array(Math.min(p.hand.length,3)).fill(0).map((_,i)=>(
                                                    <div key={{i}} className="w-3 h-4 bg-[#334155] border border-[#475569] rounded-sm"></div>
                                                ))}}
                                                {{p.hand.length>3 && <span className="text-[8px] text-slate-500 ml-1">+{{p.hand.length-3}}</span>}}
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
                                return (
                                    <div key={{i}} className="absolute transition-all duration-500 ease-out z-10" style={{{{
                                        transform: `translate(${{Math.cos(2*Math.PI*i/gameState.trickCards.length)*rx}}px, ${{Math.sin(2*Math.PI*i/gameState.trickCards.length)*ry}}px) rotate(${{(i - gameState.trickCards.length/2)*15}}deg) ${{isWinnerCard ? 'scale(1.15)' : ''}}`
                                    }}}}>
                                        <div className="relative group">
                                            <Card card={{play.card}} size={{isMobile?'small':'normal'}}/>
                                            {{/* Halo dorado en la carta ganadora */}}
                                            {{isWinnerCard && (
                                                <div className="absolute inset-0 rounded-xl ring-4 ring-[#ffd700] shadow-[0_0_20px_rgba(255,215,0,0.8)] pointer-events-none z-30 animate-pulse"></div>
                                            )}}
                                            <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-[10px] font-bold bg-black/80 text-white px-2 py-0.5 rounded-full whitespace-nowrap border border-white/10 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                                                {{play.playerName}}
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
                                <div className={{`flex justify-center overflow-x-auto px-4 pb-4 gap-2 hide-scrollbar transition-opacity duration-200 ${{isHandMinimized?'opacity-0 pointer-events-none':'opacity-100'}}`}}>
                                    <div className="flex md:-space-x-6 min-w-max pt-2 gap-2 md:gap-0">
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
