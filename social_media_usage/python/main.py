import pandas as pd
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to correct swapped Age and Gender values
def correct_age_gender(df, age_col='Age', gender_col='Gender'):
    def correct_row(row):
        age, gender = row[age_col], row[gender_col]

        # Convert strings to numeric values if possible
        try:
            age = int(age)
        except (ValueError, TypeError):
            pass

        if isinstance(age, int) and (0 <= age <= 120):
            # Age is valid
            return age, gender

        # Otherwise, check if gender is actually the age
        try:
            potential_age = int(gender)
            if 0 <= potential_age <= 120:
                # Swap age and gender if the potential age is valid
                return potential_age, age
        except (ValueError, TypeError):
            pass

        # Default return original values
        return row[age_col], row[gender_col]

    df[age_col], df[gender_col] = zip(*df.apply(correct_row, axis=1))
    return df

# Define the absolute path to the CSV file
csv_input_path = os.path.join(os.path.dirname(__file__), '../test.csv')

# Create DataFrame
df = pd.read_csv(csv_input_path, encoding='utf-8')

# Correct Age and Gender columns
df = correct_age_gender(df)

# Ensure Age column contains only numeric values and convert to int
df['Age'] = pd.to_numeric(df['Age'], errors='coerce').fillna(0).astype(int)

# Handle incorrect gender entries, assume valid genders are 'Male', 'Female', 'Other'
valid_genders = ['Male', 'Female', 'Other']
df['Gender'] = df['Gender'].apply(lambda x: x if x in valid_genders else 'Other')

# Calculate total metrics
total_likes = df['Likes_Received_Per_Day'].sum()
total_messages = df['Messages_Sent_Per_Day'].sum()
total_platforms = df['Platform'].nunique()

# Calculate likes and messages by platform
likes_by_platform = df.groupby('Platform')['Likes_Received_Per_Day'].sum().reset_index()
messages_by_platform = df.groupby('Platform')['Messages_Sent_Per_Day'].sum().reset_index()

# Combine data for likes and messages
agg_data = pd.merge(likes_by_platform, messages_by_platform, on='Platform')

# Create a subplot figure
fig = make_subplots(
    rows=3, cols=4,
    specs=[
        [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],  # Row for indicators
        [{"colspan": 4}, None, None, None],  # Row for the first plot
        [{"colspan": 4}, None, None, None]   # Row for the second plot
    ],
)

# Add big numbers (indicators) with titles and labels
indicators = [
    ("Total Likes", total_likes, 1, 1),
    ("Total Messages", total_messages, 1, 2),
    ("Total Platforms", total_platforms, 1, 3),
    (f"Age Range: {df['Age'].min()} - {df['Age'].max()}", df['Age'].max(), 1, 4)
]

for title, value, row, col in indicators:
    fig.add_trace(
        go.Indicator(
            mode="number",
            value=value,
            title={"text": title, "font": {"size": 15}},
            number={"font": {"size": 20}}
        ),
        row=row,
        col=col
    )

# Add line plots for likes and messages by platform
for i, color in enumerate(['indianred', 'lightsalmon']):
    fig.add_trace(
        go.Scatter(
            x=agg_data['Platform'],
            y=agg_data.iloc[:, i + 1],  # Likes or Messages
            mode='lines+markers',
            name=agg_data.columns[i + 1],
            line=dict(color=color, width=2),
            marker=dict(color=color, size=8),
        ),
        row=2,
        col=1
    )

# Add title to the line plot
fig.update_layout(
    height=900,
    showlegend=True,  # Show legend
    legend=dict(
        orientation="h",
        yanchor="bottom",  # Anchor legend to the bottom
        y=0.64,  # Position it at the bottom of the page
        xanchor="center",
        x=0.5
    ),
    title={"text": "<b>Social Media Usage Dashboard</b>", "y": 0.95, "x": 0.5, "xanchor": "center", "yanchor": "top"},
    margin=dict(t=30, b=20)  # Reduce bottom margin to reduce space
)

# Add y-axis title to the line plot
fig.update_yaxes(title_text='Total', row=2, col=1)

# Add title to the line plot
fig.update_layout(
    annotations=[
        dict(
            xref='paper',
            yref='paper',
            x=0.5,
            y=0.7,
            xanchor='center',
            yanchor='middle',
            text='Total of Likes and Messages by Platform',
            font=dict(size=15),
            showarrow=False
        )
    ]
)

# Add x and y axis titles to the line plot
fig.update_xaxes(title_text='Platform', row=2, col=1)
fig.update_yaxes(title_text='Total', row=2, col=1)

# Save as PDF
pdf_output_path = os.path.join(os.path.dirname(__file__), 'dashboard.pdf')
fig.write_image(pdf_output_path, engine="kaleido")

print(f'Dashboard saved as {pdf_output_path}')
