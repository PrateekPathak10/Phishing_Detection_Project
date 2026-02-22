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


# NOTE: The data must be generated with the new features before running this.
DATA_FILE = '3_class_training_data.csv' 
MODEL_FILENAME = 'final_phishing_model_pipeline.joblib'
MODEL_SAVE_PATH = 'model/'
TARGET_LABEL = 'Label'


try:
    df = pd.read_csv(DATA_FILE)
    print(f"Data loaded successfully from {DATA_FILE}. Total rows: {len(df)}")
except FileNotFoundError:
    print(f"\nFATAL ERROR: Training data not found. Please ensure {DATA_FILE} is in the same directory.")

    exit()


numerical_features = [
    'Levenshtein_Ratio', 
    'Length_Difference', 
  
    'URL_Length',
    'Num_Slashes',
    'Num_Underscores',
    'Num_Question_Marks',
    'Num_Equal_Signs',
    'Special_Chars_Count',
    'Path_Length',
    'Has_Query',
    'Num_Subdomains',
    'Domain_Length',
    'Num_Dots',
    'Num_Hyphens',
    
    'Domain_Age_Days'
]

categorical_features = ['Critical Sector Entity Name'] 


missing_features = [f for f in numerical_features if f not in df.columns]
if missing_features:
    print(f"\nFATAL ERROR: Missing features in {DATA_FILE}: {missing_features}")
    print("Please re-run the feature engineering/data prep notebook!")
    exit()


X = df[numerical_features + categorical_features]
y = df[TARGET_LABEL]

# Split data (necessary for GridSearchCV which uses cross-validation)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)


preprocessor = ColumnTransformer(
    transformers=[
        ('num', 'passthrough', numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
    ],
    remainder='drop' 
)


model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(random_state=42))
])


param_grid = {
    'classifier__n_estimators': [100], 
    'classifier__max_depth': [20],      
    'classifier__min_samples_leaf': [5]   
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


final_model_pipeline = grid_search.best_estimator_


os.makedirs(MODEL_SAVE_PATH, exist_ok=True)
full_path = os.path.join(MODEL_SAVE_PATH, MODEL_FILENAME)

joblib.dump(final_model_pipeline, full_path)

print("\n--- Model Creation Complete ---")
print(f"File created successfully: {full_path}")