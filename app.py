import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------
# Page settings
# ---------------------------------------------------------
st.set_page_config(
    page_title="Student Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

sns.set_theme(style="whitegrid")

# ---------------------------------------------------------
# Title
# ---------------------------------------------------------
st.title("📊 Student Performance Dashboard")
st.write("FDS Final Project — Interactive analysis of student performance")

# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file)

    numeric_cols = [
        "Age", "Attendance (%)", "Midterm_Score", "Final_Score",
        "Assignments_Avg", "Quizzes_Avg", "Participation_Score",
        "Projects_Score", "Total_Score", "test_preparation_course",
        "math_score", "reading_score", "writing_score", "science_score"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str)
                .str.replace(r"[\t\r\n]", "", regex=True)
                .str.strip(),
                errors="coerce"
            )
            df[col] = df[col].fillna(df[col].median())

    if "test_preparation_course" in df.columns:
        df["Test_Preparation"] = np.where(
            df["test_preparation_course"] == 1,
            "Completed",
            "Not Completed"
        )

    return df


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
st.sidebar.header("⚙️ Dashboard Controls")

uploaded_file = st.sidebar.file_uploader(
    "Upload student_data(1).csv",
    type=["csv"]
)

if uploaded_file is None:
    st.info(
        "👈 Upload your `student_data(1).csv` file from the sidebar to start the dashboard."
    )
    st.markdown("""
    ### How to use
    1. Put the `app.py` and your CSV file in the same folder, or upload the CSV using the sidebar.
    2. Run `streamlit run app.py`.
    3. Upload the dataset if it is not automatically available.
    4. Use the filters on the left.
    """)
    st.stop()

df = load_data(uploaded_file)

# ---------------------------------------------------------
# Filters
# ---------------------------------------------------------
st.sidebar.subheader("Filters")

departments = st.sidebar.multiselect(
    "Department",
    sorted(df["Department"].dropna().unique()),
    default=sorted(df["Department"].dropna().unique())
)

genders = st.sidebar.multiselect(
    "Gender",
    sorted(df["Gender"].dropna().unique()),
    default=sorted(df["Gender"].dropna().unique())
)

grades = st.sidebar.multiselect(
    "Grade",
    sorted(df["Grade"].dropna().unique()),
    default=sorted(df["Grade"].dropna().unique())
)

prep_options = st.sidebar.multiselect(
    "Test Preparation",
    sorted(df["Test_Preparation"].dropna().unique()),
    default=sorted(df["Test_Preparation"].dropna().unique())
)

filtered = df[
    df["Department"].isin(departments)
    & df["Gender"].isin(genders)
    & df["Grade"].isin(grades)
    & df["Test_Preparation"].isin(prep_options)
].copy()

# ---------------------------------------------------------
# KPI cards
# ---------------------------------------------------------
st.subheader("📌 Key Performance Indicators")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Students", f"{len(filtered):,}")
c2.metric("Avg Attendance", f"{filtered['Attendance (%)'].mean():.2f}%")
c3.metric("Avg Total Score", f"{filtered['Total_Score'].mean():.2f}")
c4.metric("Avg Final Score", f"{filtered['Final_Score'].mean():.2f}")

st.divider()

# ---------------------------------------------------------
# Row 1 - Bar + Pie
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Average Total Score by Department")

    department_average = (
        filtered.groupby("Department")["Total_Score"]
        .mean()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    department_average.plot(kind="bar", ax=ax)
    ax.set_xlabel("Department")
    ax.set_ylabel("Average Total Score")
    ax.set_title("Average Total Score by Department")
    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

with col2:
    st.subheader("🥧 Grade Distribution")

    grade_counts = filtered["Grade"].value_counts()

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.pie(
        grade_counts.values,
        labels=grade_counts.index,
        autopct="%1.1f%%",
        startangle=90
    )
    ax.set_title("Grade Distribution")

    st.pyplot(fig)
    plt.close(fig)

# ---------------------------------------------------------
# Row 2 - Histogram + Line
# ---------------------------------------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("📈 Total Score Distribution")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(
        filtered["Total_Score"],
        bins=20,
        edgecolor="black"
    )
    ax.set_xlabel("Total Score")
    ax.set_ylabel("Number of Students")
    ax.set_title("Distribution of Total Scores")
    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

