Auth0 login demo for Space Cowboys

What this is

- A simple static website with landing page and Auth0-based authentication.
- Files included:
  - `index.html` — landing page with game overview
  - `login.html` — authentication page using Auth0 SPA SDK
  - `style.css` — styling for both pages

Setup (Auth0)

1. Create an application in your Auth0 dashboard (Regular Web Application or SPA). Note the Domain and Client ID.
2. In the application settings, add the allowed callback/logout/origin URLs you will use to test. For local testing, add:
   - Allowed Callback URLs: `http://localhost:8000`
   - Allowed Logout URLs: `http://localhost:8000`
   - Allowed Web Origins: `http://localhost:8000`

Replace placeholders

Open `Web/index.html` and replace the two placeholder strings:

- `YOUR_AUTH0_DOMAIN`  -> your Auth0 domain (example: `dev-abc123.us.auth0.com`)
- `YOUR_AUTH0_CLIENT_ID` -> your Auth0 client id

Run locally

Serve the `Web/` directory as static files. E.g. from the project root:

```bash
cd Web
python3 -m http.server 8000
```

Then open `http://localhost:8000` in your browser.

Notes

- For production, don't store secrets in client-side code in plaintext; use proper configuration and environment variables, and ensure you follow Auth0 best practices for SPAs.
- This demo uses redirect-based login which is simple for static hosting. You can adapt to popup-based auth if you prefer.
