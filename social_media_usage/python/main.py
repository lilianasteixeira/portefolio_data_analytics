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

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the absolute path to the CSV file
csv_input_path = os.path.join(script_dir, '../test.csv')

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

# Calculate age range
age_min = df['Age'].min()
age_max = df['Age'].max()

# Create a subplot figure
fig = make_subplots(
    rows=4, cols=2,
    specs=[[{"type": "indicator"}, {"type": "indicator"}],
           [{"type": "indicator"}, {"type": "indicator"}],
           [{"colspan": 2}, None],
           [{"colspan": 2}, None]],
    subplot_titles=(
        "Total Likes", "Total Messages",
        "Total Platforms", "Age Range",
        "Sum of Likes Received by Platform",
        "Mean Messages Sent by Platform"
    )
)

# Add big numbers (indicators) with titles and labels
fig.add_trace(go.Indicator(
    mode="number",
    value=total_likes,
    #title={"text": "Total Likes"},
    number={"font": {"size": 50}},
), row=1, col=1)

fig.add_trace(go.Indicator(
    mode="number",
    value=total_messages,
    #title={"text": "Total Messages"},
    number={"font": {"size": 50}},
), row=1, col=2)

fig.add_trace(go.Indicator(
    mode="number",
    value=total_platforms,
    #title={"text": "Total Platforms"},
    number={"font": {"size": 50}},
), row=2, col=1)

# Display age range as text with title and label
fig.add_trace(go.Indicator(
    mode="number",
    value=age_max,  # Using age_max just to utilize the number indicator
    #title={"text": f"Age Range: {age_min} - {age_max}"},
    number={"font": {"size": 50}, "suffix": ""},
), row=2, col=2)

# Add bar plots with titles and labels
fig.add_trace(go.Bar(
    x=df['Platform'],
    y=df['Likes_Received_Per_Day'],
    name="Sum of Likes Received Per Day",
    marker_color='indianred'
), row=3, col=1)

fig.add_trace(go.Bar(
    x=df['Platform'],
    y=df['Messages_Sent_Per_Day'],
    name="Mean Messages Sent Per Day",
    marker_color='lightsalmon'
), row=4, col=1)

# Update layout with titles and labels
fig.update_layout(
    height=900,
    showlegend=False,
    title_text="Social Media Usage Dashboard",
)

# Save as PDF in the same directory as the script
pdf_output_path = os.path.join(script_dir, 'dashboard.pdf')
fig.write_image(pdf_output_path, engine="kaleido")

print(f'Dashboard saved as {pdf_output_path}')
