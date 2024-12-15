import openai
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy import stats
import os


openai.api_key = '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'


def load_data(file_name):
    try:
        data = pd.read_csv(file_name, encoding='latin1')
        return data
    except Exception as e:
        print(f"Error loading file: {e}")
        return None

def analyze_data(data):

    summary_stats = data.describe()

    missing_values = data.isnull().sum()

    numeric_data = data.select_dtypes(include=[float, int])

    numeric_data = numeric_data.fillna(numeric_data.mean())

    if not numeric_data.empty:
        correlation_matrix = numeric_data.corr()
    else:
        correlation_matrix = None

    z_scores = stats.zscore(numeric_data) if not numeric_data.empty else None
    outliers = (z_scores > 3).sum(axis=0) if z_scores is not None else None

    if len(numeric_data) > 0:
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(numeric_data)

        kmeans = KMeans(n_clusters=3)
        kmeans.fit(scaled_data)

        data['Cluster'] = kmeans.labels_

        data = data.reset_index(drop=True)
    else:
        data['Cluster'] = None

    return summary_stats, missing_values, correlation_matrix, outliers, data


def visualize_analysis(correlation_matrix, outliers, data):

    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title('Correlation Matrix')
    plt.savefig('correlation_matrix.png')
    plt.close()

    plt.figure(figsize=(10, 6))
    sns.barplot(x=outliers.index, y=outliers.values)
    plt.title('Outliers per Column')
    plt.xlabel('Columns')
    plt.ylabel('Outliers Count')
    plt.savefig('outliers.png')
    plt.close()

    if 'Cluster' in data.columns:
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=data, x=data.columns[0], y=data.columns[1], hue='Cluster', palette='Set1')
        plt.title('Cluster Distribution')
        plt.savefig('clusters.png')
        plt.close()


def ask_llm_for_insights(data, summary_stats, missing_values, correlation_matrix, outliers):

    prompt = f"""
    Dataset Overview:
    Column Names and Types: {list(data.dtypes.items())}
    Summary Statistics: {summary_stats}
    Missing Values: {missing_values}
    Correlation Matrix: {correlation_matrix}
    Outliers Detected: {outliers}

    Can you narrate the analysis process and provide insights on the data, including the implications of your findings and possible next steps for improvement or action?
    """

    try:

        response = openai.Completion.create(
            model="gpt-4o-mini",
            prompt=prompt,
            max_tokens=1000
        )

        print("\nNarrative Summary:")
        narrative = response.choices[0].text.strip()
        print(narrative)
        return narrative
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None


def main(file_name):
  
    data = load_data(file_name)
    if data is None:
        return

    summary_stats, missing_values, correlation_matrix, outliers, analyzed_data = analyze_data(data)

    visualize_analysis(correlation_matrix, outliers, analyzed_data)

    narrative = ask_llm_for_insights(analyzed_data, summary_stats, missing_values, correlation_matrix, outliers)

    print("Analysis complete. Visualizations saved as PNG files.")
    return narrative


if __name__ == "__main__":
    file_name = input("Enter the CSV filename: ")
    main(file_name)
