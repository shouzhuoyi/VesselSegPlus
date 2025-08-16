# 3VV Evaluation Project

## Overview
The 3VV Evaluation project is designed to process medical images and evaluate the performance of various models in measuring anatomical structures. The project includes scripts for image processing, model evaluation, and summarizing results, making it a comprehensive tool for analyzing vascular measurements.

## File Structure
```
3vv-evaluation
├── src
│   ├── biometric.py       # Processes images to measure diameters of anatomical structures
│   ├── evaluate.py        # Evaluates model performance by comparing expert annotations with model predictions
│   └── summary.py         # Calculates global averages from evaluation results
├── config.yaml            # Configuration settings for input/output paths and model file mappings
├── requirements.txt       # Lists Python dependencies required for the project
└── README.md              # Documentation for the project
```

## Installation
To set up the project, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd 3vv-evaluation
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration
Before running the scripts, ensure that the `config.yaml` file is properly configured with the correct paths for your input images, output directories, and model files.

## Usage
### Image Processing
To process images and measure diameters, run the `biometric.py` script:
```
python src/biometric.py
```
This script will read images from the specified input folder, measure the diameters of anatomical structures, and save the results in both CSV and JSON formats.

### Model Evaluation
To evaluate model performance, use the `evaluate.py` script:
```
python src/evaluate.py
```
This script will load measurements from CSV files, calculate errors, and save the evaluation results in JSON format.

### Summary Calculation
To calculate global averages from the evaluation results, execute the `summary.py` script:
```
python src/summary.py
```
This script will compute averages while ignoring outliers and save the summarized results back to JSON files.

## Contribution
Contributions to the project are welcome. Please submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for details.