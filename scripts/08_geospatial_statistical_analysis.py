#!/usr/bin/env python
# coding: utf-8

"""
Advanced Geospatial Statistical Analysis
- Center of gravity (geographic centroid) changes over time
- Spatial dispersion and clustering metrics
- Hotspot detection using Kernel Density Estimation
- Standard deviational ellipse (directional distribution)
- Distance-based analysis from downtown LA
- Substance-specific spatial patterns
- Statistical tests for spatial clustering
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.spatial.distance import cdist
from sklearn.cluster import DBSCAN
from sklearn.neighbors import KernelDensity
import warnings

warnings.filterwarnings('ignore')

# Settings
sns.set_style("whitegrid")
os.makedirs("results/08_geospatial_statistics", exist_ok=True)

DATA_PATH = "/data2/fabricehc/epi/data/2012-01-2024-08-overdoses.csv"

# Downtown LA coordinates (approximate center)
DOWNTOWN_LA = (34.0522, -118.2437)

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two lat/lon points"""
    R = 6371  # Earth's radius in km

    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

def calculate_spatial_statistics(lats, lons):
    """Calculate various spatial statistics"""
    # Center of gravity (mean center)
    center_lat = lats.mean()
    center_lon = lons.mean()

    # Standard distance (spatial dispersion)
    std_distance = np.sqrt(
        ((lats - center_lat)**2).sum() / len(lats) +
        ((lons - center_lon)**2).sum() / len(lons)
    )

    # Convert to km (rough approximation at LA latitude)
    km_per_degree_lat = 111
    km_per_degree_lon = 111 * np.cos(np.radians(center_lat))
    std_distance_km = std_distance * np.sqrt((km_per_degree_lat**2 + km_per_degree_lon**2) / 2)

    return {
        'center_lat': center_lat,
        'center_lon': center_lon,
        'std_distance': std_distance,
        'std_distance_km': std_distance_km,
        'n_points': len(lats)
    }

def calculate_standard_ellipse(lats, lons, confidence=1.0):
    """Calculate standard deviational ellipse"""
    center_lat = lats.mean()
    center_lon = lons.mean()

    # Deviations
    dx = lons - center_lon
    dy = lats - center_lat

    # Covariance matrix
    cov = np.cov(dx, dy)

    # Eigenvalues and eigenvectors
    eigenvalues, eigenvectors = np.linalg.eig(cov)

    # Angle of rotation
    angle = np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0])

    # Semi-major and semi-minor axes
    semi_major = confidence * np.sqrt(eigenvalues[0])
    semi_minor = confidence * np.sqrt(eigenvalues[1])

    return {
        'center_lat': center_lat,
        'center_lon': center_lon,
        'semi_major': semi_major,
        'semi_minor': semi_minor,
        'angle_rad': angle,
        'angle_deg': np.degrees(angle)
    }

