# Radio Harrow Myriad Search – Streamlit v1.0

A browser-based version of the Windows v4.6 search, for presenters on Windows, Mac, Linux, tablets and phones.

## Deploy using GitHub and Streamlit Community Cloud

1. Create a **public** GitHub repository (for example `radio-harrow-myriad-search`). **Important:** a public repository exposes the included catalogue CSV to anyone on the internet. Confirm the Myriad metadata is appropriate to publish before uploading.
2. Upload **all files in this folder** to the repository root (not the ZIP and not the containing folder).
3. Sign in at https://share.streamlit.io/ using GitHub, select **Create app**, and choose your repository, branch `main`, and entrypoint `app.py`.
4. Deploy and share the resulting `.streamlit.app` URL. No installation or login is needed for presenters on a public deployment.

## Update the catalogue

Replace `Myriad Data.csv` in GitHub with a fresh Myriad CSV that has the same columns. Update `Myriad Extract Date.txt` with the correct extract date. Commit the changes; Streamlit will redeploy the application.

## Features

- Case-insensitive substring artist and title search
- Search results with duration, year, Media ID, category, intro and ending
- Add tracks across searches; no duplicate Media IDs
- Remove, reorder, or clear Pad List
- Download CSV with the same 18-column format as the supplied example
- Copy artist, title and duration with the copy icon on the code field
- Each visitor has an independent in-memory Pad List

## Local test (optional)

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

**Privacy:** This public app contains metadata only; it does not include audio files. It does not authenticate users. Pad Lists are session-only and can be lost if the session ends or the app restarts. Streamlit Community Cloud free hosting has resource and availability limits.
