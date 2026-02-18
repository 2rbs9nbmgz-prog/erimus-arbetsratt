# Erimus Arbetsrättsdatabas

En interaktiv webbapplikation för att söka och utforska rättsfall från Arbetsdomstolen inom svensk arbetsrätt.

## 📚 Om databasen

Databasen innehåller rättsfall inom:
- **Lag om anställningsskydd (LAS)** – inklusive LAS-reformen 2022 och sakliga skäl
- **Diskrimineringslagen** – alla former av diskriminering i arbetslivet
- **Arbetstidslagen och EU-direktivet** – dygnsvila, övertid, restid som arbetstid

## 🚀 Live-demo

Appen körs på Streamlit Cloud: **[Länk kommer efter deployment]**

## 💻 Lokal installation

```bash
# Klona repot
git clone https://github.com/[ditt-användarnamn]/erimus-arbetsratt.git
cd erimus-arbetsratt

# Installera dependencies
pip install -r requirements.txt

# Kör appen
streamlit run web_app.py
```

Appen öppnas automatiskt i din webbläsare på http://localhost:8501

## 📊 Funktioner

- 🔍 **Sök rättsfall** – fritextsökning, filter på lagområde, tema och år
- 📄 **Detaljerad information** – sammanfattning, lagrum, teman och länkar
- 📈 **Statistik** – översikt över rättsfallsfördelning
- 📱 **Responsiv design** – fungerar på alla enheter

## 🗄️ Databas

- **Typ:** SQLite 3
- **Antal rättsfall:** 32 (växande)
- **Källa:** Arbetsdomstolens officiella domar
- **Uppdaterad:** 2025-01-29

## 📁 Filstruktur

```
erimus-arbetsratt/
├── web_app.py                    # Huvudapplikation
├── arbetsratt_rattsfall.db       # SQLite-databas
├── requirements.txt              # Python dependencies
├── .streamlit/
│   └── config.toml              # Streamlit-konfiguration
└── README.md                     # Denna fil
```

## 🏢 Om Erimus AB

Denna databas utvecklas och underhålls av Erimus Aktiebolag.

Website: [erimus.se](https://erimus.se)

## 📄 Licens

© 2025 Erimus AB. All rights reserved.

## ⚠️ Ansvarsfriskrivning

Denna databas är avsedd för informationsändamål och utgör inte juridisk rådgivning. 
För juridisk rådgivning, kontakta en jurist eller advokat.

---

Utvecklad med ❤️ av Erimus AB
