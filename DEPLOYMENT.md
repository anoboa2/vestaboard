# Deployment Guide

This guide covers deploying the Vestaboard application using **Vercel** (frontend) and **Fly.io** (backend).

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Vercel      │────▶│     Fly.io      │────▶│   Vestaboard    │
│   (Frontend)    │     │    (Backend)    │     │     Device      │
│   Next.js App   │     │  FastAPI + Orch │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │  External APIs  │
                        │ Spotify, MLB    │
                        └─────────────────┘
```

## Prerequisites

- [Fly.io CLI](https://fly.io/docs/hands-on/install-flyctl/) installed
- [Vercel CLI](https://vercel.com/docs/cli) installed (optional, can use dashboard)
- Accounts on both platforms (free tiers available)

## Backend Deployment (Fly.io)

### 1. Initial Setup

```bash
# Login to Fly.io
fly auth login

# Launch the app (first time only)
fly launch --no-deploy

# This will prompt you to:
# - Choose an app name (e.g., vestaboard-api)
# - Select a region (choose one close to you)
```

### 2. Set Environment Secrets

```bash
# Required
fly secrets set VESTABOARD_API_KEY=your_api_key_here

# Optional: Spotify integration
fly secrets set SPOTIFY_CLIENT_ID=your_client_id
fly secrets set SPOTIFY_CLIENT_SECRET=your_client_secret
fly secrets set SPOTIFY_REDIRECT_URI=https://your-app.fly.dev/spotify/callback

# After deploying frontend, add:
fly secrets set FRONTEND_URL=https://your-app.vercel.app
```

### 3. Deploy

```bash
fly deploy
```

### 4. Verify Deployment

```bash
# Check status
fly status

# View logs
fly logs

# Open in browser
fly open
```

## Frontend Deployment (Vercel)

### 1. Deploy via CLI

```bash
cd frontend

# Login (first time)
npx vercel login

# Deploy
npx vercel

# For production
npx vercel --prod
```

### 2. Configure Environment Variables

In the Vercel dashboard (or via CLI):

```bash
# Set the backend API URL
npx vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://your-app.fly.dev
```

Or via the Vercel Dashboard:
1. Go to your project settings
2. Navigate to Environment Variables
3. Add `NEXT_PUBLIC_API_URL` = `https://your-app.fly.dev`

### 3. Update Backend CORS

After getting your Vercel URL, update the backend:

```bash
fly secrets set FRONTEND_URL=https://your-app.vercel.app
```

## Post-Deployment Checklist

- [ ] Backend health check: `curl https://your-app.fly.dev/`
- [ ] Frontend loads and connects to backend
- [ ] Vestaboard receives updates
- [ ] CORS working (no console errors)

## Spotify Integration Notes

The Spotify OAuth flow requires user interaction (browser-based login). For production:

1. **Initial Setup**: Run the app locally first to complete Spotify OAuth
2. The token is cached in `.cache_spotify`
3. For production, you may need to:
   - Use a long-lived refresh token
   - Implement a token refresh endpoint
   - Or run OAuth setup on the server once via `fly ssh console`

## Cost Estimates

| Service | Free Tier | Estimated Monthly Cost |
|---------|-----------|------------------------|
| Fly.io | 3 shared VMs | $0-5 (within free tier) |
| Vercel | 100GB bandwidth | $0 (within free tier) |
| **Total** | | **$0-5/month** |

## Troubleshooting

### Backend not responding
```bash
fly logs          # Check logs
fly status        # Check machine status
fly restart       # Restart the app
```

### CORS errors
Ensure `FRONTEND_URL` is set correctly in Fly.io secrets:
```bash
fly secrets list
fly secrets set FRONTEND_URL=https://your-exact-vercel-url.vercel.app
```

### Spotify not working
- Check credentials are set: `fly secrets list`
- View logs: `fly logs | grep -i spotify`
- May need to re-authenticate via SSH: `fly ssh console`

## Updating the Application

### Backend
```bash
fly deploy
```

### Frontend
```bash
cd frontend
npx vercel --prod
```

Or connect GitHub for automatic deployments on both platforms.
