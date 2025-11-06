"""
Combine Analysis READMEs

Creates a comprehensive master document by combining all individual analysis
README files into a single reference document.
"""

import re
from pathlib import Path
from datetime import datetime

# Paths
RESULTS_DIR = Path('results')
OUTPUT_FILE = RESULTS_DIR / 'ANALYSIS_SUMMARIES.md'

def extract_title(readme_content):
    """Extract the title from README content"""
    lines = readme_content.split('\n')
    for line in lines:
        if line.startswith('# ') and not line.startswith('## '):
            return line.replace('# ', '').strip()
    return "Unknown"

def get_analysis_number(folder_name):
    """Extract analysis number from folder name"""
    match = re.match(r'^(\d+)_', folder_name)
    if match:
        return int(match.group(1))
    return 999  # Put non-numbered at end

def main():
    print("="*70)
    print("Combining Analysis READMEs")
    print("="*70)

    # Find all analysis directories with README files
    analysis_dirs = []
    for path in sorted(RESULTS_DIR.iterdir()):
        if path.is_dir() and re.match(r'^\d+_', path.name):
            readme_path = path / 'README.md'
            if readme_path.exists():
                analysis_dirs.append({
                    'path': path,
                    'readme': readme_path,
                    'number': get_analysis_number(path.name),
                    'folder': path.name
                })

    # Sort by analysis number
    analysis_dirs.sort(key=lambda x: x['number'])

    print(f"\nFound {len(analysis_dirs)} analyses with README files")

    # Start building the master document
    master_content = []

    # Header
    master_content.append("# LA County Overdose Crisis: Complete Analysis Summaries")
    master_content.append("")
    master_content.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    master_content.append(f"**Total Analyses**: {len(analysis_dirs)}")
    master_content.append("")
    master_content.append("This document combines all individual analysis README files into a single comprehensive reference.")
    master_content.append("")

    # Table of Contents
    master_content.append("---")
    master_content.append("")
    master_content.append("## Table of Contents")
    master_content.append("")

    # Build TOC
    for analysis in analysis_dirs:
        readme_content = analysis['readme'].read_text()
        title = extract_title(readme_content)
        num = analysis['number']
        master_content.append(f"- [Analysis {num:02d}: {title}](#analysis-{num:02d}-{title.lower().replace(' ', '-').replace('(', '').replace(')', '').replace(',', '').replace(':', '')})")

    master_content.append("")
    master_content.append("---")
    master_content.append("")

    # Add each analysis
    for i, analysis in enumerate(analysis_dirs):
        print(f"  Processing: {analysis['folder']}")

        readme_content = analysis['readme'].read_text()

        # Add analysis header
        master_content.append(f"## Analysis {analysis['number']:02d}")
        master_content.append("")

        # Add the README content (skip the first H1 title since we have our own)
        lines = readme_content.split('\n')
        skip_first_h1 = False
        for line in lines:
            if line.startswith('# ') and not skip_first_h1:
                skip_first_h1 = True
                continue
            master_content.append(line)

        # Add separator between analyses (except last one)
        if i < len(analysis_dirs) - 1:
            master_content.append("")
            master_content.append("---")
            master_content.append("")
            master_content.append("<div style='page-break-after: always;'></div>")
            master_content.append("")
            master_content.append("---")
            master_content.append("")

    # Add footer
    master_content.append("")
    master_content.append("---")
    master_content.append("")
    master_content.append("## Document Information")
    master_content.append("")
    master_content.append(f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    master_content.append(f"- **Source**: Individual README files from {len(analysis_dirs)} analyses")
    master_content.append("- **Script**: `scripts/combine_analysis_readmes.py`")
    master_content.append("")
    master_content.append("### Analysis Categories")
    master_content.append("")
    master_content.append("**Foundation (00-05)**: Descriptive statistics, fentanyl timeline, demographics, homelessness, geography")
    master_content.append("**Temporal (06-07)**: Seasonal patterns, COVID impact")
    master_content.append("**Geospatial (08)**: Advanced spatial statistics")
    master_content.append("**Race-Substance (09-10)**: Interaction trends, age-race patterns")
    master_content.append("**SES Context (11-17)**: Population rates, SES context, correlations, YPLL, disparities")
    master_content.append("**Advanced SES (18-27)**: Census-based detailed SES analyses")
    master_content.append("**Economic Context (28-35)**: FRED-based economic analyses")
    master_content.append("")

    # Write the master file
    OUTPUT_FILE.write_text('\n'.join(master_content))

    print(f"\n✓ Created master document: {OUTPUT_FILE}")
    print(f"  Total lines: {len(master_content):,}")
    print(f"  File size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")

    # Also create a summary table
    summary_content = []
    summary_content.append("# Analysis Summary Table")
    summary_content.append("")
    summary_content.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d')}")
    summary_content.append("")
    summary_content.append("| # | Analysis | Status | Key Finding/Correlation |")
    summary_content.append("|---|----------|--------|------------------------|")

    for analysis in analysis_dirs:
        readme_content = analysis['readme'].read_text()
        title = extract_title(readme_content)

        # Try to extract status
        status = "✅ Verified" if "✅ Verified" in readme_content else "📊 Complete"

        # Try to extract key correlation or finding
        key_finding = ""
        if "r = " in readme_content or "r=" in readme_content:
            # Extract correlation
            match = re.search(r'r\s*=\s*([-\d.]+)', readme_content)
            if match:
                key_finding = f"r={match.group(1)}"
        elif "⭐" in readme_content:
            key_finding = "⭐ Significant"

        summary_content.append(f"| {analysis['number']:02d} | {title} | {status} | {key_finding} |")

    summary_content.append("")

    summary_file = RESULTS_DIR / 'ANALYSIS_TABLE.md'
    summary_file.write_text('\n'.join(summary_content))
    print(f"✓ Created summary table: {summary_file}")

    print("\n" + "="*70)
    print("Complete!")
    print("="*70)
    print(f"\nMaster document: {OUTPUT_FILE}")
    print(f"Summary table: {summary_file}")
    print(f"\nTotal analyses documented: {len(analysis_dirs)}")

if __name__ == '__main__':
    main()
