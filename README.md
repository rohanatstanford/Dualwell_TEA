# TEA Web App

Technoeconomic Analysis (TEA) web application for Geothermal / CO2 Sequestration projects. Based on the TEA Model notebook.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Deploy to Streamlit Community Cloud (free)

1. **Create a GitHub repository**
   - Go to [github.com/new](https://github.com/new)
   - Name it (e.g. `tea-web-app`) and create

2. **Push your code to GitHub**

   ```bash
   cd "TEA Web App"
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/tea-web-app.git
   git push -u origin main
   ```

3. **Deploy on Streamlit Community Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click **New app**
   - Choose your repo, branch (`main`), and set **Main file path** to `app.py`
   - Click **Deploy**

Your app will be live at `https://YOUR_APP_NAME.streamlit.app`

## Features

- Input all model parameters (CO2, financial, operations)
- Power price ($/MWh)
- Outputs: LCOE, NPV, IRR (base case defaults pre-filled)
- Run history table with Export to Excel and Clear
