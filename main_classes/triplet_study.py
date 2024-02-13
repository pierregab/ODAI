import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd

# Load the dataset
df = pd.read_csv('final_comparison_results.csv')

# Display the first few rows to verify it's loaded correctly
print(df.head())

# Calculating improvement
df['Improvement'] = ((df['Tabulated Merit Function'] - df['Optimized Merit Function']) / df['Tabulated Merit Function']) * 100

# Finding the best starting point for each glass combination
best_starting_points = df.loc[df.groupby('Glass Combination')['Optimized Merit Function'].idxmin()]

# Highlight the best starting point row
def highlight_best(row, best):
    if row.name in best.index:
        return ['background-color: yellow']*len(row)
    return ['']*len(row)

styled_df = best_starting_points.style.apply(highlight_best, best=best_starting_points, axis=1)

# Display or save the styled DataFrame
styled_df.to_excel('optimized_results_highlighted.xlsx')  # Saving to an Excel file


# Plotting
fig, ax = plt.subplots(figsize=(10, 8))

# Extracting unique glass combinations for X-axis labels
glass_combinations = df['Glass Combination'].unique()

# Bar width
bar_width = 0.35

# Positions of the bars on the X-axis
r1 = range(len(glass_combinations))
r2 = [x + bar_width for x in r1]

# Data for bar charts
tabulated_merits = [df[df['Glass Combination'] == gc]['Tabulated Merit Function'].values[0] for gc in glass_combinations]
optimized_merits = [df[df['Glass Combination'] == gc]['Optimized Merit Function'].min() for gc in glass_combinations]

# Creating the bars
plt.bar(r1, tabulated_merits, color='blue', width=bar_width, edgecolor='grey', label='Tabulated Merit Function')
plt.bar(r2, optimized_merits, color='green', width=bar_width, edgecolor='grey', label='Optimized Merit Function (Best)')

# Adding names on the X-axis
plt.xlabel('Glass Combination', fontweight='bold')
plt.xticks([r + bar_width/2 for r in range(len(glass_combinations))], glass_combinations, rotation=45, ha="right")

# Graph labels and title
plt.ylabel('Merit Function Value')
plt.title('Comparison of Tabulated and Optimized Merit Functions')

# Create legend & Show graphic
plt.legend()

plt.tight_layout()  # Adjust layout to not cut off labels
plt.show()