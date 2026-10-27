# Companion server (Cloudflare Worker)

Lets the Hub's AI companion work on any host without exposing your API key.

1. Create a free Cloudflare account and install Node.js.
2. In this folder, edit `wrangler.toml`: set `ALLOWED_ORIGIN` to your site's origin, for example `https://YOUR-USERNAME.github.io`.
3. Sign in and store your key as a secret (never put it in a file):
       npx wrangler login
       npx wrangler secret put ANTHROPIC_API_KEY
4. Deploy: `npx wrangler deploy`. Copy the URL it prints.
5. In `../index.html`, set `var ENDPOINT='https://spectrum-companion.YOURNAME.workers.dev';` and commit.
6. Optional: bind a KV namespace named RL (see `wrangler.toml`) to rate-limit each visitor.
7. In the Anthropic console, set a monthly spend limit for this key. Rotate the key if you ever think it leaked.

What it does: accepts POST `{prompt}` only from your allowed origin, rejects oversized requests, calls the API with your secret key, and returns `{reply, resources}`. It does not log conversations. Crisis phrases are handled in the page and never reach this server.
