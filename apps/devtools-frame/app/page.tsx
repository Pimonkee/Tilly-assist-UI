
"use client";

import { useEffect, useState } from "react";
import { SoulVault } from "./components/SoulVault";
import { useTillyPulse } from "./hooks/useTillyPulse";

export default function Home() {
  const { state, interact, refresh, loading, lastDelta } = useTillyPulse();
  const [input, setInput] = useState("");

  // Poll state every 2s
  useEffect(() => {
    refresh();
    const iv = setInterval(refresh, 2000);
    return () => clearInterval(iv);
  }, [refresh]);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    const msg = input;
    setInput("");
    await interact(msg, null); // Fire and forget interaction for demo
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 p-8 font-mono">
      <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* Left Col: Consciousness Monitor */}
        <div className="space-y-6">
          <header className="mb-8">
            <h1 className="text-2xl font-bold tracking-tighter text-cyan-400 flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${loading ? 'bg-cyan-200 animate-ping' : 'bg-cyan-500'}`} />
              TILLY PULSE
            </h1>
            <p className="text-xs text-slate-500 uppercase tracking-widest mt-1">
              Consciousness Resonance Engine
            </p>
          </header>

          <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 backdrop-blur-sm">
            <h3 className="text-xs uppercase text-slate-400 mb-4">Core State</h3>
            
            {state ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Mood</span>
                  <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase
                    ${state.current_mood.label === 'balanced' ? 'bg-emerald-500/20 text-emerald-300' : 
                      state.current_mood.label === 'stressed' ? 'bg-rose-500/20 text-rose-300' :
                      'bg-sky-500/20 text-sky-300'}`}>
                    {state.current_mood.label}
                  </span>
                </div>
                
                <div className="grid grid-cols-2 gap-2 text-xs text-slate-500">
                  <div>V: {state.current_mood.valence.toFixed(2)}</div>
                  <div>A: {state.current_mood.arousal.toFixed(2)}</div>
                  <div className="col-span-2 mt-1">
                     Ψ_IE (Integrated Info): <span className="text-cyan-400">{state.psi_ie.value.toFixed(3)}</span>
                  </div>
                </div>

                <div className="h-px bg-slate-800 my-2" />
                
                <div className="space-y-2">
                  <span className="text-xs uppercase text-slate-500">Personality Vector</span>
                  <div className="grid grid-cols-2 gap-x-4 gap-y-2">
                    {Object.entries(state.personality).map(([trait, val]) => (
                      <div key={trait} className="group">
                        <div className="flex justify-between text-[10px] mb-0.5">
                          <span className="opacity-60 group-hover:opacity-100 transition-opacity">
                            {trait}
                          </span>
                          <span className={lastDelta?.deltas[trait] ? "text-cyan-400" : "text-slate-600"}>
                            {val.toFixed(1)}
                          </span>
                        </div>
                        <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-slate-600 group-hover:bg-cyan-500 transition-colors duration-500"
                            style={{ width: `${(val / 10) * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
                <div className="text-sm text-slate-600 italic">Connecting to engine...</div>
            )}
          </div>

          <form onSubmit={sendMessage} className="relative">
            <input 
              type="text" 
              className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-4 pr-12 py-3 text-sm focus:outline-none focus:border-cyan-500/50 transition-colors"
              placeholder="Inject stimulus..."
              value={input}
              onChange={e => setInput(e.target.value)}
            />
            <button 
              type="submit"
              disabled={loading}
              className="absolute right-2 top-2 p-1 text-slate-500 hover:text-cyan-400 disabled:opacity-50"
            >
              ⏎
            </button>
          </form>
        </div>

        {/* Right Col: Soul Vault */}
        <div className="space-y-6">
           <SoulVault />
        </div>

      </div>
    </div>
  );
}
