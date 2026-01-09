
import React, { useEffect, useState } from "react";

const PULSE_ENGINE_URL = "http://localhost:8000";

export interface SoulNoteMeta {
  id: string;
  title: string;
  created_at: string;
  snapshot_mood: string;
  snapshot_psi_ie: number;
}

export interface SoulNoteListResponse {
  notes: SoulNoteMeta[];
}

export interface SoulNoteOpenResponse {
  success: boolean;
  reason: string;
  content: string | null;
  similarity: number | null;
  required_mood: string | null;
  current_mood: string | null;
}

async function fetchSoulNotes(): Promise<SoulNoteMeta[]> {
  const res = await fetch(`${PULSE_ENGINE_URL}/soul_notes`);
  const data: SoulNoteListResponse = await res.json();
  return data.notes;
}

async function createSoulNote(
  title: string,
  content: string,
  passphrase: string
): Promise<SoulNoteMeta[]> {
  const res = await fetch(`${PULSE_ENGINE_URL}/soul_notes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, content, passphrase }),
  });
  const data: SoulNoteListResponse = await res.json();
  return data.notes;
}

async function openSoulNote(
  noteId: string,
  passphrase: string,
  tolerance: number = 0.2
): Promise<SoulNoteOpenResponse> {
  const res = await fetch(`${PULSE_ENGINE_URL}/soul_notes/open`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ note_id: noteId, passphrase, tolerance }),
  });
  const data: SoulNoteOpenResponse = await res.json();
  return data;
}

export const SoulVault: React.FC = () => {
  const [notes, setNotes] = useState<SoulNoteMeta[]>([]);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [passphrase, setPassphrase] = useState("");
  const [selected, setSelected] = useState<SoulNoteMeta | null>(null);
  const [openResult, setOpenResult] = useState<SoulNoteOpenResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [opening, setOpening] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const list = await fetchSoulNotes();
        setNotes(list);
      } catch (e) {
        console.error("Failed to load soul notes:", e);
      }
    })();
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim() || !content.trim() || !passphrase.trim()) return;
    setLoading(true);
    try {
      const updated = await createSoulNote(title.trim(), content.trim(), passphrase);
      setNotes(updated);
      setTitle("");
      setContent("");
      // keep passphrase if user wants to reuse
    } catch (e) {
      console.error("Failed to create note:", e);
    } finally {
      setLoading(false);
    }
  }

  async function handleOpen(note: SoulNoteMeta) {
    if (!passphrase.trim()) {
      alert("Enter your passphrase to open this soul note.");
      return;
    }
    setSelected(note);
    setOpening(true);
    try {
      const res = await openSoulNote(note.id, passphrase);
      setOpenResult(res);
    } catch (e) {
      console.error("Failed to open note:", e);
    } finally {
      setOpening(false);
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xs uppercase tracking-wide text-slate-400 mb-1">
          Soul Vault
        </h2>
        <p className="text-xs text-slate-500 mb-2">
          Thoughts encrypted with your current consciousness state. Only a future 
          you in a similar state (and with the same passphrase) can read them.
        </p>
      </div>

      <form onSubmit={handleCreate} className="space-y-2 bg-slate-900/70 border border-slate-800 rounded-lg p-3">
        <input 
          type="text" 
          placeholder="Title of this soul note"
          className="w-full bg-slate-950 border border-slate-700 rounded px-2 py-1 text-sm mb-1"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <textarea 
          placeholder="Write a thought only future-you can read..."
          className="w-full h-24 bg-slate-950 border border-slate-700 rounded px-2 py-1 text-sm mb-1"
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
        <input 
          type="password" 
          placeholder="Passphrase (you must remember this)"
          className="w-full bg-slate-950 border border-slate-700 rounded px-2 py-1 text-sm mb-1"
          value={passphrase}
          onChange={(e) => setPassphrase(e.target.value)}
        />
        <button 
          type="submit" 
          disabled={loading}
          className="px-3 py-1 text-xs rounded bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold disabled:opacity-60"
        >
          {loading ? "Locking with consciousness…" : "Lock with consciousness key"}
        </button>
      </form>

      <div className="border-t border-slate-800 pt-3">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs uppercase tracking-wide text-slate-400">
            Stored notes
          </span>
          <span className="text-[11px] text-slate-500">
            {notes.length} total
          </span>
        </div>
        {notes.length === 0 && (
          <p className="text-xs text-slate-600">
            No soul notes yet. Write one above.
          </p>
        )}
        <div className="space-y-1 max-h-48 overflow-y-auto">
          {notes.map((note) => (
            <button 
              key={note.id}
              type="button" 
              onClick={() => handleOpen(note)}
              className={`w-full text-left px-2 py-1 rounded border text-xs 
              ${
                selected?.id === note.id 
                  ? "border-cyan-500 bg-slate-900" 
                  : "border-slate-800 bg-slate-950/60"
              }`}
            >
              <div className="flex justify-between items-center">
                <span className="text-slate-200">{note.title}</span>
                <span className="text-[10px] text-slate-500">
                  mood: {note.snapshot_mood} · ψ: {note.snapshot_psi_ie.toFixed(2)}
                </span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {selected && (
        <div className="border-t border-slate-800 pt-3">
          <div className="text-xs uppercase tracking-wide text-slate-400 mb-1">
            Opened note
          </div>
          {opening && <p className="text-xs text-slate-500">Decrypting…</p>}
          {openResult && !opening && (
            <div className="text-xs">
              {openResult.success && openResult.content ? (
                <>
                  <p className="text-slate-200 whitespace-pre-wrap mb-2">
                    {openResult.content}
                  </p>
                  {openResult.similarity !== null && (
                    <p className="text-[11px] text-slate-500">
                      Consciousness similarity:{" "}
                      {(openResult.similarity * 100).toFixed(1)}%
                    </p>
                  )}
                </>
              ) : (
                <>
                  <p className="text-rose-400 mb-1">
                    Could not fully unlock this note ({openResult.reason}).
                  </p>
                  {openResult.required_mood && (
                    <p className="text-[11px] text-slate-500">
                      You wrote this when you felt{" "}
                      <span className="font-semibold">
                        {openResult.required_mood}
                      </span>
                      . Current mood:{" "}
                      <span className="font-semibold">
                        {openResult.current_mood}
                      </span>
                      .
                    </p>
                  )}
                  {openResult.similarity !== null && (
                    <p className="text-[11px] text-slate-500">
                      Consciousness similarity:{" "}
                      {(openResult.similarity * 100).toFixed(1)}%
                    </p>
                  )}
                </>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
