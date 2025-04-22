# main.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import openai
from dotenv import load_dotenv
import os
import numpy as np
from scipy.stats import zscore
import altair as alt


# Load .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize session state for tag selection
if "selected_tags" not in st.session_state:
    st.session_state.selected_tags = []

from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_issues(issues):
    if len(issues) == 0:
        return "No issues to summarize."

    prompt = (
        "Summarize the following customer support issues into 3-5 key complaint themes:\n\n"
        + "\n".join(f"- {i}" for i in issues)
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating summary: {e}"

def tag_issue_with_gpt(issue_text):
    possible_tags = "login, payment, crash, ux, billing, bug, speed, account, ui, feedback"
    prompt = (
        f"Assign one lowercase category tag to this issue:\n"
        f"\"{issue_text}\"\n\n"
        f"Only use ONE word from this list:\n{possible_tags}.\n"
        f"Only return the tag, nothing else."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        raw_tag = response.choices[0].message.content.strip().lower()
        clean_tag = raw_tag.split()[0].replace(":", "").replace("\"", "")
        return clean_tag
    except Exception as e:
        return f"error: {e}"

# Load data
df = pd.read_csv("support_tickets.csv")
if "gpt_tag" not in df.columns:
    df["gpt_tag"] = None

df['timestamp'] = pd.to_datetime(df['timestamp'])
df['month'] = df['timestamp'].dt.to_period('M')
df['date'] = df['timestamp'].dt.date

# Page title
st.title("SupportGPT: Customer Feedback Dashboard")

# Layout columns and metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Tagged", df["gpt_tag"].notna().sum())
with col2:
    st.metric("Total Tickets", len(df))
with col3:
    date_range = f"{df['date'].min()} → {df['date'].max()}"
    st.metric("Date Range", date_range)

# Sidebar filters
st.sidebar.header("Filter Tickets")
categories = df['category'].unique().tolist()
selected_categories = st.sidebar.multiselect("Select Categories", categories, default=categories)
filtered_df = df[df['category'].isin(selected_categories)]

# Tag filter section
st.sidebar.markdown("---")
st.sidebar.header("Filter by GPT Tag")
all_tags = df["gpt_tag"].dropna().unique().tolist()
if "selected_tags" not in st.session_state or not st.session_state.selected_tags:
    st.session_state.selected_tags = all_tags
selected_tags = st.sidebar.multiselect("Select Tags", options=all_tags, default=st.session_state.selected_tags, key="tag_filter")
st.session_state.selected_tags = selected_tags

# Ticket trend chart
st.subheader("Monthly Ticket Volume by Category")
monthly_counts = filtered_df.groupby(['month', 'category']).size().unstack().fillna(0)
st.line_chart(monthly_counts)

# Detect spikes using Z-score
st.subheader("Complaint Spikes by Category")
monthly_counts_numeric = monthly_counts.copy()
z_scores = monthly_counts_numeric.apply(zscore)
spikes = (z_scores > 2).fillna(False)
for month in spikes.index:
    for category in spikes.columns:
        if spikes.loc[month, category]:
            st.warning(f"Spike detected in '{category}' during {month}")

# GPT Issue Tagging
st.subheader("GPT Issue Tagging")
if st.button("Auto-tag 10 Recent Tickets"):
    latest_indices = df[df['gpt_tag'].isna()].sort_values(by="timestamp", ascending=False).head(10).index
    for i in latest_indices:
        df.at[i, "gpt_tag"] = tag_issue_with_gpt(df.at[i, "issue"])
    filtered_df = df[df['category'].isin(selected_categories)]
    all_tags = filtered_df["gpt_tag"].dropna().unique().tolist()
    filtered_by_tag = filtered_df[filtered_df["gpt_tag"].isin(selected_tags)]
    st.success("Tags generated and saved!")
    st.dataframe(df.loc[latest_indices, ["timestamp", "issue", "gpt_tag"]])

# Final filtered result
filtered_by_tag = filtered_df[filtered_df["gpt_tag"].isin(selected_tags)] if selected_tags else filtered_df

# Table view
st.subheader("Tagged Ticket Data")
col_data, col_summary = st.columns([3, 2])
with col_data:
    st.dataframe(filtered_by_tag.sort_values(by="timestamp", ascending=False).reset_index(drop=True))
with col_summary:
    if st.button("Generate GPT Insight"):
        sample_issues = filtered_by_tag["issue"].tolist()[:10]
        insight = summarize_issues(sample_issues)
        st.info(insight)

# GPT Insights & Metrics Summary
st.subheader("Top GPT Tags")
if "gpt_tag" in filtered_by_tag.columns:
    tag_counts = filtered_by_tag["gpt_tag"].value_counts().head(10)
    if not tag_counts.empty:
        st.bar_chart(tag_counts)
    else:
        st.info("No tag data to show.")

# Tag frequency heatmap
heat_df = filtered_by_tag.groupby(["month", "gpt_tag"]).size().reset_index(name="count")
if not heat_df.empty:
    heat_chart = alt.Chart(heat_df).mark_rect().encode(
        x='month:O',
        y='gpt_tag:N',
        color='count:Q'
    ).properties(title="Tag Frequency by Month")
    st.altair_chart(heat_chart, use_container_width=True)
else:
    st.info("No tag frequency data to show.")

# GPT Summary
st.subheader("GPT Summary of Common Complaints")
num_to_summarize = st.slider("Number of recent issues to summarize", 5, 50, 25)
if st.button("Generate Summary"):
    recent_issues = filtered_df.sort_values(by="timestamp", ascending=False).head(num_to_summarize)
    summary = summarize_issues(recent_issues["issue"].tolist())
    st.success(summary)
    with open("summaries.txt", "a", encoding="utf-8") as f:
        f.write("\n--- Summary ---\n")
        f.write(summary + "\n")
        f.write("--- End ---\n\n")

# Allow download
st.download_button(
    "Download Tagged Data as CSV",
    data=filtered_by_tag.to_csv(index=False),
    file_name="tagged_tickets.csv",
    mime="text/csv"
)

# Business-Focused KPIs
st.markdown("---")
st.subheader("Business KPIs")
col1, col2 = st.columns(2)
with col1:
    if not filtered_by_tag.empty:
        avg_response_time = filtered_by_tag['timestamp'].diff().dt.total_seconds().mean() / 60
        st.metric("Avg Time Between Tickets (min)", f"{avg_response_time:.2f}")
with col2:
    tag_diversity = filtered_by_tag['gpt_tag'].nunique()
    st.metric("Tag Diversity Score", tag_diversity)





st.markdown("---")
st.subheader("Ask SupportGPT to Improve Itself")

improvement_options = [
    "Add new KPI to dashboard",
    "Visualize tag trends with pie chart",
    "Highlight urgent tickets",
    "Cluster similar tickets with GPT",
    "Suggest UI/UX improvements"
]

selected_improvement = st.selectbox("What would you like to improve?", improvement_options)

if st.button("Make It Happen"):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Given this request: '{selected_improvement}', describe how a Streamlit app analyzing support tickets could improve itself. Give a one-paragraph strategy and include example code."}
            ]
        )
        suggestion = response.choices[0].message.content
        st.success("Here's how SupportGPT could evolve:")
        st.markdown(suggestion)

        # Extract and show editable code block
        st.markdown("### Suggested Code Snippet")
        initial_code = suggestion.split("```python")[-1].split("```")[0] if "```python" in suggestion else suggestion
        st.code(initial_code, language="python")

        st.download_button(
            label="Download Suggested Snippet",
            data=initial_code,
            file_name="suggested_snippet.py",
            mime="text/x-python"
        )

    except Exception as e:
        st.error(f"Error generating improvement strategy: {e}")