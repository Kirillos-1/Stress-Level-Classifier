# GitHub Upload Guide

## 1. Create a new GitHub repository

Suggested repository name:

```text
Stress-level-classifier
```

Suggested description:

```text
A machine-learning text classifier that predicts Low, Medium, or High stress levels from written responses using TF-IDF, scikit-learn, and Streamlit.
```

## 2. Upload from your computer

Open a terminal inside the project folder and run:

```bash
git init
git add .
git commit -m "Initial GitHub-ready stress level classifier project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/Stress-level-classifier.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## 3. Recommended repository settings

- Add topics: `machine-learning`, `text-classification`, `nlp`, `tf-idf`, `streamlit`, `scikit-learn`, `stress-classification`.
- Add the final report PDF in the repository description or pinned files.
- Add a screenshot of the app later if you want the README to look even stronger.
- Choose a license only if you want others to reuse the work.

## 4. Check before posting

Before sharing publicly:

- Make sure there is no private information in reports or notebooks.
- Make sure the app runs using `streamlit run app.py`.
- Make sure GitHub displays the README correctly.
- Confirm whether your course allows publishing the full dataset and reports publicly.
