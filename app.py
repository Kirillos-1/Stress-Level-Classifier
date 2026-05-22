from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Stress Level Classifier",
    page_icon="🧠",
    layout="wide",
)

PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_ROOT / "models" / "best_stress_level_pipeline.joblib"
METRICS_PATH = PROJECT_ROOT / "reports" / "phase2" / "model_comparison_metrics.csv"
DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "stress_level_dataset_v2_balanced.csv"
FIGURE_PATH = PROJECT_ROOT / "reports" / "figures" / "model_comparison_macro_f1.png"

LABEL_MESSAGES = {
    "Low": "The text appears to show low stress signals.",
    "Medium": "The text appears to show moderate stress signals.",
    "High": "The text appears to show stronger stress signals.",
}

LABEL_EMOJI = {
    "Low": "🟢",
    "Medium": "🟡",
    "High": "🔴",
}


@st.cache_resource
def load_model():
    """Load the saved scikit-learn pipeline once per app session."""
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_metrics():
    """Load model-comparison metrics if the CSV is available."""
    if METRICS_PATH.exists():
        return pd.read_csv(METRICS_PATH)
    return pd.DataFrame()


@st.cache_data
def load_dataset_counts():
    """Load final class counts for the project-info page."""
    if DATASET_PATH.exists():
        df = pd.read_csv(DATASET_PATH, usecols=["stress_level"])
        return df["stress_level"].value_counts().reindex(["Low", "Medium", "High"])
    return pd.Series(dtype="int64")


st.sidebar.title("🧠 Stress Classifier")
page = st.sidebar.radio(
    "Navigation",
    ["Predict", "Project Overview", "Model Results"],
)

st.sidebar.divider()
st.sidebar.caption("Educational ML project — not a medical diagnosis tool.")

if not MODEL_PATH.exists():
    st.error("The saved model file was not found.")
    st.code(str(MODEL_PATH))
    st.info("Run the Phase 2 modeling notebook first to train and save the best model pipeline.")
    st.stop()

model = load_model()
metrics_df = load_metrics()

# --------------------------------------------------
# Page 1: Prediction
# --------------------------------------------------
if page == "Predict":
    st.title("Stress Level Classifier")
    st.write(
        "Enter a short text response and the model will classify it as "
        "**Low**, **Medium**, or **High** stress."
    )

    st.warning(
        "This app is for a machine-learning course project. "
        "It should not be used for diagnosis, crisis detection, or medical decisions."
    )

    example_text = (
        "I am worried about my exams, but I made a study plan and I think I can manage it."
    )

    col_input, col_result = st.columns([1.25, 1])

    with col_input:
        user_text = st.text_area(
            "Text input",
            value=example_text,
            height=220,
            help="Write a journal entry, survey answer, or short reflection.",
        )

        predict_button = st.button("Predict stress level", type="primary")

    with col_result:
        st.subheader("Prediction")

        if predict_button:
            if not user_text.strip():
                st.warning("Please enter text before predicting.")
            else:
                prediction = model.predict([user_text])[0]
                emoji = LABEL_EMOJI.get(prediction, "")

                if prediction == "Low":
                    st.success(f"{emoji} Predicted stress level: **{prediction}**")
                elif prediction == "Medium":
                    st.warning(f"{emoji} Predicted stress level: **{prediction}**")
                else:
                    st.error(f"{emoji} Predicted stress level: **{prediction}**")

                st.write(LABEL_MESSAGES.get(prediction, "Prediction completed."))

                if hasattr(model, "predict_proba"):
                    probabilities = model.predict_proba([user_text])[0]
                    probability_df = pd.DataFrame(
                        {
                            "Stress Level": model.classes_,
                            "Probability": probabilities,
                        }
                    ).sort_values("Probability", ascending=False)

                    st.write("Class confidence")
                    for _, row in probability_df.iterrows():
                        st.progress(
                            float(row["Probability"]),
                            text=f"{row['Stress Level']}: {row['Probability']:.2%}",
                        )
        else:
            st.info("Click the prediction button to classify the text.")

# --------------------------------------------------
# Page 2: Project overview
# --------------------------------------------------
elif page == "Project Overview":
    st.title("Project Overview")

    st.markdown(
        """
        This project follows a complete supervised machine-learning workflow for text classification.

        **Goal:** classify written responses into three stress levels: **Low**, **Medium**, and **High**.

        **Main workflow:**
        1. Collect and standardize text data.
        2. Clean missing or duplicate text.
        3. Balance the three target classes.
        4. Convert text into TF-IDF features.
        5. Train and compare five machine-learning models.
        6. Save the best model as a pipeline.
        7. Use the saved pipeline in this Streamlit app.
        """
    )

    counts = load_dataset_counts()
    if not counts.empty:
        total = int(counts.sum())
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total rows", f"{total:,}")
        col2.metric("Low", f"{int(counts.get('Low', 0)):,}")
        col3.metric("Medium", f"{int(counts.get('Medium', 0)):,}")
        col4.metric("High", f"{int(counts.get('High', 0)):,}")

    st.subheader("Dataset file")
    st.code("data/processed/stress_level_dataset_v2_balanced.csv")

    st.subheader("Why balancing matters")
    st.write(
        "The final dataset has the same number of examples for Low, Medium, and High stress. "
        "This helps prevent the model from favoring the largest class and makes the comparison fairer."
    )

# --------------------------------------------------
# Page 3: Model results
# --------------------------------------------------
elif page == "Model Results":
    st.title("Model Results")

    if metrics_df.empty:
        st.warning("Model metrics file was not found.")
        st.code(str(METRICS_PATH))
    else:
        display_df = metrics_df.copy()
        numeric_cols = ["Accuracy", "Macro Precision", "Macro Recall", "Macro F1"]
        for col in numeric_cols:
            if col in display_df.columns:
                display_df[col] = display_df[col].map(lambda value: f"{value:.3f}")

        best_row = metrics_df.sort_values("Macro F1", ascending=False).iloc[0]

        col1, col2 = st.columns(2)
        col1.metric("Best model", best_row["Model"])
        col2.metric("Best Macro F1", f"{best_row['Macro F1']:.3f}")

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        if FIGURE_PATH.exists():
            st.image(str(FIGURE_PATH), caption="Macro F1 comparison across trained models")

        st.markdown(
            """
            **Why Macro F1?**  
            Macro F1 calculates the F1-score for each class and averages them equally. 
            This is useful because the project cares about performance on all three stress levels, not only overall accuracy.
            """
        )
