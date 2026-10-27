// Cloudflare Worker: private proxy between the Spectrum Hub page and the Anthropic API.
// The API key lives here as a secret and is never sent to the browser.
const MAX_PROMPT = 9000;

export default {
  async fetch(req, env) {
    const origin = req.headers.get('Origin') || '';
    const allowed = (env.ALLOWED_ORIGIN || '').split(',').map((s) => s.trim()).filter(Boolean);
    const ok = allowed.includes(origin);
    const cors = {
      'Access-Control-Allow-Origin': ok ? origin : 'null',
      'Vary': 'Origin',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };
    const json = (obj, status = 200) =>
      new Response(JSON.stringify(obj), { status, headers: { ...cors, 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } });

    if (req.method === 'OPTIONS') return new Response(null, { status: ok ? 204 : 403, headers: cors });
    if (req.method !== 'POST' || !ok) return json({ error: 'forbidden' }, 403);

    // Optional rate limit: 20 requests per IP per 10 minutes (bind a KV namespace named RL).
    if (env.RL) {
      const ip = req.headers.get('CF-Connecting-IP') || 'unknown';
      const key = 'rl:' + ip + ':' + Math.floor(Date.now() / 600000);
      const n = parseInt((await env.RL.get(key)) || '0', 10);
      if (n >= 20) return json({ error: 'slow down' }, 429);
      await env.RL.put(key, String(n + 1), { expirationTtl: 700 });
    }

    let body;
    try { body = await req.json(); } catch { return json({ error: 'bad request' }, 400); }
    const prompt = typeof body.prompt === 'string' ? body.prompt : '';
    if (!prompt || prompt.length > MAX_PROMPT) return json({ error: 'bad request' }, 400);

    // No conversation content is logged anywhere in this file.
    const r = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'content-type': 'application/json', 'x-api-key': env.ANTHROPIC_API_KEY, 'anthropic-version': '2023-06-01' },
      body: JSON.stringify({ model: env.MODEL || 'claude-sonnet-5-5', max_tokens: 500, messages: [{ role: 'user', content: prompt }] }),
    });
    if (!r.ok) return json({ error: 'upstream' }, 502);
    const data = await r.json();
    const text = (data.content || []).filter((b) => b.type === 'text').map((b) => b.text).join('').trim();
    const cleaned = text.replace(/^```(?:json)?\s*|\s*```$/g, '');
    try {
      const o = JSON.parse(cleaned);
      return json({ reply: String(o.reply || ''), resources: Array.isArray(o.resources) ? o.resources : [] });
    } catch {
      return json({ reply: text, resources: [] });
    }
  },
};
