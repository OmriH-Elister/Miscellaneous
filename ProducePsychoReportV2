#!/bin/bash

# --- User Input ---
read -p "Name?" Name
read -p "male/female?" Sex
read -p "Age?" Age

# --- File Paths ---
DATA_FILE="PsychoData_${Name}"
REPORT_FILE="$HOME/reports/psycho_analysis_${Name}.txt"
FABRIC_PATH="$(which fabric)" # Define path to fabric executable

# Ensure the reports directory exists
mkdir -p "$(dirname "$REPORT_FILE")"

# --- Data Aggregation ---
echo "Aggregating data for $Name..."
numb=1
# Create or clear the data file
> "$DATA_FILE"

for i in $(ls *.txt *.ps1 *.sh *.bat ); do
    echo -e "--- Text number $numb: ($i) ---\n" >> "$DATA_FILE"
    cat "$i" | grep -v "\n" >> "$DATA_FILE"
    echo -e "\n" >> "$DATA_FILE"
    numb=$((numb + 1))
done

# --- Report Generation ---
echo "Generating report at $REPORT_FILE..."

# 1. Add Header and Raw Data to Report
{
    echo "================================================="
    echo "        PSYCHO-ANALYSIS REPORT FOR: $Name"
    echo "================================================="
    echo "Age: $Age"
    echo "Sex: $Sex"
    echo -e "\n--- RAW DATA ---\n"
    cat "$DATA_FILE"
    echo -e "\n\n"
} > "$REPORT_FILE"

# 2. Run Analyses and Append to Report
echo "Running Personality Analysis..."
{
    echo "================================================="
    echo "              PERSONALITY ANALYSIS"
    echo "================================================="
    cat "$DATA_FILE" | grep -v "\n" | "$FABRIC_PATH" -sp analyze_personality -g en
    echo -e "\n\n"
} >> "$REPORT_FILE"

echo "Describing Life Outlook..."
{
    echo "================================================="
    echo "                 LIFE OUTLOOK"
    echo "================================================="
    cat "$DATA_FILE" |grep -v "\n" | "$FABRIC_PATH" -sp t_describe_life_outlook -g en
    echo -e "\n\n"
} >> "$REPORT_FILE"

echo "Extracting Key Insights..."
{
    echo "================================================="
    echo "             KEY INSIGHTS & THEMES"
    echo "================================================="
    cat "$DATA_FILE" |grep -v "\n"| "$FABRIC_PATH" -sp extract_insights -g en
    echo -e "\n\n"
} >> "$REPORT_FILE"

echo "Analyzing Writing Style..."
{
    echo "================================================="
    echo "             WRITING STYLE ANALYSIS"
    echo "================================================="
    cat "$DATA_FILE" |grep -v "\n"| "$FABRIC_PATH" -sp analyze_prose_pinker -m gemini-2.5-pro -g en
    echo -e "\n\n"
} >> "$REPORT_FILE"


# --- Cleanup ---
rm "$DATA_FILE" # Uncomment to delete the intermediate data file

echo "Report generation complete."
echo "Report is saved in $REPORT_FILE"