with col4:
    st.subheader("📉 Average Score Across Assessments")

    names = [
        "Midterm",
        "Final",
        "Assignments",
        "Quizzes",
        "Projects",
        "Total"
    ]

    values = [
        filtered["Midterm_Score"].mean(),
        filtered["Final_Score"].mean(),
        filtered["Assignments_Avg"].mean(),
        filtered["Quizzes_Avg"].mean(),
        filtered["Projects_Score"].mean(),
        filtered["Total_Score"].mean()
    ]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(names, values, marker="o")
    ax.set_xlabel("Assessment")
    ax.set_ylabel("Average Score")
    ax.set_title("Average Score Across Assessments")
    plt.xticks(rotation=30)
    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

# ---------------------------------------------------------
# Row 3 - Scatter + Box
# ---------------------------------------------------------
col5, col6 = st.columns(2)

with col5:
    st.subheader("🔵 Attendance vs Total Score")

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(
        data=filtered,
        x="Attendance (%)",
        y="Total_Score",
        hue="Grade",
        alpha=0.6,
        ax=ax
    )
    ax.set_title("Attendance vs Total Score")
    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

with col6:
    st.subheader("📦 Total Score by Department")

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(
        data=filtered,
        x="Department",
        y="Total_Score",
        ax=ax
    )
    ax.set_title("Total Score Distribution by Department")
    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

# ---------------------------------------------------------
# Heatmap
# ---------------------------------------------------------
st.subheader("🔥 Correlation Heatmap")

corr_columns = [
    "Attendance (%)",
    "Midterm_Score",
    "Final_Score",
    "Assignments_Avg",
    "Quizzes_Avg",
    "Projects_Score",
    "Total_Score",
    "math_score",
    "reading_score",
    "writing_score",
    "science_score"
]

correlation = filtered[corr_columns].corr()

fig, ax = plt.subplots(figsize=(14, 9))
sns.heatmap(
    correlation,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    linewidths=0.5,
    ax=ax
)
ax.set_title("Correlation Between Numerical Variables")
plt.tight_layout()

st.pyplot(fig)
plt.close(fig)

# ---------------------------------------------------------
# Grouped bar chart
# ---------------------------------------------------------
st.subheader("👥 Average Total Score by Department and Gender")

grouped = (
    filtered.groupby(["Department", "Gender"])["Total_Score"]
    .mean()
    .unstack()
)

fig, ax = plt.subplots(figsize=(11, 6))
grouped.plot(kind="bar", ax=ax)
ax.set_xlabel("Department")
ax.set_ylabel("Average Total Score")
ax.set_title("Department and Gender Comparison")
plt.xticks(rotation=45)
plt.legend(title="Gender")
plt.tight_layout()

st.pyplot(fig)
plt.close(fig)

# ---------------------------------------------------------
# Findings
# ---------------------------------------------------------
st.subheader("📝 Key Findings")

if len(filtered) > 0:
    highest_department = (
        filtered.groupby("Department")["Total_Score"]
        .mean()
        .idxmax()
    )

    common_grade = filtered["Grade"].mode()[0]

    st.write(
        f"- **Highest average-performing department:** {highest_department}"
    )
    st.write(f"- **Most common grade:** {common_grade}")
    st.write(
        f"- **Average attendance:** "
        f"{filtered['Attendance (%)'].mean():.2f}%"
    )
    st.write(
        f"- **Average total score:** "
        f"{filtered['Total_Score'].mean():.2f}"
    )

# ---------------------------------------------------------
# Data table + download
# ---------------------------------------------------------
st.subheader("📋 Filtered Student Data")

st.dataframe(
    filtered,
    use_container_width=True,
    height=400
)

csv_data = filtered.to_csv(index=False)

st.download_button(
    label="⬇️ Download Filtered Dataset",
    data=csv_data,
    file_name="filtered_student_data.csv",
    mime="text/csv"
)

st.success("Dashboard loaded successfully!")
