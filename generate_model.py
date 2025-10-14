import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import os
import warnings

# Suppress harmless warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# --- Configuration ---
DATA_FILE = '3_class_training_data.csv'
MODEL_FILENAME = 'final_phishing_model_pipeline.joblib'
MODEL_SAVE_PATH = 'model/' # Assuming a subdirectory named 'model'
TARGET_LABEL = 'Label'

# --- 1. Load Data ---
try:
    df = pd.read_csv(DATA_FILE)
    print(f"Data loaded successfully from {DATA_FILE}. Total rows: {len(df)}")
except FileNotFoundError:
    print(f"\nFATAL ERROR: Training data not found. Please ensure {DATA_FILE} is in the same directory.")
    exit()

# --- 2. Define Features and Target ---
numerical_features = ['Levenshtein_Ratio', 'Length_Difference', 'Domain_Length', 'Num_Dots', 'Num_Hyphens']
categorical_features = ['Critical Sector Entity Name'] 

X = df[numerical_features + categorical_features]
y = df[TARGET_LABEL]

# Split data (necessary for GridSearchCV which uses cross-validation)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

# --- 3. Create Preprocessor and Pipeline ---
preprocessor = ColumnTransformer(
    transformers=[
        ('num', 'passthrough', numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
    ],
    remainder='drop' 
)

# Define the base model pipeline
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(random_state=42))
])

# --- 4. Hyperparameter Tuning (Re-running the best fit from our analysis) ---
# We use a limited grid search here to confirm the model structure and save the best one.
param_grid = {
    'classifier__n_estimators': [100],  # Best value found previously
    'classifier__max_depth': [20],      # Best value found previously
    'classifier__min_samples_leaf': [5]   # Best value found previously
}

grid_search = GridSearchCV(
    model, 
    param_grid, 
    cv=3, 
    scoring='precision_macro',
    verbose=0, 
    n_jobs=-1 
)

print("Starting model training and hyperparameter optimization...")
grid_search.fit(X_train, y_train)

# Get the final tuned model
final_model_pipeline = grid_search.best_estimator_

# --- 5. Save the Final Model Pipeline ---
# Ensure the directory exists
os.makedirs(MODEL_SAVE_PATH, exist_ok=True)
full_path = os.path.join(MODEL_SAVE_PATH, MODEL_FILENAME)

joblib.dump(final_model_pipeline, full_path)

print("\n--- Model Creation Complete ---")
print(f"Best Hyperparameters: {grid_search.best_params_}")
print(f"File created successfully: {full_path}")
print("Your API server (app.py) is now ready to run.")