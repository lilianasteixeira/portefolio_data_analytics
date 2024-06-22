import pandas as pd
import plotly.express as px
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
csv_input_path = os.path.join(os.path.dirname(__file__), '../test.csv')

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

# Calculate total metrics
total_likes = df['Likes_Received_Per_Day'].sum()
total_messages = df['Messages_Sent_Per_Day'].sum()
total_platforms = df['Platform'].nunique()

# Calculate likes and messages by platform
likes_by_platform = df.groupby('Platform')['Likes_Received_Per_Day'].sum().reset_index()
messages_by_platform = df.groupby('Platform')['Messages_Sent_Per_Day'].sum().reset_index()

# Combine data for likes and messages
agg_data = pd.merge(likes_by_platform, messages_by_platform, on='Platform')

# Initialize Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1('Social Media Usage Dashboard'),

    html.Div([
        html.Div([
            html.H2('Total Likes'),
            html.P(f"{total_likes}")
        ], className='metric'),

        html.Div([
            html.H2('Total Messages'),
            html.P(f"{total_messages}")
        ], className='metric'),

        html.Div([
            html.H2('Total Platforms'),
            html.P(f"{total_platforms}")
        ], className='metric'),

        html.Div([
            html.H2(f"Age Range: {df['Age'].min()} - {df['Age'].max()}"),
            html.P(f"{df['Age'].max()}")
        ], className='metric'),
    ], className='metrics-container'),

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
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            page_size=10,
        ),
    ]),
])

if __name__ == '__main__':
    print("Starting Dash server")
    app.run_server(debug=True)
