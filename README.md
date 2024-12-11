# RCPY Chatbot Project for NLP

This project was created for the course NLP at Reutlingen University.

## Setup

To set up the project environment, follow these steps:

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Install Dependencies

You can set up the environment using either Conda or Pip:

#### Option 1: Using Conda (`conda_env.yml`)
```
# Create the environment using the conda_env.yml file
conda env create -f conda_env.yml

# Activate the environment
conda activate <environment-name>

# Verify the installation
conda list
```

#### Option 2: Using `requirements.txt` (Pip)
```
# (Optional) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate    # On Linux/Mac
venv\Scripts\activate       # On Windows

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Verify the installation
pip list
```

### Notes
- **Option 1 (Conda)**: Use this if you want the exact environment configuration, including Conda-specific dependencies.
- **Option 2 (Pip)**: Use this if you prefer using Pip or do not have Conda installed.

### 3. Configure Environment Variables

Copy the provided `sample.env` file to `.env`:

```
cp sample.env .env
```

Open the `.env` file in your favorite text editor and fill in the missing values as needed. Ensure all required fields are completed before running the application.

<!-- TODO: Write the rest -->