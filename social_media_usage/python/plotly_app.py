import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, dash_table
import os

# Function to correct swapped Age and Gender values
def correct_age_gender(df, age_col='Age', gender_col='Gender'):
    def correct_row(row):
        age, gender = row[age_col], row[gender_col]

        try:
            age = int(age)
        except (ValueError, TypeError):
            pass

        if isinstance(age, int) and (0 <= age <= 120):
            return age, gender

        try:
            potential_age = int(gender)
            if 0 <= potential_age <= 120:
                return potential_age, age
        except (ValueError, TypeError):
            pass

        return row[age_col], row[gender_col]

    df[age_col], df[gender_col] = zip(*df.apply(correct_row, axis=1))
    return df

# Define the absolute path to the CSV file
csv_input_path = os.path.abspath('../test.csv')
print(f"CSV Input Path: {csv_input_path}")

# Create DataFrame
df = pd.read_csv(csv_input_path, encoding='utf-8')
print("DataFrame loaded successfully")

# Correct Age and Gender columns
df = correct_age_gender(df)
print("Age and Gender columns corrected")

# Ensure Age column contains only numeric values and convert to int
df['Age'] = pd.to_numeric(df['Age'], errors='coerce').fillna(0).astype(int)

# Handle incorrect gender entries, assume valid genders are 'Male', 'Female', 'Other'
valid_genders = ['Male', 'Female', 'Other']
df['Gender'] = df['Gender'].apply(lambda x: x if x in valid_genders else 'Other')

# Create age ranges
bins = [0, 18, 30, 45, 60, 120]
labels = ['0-18', '19-30', '31-45', '46-60', '60+']
df['Age Range'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False, include_lowest=True)

# Remove duplicates
df = df.drop_duplicates()

# Calculate total metrics
total_likes = df['Likes_Received_Per_Day'].sum()
total_messages = df['Messages_Sent_Per_Day'].sum()
total_platforms = df['Platform'].nunique()
age_range = f"{df['Age'].min()} - {df['Age'].max()}"

print(f"Total Likes: {total_likes}")
print(f"Total Messages: {total_messages}")
print(f"Total Platforms: {total_platforms}")

# Calculate likes and messages by platform
likes_by_platform = df.groupby('Platform')['Likes_Received_Per_Day'].sum().reset_index()
messages_by_platform = df.groupby('Platform')['Messages_Sent_Per_Day'].sum().reset_index()

# Combine data for likes and messages
agg_data = pd.merge(likes_by_platform, messages_by_platform, on='Platform')

# Aggregate data by age range, gender, platform, and dominant emotion
agg_age_range_gender_platform = df.groupby(['Age Range', 'Gender', 'Platform', 'Dominant_Emotion']).agg({
    'Likes_Received_Per_Day': 'sum',
    'Messages_Sent_Per_Day': 'sum',
    'Posts_Per_Day': 'sum'
}).reset_index()

# Remove rows where all numerical values are zero or NaN
agg_age_range_gender_platform = agg_age_range_gender_platform.replace(0, pd.NA)  # Replace zeros with NA
agg_age_range_gender_platform = agg_age_range_gender_platform.dropna(subset=['Likes_Received_Per_Day', 'Messages_Sent_Per_Day', 'Posts_Per_Day'], how='all')

# Sort by Likes_Received_Per_Day, Messages_Sent_Per_Day, and Posts_Per_Day in descending order
agg_age_range_gender_platform = agg_age_range_gender_platform.sort_values(
    by=['Likes_Received_Per_Day', 'Messages_Sent_Per_Day', 'Posts_Per_Day'],
    ascending=[False, False, False]
)

# Initialize Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1(['Social Media Usage Dashboard'], style={'textAlign': 'center'}),

    html.Div([
        dcc.Graph(
            figure=go.Figure(go.Indicator(
                mode="number",
                value=total_likes,
                title={"text": "Total Likes", "font": {"size": 20}, "align": "center"},
                number={"font": {"size": 40}},
                domain={'x': [0, 1], 'y': [0, 1]}
            )),
            style={'display': 'inline-block', 'width': '24%', 'padding': '0', 'margin': '0', 'height': '150px'}
        ),
        dcc.Graph(
            figure=go.Figure(go.Indicator(
                mode="number",
                value=total_messages,
                title={"text": "Total Messages", "font": {"size": 20}, "align": "center"},
                number={"font": {"size": 40}},
                domain={'x': [0, 1], 'y': [0, 1]}
            )),
            style={'display': 'inline-block', 'width': '24%', 'padding': '0', 'margin': '0', 'height': '150px'}
        ),
        dcc.Graph(
            figure=go.Figure(go.Indicator(
                mode="number",
                value=total_platforms,
                title={"text": "Total Platforms", "font": {"size": 20}, "align": "center"},
                number={"font": {"size": 40}},
                domain={'x': [0, 1], 'y': [0, 1]}
            )),
            style={'display': 'inline-block', 'width': '24%', 'padding': '0', 'margin': '0', 'height': '150px'}
        ),
        dcc.Graph(
            figure=go.Figure(go.Indicator(
                mode="number",
                value=df['Age'].max(),
                title={"text": f"Age Range: {age_range}", "font": {"size": 20}, "align": "center"},
                number={"font": {"size": 40}},
                domain={'x': [0, 1], 'y': [0, 1]}
            )),
            style={'display': 'inline-block', 'width': '24%', 'padding': '0', 'margin': '0', 'height': '150px'}
        ),
    ], style={'textAlign': 'center', 'display': 'flex', 'justify-content': 'space-around'}),

    html.Div([
        dcc.Graph(
            id='likes-messages-platform',
            figure=px.line(agg_data, x='Platform', y=['Likes_Received_Per_Day', 'Messages_Sent_Per_Day'],
                           labels={'value': 'Total', 'variable': 'Metric'},
                           title='Total Likes and Messages by Platform')
        ),
    ]),

    html.Div([
        html.H2('Data Table'),
        dash_table.DataTable(
            id='data-table',
            columns=[{"name": i, "id": i} for i in agg_age_range_gender_platform.columns],
            data=agg_age_range_gender_platform.to_dict('records'),
            page_size=10,
            sort_action='native',  # Enable sorting
            sort_by=[{'column_id': 'Likes_Received_Per_Day', 'direction': 'desc'}],  # Initial sort
        ),
    ]),
])

if __name__ == '__main__':
    print("Starting Dash server")
    app.run_server(debug=True)
