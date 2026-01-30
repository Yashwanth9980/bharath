# Deployment to Render

## Prerequisites
- GitHub account (push code to GitHub first)
- Render account (https://render.com)

## Step 1: Push Code to GitHub
```bash
git init
git add .
git commit -m "Initial commit: Bharat Heritage Explorer"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/googlehackathon.git
git push -u origin main
```

## Step 2: Create Render Web Service
1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the `googlehackathon` repository

## Step 3: Configure Service
Fill in the following settings:

**Name:** bharat-heritage-explorer (or your preferred name)

**Environment:** Python 3

**Build Command:** 
```
pip install -r requirements.txt
```

**Start Command:** 
```
gunicorn app:app
```

**Root Directory:** `backend`

## Step 4: Set Environment Variables
In Render dashboard, go to **Environment** and add:

```
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
FLASK_ENV=production
```

Replace with your actual API keys.

## Step 5: Deploy
1. Click "Create Web Service"
2. Render will automatically deploy from your main branch
3. Your app will be live at: `https://bharat-heritage-explorer.onrender.com`

## Step 6: Auto-Deploy
Any push to main branch will auto-deploy. Commits to other branches won't deploy.

## Important Notes
- Free tier has 15-minute inactivity timeout (app spins down)
- Use paid plan for always-on service
- Images must be served from `/static/images/` directory
- Log errors in Render's dashboard for debugging

## Troubleshooting
- Check **Logs** tab if deployment fails
- Verify all environment variables are set
- Ensure `Procfile` is in the root of backend directory
- Static files must exist in `/static/images/`
