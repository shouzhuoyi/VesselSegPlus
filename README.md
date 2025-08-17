# VesselSeg+

## Overview
The VesselSeg+ project is designed to process medical images and evaluate the performance of various models in measuring anatomical structures. The project includes scripts for image processing, model evaluation, and summarizing results, making it a comprehensive tool for analyzing vascular measurements.

## File Structure
```
VesselSeg+
├── 3VV-agent/
│   ├── agent_main.py      # Main script for the agent
│   ├── main_app.py        # Main application script for the Gradio interface
│   ├── chatbot.py         # Handles chatbot functionalities
│   ├── plugin/
│   │   ├── analyzer.py    # Analyzes medical images
│   │   └── utils/         # Utility scripts for segmentation, measurement, etc.
│   └── checkpoints/       # Contains pre-trained model checkpoints
├── src/
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
   git clone https://github.com/shouzhuoyi/VesselSeg_Plus#
   cd VesselSeg+
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration
Before running the scripts, ensure that the `config.yaml` file is properly configured with the correct paths for your input images, output directories, and model files.

## Usage
### Image Segmentation
Download and configure [nnUNet](https://github.com/MIC-DKFZ/nnUNet).
### Biometric Measurement
To process images and measure diameters, run the `biometric.py` script:
```
python src/biometric.py
```
This script will read images from the specified input folder, measure the diameters of anatomical structures, and save the results in both CSV and JSON formats.

#### Model Evaluation
To evaluate model performance, use the `evaluate.py` script:
```
python src/evaluate.py
```
This script will load measurements from CSV files, calculate errors, and save the evaluation results in JSON format.

#### Summary Calculation
To calculate global averages from the evaluation results, execute the `summary.py` script:
```
python src/summary.py
```
This script will compute averages while ignoring outliers and save the summarized results back to JSON files.

### Use the 3VV agent

The 3VV agent is an intelligent component that uses a large language model (LLM) to analyze medical images and generate diagnostic reports. It requires a backend analysis service to be running.

#### Step 1: Start the Analysis Plugin Service

First, you need to start the backend plugin service, which handles the core image processing tasks. This service runs as a Flask web server.

Open a terminal and run the following command:
```bash
python 3VV-agent/plugin/app.py
```
This will start the service, typically listening on `http://localhost:5000`. Keep this terminal running.

#### Step 2: Run the Agent Interface

With the service running, you can now use one of the agent interfaces to interact with the system. Open a **new terminal** for this step.

There are three different interfaces available:

**Option A: Simple Agent (`agent_main.py`)**

This is a non-interactive script that analyzes a default image specified in `config.yaml` and prints a generated report.

```bash
python 3VV-agent/agent_main.py
```

**Option B: Interactive Command-Line App (`main_app.py`)**

This provides an interactive command-line application for analyzing images and generating reports on demand.

```bash
python 3VV-agent/main_app.py
```
Once started, you can use the following commands:
- `analyze <path_to_your_image.png>`: Analyzes a specific image.
- `report`: Generates a report based on the last analysis.
- `report <path_to_your_image.png>`: Analyzes and generates a report in one step.
- `quit`: Exits the application.

**Option C: Interactive Chatbot (`chatbot.py`)**

This provides a conversational interface where you can interact with the agent using natural language.

```bash
python 3VV-agent/chatbot.py
```
You can then chat with the bot, for example:
- "Please analyze the image at D:/path/to/my/image.png"
- "Generate a report for me."

**Note:** The agent relies on a large language model provided by Ollama. Ensure that you have Ollama installed and running, and that the model specified in `config.yaml` (e.g., `llama3:instruct`) is available.

## Contribution
Contributions to the project are welcome. Please submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for details.