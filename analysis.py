import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import warnings
import logging

warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO,format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

sns.set_theme(style="whitegrid")
output_dir = "results"


def load_enriched_years(data_dir="datasets", start_year=2016, end_year=2025):
    logger.info(f"Loading enriched yearly datasets from '{data_dir}' ({start_year}–{end_year})...")
    dfs = []
    for year in range(start_year, end_year + 1):
        path = os.path.join(data_dir, f"enriched_{year}.csv")
        if os.path.exists(path):
            logger.info(f"  - Found file: {path}, reading...")
            df_y = pd.read_csv(path)
            if 'CRASH DATE' in df_y.columns:
                df_y['year'] = pd.to_datetime(df_y['CRASH DATE'], errors='coerce').dt.year
            else:
                df_y['year'] = year
            dfs.append(df_y)
        else:
            logger.warning(f"  - Warning: {path} not found, skipping.")
    if not dfs:
        logger.error("No enriched_YYYY.csv files found. Exiting.")
        raise FileNotFoundError("No enriched_YYYY.csv files found.")
    combined = pd.concat(dfs, ignore_index=True)
    logger.info(f"Loaded {len(combined):,} total rows from {start_year}–{end_year}")
    return combined

def main():
    logger.info("Starting NYC weather–traffic analysis...")

    traffic_data = load_enriched_years("datasets", 2016, 2025)

    traffic_data['severity'] = (
        traffic_data['NUMBER OF PERSONS INJURED'] +
        traffic_data['NUMBER OF PERSONS KILLED']
    )

    weather_accidents = traffic_data.groupby('weather_condition').size().reset_index(name='accident_count')

    severity_data = (traffic_data.groupby(['weather_condition']).agg(
        total_severity=('severity', 'sum'),
        mean_severity=('severity', 'mean'),
        accident_count=('severity', 'size')
    ).reset_index()
)

    severity_plot_data = severity_data.copy()
    severity_plot_data["accident_share"] = (severity_plot_data["accident_count"] / severity_plot_data["accident_count"].sum())
    severity_plot_data["severity_rate"] = (severity_plot_data["total_severity"] / severity_plot_data["accident_count"])

    overall_severity_rate = traffic_data["severity"].sum() / len(traffic_data)

    equal_share = 1.0 / len(severity_plot_data)

    plt.figure(figsize=(10, 8))
    size_scale = 3000 / severity_plot_data["accident_count"].max()

    plt.scatter(severity_plot_data["accident_share"] * 100,severity_plot_data["severity_rate"],s=severity_plot_data["accident_count"] * size_scale,alpha=0.7)

    for _, row in severity_plot_data.iterrows():
        plt.text(
            row["accident_share"] * 100,
            row["severity_rate"],
            row["weather_condition"],
            fontsize=8,
            ha="center",
            va="center"
        )

    plt.axvline(equal_share * 100, linestyle="--", color="gray", alpha=0.7)
    plt.axhline(overall_severity_rate, linestyle="--", color="gray", alpha=0.7)

    plt.xlabel("Share of All Accidents (%)")
    plt.ylabel("Average Severity per Accident")
    plt.title("Risk Profile of Weather Conditions:\nFrequency vs Severity of NYC Traffic Accidents (2016–2025)")

    plt.tight_layout()
    plt.savefig(f"{output_dir}/weather_risk_profile_scatter.png")
    plt.close()

    weather_accidents['accident_percentage'] = (weather_accidents['accident_count'] / 
                                                weather_accidents['accident_count'].sum()) * 100

    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=weather_accidents,
        x='weather_condition',
        y='accident_percentage',
        order=weather_accidents.sort_values('accident_percentage', ascending=False)['weather_condition']
    )
    plt.xticks(rotation=45)
    plt.title("Proportion of Traffic Accidents by Weather Condition in NYC")
    plt.xlabel("Weather Condition")
    plt.ylabel("Percentage of Total Accidents (%)")
    plt.tight_layout()
    plt.savefig("results/proportion_of_accidents_by_weather_condition.png")
    plt.close()

    plt.figure(figsize=(12, 6))
    plt.scatter(
        severity_data['weather_condition'],
        severity_data['mean_severity'],
        s=severity_data['accident_count'] * 10, 
        alpha=0.7
    )
    plt.xticks(rotation=45)
    plt.title("Bubble Chart: Mean Severity and Total Accidents by Weather Condition")
    plt.xlabel("Weather Condition")
    plt.ylabel("Mean Severity (Average Injuries + Fatalities)")
    plt.tight_layout()
    plt.savefig("results/bubble_chart_severity_weather_condition.png")
    plt.close()

    borough_weather_accidents = traffic_data.groupby(['BOROUGH', 'weather_condition']).size().unstack(fill_value=0)

    plt.figure(figsize=(14, 8))
    sns.heatmap(borough_weather_accidents, annot=False, cmap="YlGnBu", cbar=True, linewidths=0.5)
    plt.title("Traffic Accidents by Borough and Weather Condition in NYC")
    plt.xlabel("Weather Condition")
    plt.ylabel("Borough")
    plt.tight_layout()
    plt.savefig("results/heatmap_borough_weather_condition.png")
    plt.close()

    traffic_data['CRASH TIME'] = pd.to_datetime(traffic_data['CRASH TIME'], errors='coerce')
    traffic_data['hour'] = traffic_data['CRASH TIME'].dt.hour
    hourly_weather_accidents = traffic_data.groupby(['hour', 'weather_condition']).size().reset_index(name='accident_count')

    plt.figure(figsize=(14, 8))
    sns.lineplot(data=hourly_weather_accidents, x='hour', y='accident_count', hue='weather_condition', marker="o")
    plt.title("Traffic Accidents by Hour and Weather Condition in NYC")
    plt.xlabel("Hour of Day")
    plt.ylabel("Number of Accidents")
    plt.legend(title="Weather Condition", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig("results/accidents_by_hour_and_weather_condition.png")
    plt.close()

    traffic_data['month'] = pd.to_datetime(traffic_data['CRASH DATE'], errors='coerce').dt.month
    monthly_accidents = traffic_data.groupby(['month', 'weather_condition']).size().reset_index(name='accident_count')

    plt.figure(figsize=(14, 8))
    sns.lineplot(data=monthly_accidents, x='month', y='accident_count', hue='weather_condition', marker="o")
    plt.title("Monthly Traffic Accidents by Weather Condition in NYC")
    plt.xlabel("Month")
    plt.ylabel("Number of Accidents")
    plt.legend(title="Weather Condition", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig("results/monthly_accidents_by_weather_condition.png")
    plt.close()

    year_weather = (
        traffic_data.groupby(["year", "weather_condition"])
        .size()
        .reset_index(name="accidents")
    )

    plt.figure(figsize=(16, 8))
    sns.lineplot(
        data=year_weather,
        x="year",
        y="accidents",
        hue="weather_condition",
        marker="o"
    )
    plt.title("Weather-Specific Accident Trends (2016–2025)")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/weather_year_trends.png")
    plt.close()

    logger.info("Analysis complete. Check the './results' directory for all generated plots.")

if __name__ == "__main__":
    main()
