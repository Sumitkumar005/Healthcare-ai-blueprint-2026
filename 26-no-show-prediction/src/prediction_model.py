"""
ML model for no-show prediction
"""
import logging
from typing import Dict, Optional
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pickle
import os

logger = logging.getLogger(__name__)


class NoShowPredictor:
    """Predicts no-show risk for appointments"""
    
    def __init__(self):
        """Initialize the predictor"""
        self.model = None
        self.label_encoders = {}
        self.is_trained = False
    
    def train_model(self, df: pd.DataFrame):
        """Train the prediction model"""
        try:
            # Prepare features
            df['day_of_week'] = pd.to_datetime(df['appointment_date']).dt.day_name()
            df['hour'] = pd.to_datetime(df.get('time_of_day', '12:00')).dt.hour if 'time_of_day' in df.columns else 12
            
            # Feature engineering
            features = ['appointment_type', 'day_of_week', 'hour', 'lead_time_days']
            
            # Encode categorical variables
            X = df[features].copy()
            for col in ['appointment_type', 'day_of_week']:
                if col in X.columns:
                    le = LabelEncoder()
                    X[col] = le.fit_transform(X[col].astype(str))
                    self.label_encoders[col] = le
            
            y = df['no_show'].astype(int)
            
            # Train model
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)
            
            # Calculate accuracy
            accuracy = self.model.score(X_test, y_test)
            logger.info(f"Model trained with accuracy: {accuracy:.2%}")
            
            self.is_trained = True
            
            # Save model
            with open('no_show_model.pkl', 'wb') as f:
                pickle.dump(self.model, f)
        except Exception as e:
            logger.error(f"Error training model: {e}")
            # Use simple heuristic if training fails
            self.is_trained = False
    
    def predict(
        self,
        appointment_type: str,
        day_of_week: str,
        time_of_day: str,
        lead_time_days: int,
        patient_history: Dict
    ) -> float:
        """
        Predict no-show risk (0-1)
        
        Returns:
            Risk score between 0 and 1
        """
        if not self.is_trained or self.model is None:
            # Fallback heuristic
            return self._heuristic_prediction(
                appointment_type, day_of_week, time_of_day, lead_time_days, patient_history
            )
        
        try:
            # Prepare features
            features = {
                'appointment_type': appointment_type,
                'day_of_week': day_of_week,
                'hour': int(time_of_day.split(':')[0]) if ':' in time_of_day else 12,
                'lead_time_days': lead_time_days
            }
            
            # Encode
            X = pd.DataFrame([features])
            for col in ['appointment_type', 'day_of_week']:
                if col in self.label_encoders:
                    X[col] = self.label_encoders[col].transform([features[col]])[0]
            
            # Predict probability
            prob = self.model.predict_proba(X)[0][1]  # Probability of no-show
            return float(prob)
        except Exception as e:
            logger.warning(f"Prediction error: {e}, using heuristic")
            return self._heuristic_prediction(
                appointment_type, day_of_week, time_of_day, lead_time_days, patient_history
            )
    
    def _heuristic_prediction(
        self,
        appointment_type: str,
        day_of_week: str,
        time_of_day: str,
        lead_time_days: int,
        patient_history: Dict
    ) -> float:
        """Simple heuristic-based prediction"""
        risk = 0.3  # Base risk
        
        # Adjust based on factors
        if lead_time_days > 14:
            risk += 0.2
        if lead_time_days > 30:
            risk += 0.1
        
        # Day of week
        if day_of_week in ['Monday', 'Friday']:
            risk += 0.1
        
        # Time of day
        hour = int(time_of_day.split(':')[0]) if ':' in time_of_day else 12
        if hour < 9 or hour > 17:
            risk += 0.1
        
        # Patient history
        if patient_history.get('previous_no_shows', 0) > 0:
            risk += 0.2
        if patient_history.get('previous_no_shows', 0) > 2:
            risk += 0.1
        
        return min(risk, 0.95)  # Cap at 95%



