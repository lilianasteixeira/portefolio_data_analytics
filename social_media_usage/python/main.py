import pandas as pd
import os
from matplotlib import pyplot as plt
import seaborn as sns

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the absolute path to the CSV file
csv_input_path = os.path.join(script_dir, '../test.csv')

# Create Dataframe
df = pd.read_csv(csv_input_path, encoding='utf-8')

# Check for null values
null_values = df.isnull().sum()
print(null_values)

# Explore the data
print(df.info())

# Sum Likes
group_sum = df.groupby('Platform')['Likes_Received_Per_Day'].sum().reset_index()
print(group_sum)
    
# Mean messages sented
group_mean = df.groupby('Platform')['Messages_Sent_Per_Day'].mean().reset_index()
print(group_mean)

# Count
group_count = df['Platform'].value_counts().reset_index()
group_count.columns = ['Platform', 'count']
print(group_count)
    
 
# Plotting the group_sum
plt.figure(figsize=(10, 6))
sns.barplot(x='Platform', y='Likes_Received_Per_Day', data=group_sum)
plt.title("Sum of Likes_Received_Per_Day grouped by Platform")
plt.xlabel('Platform')
plt.ylabel('Sum of Likes_Received_Per_Day')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Plotting the group_mean
plt.figure(figsize=(10, 6))
sns.barplot(x='Platform', y='Messages_Sent_Per_Day', data=group_mean)
plt.title("Mean of Messages_Sent_Per_Day grouped by Platform")
plt.xlabel('Age')
plt.ylabel('Mean of Messages_Sent_Per_Day')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Plotting the group_count
plt.figure(figsize=(10, 6))
sns.barplot(x='Platform', y='count', data=group_count)
plt.title("Count of 'Platform'")
plt.xlabel('Platform')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
