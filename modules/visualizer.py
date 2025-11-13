import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def plot_score_trends(df):
    """Create a line chart showing score trends over time."""
    fig = px.line(df, x='date', y='score', 
                  title='Golf Score Trends',
                  labels={'date': 'Date', 'score': 'Score'})
    # Make layout responsive-friendly for embedding in Streamlit
    fig.update_layout(autosize=True, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def plot_course_averages(df):
    """Create a bar chart showing average score by course."""
    course_avg = df.groupby('course')['score'].mean().reset_index()
    fig = px.bar(course_avg, x='course', y='score',
                 title='Average Score by Course',
                 labels={'course': 'Course', 'score': 'Average Score'})
    fig.update_layout(autosize=True, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def plot_score_distribution(df):
    """Create a histogram of score distribution."""
    fig = px.histogram(df, x='score',
                       title='Score Distribution',
                       labels={'score': 'Score'},
                       nbins=20)
    fig.update_layout(autosize=True, margin=dict(l=20, r=20, t=40, b=20))
    return fig
