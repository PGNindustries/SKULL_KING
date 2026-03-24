import streamlit as st
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE LA PÁGINA STREAMLIT ---
st.set_page_config(layout="wide", page_title="Skull King Pirata", page_icon="🏴‍☠️")

# Ocultar elementos de la interfaz de Streamlit para pantalla completa
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container {padding: 0rem; max-width: 100%;}
            iframe {border: none; width: 100vw; height: 100vh;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- CÓDIGO HTML/REACT DEL JUEGO ---
html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Skull King</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <style>
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: #1e293b; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #c5a059; border-radius: 4px; }
        .hide-scrollbar::-webkit-scrollbar { display: none; }
        .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        body { margin: 0; overflow: hidden; background-color: #0f172a; }
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel" data-type="module">
        import React, { useState, useEffect, useMemo, useRef } from 'https://esm.sh/react@18';
        import { createRoot } from 'https://esm.sh/react-dom@18/client';
        import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js';
        import { getAuth, signInAnonymously, onAuthStateChanged } from 'https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js';
        import { getFirestore, collection, doc, setDoc, getDoc, onSnapshot, updateDoc, arrayUnion, increment, serverTimestamp, runTransaction } from 'https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js';
        import { Skull, Anchor, Map, Trees, Coins, XCircle, Flag, Trophy, Users, PlayCircle, LogIn, Crown, Swords, Ghost, HelpCircle, Copy, Check, Loader, AlertCircle, ArrowUp, ArrowDown, Handshake, RefreshCw, Eye, Gavel, ListOrdered, X, Compass, Ship, Home, ChevronDown, ChevronUp } from 'https://esm.sh/lucide-react@0.358.0';

        // =====================================================================
        // ⚠️ IMPORTANTE: CONFIGURACIÓN DE FIREBASE 
        // Reemplaza estos valores con los de tu proyecto de Firebase
        // =====================================================================
        const firebaseConfig = {
            apiKey: "TU_API_KEY",
            authDomain: "TU_PROYECTO.firebaseapp.com",
            projectId: "TU_PROYECTO",
            storageBucket: "TU_PROYECTO.appspot.com",
            messagingSenderId: "TU_SENDER_ID",
            appId: "TU_APP_ID"
        };

        const app = initializeApp(firebaseConfig);
        const auth = getAuth(app);
        const db = getFirestore(app);
        const appId = 'skull-king-custom-streamlit';
        const ROOM_COLLECTION = 'skull_king_rooms';

        // --- UTILIDADES ---
        const SUITS = {
          PARROT: { color: 'bg-emerald-700', text: 'text-emerald-100', border: 'border-emerald-900', icon: Trees, label: 'Loro', bonus: 10 },
          MAP: { color: 'bg-indigo-700', text: 'text-indigo-100', border: 'border-indigo-900', icon: Map, label: 'Mapa', bonus: 10 },
          CHEST: { color: 'bg-amber-600', text: 'text-amber-100', border: 'border-amber-900', icon: Coins, label: 'Cofre', bonus: 10 },
          TRUMP: { color: 'bg-gray-900', text: 'text-gray-100', border: 'border-black', icon: Skull, label: 'Jolly Roger', bonus: 20 }
        };

        const CARD_TYPES = { SUIT: 'suit', ESCAPE: 'escape', PIRATE: 'pirate', SKULLKING: 'skullking', MERMAID: 'mermaid', TIGRESS: 'tigress', KRAKEN: 'kraken', WHALE: 'whale', COINS: 'coins' };

        const PIRATE_NAMES = {
          PEDRO: { name: 'Capitán Pedro', desc: 'Modifica tu apuesta (-1, 0, +1)' },
          ELIAS: { name: 'Contramaestre Elías', desc: 'Apuesta secundaria (0, 10, 20)' },
          JAVI: { name: 'Vigía Javi', desc: 'Siguiente ronda gana la carta más baja' },
          SERGIO: { name: 'Timonel Sergio', desc: 'Elige quién empieza la siguiente' },
          TORRI: { name: 'Corsario Torri', desc: 'Intercambia mano con otro jugador' }
        };

        const generateRoomId = () => {
          const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; 
          let result = '';
          for (let i = 0; i < 5; i++) result += chars.charAt(Math.floor(Math.random() * chars.length));
          return result;
        };

        const generateDeck = () => {
          let deck = [];
          let idCounter = 0;
          ['PARROT', 'MAP', 'CHEST'].forEach(suitKey => {
            for (let i = 1; i <= 14; i++) deck.push({ id: `c-${idCounter++}`, type: CARD_TYPES.SUIT, suit: suitKey, value: i, rank: i, bonus: i === 14 ? 10 : 0 });
          });
          for (let i = 1; i <= 14; i++) deck.push({ id: `c-${idCounter++}`, type: CARD_TYPES.SUIT, suit: 'TRUMP', value: i, rank: 20 + i, bonus: i === 14 ? 20 : 0 });
          for(let i=0; i<5; i++) deck.push({ id: `c-${idCounter++}`, type: CARD_TYPES.ESCAPE, value: 0, label: 'Huida' });
          Object.keys(PIRATE_NAMES).forEach(key => deck.push({ id: `c-${idCounter++}`, type: CARD_TYPES.PIRATE, value: 50, label: 'Pirata', pirateId: key }));
          deck.push({ id: `c-${idCounter++}`, type: CARD_TYPES.TIGRESS, value: 55, label: 'Tigresa' }); 
          deck.push({ id: `c-${idCounter++}`, type: CARD_TYPES.SKULLKING, value: 60, label: 'Skull King' });
          deck.push({ id: `c-${idCounter++}`, type: CARD_TYPES.MERMAID, value: 45, label: 'Sirena 1' });
          deck.push({ id: `c-${idCounter++}`, type: CARD_TYPES.MERMAID, value: 45, label: 'Sirena 2' });
          deck.push({ id: `c-${idCounter++}`, type: CARD_TYPES.KRAKEN, value: 0, label: 'Kraken' });
          deck.push({ id: `c-${idCounter++}`, type: CARD_TYPES.WHALE, value: 0, label: 'Ballena' });
          deck.push({ id: `c-${idCounter++}`, type: CARD_TYPES.COINS, value: 0, label: 'Monedas' });

          let currentIndex = deck.length, randomIndex;
          while (currentIndex !== 0) {
            randomIndex = Math.floor(Math.random() * currentIndex);
            currentIndex--;
            [deck[currentIndex], deck[randomIndex]] = [deck[randomIndex], deck[currentIndex]];
          }
          return deck;
        };

        const determineTrickWinner = (playedCards, isLowCardMode = false) => {
          if (!playedCards || playedCards.length === 0) return null;
          const sortedCards = [...playedCards].sort((a,b) => a.order - b.order);

          if (sortedCards.some(p => p.card.type === CARD_TYPES.KRAKEN)) return 'KRAKEN';

          if (isLowCardMode) {
              const numberCards = sortedCards.filter(p => p.card.type === CARD_TYPES.SUIT);
              if (numberCards.length > 0) return numberCards.sort((a,b) => a.card.value - b.card.value)[0].playerId;
              return sortedCards[0].playerId;
          }

          if (sortedCards.some(p => p.card.type === CARD_TYPES.WHALE)) {
              const numberCards = sortedCards.filter(p => p.card.type === CARD_TYPES.SUIT);
              if (numberCards.length > 0) return numberCards.sort((a,b) => b.card.value - a.card.value)[0].playerId;
              const firstNonWhale = sortedCards.find(p => p.card.type !== CARD_TYPES.WHALE);
              return firstNonWhale ? firstNonWhale.playerId : sortedCards[0].playerId; 
          }

          const hasSkullKing = sortedCards.some(p => p.card.type === CARD_TYPES.SKULLKING);
          const hasMermaid = sortedCards.some(p => p.card.type === CARD_TYPES.MERMAID);
          const hasPirate = sortedCards.some(p => p.card.type === CARD_TYPES.PIRATE || (p.card.type === CARD_TYPES.TIGRESS && p.card.playedAs === 'pirate'));

          if (hasSkullKing) {
            if (hasMermaid) {
                const skPlay = sortedCards.find(p => p.card.type === CARD_TYPES.SKULLKING);
                const mermaidPlay = sortedCards.find(p => p.card.type === CARD_TYPES.MERMAID);
                return (mermaidPlay.order > skPlay.order) ? mermaidPlay.playerId : skPlay.playerId;
            }
            return sortedCards.find(p => p.card.type === CARD_TYPES.SKULLKING).playerId;
          }

          if (hasPirate) return sortedCards.find(p => p.card.type === CARD_TYPES.PIRATE || (p.card.type === CARD_TYPES.TIGRESS && p.card.playedAs === 'pirate')).playerId;
          if (hasMermaid) return sortedCards.find(p => p.card.type === CARD_TYPES.MERMAID).playerId;

          const nonEscapeCards = sortedCards.filter(p => p.card.type !== CARD_TYPES.ESCAPE && p.card.type !== CARD_TYPES.COINS && !(p.card.type === CARD_TYPES.TIGRESS && p.card.playedAs === 'escape'));
          if (nonEscapeCards.length === 0) return sortedCards[0].playerId;

          const leadCard = nonEscapeCards[0].card;
          const leadSuit = leadCard.suit;
          let bestPlay = nonEscapeCards[0];

          for (let i = 1; i < nonEscapeCards.length; i++) {
              const challenger = nonEscapeCards[i];
              const winnerCard = bestPlay.card;
              const challengerCard = challenger.card;
              if (challengerCard.suit === 'TRUMP' && winnerCard.suit !== 'TRUMP') { bestPlay = challenger; continue; }
              if (challengerCard.suit === 'TRUMP' && winnerCard.suit === 'TRUMP') {
                  if (challengerCard.value > winnerCard.value) bestPlay = challenger;
                  continue;
              }
              if (winnerCard.suit !== 'TRUMP') {
                  if (challengerCard.suit === leadSuit && winnerCard.suit === leadSuit) {
                      if (challengerCard.value > winnerCard.value) bestPlay = challenger;
                  }
                  else if (challengerCard.suit === leadSuit && winnerCard.suit !== leadSuit) bestPlay = challenger;
              }
          }
          return bestPlay.playerId;
        };

        const Waves = ({size}) => <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1" /><path d="M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1" /><path d="M2 18c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1" /></svg>;

        const Card = ({ card, onClick, playable = false, size = 'normal', hidden = false }) => {
          if (hidden) {
            return (
              <div className={`
                ${size === 'small' ? 'w-10 h-14' : 'w-24 h-36'} 
                bg-[#1a1a2e] border-2 border-[#c5a059] rounded-lg shadow-lg flex items-center justify-center flex-shrink-0 relative overflow-hidden group
              `}>
                <div className="absolute inset-0 opacity-10 bg-[url('https://www.transparenttextures.com/patterns/wood-pattern.png')]"></div>
                <Skull className="text-[#c5a059] opacity-30" size={32} />
              </div>
            );
          }

          const isSuit = card.type === CARD_TYPES.SUIT;
          const suitConfig = isSuit ? SUITS[card.suit] : null;
          
          let bgColor = 'bg-slate-700', textColor = 'text-white', borderColor = 'border-slate-600', Icon = HelpCircle, label = '';

          if (isSuit) {
            bgColor = suitConfig.color; textColor = suitConfig.text; borderColor = suitConfig.border; Icon = suitConfig.icon; label = card.value;
          } else {
            switch(card.type) {
              case CARD_TYPES.ESCAPE: bgColor = 'bg-sky-200'; textColor = 'text-sky-900'; borderColor='border-sky-400'; Icon = Flag; label = 'Huida'; break;
              case CARD_TYPES.PIRATE: bgColor = 'bg-red-800'; textColor = 'text-red-100'; borderColor='border-red-950'; Icon = Swords; label = PIRATE_NAMES[card.pirateId]?.name || 'Pirata'; break;
              case CARD_TYPES.SKULLKING: bgColor = 'bg-gray-950'; textColor = 'text-white'; borderColor='border-yellow-500'; Icon = Crown; label = 'King'; break;
              case CARD_TYPES.MERMAID: bgColor = 'bg-cyan-600'; textColor = 'text-cyan-50'; borderColor='border-cyan-800'; Icon = Anchor; label = 'Sirena'; break;
              case CARD_TYPES.TIGRESS: bgColor = 'bg-orange-600'; textColor = 'text-orange-100'; borderColor='border-orange-800'; Icon = Ghost; label = 'Tigresa'; break;
              case CARD_TYPES.KRAKEN: bgColor = 'bg-emerald-950'; textColor = 'text-emerald-400'; borderColor='border-emerald-600'; Icon = XCircle; label = 'Kraken'; break;
              case CARD_TYPES.WHALE: bgColor = 'bg-blue-900'; textColor = 'text-blue-200'; borderColor='border-blue-950'; Icon = Waves; label = 'Ballena'; break;
              case CARD_TYPES.COINS: bgColor = 'bg-yellow-500'; textColor = 'text-yellow-950'; borderColor='border-yellow-700'; Icon = Handshake; label = 'Alianza'; break;
            }
          }

          const baseClasses = `relative rounded-xl shadow-xl flex flex-col items-center justify-between p-2 select-none transition-all duration-200 ${size === 'small' ? 'w-12 h-16 text-[10px]' : 'w-24 h-36 text-base hover:-translate-y-4 hover:shadow-2xl hover:z-10'} ${playable ? 'cursor-pointer ring-2 ring-[#ffd700] ring-offset-2 ring-offset-black' : 'cursor-not-allowed opacity-80 brightness-75'} ${bgColor} ${textColor} border-2 ${borderColor} flex-shrink-0 font-serif`;

          return (
            <div className={baseClasses} onClick={onClick}>
              <div className="absolute inset-0 opacity-10 pointer-events-none mix-blend-multiply bg-white"></div>
              <div className="self-start font-bold truncate w-full text-center z-10">{label}</div>
              <Icon size={size === 'small' ? 16 : 32} className="z-10 drop-shadow-md" />
              <div className="self-end font-bold transform rotate-180 w-full text-center z-10">{label}</div>
              {card.bonus > 0 && <div className="absolute -top-1 -right-1 text-[9px] bg-[#ffd700] text-black px-1.5 py-0.5 rounded-full border border-yellow-700 font-bold z-20 shadow-sm">+{card.bonus}</div>}
              {card.playedAs && <div className="absolute inset-0 flex items-center justify-center bg-black/60 rounded-xl z-20"><span className="text-[10px] font-bold text-[#ffd700] bg-black/80 px-2 py-1 rounded border border-[#ffd700] uppercase tracking-wider">{card.playedAs}</span></div>}
            </div>
          );
        };

        function SkullKingApp() {
          const [user, setUser] = useState(null);
          const [activeRoomId, setActiveRoomId] = useState(''); 
          const [inputRoomId, setInputRoomId] = useState('');
          const [playerName, setPlayerName] = useState('');
          const [gameState, setGameState] = useState(null); 
          const [loading, setLoading] = useState(false);
          const [error, setError] = useState('');
          const [copied, setCopied] = useState(false);
          const [toast, setToast] = useState(null);
          const [showLeaderboard, setShowLeaderboard] = useState(false);
          
          const [tigressModal, setTigressModal] = useState(null);
          const [isHandMinimized, setIsHandMinimized] = useState(false);
          const resolvingTrickRef = useRef(false);

          const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
          useEffect(() => {
              const handleResize = () => setIsMobile(window.innerWidth < 768);
              window.addEventListener('resize', handleResize);
              return () => window.removeEventListener('resize', handleResize);
          }, []);

          const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(null), 3500); };

          useEffect(() => {
            const initAuth = async () => {
                try {
                    await signInAnonymously(auth);
                } catch (err) {
                    setError("Error conectando con los servidores del juego. Revisa Firebase.");
                    console.error(err);
                }
            };
            initAuth();
            const unsubscribe = onAuthStateChanged(auth, (u) => setUser(u));
            return () => unsubscribe();
          }, []);

          useEffect(() => {
            if (!user || !activeRoomId) return;
            const unsub = onSnapshot(doc(db, 'artifacts', appId, 'public', 'data', ROOM_COLLECTION, `sk_room_${activeRoomId}`), (snap) => {
              if (snap.exists()) {
                setGameState(snap.data()); setError('');
              } else {
                setError("La sala no existe o ha sido cerrada."); setActiveRoomId(''); setGameState(null);
              }
            });
            return () => unsub();
          }, [user, activeRoomId]);

          useEffect(() => {
              if (!gameState) return;
              const isInteraction = gameState.phase === 'PIRATE_ACTION' || !!tigressModal;
              setIsHandMinimized(isInteraction);
          }, [gameState?.phase, tigressModal]);

          useEffect(() => {
              if (!gameState || !user) return;
              if (gameState.hostId !== user.uid) return;
              const playersCount = gameState.players.length;
              if (gameState.phase === 'PLAYING' && gameState.trickCards.length >= playersCount) {
                  if (!resolvingTrickRef.current) {
                      resolvingTrickRef.current = true;
                      setTimeout(() => resolveTrick(gameState.trickCards).finally(() => resolvingTrickRef.current = false), 3000); 
                  }
              }
          }, [gameState?.trickCards?.length, gameState?.phase]);

          const createRoom = async () => {
            if (!playerName) return setError("Falta nombre");
            const newRoomId = generateRoomId();
            const initialData = {
              roomId: newRoomId, hostId: user.uid, phase: 'LOBBY', round: 1, turnIndex: 0, dealerIndex: 0,
              players: [{ uid: user.uid, name: playerName, score: 0, hand: [], bid: null, tricksWon: 0, lastRoundScore: 0, bonusPoints: 0, eliasBet: null }],
              trickCards: [], nextTrickLowWins: false, nextTrickStarter: null, alliances: [], createdAt: serverTimestamp()
            };
            await setDoc(doc(db, 'artifacts', appId, 'public', 'data', ROOM_COLLECTION, `sk_room_${newRoomId}`), initialData);
            setActiveRoomId(newRoomId);
          };

          const joinRoom = async () => {
            if (!playerName || !inputRoomId) return setError("Faltan datos");
            const targetRoomId = inputRoomId.trim().toUpperCase().replace(/[^A-Z0-9]/g, '');
            const roomRef = doc(db, 'artifacts', appId, 'public', 'data', ROOM_COLLECTION, `sk_room_${targetRoomId}`);
            try {
                await runTransaction(db, async (t) => {
                    const docSnap = await t.get(roomRef);
                    if (!docSnap.exists()) throw new Error("No existe");
                    const data = docSnap.data();
                    if (!data.players.some(p => p.uid === user.uid)) {
                        if (data.phase !== 'LOBBY') throw new Error("Empezado");
                        t.update(roomRef, { players: [...data.players, { uid: user.uid, name: playerName, score: 0, hand: [], bid: null, tricksWon: 0, lastRoundScore: 0, bonusPoints: 0, eliasBet: null }] });
                    }
                });
                setActiveRoomId(targetRoomId);
            } catch (e) { setError(e.message); }
          };

          const resetToLobby = async () => {
              const resetPlayers = gameState.players.map(p => ({ uid: p.uid, name: p.name, score: 0, hand: [], bid: null, tricksWon: 0, lastRoundScore: 0, bonusPoints: 0, eliasBet: null }));
              await updateDoc(doc(db, 'artifacts', appId, 'public', 'data', ROOM_COLLECTION, `sk_room_${activeRoomId}`), {
                  phase: 'LOBBY', round: 1, turnIndex: 0, dealerIndex: 0, players: resetPlayers, trickCards: [],
                  nextTrickLowWins: false, nextTrickStarter: null, alliances: [], pendingPirateAction: null, createdAt: serverTimestamp() 
              });
          };

          const startRound = async (roundNum) => {
            const deck = generateDeck();
            const updatedPlayers = JSON.parse(JSON.stringify(gameState.players));
            updatedPlayers.forEach(p => { p.hand = deck.splice(0, roundNum); p.bid = null; p.tricksWon = 0; p.bonusPoints = 0; p.eliasBet = null; });
            await updateDoc(doc(db, 'artifacts', appId, 'public', 'data', ROOM_COLLECTION, `sk_room_${activeRoomId}`), {
                phase: 'BIDDING', round: roundNum, players: updatedPlayers, trickCards: [],
                turnIndex: (gameState.dealerIndex + 1) % gameState.players.length,
                nextTrickLowWins: false, nextTrickStarter: null, alliances: [], pendingPirateAction: null
            });
          };

          const submitBid = async (amount) => {
              const newPlayers = [...gameState.players];
              const me = newPlayers.find(p => p.uid === user.uid);
              me.bid = amount;
              const allBid = newPlayers.every(p => p.bid !== null);
              await updateDoc(doc(db, 'artifacts', appId, 'public', 'data', ROOM_COLLECTION, `sk_room_${activeRoomId}`), {
                  players: newPlayers, phase: allBid ? 'PLAYING' : 'BIDDING'
              });
          };

          const handleCardClick = (card) => {
              if (gameState.phase !== 'PLAYING') return;
              if (gameState.trickCards.length >= gameState.players.length) return showToast("Esperando resolución...");
              if (gameState.players[gameState.turnIndex].uid !== user.uid) return showToast("No es tu turno");
              if (!canPlayCard(card)) return showToast("Debes seguir el palo");
              if (card.type === CARD_TYPES.TIGRESS && !card.playedAs) return setTigressModal(card);
              playCard(card);
          };

          const playCard = async (card, extraData = {}) => {
              const myIndex = gameState.players.findIndex(p => p.uid === user.uid);
              const newPlayers = JSON.parse(JSON.stringify(gameState.players));
              const myPlayer = newPlayers[myIndex];
              myPlayer.hand = myPlayer.hand.filter(c => c.id !== card.id);
              const cardOnTable = { ...card, ...extraData };
              const newTrickCards = [...gameState.trickCards, { playerId: user.uid, playerName: myPlayer.name, card: cardOnTable, order: gameState.trickCards.length }];
              
              await updateDoc(doc(db, 'artifacts', appId, 'public', 'data', ROOM_COLLECTION, `sk_room_${activeRoomId}`), {
                  players: newPlayers, trickCards: newTrickCards, turnIndex: (gameState.turnIndex + 1) % gameState.players.length
              });
              setTigressModal(null);
          };

          const resolveTrick = async (cards) => {
              try {
                  let winnerId = determineTrickWinner(cards, gameState.nextTrickLowWins);
                  if (!winnerId && cards.length > 0) winnerId = cards[0].playerId;
                  const newPlayers = JSON.parse(JSON.stringify(gameState.players));
                  
                  let pirateAction = null;
                  if (winnerId !== 'KRAKEN') {
                      const winningPlay = cards.find(p => p.playerId === winnerId);
                      if (winningPlay && winningPlay.card.type === CARD_TYPES.PIRATE && PIRATE_NAMES[winningPlay.card.pirateId]) {
                          const pid = winningPlay.card.pirateId;
                          const roundOver = newPlayers[0].hand.length === 0;
                          const isEndGameAction = ['PEDRO', 'ELIAS'].includes(pid);
                          if (!roundOver || isEndGameAction) pirateAction = { pirateId: pid, winnerId: winnerId };
                      }
                  }

                  if (pirateAction) {
                      await updateDoc(doc(db, 'artifacts', appId, 'public', 'data', ROOM_COLLECTION, `sk_room_${activeRoomId}`), {
                          phase: 'PIRATE_ACTION', pendingPirateAction: pirateAction,
                          players: newPlayers.map(p => {
                              if(p.uid === winnerId) {
                                  p.tricksWon += 1;
                                  cards.forEach(play => { if (play.card.bonus) p.bonusPoints += play.card.bonus; });
                              }
                              return p;
                          })
                      });
                      return;
                  }
                  finishTrickResolution(winnerId, cards, newPlayers);
              } catch (e) { console.error(e); }
          };

          const executePirateAction = async (payload) => {
              const action = gameState.pendingPirateAction;
              if (!action || gameState.phase !== 'PIRATE_ACTION') return;
              const newPlayers = JSON.parse(JSON.stringify(gameState.players));
              const myIndex = newPlayers.findIndex(p => p.uid === user.uid);
              const me = newPlayers[myIndex];

              let nextLowWins = false, nextStarterOverride = null;
              if (action.pirateId === 'PEDRO') me.bid = Math.max(0, me.bid + payload.mod);
              else if (action.pirateId === 'ELIAS') me.eliasBet = payload.bet;
              else if (action.pirateId === 'TORRI') {
                  const targetIndex = newPlayers.findIndex(p => p.uid === payload.targetId);
                  if (targetIndex !== -1) {
                      const myHand = [...me.hand]; me.hand = [...newPlayers[targetIndex].hand]; newPlayers[targetIndex].hand = myHand;
                  }
              } 
              else if (action.pirateId === 'JAVI') nextLowWins = true;
              else if (action.pirateId === 'SERGIO') nextStarterOverride = payload.targetId;

              await finishTrickResolution(user.uid, gameState.trickCards, newPlayers, { nextLowWins, nextStarterOverride });
          };

          const finishTrickResolution = async (winnerId, cards, currentPlayers, extraEffects = {}) => {
              let nextStarterId = winnerId;
              
              if (winnerId === 'KRAKEN') {
                  const krakenPlayer = cards.find(p => p.card.type === CARD_TYPES.KRAKEN);
                  nextStarterId = krakenPlayer ? krakenPlayer.playerId : cards[0].playerId;
              } else {
                  if (gameState.phase !== 'PIRATE_ACTION') {
                       const winnerIndex = currentPlayers.findIndex(p => p.uid === winnerId);
                       if (winnerIndex !== -1) {
                           currentPlayers[winnerIndex].tricksWon += 1;
                           cards.forEach(play => { if (play.card.bonus) currentPlayers[winnerIndex].bonusPoints += play.card.bonus; });
                       }
                  }

                  const winnerIndex = currentPlayers.findIndex(p => p.uid === winnerId);
                  if (winnerIndex !== -1) {
                      const winningCard = cards.find(p => p.playerId === winnerId).card;
                      const wType = winningCard.type;
                      const wPlayedAs = winningCard.playedAs;

                      if (wType === CARD_TYPES.PIRATE || (wType === CARD_TYPES.TIGRESS && wPlayedAs === 'pirate')) {
                          cards.forEach(p => {
                              if (p.card.type === CARD_TYPES.MERMAID) { currentPlayers[winnerIndex].bonusPoints += 20; showToast("¡Pirata captura Sirena! (+20)"); }
                          });
                      }
                      if (wType === CARD_TYPES.SKULLKING) {
                          cards.forEach(p => {
                              if (p.card.type === CARD_TYPES.PIRATE || (p.card.type === CARD_TYPES.TIGRESS && p.card.playedAs === 'pirate')) { currentPlayers[winnerIndex].bonusPoints += 30; showToast("¡Skull King captura Pirata! (+30)"); }
                          });
                      }
                      if (wType === CARD_TYPES.MERMAID) {
                          if (cards.some(p => p.card.type === CARD_TYPES.SKULLKING)) { currentPlayers[winnerIndex].bonusPoints += 40; showToast("¡Sirena captura Skull King! (+40)"); }
                      }
                  }
                  
                  const coinPlays = cards.filter(p => p.card.type === CARD_TYPES.COINS);
                  const newAlliances = [...(gameState.alliances || [])];
                  coinPlays.forEach(cp => {
                      if (cp.playerId !== winnerId && winnerId !== 'KRAKEN') newAlliances.push({ p1: cp.playerId, p2: winnerId });
                  });
                  gameState.tempNewAlliances = newAlliances;
              }

              let nextTurnIndex = extraEffects.nextStarterOverride ? currentPlayers.findIndex(p => p.uid === extraEffects.nextStarterOverride) : currentPlayers.findIndex(p => p.uid === nextStarterId);
              if (nextTurnIndex === -1) nextTurnIndex = 0;

              const roundOver = currentPlayers[0].hand.length === 0;
              const roomRef = doc(db, 'artifacts', appId, 'public', 'data', ROOM_COLLECTION, `sk_room_${activeRoomId}`);

              if (roundOver) {
                  currentPlayers.forEach(p => {
                      const diff = Math.abs(p.bid - p.tricksWon);
                      let points = 0;
                      if (diff === 0) {
                          points = (p.bid === 0) ? (gameState.round * 10) : (p.bid * 20);
                          points += p.bonusPoints;
                          if (p.eliasBet) points += p.eliasBet;
                      } else {
                          points = diff * -10;
                          if (p.eliasBet) points -= p.eliasBet;
                      }
                      const allAlliances = [...(gameState.alliances || []), ...(gameState.tempNewAlliances || [])];
                      allAlliances.forEach(al => {
                          if ((al.p1 === p.uid || al.p2 === p.uid)) {
                              const partnerId = (al.p1 === p.uid) ? al.p2 : al.p1;
                              const partner = currentPlayers.find(pl => pl.uid === partnerId);
                              if (partner && partner.bid === partner.tricksWon && p.bid === p.tricksWon) points += 20; 
                          }
                      });
                      p.score += points;
                      p.lastRoundScore = points;
                  });
                  await updateDoc(roomRef, { players: currentPlayers, phase: gameState.round >= 10 ? 'GAME_END' : 'ROUND_END', trickCards: [], pendingPirateAction: null });
              } else {
                  await updateDoc(roomRef, {
                      players: currentPlayers, trickCards: [], turnIndex: nextTurnIndex, phase: 'PLAYING',
                      nextTrickLowWins: extraEffects.nextLowWins || false, nextTrickStarter: null, pendingPirateAction: null,
                      alliances: [...(gameState.alliances || []), ...(gameState.tempNewAlliances || [])]
                  });
              }
          };

          const canPlayCard = (card) => {
              if (gameState.trickCards.length >= gameState.players.length) return false;
              if (gameState.trickCards.length === 0) return true;
              const validCards = gameState.trickCards.filter(p => p.card.type !== CARD_TYPES.ESCAPE && p.card.type !== CARD_TYPES.COINS).sort((a,b) => a.order - b.order);
              let leadSuit = null;
              if (validCards.length > 0) {
                  const first = validCards[0].card;
                  if (first.type === CARD_TYPES.SUIT) leadSuit = first.suit;
              }
              if (!leadSuit) return true;
              const myHand = gameState.players.find(p => p.uid === user.uid).hand;
              const hasLead = myHand.some(c => c.type === CARD_TYPES.SUIT && c.suit === leadSuit);
              if (card.type === CARD_TYPES.SUIT) {
                  if (hasLead) return card.suit === leadSuit || card.suit === 'TRUMP';
                  return true;
              }
              return true;
          };

          if (!user) return <div className="min-h-screen bg-[#0f172a] flex items-center justify-center text-[#e2d2ac] font-serif"><Loader className="animate-spin mb-4 text-[#c5a059]" size={48} /><h2 className="text-xl font-bold ml-4">Conectando con la red pirata...</h2></div>;

          if (!activeRoomId) {
              return (
                <div className="bg-[#0f172a] min-h-screen text-[#e2d2ac] font-serif p-6 flex flex-col items-center">
                    <h1 className="text-5xl text-[#ffd700] font-bold mb-8 drop-shadow-[0_2px_2px_rgba(0,0,0,0.8)] tracking-wider mt-10">SKULL KING</h1>
                    <div className="space-y-6 w-full max-w-sm bg-[#1e293b] p-8 rounded-2xl border-4 border-[#c5a059] shadow-2xl relative">
                        <div className="absolute top-2 left-2 w-3 h-3 rounded-full bg-[#c5a059] shadow-inner"></div><div className="absolute top-2 right-2 w-3 h-3 rounded-full bg-[#c5a059] shadow-inner"></div><div className="absolute bottom-2 left-2 w-3 h-3 rounded-full bg-[#c5a059] shadow-inner"></div><div className="absolute bottom-2 right-2 w-3 h-3 rounded-full bg-[#c5a059] shadow-inner"></div>
                        <div className="space-y-2">
                            <label className="text-xs uppercase font-bold text-[#c5a059] tracking-widest">Tu Nombre</label>
                            <input className="w-full p-4 rounded-lg bg-[#0f172a] border-2 border-[#334155] text-white focus:border-[#ffd700] focus:ring-0 outline-none transition-colors" placeholder="Ej. Barbanegra" value={playerName} onChange={e=>setPlayerName(e.target.value)} />
                        </div>
                        <button onClick={createRoom} className="w-full bg-gradient-to-r from-[#ca8a04] to-[#eab308] hover:from-[#a16207] hover:to-[#ca8a04] text-[#2c1810] py-4 rounded-lg font-bold text-lg shadow-[0_4px_0_#713f12] active:shadow-none active:translate-y-1 transition-all flex items-center justify-center gap-2">
                            <Ship size={24} /> CREAR SALA
                        </button>
                        <div className="relative flex items-center py-2"><div className="flex-grow border-t border-[#334155]"></div><span className="flex-shrink-0 mx-4 text-slate-500 text-xs uppercase tracking-widest">O únete a una</span><div className="flex-grow border-t border-[#334155]"></div></div>
                        <div className="flex gap-2">
                            <input className="flex-1 p-4 rounded-lg bg-[#0f172a] border-2 border-[#334155] text-white focus:border-[#ffd700] outline-none uppercase font-mono tracking-widest text-center" placeholder="CÓDIGO" value={inputRoomId} onChange={e=>setInputRoomId(e.target.value)} />
                            <button onClick={joinRoom} className="bg-[#334155] hover:bg-[#475569] text-white px-6 rounded-lg font-bold shadow-[0_4px_0_#1e293b] active:shadow-none active:translate-y-1 transition-all"><LogIn size={24}/></button>
                        </div>
                        {error && <p className="text-red-400 text-center text-sm font-bold bg-red-900/20 p-2 rounded border border-red-900/50">{error}</p>}
                    </div>
                </div>
              );
          }

          if (!gameState) {
              return (
                <div className="min-h-screen bg-[#0f172a] flex flex-col items-center justify-center text-[#e2d2ac] font-serif">
                    <Loader className="animate-spin mb-4 text-[#c5a059]" size={48} />
                    <h2 className="text-xl font-bold">Buscando la sala...</h2>
                    <button onClick={() => setActiveRoomId('')} className="mt-4 text-slate-400 underline hover:text-white">Cancelar</button>
                </div>
              );
          }

          const me = gameState.players.find(p => p.uid === user.uid);
          if (!me) {
              return (
                <div className="min-h-screen bg-[#0f172a] flex flex-col items-center justify-center text-[#e2d2ac] font-serif">
                    <Loader className="animate-spin mb-4 text-[#c5a059]" size={48} />
                    <h2 className="text-xl font-bold">Sincronizando con la tripulación...</h2>
                    <button onClick={() => setActiveRoomId('')} className="mt-4 text-slate-400 underline hover:text-white">Cancelar</button>
                </div>
              );
          }

          if (gameState.phase === 'LOBBY') {
              return (
              <div className="bg-[#0f172a] min-h-screen text-[#e2d2ac] font-serif p-6 flex flex-col items-center relative overflow-hidden">
                  <div className="w-full max-w-md bg-[#1e293b] p-6 rounded-2xl border-2 border-[#c5a059] shadow-2xl relative z-10 mt-10">
                      <div className="absolute -top-3 -left-3 rotate-12"><Anchor className="text-[#c5a059] opacity-20" size={64}/></div>
                      <div className="bg-[#0f172a] p-4 rounded-xl mb-6 text-center border border-[#334155] relative group cursor-pointer" onClick={() => { navigator.clipboard.writeText(activeRoomId); setCopied(true); setTimeout(() => setCopied(false), 2000); }}>
                          <div className="text-xs text-slate-400 uppercase tracking-widest mb-1">Código de Sala</div>
                          <div className="text-5xl font-mono tracking-widest text-[#ffd700] font-bold">{activeRoomId}</div>
                          <div className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 group-hover:text-white transition-colors">{copied ? <Check size={20} className="text-green-500" /> : <Copy size={20} />}</div>
                      </div>
                      <div className="mb-6">
                          <h3 className="text-sm font-bold text-[#c5a059] uppercase mb-3 flex items-center gap-2"><Users size={16}/> Tripulación ({gameState.players.length})</h3>
                          <div className="space-y-2 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
                              {gameState.players.map(p => (
                                  <div key={p.uid} className="bg-[#334155] p-3 rounded-lg flex justify-between items-center border border-[#475569]">
                                      <span className="font-bold text-white">{p.name}</span>
                                      {p.uid === gameState.hostId && <span className="text-xs bg-[#ffd700] text-black px-2 py-1 rounded font-bold flex items-center gap-1"><Crown size={12}/> CAPITÁN</span>}
                                  </div>
                              ))}
                          </div>
                      </div>
                      {gameState.hostId === user.uid ? (
                          <button onClick={() => startRound(1)} className="w-full bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white py-4 rounded-xl font-bold text-lg shadow-[0_4px_0_#064e3b] active:shadow-none active:translate-y-1 transition-all uppercase tracking-wider flex justify-center items-center gap-2"><Ship /> Zarpar</button>
                      ) : (
                          <div className="bg-[#0f172a] p-4 rounded-xl border border-[#334155] text-center animate-pulse"><p className="text-slate-400 text-sm">El Capitán está reuniendo a la tripulación...</p></div>
                      )}
                  </div>
              </div>
              );
          }

          const myIndex = gameState.players.findIndex(p => p.uid === user.uid);
          const opponents = [...gameState.players.slice(myIndex), ...gameState.players.slice(0, myIndex)].slice(1);
          const isTableFull = gameState.trickCards.length >= gameState.players.length;
          const isPirateActionPhase = gameState.phase === 'PIRATE_ACTION';
          const myPirateAction = isPirateActionPhase && gameState.pendingPirateAction.winnerId === user.uid ? gameState.pendingPirateAction.pirateId : null;

          const tableRadiusX = isMobile ? 50 : 80;
          const tableRadiusY = isMobile ? 40 : 60;

          return (
            <div className="bg-[#0f172a] h-screen overflow-hidden flex flex-col text-[#e2d2ac] font-serif relative selection:bg-[#ffd700] selection:text-black">
                <div className="bg-[#1e293b] p-3 flex justify-between items-center shadow-lg z-20 border-b border-[#334155]">
                    <div className="flex items-center gap-4">
                        <div className="bg-[#0f172a] px-4 py-1 rounded-full border border-[#c5a059] flex items-center gap-2">
                            <span className="text-slate-400 text-xs uppercase">Ronda</span><span className="text-[#ffd700] font-bold text-lg">{gameState.round}</span>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <button onClick={() => setShowLeaderboard(!showLeaderboard)} className="md:hidden bg-[#334155] p-2 rounded text-white hover:bg-[#475569]"><ListOrdered size={20}/></button>
                    </div>
                </div>

                <div className={`absolute right-0 top-[60px] bottom-0 w-64 bg-[#1e293b]/95 border-l border-[#c5a059] p-4 z-40 transition-transform duration-300 transform ${showLeaderboard ? 'translate-x-0' : 'translate-x-full'} md:translate-x-0 backdrop-blur-md shadow-2xl`}>
                    <div className="text-xs font-bold text-[#c5a059] mb-4 uppercase tracking-widest text-center border-b border-[#334155] pb-2">Clasificación</div>
                    <div className="space-y-2">
                        {[...gameState.players].sort((a,b) => b.score - a.score).map((p, i) => (
                            <div key={p.uid} className={`p-3 rounded-lg flex justify-between items-center ${p.uid === user.uid ? 'bg-[#c5a059] text-[#2c1810] font-bold shadow-lg transform scale-105' : 'bg-[#0f172a] text-slate-300 border border-[#334155]'}`}>
                                <div className="flex items-center gap-2 overflow-hidden">
                                    <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${i===0 ? 'bg-yellow-500 text-black' : i===1 ? 'bg-gray-400 text-black' : i===2 ? 'bg-orange-700 text-white' : 'bg-slate-700'}`}>{i+1}</span>
                                    <span className="truncate max-w-[100px]">{p.name}</span>
                                </div>
                                <span className="font-mono text-lg">{p.score}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {toast && <div className="absolute top-20 left-1/2 -translate-x-1/2 bg-[#7f1d1d] text-white px-6 py-3 rounded-xl font-bold shadow-2xl z-50 animate-bounce flex items-center gap-3 border-2 border-red-500 text-center w-max max-w-[90vw]">{toast}</div>}

                <div className="flex justify-start md:justify-center gap-4 p-4 md:mr-64 overflow-x-auto no-scrollbar mask-gradient-x">
                    {opponents.map(p => (
                        <div key={p.uid} className={`relative flex flex-col items-center min-w-[80px] transition-all duration-300 ${gameState.players[gameState.turnIndex].uid === p.uid ? 'scale-110 z-10' : 'opacity-70 grayscale-[0.3]'}`}>
                            {gameState.players[gameState.turnIndex].uid === p.uid && <div className="absolute -top-8 text-[#ffd700] animate-bounce"><Swords size={20}/></div>}
                            <div className={`bg-[#1e293b] p-3 rounded-xl border-2 ${gameState.players[gameState.turnIndex].uid === p.uid ? 'border-[#ffd700] shadow-[0_0_15px_rgba(255,215,0,0.3)]' : 'border-[#334155]'}`}>
                                <div className="font-bold truncate w-full text-center text-xs mb-1 text-white">{p.name}</div>
                                <div className="text-xs text-[#c5a059] font-mono bg-[#0f172a] rounded px-2 py-0.5 text-center mb-1">{p.tricksWon} / {p.bid===null?'?':p.bid}</div>
                                <div className="flex -space-x-2 justify-center">
                                    {Array(Math.min(p.hand.length, 3)).fill(0).map((_,i) => <div key={i} className="w-3 h-5 bg-[#334155] border border-[#475569] rounded-sm shadow-sm"></div>)}
                                    {p.hand.length > 3 && <div className="w-3 h-5 flex items-center justify-center text-[8px] text-slate-500">+</div>}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="flex-1 relative flex items-center justify-center md:mr-64 perspective-1000 overflow-hidden">
                    <div className="absolute inset-2 md:inset-6 rounded-[2rem] md:rounded-[4rem] border-[16px] border-[#3e2723] shadow-[inset_0_0_60px_rgba(0,0,0,0.8)] overflow-hidden pointer-events-none">
                        <div className="absolute inset-0 bg-[#0f3d3e] opacity-90"></div>
                        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-transparent via-black/20 to-black/60"></div>
                        <div className="absolute inset-0 border-4 border-[#5d4037]/50 rounded-[1.5rem] md:rounded-[3.5rem]"></div>
                        <div className="absolute inset-0 flex items-center justify-center opacity-20 text-[#c5a059]"><div className="relative"><Compass size={300} strokeWidth={1} /><div className="absolute inset-0 flex items-center justify-center"><Skull size={100} strokeWidth={1.5} /></div></div></div>
                        <div className="absolute top-8 left-8 text-[#c5a059]/20 rotate-45"><Anchor size={64} /></div><div className="absolute bottom-8 right-8 text-[#c5a059]/20 -rotate-135"><Anchor size={64} /></div><div className="absolute top-8 right-8 text-[#c5a059]/20 -rotate-45"><Map size={64} /></div><div className="absolute bottom-8 left-8 text-[#c5a059]/20 rotate-135"><Map size={64} /></div>
                    </div>

                    {gameState.phase === 'BIDDING' && (
                        <div className="absolute inset-0 z-30 bg-black/80 backdrop-blur-sm flex flex-col items-center justify-center p-6 animate-fadeIn overflow-y-auto">
                            <h2 className="text-3xl font-bold mb-6 text-[#ffd700] drop-shadow-md sticky top-0 bg-black/80 py-2">¿Cuántas ganarás?</h2>
                            <div className="grid grid-cols-4 md:grid-cols-5 gap-3 max-w-lg w-full">
                                <button onClick={()=>submitBid(0)} className="col-span-4 md:col-span-5 bg-blue-600 hover:bg-blue-500 py-3 rounded-lg font-bold text-2xl shadow-lg border-2 border-blue-400 transition-transform hover:scale-[1.02]">0</button>
                                {Array.from({length:gameState.round},(_,i)=>i+1).map(n => (
                                    <button key={n} onClick={()=>submitBid(n)} className="bg-[#334155] hover:bg-[#475569] aspect-square rounded-lg font-bold text-lg shadow border border-[#64748b] text-white transition-transform hover:scale-110 flex items-center justify-center">{n}</button>
                                ))}
                            </div>
                        </div>
                    )}
                    
                    {isPirateActionPhase && (
                        <div className="absolute inset-0 z-30 bg-black/70 backdrop-blur-md flex items-center justify-center p-4">
                            {!myPirateAction ? (
                                <div className="bg-[#1e293b] p-6 rounded-2xl border-2 border-[#c5a059] text-center shadow-2xl"><h3 className="text-2xl font-bold text-[#ffd700] mb-2 flex items-center justify-center gap-2"><Gavel/> Decisión del Capitán</h3><p className="text-slate-300">El ganador está usando su habilidad...</p><Loader className="animate-spin mt-4 mx-auto text-[#c5a059]" /></div>
                            ) : (
                                <div className="bg-[#1e293b] p-6 rounded-2xl border-2 border-[#ffd700] shadow-[0_0_50px_rgba(255,215,0,0.2)] max-w-sm w-full animate-scaleIn">
                                    <div className="text-center mb-6"><h3 className="text-2xl font-bold text-[#ffd700] mb-1">{PIRATE_NAMES[myPirateAction]?.name}</h3><p className="text-sm text-slate-400 italic">{PIRATE_NAMES[myPirateAction]?.desc}</p></div>
                                    {myPirateAction === 'PEDRO' && (<div className="flex gap-4 justify-center"><button onClick={()=>executePirateAction({mod: -1})} className="bg-red-900/80 hover:bg-red-800 text-red-100 p-4 rounded-xl font-bold w-20 border border-red-500 shadow-lg text-xl">-1</button><button onClick={()=>executePirateAction({mod: 0})} className="bg-slate-700 hover:bg-slate-600 text-white p-4 rounded-xl font-bold flex-1 border border-slate-500 shadow-lg">Mantener</button><button onClick={()=>executePirateAction({mod: 1})} className="bg-green-800/80 hover:bg-green-700 text-green-100 p-4 rounded-xl font-bold w-20 border border-green-500 shadow-lg text-xl">+1</button></div>)}
                                    {myPirateAction === 'ELIAS' && (<div className="flex gap-3 justify-center"><button onClick={()=>executePirateAction({bet: 0})} className="bg-slate-700 hover:bg-slate-600 p-4 rounded-xl font-bold flex-1 border border-slate-500">0</button><button onClick={()=>executePirateAction({bet: 10})} className="bg-blue-800 hover:bg-blue-700 p-4 rounded-xl font-bold flex-1 border border-blue-500">10</button><button onClick={()=>executePirateAction({bet: 20})} className="bg-[#ca8a04] hover:bg-[#a16207] text-black p-4 rounded-xl font-bold flex-1 border border-[#facc15]">20</button></div>)}
                                    {myPirateAction === 'JAVI' && (<button onClick={()=>executePirateAction({})} className="w-full bg-red-700 hover:bg-red-600 text-white p-4 rounded-xl font-bold border border-red-500 shadow-lg text-lg flex items-center justify-center gap-2"><ArrowDown size={24}/> ¡Bajar Niveles!</button>)}
                                    {myPirateAction === 'SERGIO' && (<div className="grid grid-cols-2 gap-3">{gameState.players.map(p => (<button key={p.uid} onClick={()=>executePirateAction({targetId: p.uid})} className="bg-slate-700 hover:bg-[#c5a059] hover:text-black p-3 rounded-lg text-sm font-bold border border-slate-600 transition-colors">{p.name}</button>))}</div>)}
                                    {myPirateAction === 'TORRI' && (<div className="space-y-3"><div className="grid grid-cols-2 gap-3">{gameState.players.filter(p=>p.uid!==user.uid).map(p => (<button key={p.uid} onClick={()=>executePirateAction({targetId: p.uid})} className="bg-red-900/50 hover:bg-red-900 p-3 rounded-lg text-sm border border-red-500/50 hover:border-red-500 transition-all flex flex-col items-center"><span className="font-bold">{p.name}</span><span className="text-[10px] opacity-70">{p.hand.length} cartas</span></button>))}</div><button onClick={()=>executePirateAction({})} className="w-full py-2 text-slate-400 hover:text-white text-sm underline">No intercambiar</button></div>)}
                                </div>
                            )}
                        </div>
                    )}

                    {gameState.trickCards.map((play, i) => (
                        <div key={i} className="absolute transition-all duration-500 ease-out z-10" style={{ transform: `translate(${Math.cos(2*Math.PI*i/gameState.trickCards.length)*tableRadiusX}px, ${Math.sin(2*Math.PI*i/gameState.trickCards.length)*tableRadiusY}px) rotate(${(i-gameState.trickCards.length/2)*15}deg)`}}>
                            <div className="relative group"><Card card={play.card} size={isMobile ? "small" : "normal"} /><div className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-center text-[10px] font-bold bg-black/70 text-white px-2 py-0.5 rounded-full whitespace-nowrap border border-white/10 shadow-sm opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">{play.playerName}</div></div>
                        </div>
                    ))}

                    {isTableFull && gameState.phase === 'PLAYING' && (
                        <div className="absolute z-20 bg-black/80 backdrop-blur px-8 py-4 rounded-2xl flex items-center gap-4 animate-in fade-in zoom-in duration-300 border border-[#c5a059]/50 shadow-2xl"><Loader className="animate-spin text-[#c5a059]" size={32} /><div><div className="font-bold text-xl text-[#ffd700]">Resolviendo...</div></div></div>
                    )}
                </div>

                <div className="z-20 md:mr-64 relative"> 
                    <button onClick={() => setIsHandMinimized(!isHandMinimized)} className="absolute top-[-24px] right-4 bg-[#1e293b] text-[#c5a059] rounded-t-lg px-3 py-1 border-t border-l border-r border-[#334155] text-xs font-bold flex items-center gap-1 shadow-lg z-30">
                        {isHandMinimized ? <ChevronUp size={16}/> : <ChevronDown size={16}/>} Tus Cartas
                    </button>
                    <div className={`bg-[#1e293b] p-2 shadow-[0_-4px_20px_rgba(0,0,0,0.5)] border-t border-[#334155] transition-all duration-300 ${isHandMinimized ? 'h-16 overflow-hidden' : 'h-auto pb-6'}`}>
                        <div className="flex justify-between items-end mb-3 px-4">
                            <div className="flex items-center gap-3">
                                <div className="bg-[#0f172a] p-2 rounded-lg border border-[#334155]"><div className="text-[10px] text-slate-400 uppercase tracking-wider">Mi Apuesta</div><div className="text-xl font-bold text-[#c5a059] font-mono leading-none">{me.tricksWon} <span className="text-slate-600">/</span> {me.bid === null ? '-' : me.bid}</div></div>
                                {me.bid !== null && me.tricksWon === me.bid && (<div className="text-green-500 flex items-center gap-1 text-xs font-bold animate-pulse bg-green-900/20 px-2 py-1 rounded"><Check size={12} /> EN CAMINO</div>)}
                            </div>
                            {gameState.phase === 'PLAYING' && gameState.players[gameState.turnIndex].uid === user.uid && (<div className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-2 rounded-full text-sm font-bold animate-bounce shadow-lg shadow-green-900/50 border border-green-400">¡TU TURNO!</div>)}
                        </div>
                        <div className={`flex md:justify-center overflow-x-auto md:overflow-visible px-4 pb-2 snap-x snap-mandatory gap-3 md:gap-0 hide-scrollbar transition-opacity ${isHandMinimized ? 'opacity-0' : 'opacity-100'}`}>
                            <div className="flex md:-space-x-8 min-w-max mx-auto md:mx-0 pt-2 gap-3 md:gap-0 pb-4">
                                {me.hand.sort((a,b) => (a.type===b.type ? a.value-b.value : a.type.localeCompare(b.type))).map(card => {
                                    const isMyTurn = !isTableFull && gameState.phase==='PLAYING' && gameState.players[gameState.turnIndex].uid === user.uid;
                                    const valid = canPlayCard(card);
                                    const playable = isMyTurn && valid;
                                    return (
                                        <div key={card.id} className={`transition-all duration-300 md:hover:-translate-y-8 md:hover:z-20 relative flex-shrink-0 snap-center ${playable ? 'md:hover:scale-110' : ''}`}>
                                            <Card card={card} playable={playable} onClick={() => handleCardClick(card)} />
                                            {isMyTurn && !valid && (<div className="absolute inset-0 bg-black/60 rounded-xl z-20 flex items-center justify-center backdrop-blur-[1px] border-2 border-red-500/50"><XCircle className="text-red-500 opacity-80" /></div>)}
                                        </div>
                                    )
                                })}
                            </div>
                        </div>
                    </div>
                </div>

                {tigressModal && (
                    <div className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4 backdrop-blur-sm"><div className="bg-[#1e293b] p-8 rounded-2xl border-2 border-orange-500 shadow-2xl max-w-md w-full text-center"><h3 className="text-2xl font-bold text-orange-400 mb-2">¡Juegas la Tigresa!</h3><div className="flex gap-4"><button onClick={()=>playCard(tigressModal, {playedAs:'pirate'})} className="flex-1 bg-red-900 hover:bg-red-800 text-white py-6 rounded-xl font-bold border-2 border-red-600 transition-transform hover:scale-105 flex flex-col items-center gap-2"><Swords size={32}/> PIRATA</button><button onClick={()=>playCard(tigressModal, {playedAs:'escape'})} className="flex-1 bg-blue-900 hover:bg-blue-800 text-white py-6 rounded-xl font-bold border-2 border-blue-600 transition-transform hover:scale-105 flex flex-col items-center gap-2"><Flag size={32}/> HUIDA</button></div></div></div>
                )}

                {(gameState.phase === 'ROUND_END' || gameState.phase === 'GAME_END') && (
                    <div className="fixed inset-0 bg-black/95 z-50 flex items-center justify-center p-4 backdrop-blur-md">
                        <div className="w-full max-w-lg bg-[#1e293b] p-8 rounded-2xl border-4 border-[#c5a059] shadow-2xl relative overflow-hidden">
                            <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-transparent via-[#ffd700] to-transparent"></div>
                            <h2 className="text-4xl text-[#ffd700] font-bold text-center mb-2 drop-shadow-md">{gameState.phase === 'GAME_END' ? '¡FIN DE LA PARTIDA!' : `Resultados Ronda ${gameState.round}`}</h2>
                            <p className="text-center text-[#c5a059] mb-8 uppercase tracking-widest text-xs font-bold">Bitácora del Capitán</p>
                            <div className="space-y-3 mb-8 max-h-[50vh] overflow-y-auto pr-2 custom-scrollbar">
                                {gameState.players.sort((a,b)=>b.score-a.score).map((p,i) => (
                                    <div key={i} className={`flex justify-between items-center p-4 rounded-xl border ${p.uid === user.uid ? 'bg-[#334155] border-[#c5a059]' : 'bg-[#0f172a] border-[#334155]'}`}>
                                        <div className="flex items-center gap-4"><div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${i===0 ? 'bg-yellow-500 text-black' : 'bg-slate-700 text-slate-300'}`}>{i+1}</div><div><div className="font-bold text-lg flex items-center gap-2">{p.name}<span className={`text-xs font-bold px-2 py-0.5 rounded-full ${p.lastRoundScore >= 0 ? 'bg-green-900/50 text-green-400' : 'bg-red-900/50 text-red-400'}`}>{p.lastRoundScore > 0 ? '+' : ''}{p.lastRoundScore}</span></div><div className="text-xs text-slate-400 font-mono">Apuesta: {p.bid} | Ganadas: {p.tricksWon}</div></div></div>
                                        <div className="text-3xl font-bold text-[#ffd700] font-mono tracking-tighter">{p.score}</div>
                                    </div>
                                ))}
                            </div>
                            {gameState.hostId === user.uid && (
                                <div className="space-y-3">
                                    {gameState.phase !== 'GAME_END' && (<button onClick={async () => { const newDealer = (gameState.dealerIndex + 1) % gameState.players.length; await updateDoc(doc(db, 'artifacts', appId, 'public', 'data', ROOM_COLLECTION, `sk_room_${activeRoomId}`), { dealerIndex: newDealer }); startRound(gameState.round + 1); }} className="w-full bg-gradient-to-r from-green-600 to-emerald-600 py-4 rounded-xl font-bold text-xl text-white shadow-lg uppercase tracking-wider flex items-center justify-center gap-2 transition-transform hover:scale-[1.02]">Siguiente Ronda <ArrowUp size={24}/></button>)}
                                    {gameState.phase === 'GAME_END' && (<button onClick={resetToLobby} className="w-full bg-[#334155] hover:bg-[#475569] py-4 rounded-xl font-bold text-xl text-[#ffd700] border border-[#c5a059] shadow-lg uppercase tracking-wider flex items-center justify-center gap-2 transition-transform hover:scale-[1.02]"><Home size={24}/> Volver al Lobby</button>)}
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
          );
        }

        const root = createRoot(document.getElementById('root'));
        root.render(<SkullKingApp />);
    </script>
</body>
</html>
"""

components.html(html_code, height=1000, scrolling=True)
