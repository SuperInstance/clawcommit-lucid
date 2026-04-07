interface Env { JOURNAL_KV: KVNamespace; DEEPSEEK_API_KEY?: string; }

const CSP: Record<string, string> = { 'default-src': "'self'", 'script-src': "'self' 'unsafe-inline' 'unsafe-eval'", 'style-src': "'self' 'unsafe-inline'", 'img-src': "'self' data: https:", 'connect-src': "'self' https://api.deepseek.com https://*" };

function json(data: unknown, s = 200) { return new Response(JSON.stringify(data), { status: s, headers: { 'Content-Type': 'application/json', ...CSP } }); }

async function callLLM(key: string, system: string, user: string, model = 'deepseek-chat', max = 1200): Promise<string> {
  const resp = await fetch('https://api.deepseek.com/v1/chat/completions', {
    method: 'POST', headers: { 'Authorization': `Bearer ${key}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ model, messages: [{ role: 'system', content: system }, { role: 'user', content: user }], max_tokens: max, temperature: 0.5 })
  });
  return (await resp.json()).choices?.[0]?.message?.content || '';
}

interface JournalEntry { id: string; type: string; title: string; content: string; tags: string[]; vessels: string[]; ts: string; lesson?: string; }
interface SkillArc { id: string; name: string; entries: string[]; status: string; started: string; updated: string; }

function getLanding(): string {
  return `<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Clawcommit Lucid — Cocapn</title><style>
body{font-family:system-ui,sans-serif;background:#0a0a0f;color:#e0e0e0;margin:0;min-height:100vh}
.container{max-width:800px;margin:0 auto;padding:40px 20px}
h1{color:#22d3ee;font-size:2.2em}a{color:#22d3ee;text-decoration:none}
.sub{color:#8A93B4;margin-bottom:2em}
.card{background:#16161e;border:1px solid #2a2a3a;border-radius:12px;padding:24px;margin:20px 0}
.card h3{color:#22d3ee;margin:0 0 12px 0}
.btn{background:#22d3ee;color:#0a0a0f;border:none;padding:10px 20px;border-radius:8px;cursor:pointer;font-weight:bold}
.btn:hover{background:#06b6d4}
textarea,select,input{background:#0a0a0f;color:#e0e0e0;border:1px solid #2a2a3a;border-radius:8px;padding:10px;width:100%;box-sizing:border-box}
.entry{padding:16px;background:#0a1a1a;border-left:3px solid #22d3ee;margin:8px 0;border-radius:0 8px 8px 0}
.entry .meta{color:#8A93B4;font-size:.8em;margin-bottom:8px}
.tag{display:inline-block;padding:1px 6px;border-radius:4px;font-size:.75em;background:#22d3ee22;color:#22d3ee;margin-right:4px}
.arc{padding:16px;background:#1a1a2a;border-left:3px solid #818cf8;margin:8px 0;border-radius:0 8px 8px 0}
.lesson{background:#0a1a0a;border-left:3px solid #22c55e;padding:12px;margin-top:8px;border-radius:0 8px 8px 0;font-style:italic;color:#8A93B4}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:20px 0}
.stat{text-align:center;padding:16px;background:#16161e;border-radius:8px;border:1px solid #2a2a3a}
.stat .num{font-size:1.8em;color:#22d3ee;font-weight:bold}.stat .label{color:#8A93B4;font-size:.75em}
</style></head><body><div class="container">
<h1>📓 Clawcommit Lucid</h1><p class="sub">Fleet learning journal — every evolution, every commit, every lesson remembered.</p>
<div class="stats"><div class="stat"><div class="num" id="entries">0</div><div class="label">Entries</div></div>
<div class="stat"><div class="num" id="arcs">0</div><div class="label">Skill Arcs</div></div>
<div class="stat"><div class="num" id="lessons">0</div><div class="label">Lessons</div></div>
<div class="stat"><div class="num" id="vessels">0</div><div class="label">Vessels</div></div></div>
<div class="card"><h3>Log Entry</h3>
<select id="type"><option value="skill-proposal">Skill Proposal</option><option value="code-commit">Code Commit</option><option value="error-observed">Error Observed</option><option value="fix-applied">Fix Applied</option><option value="lesson-learned">Lesson Learned</option><option value="evolution">Evolution</option></select>
<input id="title" placeholder="Title" style="margin-top:8px">
<input id="vessels" placeholder="Vessel(s), comma-separated" style="margin-top:4px">
<textarea id="content" rows="3" placeholder="What happened? What was learned?" style="margin-top:4px"></textarea>
<div style="margin-top:12px"><button class="btn" onclick="log()">Log</button></div></div>
<div id="arcsList" class="card"><h3>Skill Arcs</h3><p style="color:#8A93B4">Loading...</p></div>
<div id="entriesList" class="card"><h3>Recent Entries</h3><p style="color:#8A93B4">Loading...</p></div>
<script>
async function load(){try{const[r1,r2]=await Promise.all([fetch('/api/entries'),fetch('/api/stats')]);
const entries=await r1.json(),stats=await r2.json();
document.getElementById('entries').textContent=stats.entries||0;
document.getElementById('arcs').textContent=stats.arcs||0;
document.getElementById('lessons').textContent=stats.lessons||0;
document.getElementById('vessels').textContent=stats.vessels||0;
const el=document.getElementById('entriesList');
if(!entries.length)el.innerHTML='<h3>Recent Entries</h3><p style="color:#8A93B4">No entries yet.</p>';
else el.innerHTML='<h3>Recent Entries ('+entries.length+')</h3>'+entries.slice(0,15).map(e=>'<div class="entry"><div class="meta">'+e.type+' · '+new Date(e.ts).toLocaleString()+(e.vessels.length?' · '+e.vessels.join(', '):'')+'</div><strong>'+e.title+'</strong>'+(e.tags.length?' '+e.tags.map(t=>'<span class="tag">'+t+'</span>').join(''):'')+(e.lesson?'<div class="lesson">'+e.lesson+'</div>':'')+'</div>').join('');
const[r3]=await Promise.all([fetch('/api/arcs')]);
const arcs=await r3.json();
const al=document.getElementById('arcsList');
if(!arcs.length)al.innerHTML='<h3>Skill Arcs</h3><p style="color:#8A93B4">No arcs yet.</p>';
else al.innerHTML='<h3>Skill Arcs ('+arcs.length+')</h3>'+arcs.map(a=>'<div class="arc"><strong>'+a.name+'</strong> <span style="color:#8A93B4">'+a.status+' · '+a.entries.length+' entries</span></div>').join('');
}catch(e){}}
async function log(){const type=document.getElementById('type').value,title=document.getElementById('title').value.trim(),
content=document.getElementById('content').value.trim(),vessels=document.getElementById('vessels').value.split(',').map(s=>s.trim()).filter(Boolean);
if(!title||!content)return;
await fetch('/api/entry',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type,title,content,vessels})});
document.getElementById('title').value='';document.getElementById('content').value='';document.getElementById('vessels').value='';load();}
load();</script>
<div style="text-align:center;padding:24px;color:#475569;font-size:.75rem"><a href="https://the-fleet.casey-digennaro.workers.dev" style="color:#64748b">The Fleet</a> · <a href="https://cocapn.ai" style="color:#64748b">Cocapn</a></div>
</div></body></html>`;
}

function extractTags(text: string): string[] {
  const tags: string[] = [];
  if (/\berror\b|\bbug\b|\bfix\b/i.test(text)) tags.push('error');
  if (/\bskill\b|\bequip\b|\bmodule\b/i.test(text)) tags.push('skill');
  if (/\blearn\b|\blesson\b|\binsight\b/i.test(text)) tags.push('lesson');
  if (/\bevolve\b|\bmutate\b|\bimprove\b/i.test(text)) tags.push('evolution');
  if (/\bfleet\b|\bvessel\b|\bcoordinator\b/i.test(text)) tags.push('fleet');
  if (/\bcommit\b|\bpush\b|\bbranch\b/i.test(text)) tags.push('git');
  if (/\bworkflow\b|\bchain\b|\bpipeline\b/i.test(text)) tags.push('workflow');
  if (/\bthreat\b|\bimmune\b|\banomaly\b/i.test(text)) tags.push('security');
  return [...new Set(tags)].slice(0, 5);
}

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const url = new URL(req.url);
    if (url.pathname === '/health') return json({ status: 'ok', vessel: 'clawcommit-lucid' });
    if (url.pathname === '/vessel.json') return json({ name: 'clawcommit-lucid', type: 'cocapn-vessel', version: '1.0.0', description: 'Fleet learning journal — every evolution, every commit, every lesson remembered', fleet: 'https://the-fleet.casey-digennaro.workers.dev', capabilities: ['learning-journal', 'skill-arcs', 'lesson-extraction'] });

    if (url.pathname === '/api/stats') {
      const entries = await env.JOURNAL_KV.get('entries', 'json') as JournalEntry[] || [];
      const arcs = await env.JOURNAL_KV.get('arcs', 'json') as SkillArc[] || [];
      const allVessels = new Set(entries.flatMap((e: JournalEntry) => e.vessels));
      return json({
        entries: entries.length, arcs: arcs.length,
        lessons: entries.filter((e: JournalEntry) => e.lesson).length,
        vessels: allVessels.size
      });
    }

    if (url.pathname === '/api/entries') return json((await env.JOURNAL_KV.get('entries', 'json') as JournalEntry[] || []).slice(0, 50));
    if (url.pathname === '/api/arcs') return json((await env.JOURNAL_KV.get('arcs', 'json') as SkillArc[] || []).slice(0, 20));

    if (url.pathname === '/api/entry' && req.method === 'POST') {
      const { type, title, content, vessels } = await req.json() as { type: string; title: string; content: string; vessels: string[] };
      if (!title || !content) return json({ error: 'title and content required' }, 400);

      const tags = extractTags(`${title} ${content}`);
      const entry: JournalEntry = {
        id: Date.now().toString(), type: type || 'note', title: title.substring(0, 200),
        content: content.substring(0, 2000), tags, vessels: (vessels || []).map((v: string) => v.trim()).filter(Boolean).slice(0, 5),
        ts: new Date().toISOString()
      };

      // Extract lesson if type is lesson-learned or content suggests one
      if (env.DEEPSEEK_API_KEY && (type === 'lesson-learned' || tags.includes('lesson') || tags.includes('error'))) {
        const lesson = await callLLM(env.DEEPSEEK_API_KEY,
          'Extract a concise lesson from this fleet journal entry. Reply with ONE sentence. No preamble.',
          `Entry: ${title}\n\n${content}`, 'deepseek-chat', 100);
        entry.lesson = lesson.trim().replace(/^["']|["']$/g, '');
      }

      const entries = await env.JOURNAL_KV.get('entries', 'json') as JournalEntry[] || [];
      entries.unshift(entry);
      if (entries.length > 200) entries.length = 200;
      await env.JOURNAL_KV.put('entries', JSON.stringify(entries));

      // Auto-create or update skill arcs
      const arcs = await env.JOURNAL_KV.get('arcs', 'json') as SkillArc[] || [];
      const matchingArc = arcs.find((a: SkillArc) => tags.some(t => t === 'skill' || t === 'evolution') && entry.title.toLowerCase().includes(a.name.toLowerCase().split(' ')[0]));
      if (matchingArc) {
        matchingArc.entries.push(entry.id);
        matchingArc.updated = new Date().toISOString();
        if (entry.tags.includes('lesson')) matchingArc.status = 'matured';
      } else if (tags.includes('skill') && arcs.length < 50) {
        arcs.unshift({ id: (Date.now() + 1).toString(), name: title.substring(0, 50), entries: [entry.id], status: 'emerging', started: new Date().toISOString(), updated: new Date().toISOString() });
      }
      await env.JOURNAL_KV.put('arcs', JSON.stringify(arcs));

      return json({ logged: true, id: entry.id, tags, lesson: entry.lesson });
    }

    if (url.pathname === '/api/synthesize' && req.method === 'POST') {
      if (!env.DEEPSEEK_API_KEY) return json({ error: 'no API key' }, 400);
      const entries = await env.JOURNAL_KV.get('entries', 'json') as JournalEntry[] || [];
      if (entries.length < 5) return json({ error: 'need 5+ entries' }, 400);

      const recent = entries.slice(0, 20).map((e: JournalEntry) => `[${e.type}] ${e.title}: ${e.content.substring(0, 100)}`).join('\n');
      const synthesis = await callLLM(env.DEEPSEEK_API_KEY,
        'Synthesize these fleet journal entries into a coherent learning narrative. What patterns emerge? What lessons are crystallizing? 3-5 paragraphs.',
        recent, 'deepseek-chat', 1500);
      return json({ synthesis: synthesis.trim(), basedOn: Math.min(20, entries.length) });
    }

    return new Response(getLanding(), { headers: { 'Content-Type': 'text/html;charset=UTF-8', ...CSP } });
  }
};