def main():
    print("Loading data...")
    df = pd.read_csv(DATA_PATH, low_memory=False)

    # Process dates
    df['Date of Death'] = pd.to_datetime(df['DeathDate'], errors='coerce')
    df['Year'] = df['Date of Death'].dt.year
    df = df[df['Year'].between(2012, 2023)]

    # Filter to valid LA County coordinates
    df = df[(df['lat'].notna()) & (df['lon'].notna())].copy()
    df = df[
        (df['lat'].between(33.7, 34.8)) &
        (df['lon'].between(-118.7, -117.6))
    ]

    print(f"Analyzing {len(df):,} overdoses with valid coordinates")

    substance_cols = ['Heroin', 'Fentanyl', 'Prescription.opioids',
                      'Methamphetamine', 'Cocaine', 'Benzodiazepines', 'Alcohol', 'Others']

    # === 1. Center of Gravity Over Time ===
    print("\nCalculating center of gravity changes over time...")

    yearly_stats = []
    for year in sorted(df['Year'].unique()):
        year_data = df[df['Year'] == year]
        stats_dict = calculate_spatial_statistics(year_data['lat'], year_data['lon'])
        stats_dict['Year'] = year
        yearly_stats.append(stats_dict)

    yearly_df = pd.DataFrame(yearly_stats)
    yearly_df.to_csv('results/08_geospatial_statistics/center_of_gravity_annual.csv', index=False)

    # Plot center of gravity trajectory
    fig, ax = plt.subplots(figsize=(12, 10))

    # Plot all points (light background)
    ax.scatter(df['lon'], df['lat'], alpha=0.02, s=0.5, color='gray')

    # Plot center of gravity trajectory
    ax.plot(yearly_df['center_lon'], yearly_df['center_lat'],
           marker='o', linewidth=2, markersize=8, color='red',
           label='Center of Gravity', zorder=5)

    # Annotate years
    for _, row in yearly_df.iterrows():
        ax.annotate(f"{row['Year']:.0f}",
                   (row['center_lon'], row['center_lat']),
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=8, color='red')

    # Mark downtown LA
    ax.scatter(DOWNTOWN_LA[1], DOWNTOWN_LA[0],
              marker='*', s=300, color='blue',
              edgecolors='black', linewidth=2,
              label='Downtown LA', zorder=10)

    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    ax.set_title('Geographic Center of Gravity of Overdose Deaths Over Time\nLos Angeles County 2012-2023',
                fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.set_aspect('equal')

    plt.tight_layout()
    plt.savefig('results/08_geospatial_statistics/center_of_gravity_trajectory.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: center_of_gravity_trajectory.png")

    # === 2. Spatial Dispersion Over Time ===
    print("Analyzing spatial dispersion trends...")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Standard distance over time
    ax1.plot(yearly_df['Year'], yearly_df['std_distance_km'],
            marker='o', linewidth=2, color='#ED0000')
    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('Standard Distance (km)', fontsize=12)
    ax1.set_title('Spatial Dispersion of Overdoses Over Time', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # Number of points
    ax2.bar(yearly_df['Year'], yearly_df['n_points'], color='#00468B', alpha=0.7)
    ax2.set_xlabel('Year', fontsize=12)
    ax2.set_ylabel('Number of Geocoded Deaths', fontsize=12)
    ax2.set_title('Annual Overdose Deaths with Coordinates', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('results/08_geospatial_statistics/spatial_dispersion.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: spatial_dispersion.png")

    # === 3. Distance from Downtown LA ===
    print("Calculating distance from downtown LA...")

    df['distance_from_downtown_km'] = haversine_distance(
        df['lat'], df['lon'],
        DOWNTOWN_LA[0], DOWNTOWN_LA[1]
    )

    # Annual average distance
    annual_distance = df.groupby('Year')['distance_from_downtown_km'].agg(['mean', 'median', 'std']).reset_index()
    annual_distance.to_csv('results/08_geospatial_statistics/distance_from_downtown_annual.csv', index=False)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(annual_distance['Year'], annual_distance['mean'],
           marker='o', linewidth=2, label='Mean Distance', color='#ED0000')
    ax.plot(annual_distance['Year'], annual_distance['median'],
           marker='s', linewidth=2, label='Median Distance', color='#00468B', linestyle='--')
    ax.fill_between(annual_distance['Year'],
                     annual_distance['mean'] - annual_distance['std'],
                     annual_distance['mean'] + annual_distance['std'],
                     alpha=0.2, color='#ED0000')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Distance from Downtown LA (km)', fontsize=12)
    ax.set_title('Average Distance of Overdoses from Downtown LA\nLos Angeles County 2012-2023',
                fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/08_geospatial_statistics/distance_from_downtown.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: distance_from_downtown.png")

    # === 4. Standard Deviational Ellipse Over Time ===
    print("Calculating standard deviational ellipses...")

    fig, ax = plt.subplots(figsize=(12, 10))

    # Background points
    ax.scatter(df['lon'], df['lat'], alpha=0.02, s=0.5, color='gray')

    # Colors for different time periods
    periods = {
        '2012-2015': (df['Year'] >= 2012) & (df['Year'] <= 2015),
        '2016-2019': (df['Year'] >= 2016) & (df['Year'] <= 2019),
        '2020-2023': (df['Year'] >= 2020) & (df['Year'] <= 2023)
    }
    colors = {'2012-2015': '#00468B', '2016-2019': '#42B540', '2020-2023': '#ED0000'}

    for period, mask in periods.items():
        period_data = df[mask]
        if len(period_data) > 0:
            ellipse = calculate_standard_ellipse(period_data['lat'], period_data['lon'], confidence=2.0)

            # Create ellipse
            theta = np.linspace(0, 2*np.pi, 100)
            x = ellipse['semi_major'] * np.cos(theta)
            y = ellipse['semi_minor'] * np.sin(theta)

            # Rotate
            cos_angle = np.cos(ellipse['angle_rad'])
            sin_angle = np.sin(ellipse['angle_rad'])
            x_rot = cos_angle * x - sin_angle * y + ellipse['center_lon']
            y_rot = sin_angle * x + cos_angle * y + ellipse['center_lat']

            ax.plot(x_rot, y_rot, linewidth=3, label=period, color=colors[period])
            ax.scatter(ellipse['center_lon'], ellipse['center_lat'],
                      marker='o', s=100, color=colors[period], edgecolors='black', linewidth=2)

    ax.scatter(DOWNTOWN_LA[1], DOWNTOWN_LA[0],
              marker='*', s=300, color='gold',
              edgecolors='black', linewidth=2,
              label='Downtown LA', zorder=10)

    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    ax.set_title('Standard Deviational Ellipses (2σ) Over Time\nLos Angeles County',
                fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, loc='upper left')
    ax.set_aspect('equal')

    plt.tight_layout()
    plt.savefig('results/08_geospatial_statistics/standard_ellipses.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: standard_ellipses.png")

    # === 5. Substance-Specific Centers of Gravity ===
    print("Analyzing substance-specific spatial patterns...")

    substance_centers = []
    for substance in substance_cols:
        sub_data = df[df[substance] == 1]
        if len(sub_data) > 0:
            stats_dict = calculate_spatial_statistics(sub_data['lat'], sub_data['lon'])
            stats_dict['Substance'] = substance
            substance_centers.append(stats_dict)

    substance_df = pd.DataFrame(substance_centers)
    substance_df.to_csv('results/08_geospatial_statistics/substance_centers_of_gravity.csv', index=False)

    fig, ax = plt.subplots(figsize=(12, 10))

    # Background
    ax.scatter(df['lon'], df['lat'], alpha=0.02, s=0.5, color='gray')

    # Substance centers
    colors_sub = {
        'Fentanyl': '#ED0000',
        'Heroin': '#00468B',
        'Methamphetamine': '#42B540',
        'Cocaine': '#0099B4',
        'Prescription.opioids': '#925E9F',
        'Benzodiazepines': '#FDAF91',
        'Alcohol': '#FF8C00',
        'Others': '#808080'
    }

    for _, row in substance_df.iterrows():
        ax.scatter(row['center_lon'], row['center_lat'],
                  marker='o', s=300,
                  color=colors_sub.get(row['Substance'], 'gray'),
                  edgecolors='black', linewidth=2,
                  label=row['Substance'], alpha=0.8)

        # Draw circle for standard distance
        circle = plt.Circle((row['center_lon'], row['center_lat']),
                           row['std_distance'],
                           fill=False, linestyle='--',
                           color=colors_sub.get(row['Substance'], 'gray'),
                           linewidth=2, alpha=0.5)
        ax.add_patch(circle)

    ax.scatter(DOWNTOWN_LA[1], DOWNTOWN_LA[0],
              marker='*', s=300, color='gold',
              edgecolors='black', linewidth=2,
              label='Downtown LA', zorder=10)

    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    ax.set_title('Centers of Gravity by Substance\nLos Angeles County 2012-2023\n(Dashed circles = 1 standard distance)',
                fontsize=14, fontweight='bold')
    ax.legend(fontsize=9, loc='upper left', ncol=2)
    ax.set_aspect('equal')

    plt.tight_layout()
    plt.savefig('results/08_geospatial_statistics/substance_centers.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: substance_centers.png")

    # === 6. Kernel Density Estimation Hotspots ===
    print("Creating kernel density estimation hotspots...")

    # Use 2020-2023 data for recent hotspots
    recent_data = df[df['Year'] >= 2020]

    # Create grid
    lon_range = np.linspace(df['lon'].min(), df['lon'].max(), 100)
    lat_range = np.linspace(df['lat'].min(), df['lat'].max(), 100)
    lon_grid, lat_grid = np.meshgrid(lon_range, lat_range)
    grid_points = np.c_[lon_grid.ravel(), lat_grid.ravel()]

    # KDE
    coords = np.c_[recent_data['lon'], recent_data['lat']]
    kde = KernelDensity(bandwidth=0.02, kernel='gaussian')
    kde.fit(coords)

    # Score grid
    log_density = kde.score_samples(grid_points)
    density = np.exp(log_density).reshape(lon_grid.shape)

    fig, ax = plt.subplots(figsize=(14, 10))

    # Plot density
    contour = ax.contourf(lon_grid, lat_grid, density, levels=20, cmap='YlOrRd', alpha=0.7)
    plt.colorbar(contour, ax=ax, label='Density')

    # Overlay points
    ax.scatter(recent_data['lon'], recent_data['lat'],
              alpha=0.1, s=1, color='black')

    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    ax.set_title('Overdose Death Hotspots (Kernel Density Estimation)\nLos Angeles County 2020-2023',
                fontsize=14, fontweight='bold')
    ax.set_aspect('equal')

    plt.tight_layout()
    plt.savefig('results/08_geospatial_statistics/kde_hotspots.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: kde_hotspots.png")

    # === 7. DBSCAN Clustering ===
    print("Performing DBSCAN clustering...")

    # Use recent data
    coords_recent = np.c_[recent_data['lat'], recent_data['lon']]

    # DBSCAN (eps in degrees, roughly 0.01 degree ≈ 1km at LA latitude)
    db = DBSCAN(eps=0.015, min_samples=10)
    clusters = db.fit_predict(coords_recent)

    n_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
    n_noise = list(clusters).count(-1)

    print(f"Found {n_clusters} clusters with {n_noise} noise points")

    fig, ax = plt.subplots(figsize=(14, 10))

    # Plot clusters
    unique_labels = set(clusters)
    colors_cluster = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))

    for k, col in zip(unique_labels, colors_cluster):
        if k == -1:
            # Noise points
            col = [0.5, 0.5, 0.5, 0.3]
            marker_size = 1
        else:
            marker_size = 10

        class_member_mask = (clusters == k)
        xy = coords_recent[class_member_mask]
        ax.scatter(xy[:, 1], xy[:, 0], s=marker_size, c=[col], alpha=0.6)

    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    ax.set_title(f'DBSCAN Clustering of Overdose Deaths\nLos Angeles County 2020-2023\n({n_clusters} clusters identified)',
                fontsize=14, fontweight='bold')
    ax.set_aspect('equal')

    plt.tight_layout()
    plt.savefig('results/08_geospatial_statistics/dbscan_clusters.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: dbscan_clusters.png")

    # === 8. Directional Analysis ===
    print("Performing directional analysis...")

    # Calculate movement of center of gravity
    yearly_df['lat_change'] = yearly_df['center_lat'].diff()
    yearly_df['lon_change'] = yearly_df['center_lon'].diff()
    yearly_df['distance_moved_km'] = np.sqrt(
        (yearly_df['lat_change'] * 111)**2 +
        (yearly_df['lon_change'] * 111 * np.cos(np.radians(yearly_df['center_lat'])))**2
    )

    # Direction (bearing)
    yearly_df['direction_deg'] = np.degrees(np.arctan2(yearly_df['lon_change'], yearly_df['lat_change']))

    yearly_df.to_csv('results/08_geospatial_statistics/center_of_gravity_movement.csv', index=False)

    # Create improved directional visualization
    fig = plt.figure(figsize=(16, 6))

    # Plot 1: Cartesian trajectory with arrows (easier to understand)
    ax1 = plt.subplot(1, 2, 1)

    # Plot trajectory line
    ax1.plot(yearly_df['center_lon'], yearly_df['center_lat'],
            linewidth=2, color='#ED0000', alpha=0.7, zorder=2)

    # Plot points with year labels
    for idx, row in yearly_df.iterrows():
        ax1.scatter(row['center_lon'], row['center_lat'],
                   s=200, c=row['Year'], cmap='coolwarm', vmin=2012, vmax=2024,
                   edgecolors='black', linewidth=2, zorder=3)
        ax1.annotate(f"{row['Year']:.0f}",
                    (row['center_lon'], row['center_lat']),
                    xytext=(8, 8), textcoords='offset points',
                    fontsize=9, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

    # Add arrows between points
    for i in range(len(yearly_df)-1):
        if yearly_df['distance_moved_km'].iloc[i+1] > 0:
            ax1.annotate('',
                        xy=(yearly_df['center_lon'].iloc[i+1], yearly_df['center_lat'].iloc[i+1]),
                        xytext=(yearly_df['center_lon'].iloc[i], yearly_df['center_lat'].iloc[i]),
                        arrowprops=dict(arrowstyle='->', lw=2, color='black', alpha=0.5))

    # Add compass rose
    compass_lon = yearly_df['center_lon'].min() + 0.001
    compass_lat = yearly_df['center_lat'].max() - 0.002
    arrow_length = 0.003
    ax1.annotate('N', xy=(compass_lon, compass_lat + arrow_length),
                xytext=(compass_lon, compass_lat),
                arrowprops=dict(arrowstyle='->', lw=3, color='blue'),
                fontsize=14, fontweight='bold', ha='center')

    ax1.set_xlabel('Longitude (degrees)', fontsize=12)
    ax1.set_ylabel('Latitude (degrees)', fontsize=12)
    ax1.set_title('Year-by-Year Movement of Overdose Center of Gravity\nLos Angeles County 2012-2023',
                 fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal')

    # Plot 2: Improved polar plot with clear labels
    ax2 = plt.subplot(1, 2, 2, projection='polar')

    # Prepare data
    years_moved = yearly_df['Year'].dropna()[1:].values
    distances = yearly_df['distance_moved_km'].dropna().values
    directions_rad = np.radians(yearly_df['direction_deg'].dropna().values)

    # Plot with year labels
    scatter = ax2.scatter(directions_rad, distances,
                         s=200, c=years_moved, cmap='coolwarm',
                         vmin=2012, vmax=2024,
                         edgecolors='black', linewidth=2, alpha=0.9, zorder=5)

    # Add year labels
    for angle, dist, year in zip(directions_rad, distances, years_moved):
        ax2.annotate(f"{year:.0f}",
                    (angle, dist),
                    xytext=(0, 5), textcoords='offset points',
                    fontsize=8, ha='center', fontweight='bold')

    # Set up compass
    ax2.set_theta_zero_location('N')
    ax2.set_theta_direction(-1)

    # Add cardinal direction labels
    ax2.text(0, ax2.get_ylim()[1]*1.15, 'NORTH', ha='center', fontsize=12, fontweight='bold')
    ax2.text(np.pi/2, ax2.get_ylim()[1]*1.15, 'EAST', ha='center', fontsize=12, fontweight='bold')
    ax2.text(np.pi, ax2.get_ylim()[1]*1.15, 'SOUTH', ha='center', fontsize=12, fontweight='bold')
    ax2.text(3*np.pi/2, ax2.get_ylim()[1]*1.15, 'WEST', ha='center', fontsize=12, fontweight='bold')

    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax2, pad=0.1)
    cbar.set_label('Year', fontsize=11)

    ax2.set_title('Distance & Direction Each Year Moved\n(Distance from center = km moved that year)',
                 fontsize=13, fontweight='bold', pad=30)

    plt.tight_layout()
    plt.savefig('results/08_geospatial_statistics/directional_analysis_improved.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: directional_analysis_improved.png")

    # === 9. Simple Bar Chart of Movement ===
    print("Creating simple movement summary...")

    # Filter to years with movement data
    movement_data = yearly_df[yearly_df['distance_moved_km'].notna()].copy()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Bar chart of distance moved
    ax1.bar(movement_data['Year'], movement_data['distance_moved_km'],
           color='#ED0000', alpha=0.7, edgecolor='black')
    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('Distance Moved (km)', fontsize=12)
    ax1.set_title('How Far the Center Moved Each Year', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.axhline(y=movement_data['distance_moved_km'].mean(), color='blue',
               linestyle='--', linewidth=2, label=f"Average: {movement_data['distance_moved_km'].mean():.2f} km")
    ax1.legend(fontsize=10)

    # Categorize direction into simple categories
    def categorize_direction(deg):
        if pd.isna(deg):
            return 'Unknown'
        deg = deg % 360
        if deg < 22.5 or deg >= 337.5:
            return 'North'
        elif deg < 67.5:
            return 'Northeast'
        elif deg < 112.5:
            return 'East'
        elif deg < 157.5:
            return 'Southeast'
        elif deg < 202.5:
            return 'South'
        elif deg < 247.5:
            return 'Southwest'
        elif deg < 292.5:
            return 'West'
        else:
            return 'Northwest'

    movement_data['Direction_Category'] = movement_data['direction_deg'].apply(categorize_direction)

    # Count by direction
    direction_counts = movement_data['Direction_Category'].value_counts()
    colors_dir = {'North': '#ED0000', 'Northeast': '#FFA500', 'East': '#FFD700',
                  'Southeast': '#90EE90', 'South': '#00CED1', 'Southwest': '#4169E1',
                  'West': '#9370DB', 'Northwest': '#FF69B4'}

    ax2.bar(range(len(direction_counts)), direction_counts.values,
           color=[colors_dir.get(x, 'gray') for x in direction_counts.index],
           alpha=0.7, edgecolor='black')
    ax2.set_xticks(range(len(direction_counts)))
    ax2.set_xticklabels(direction_counts.index, rotation=45, ha='right')
    ax2.set_ylabel('Number of Years', fontsize=12)
    ax2.set_title('Which Direction Did the Center Move?\n(Count of years moving in each direction)',
                 fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('results/08_geospatial_statistics/movement_summary_simple.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: movement_summary_simple.png")

    # Print key findings
    print("\n" + "="*60)
    print("KEY FINDINGS:")
    print("="*60)

    print(f"\n1. Overall spatial movement:")
    first_year = yearly_df.iloc[0]
    last_year = yearly_df.iloc[-1]
    total_distance = haversine_distance(
        first_year['center_lat'], first_year['center_lon'],
        last_year['center_lat'], last_year['center_lon']
    )
    print(f"   Center of gravity {first_year['Year']:.0f}: ({first_year['center_lat']:.4f}, {first_year['center_lon']:.4f})")
    print(f"   Center of gravity {last_year['Year']:.0f}: ({last_year['center_lat']:.4f}, {last_year['center_lon']:.4f})")
    print(f"   Total movement: {total_distance:.2f} km")

    print(f"\n2. Spatial dispersion:")
    print(f"   {first_year['Year']:.0f}: {first_year['std_distance_km']:.2f} km")
    print(f"   {last_year['Year']:.0f}: {last_year['std_distance_km']:.2f} km")
    print(f"   Change: {((last_year['std_distance_km'] / first_year['std_distance_km'] - 1) * 100):+.1f}%")

    print(f"\n3. Distance from downtown LA:")
    first_dist = annual_distance.iloc[0]
    last_dist = annual_distance.iloc[-1]
    print(f"   {first_dist['Year']:.0f}: {first_dist['mean']:.2f} km (median: {first_dist['median']:.2f})")
    print(f"   {last_dist['Year']:.0f}: {last_dist['mean']:.2f} km (median: {last_dist['median']:.2f})")

    print(f"\n4. Clustering analysis:")
    print(f"   DBSCAN identified {n_clusters} major clusters (2020-2023)")
    print(f"   {n_noise} isolated cases ({n_noise/len(recent_data)*100:.1f}%)")

    print(f"\n5. Substance-specific centers:")
    for _, row in substance_df.iterrows():
        dist_from_downtown = haversine_distance(
            row['center_lat'], row['center_lon'],
            DOWNTOWN_LA[0], DOWNTOWN_LA[1]
        )
        print(f"   {row['Substance']}: {dist_from_downtown:.2f} km from downtown")

    print("\n" + "="*60)
    print("Analysis complete!")

if __name__ == "__main__":
    main()
