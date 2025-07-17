"""
AI Model Optimization System using Optuna
Hyperparameter tuning and model optimization for Claude Desktop AI
"""

import optuna
import numpy as np
import pandas as pd
import sqlite3
from typing import Dict, List, Tuple, Optional, Any
import json
import logging
from datetime import datetime, timedelta
import threading
import time
import pickle
import os
from dataclasses import dataclass
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OptimizationResult:
    """Result container for optimization runs"""
    study_name: str
    best_params: Dict[str, Any]
    best_value: float
    n_trials: int
    optimization_time: float
    timestamp: datetime
    model_type: str

class ModelOptimizer:
    """Main class for AI model optimization using Optuna"""
    
    def __init__(self, db_path: str = "conversations.db"):
        self.db_path = db_path
        self.studies = {}
        self.optimization_results = []
        self.init_optimization_db()
        self.init_conversation_db()  # Initialize conversation tables if they don't exist
        
    def init_optimization_db(self):
        """Initialize database tables for optimization tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Optimization studies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_studies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                study_name TEXT UNIQUE NOT NULL,
                model_type TEXT NOT NULL,
                objective_direction TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Optimization trials table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_trials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                study_id INTEGER,
                trial_number INTEGER,
                params TEXT NOT NULL,
                value REAL,
                state TEXT,
                duration REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (study_id) REFERENCES optimization_studies (id)
            )
        ''')
        
        # Best parameters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS best_parameters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                study_name TEXT NOT NULL,
                model_type TEXT NOT NULL,
                parameters TEXT NOT NULL,
                performance_score REAL NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def init_conversation_db(self):
        """Initialize conversation database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                title TEXT,
                summary TEXT,
                total_messages INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                duration_minutes REAL DEFAULT 0,
                quality_score REAL DEFAULT 0
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                tokens INTEGER DEFAULT 0,
                response_time REAL DEFAULT 0,
                quality_score REAL DEFAULT 0,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_study_info(self, study_name: str, model_type: str, direction: str):
        """Save study information to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO optimization_studies 
            (study_name, model_type, objective_direction)
            VALUES (?, ?, ?)
        ''', (study_name, model_type, direction))
        
        conn.commit()
        conn.close()
    
    def trial_callback(self, study: optuna.Study, trial: optuna.Trial):
        """Callback function called after each trial"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get study ID
        cursor.execute('SELECT id FROM optimization_studies WHERE study_name = ?', (study.study_name,))
        study_id = cursor.fetchone()[0]
        
        # Save trial information
        cursor.execute('''
            INSERT INTO optimization_trials 
            (study_id, trial_number, params, value, state, duration)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            study_id,
            trial.number,
            json.dumps(trial.params),
            trial.value,
            trial.state.name,
            trial.duration.total_seconds() if trial.duration else None
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Trial {trial.number}: {trial.value:.4f} - {trial.params}")
    
    def save_optimization_result(self, result: OptimizationResult):
        """Save optimization result to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO best_parameters 
            (study_name, model_type, parameters, performance_score)
            VALUES (?, ?, ?, ?)
        ''', (
            result.study_name,
            result.model_type,
            json.dumps(result.best_params),
            result.best_value
        ))
        
        conn.commit()
        conn.close()

class ConversationQualityOptimizer(ModelOptimizer):
    """Optimizer for conversation quality prediction models"""
    
    def __init__(self, db_path: str = "conversations.db"):
        super().__init__(db_path)
        self.model_type = "conversation_quality"
        
    def prepare_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data from conversation database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get conversation data with quality scores
        cursor.execute('''
            SELECT 
                c.total_messages,
                c.total_tokens,
                c.duration_minutes,
                c.quality_score,
                AVG(m.response_time) as avg_response_time,
                AVG(m.quality_score) as avg_message_quality
            FROM conversations c
            JOIN messages m ON c.id = m.conversation_id
            WHERE c.quality_score IS NOT NULL
            GROUP BY c.id
        ''')
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            # Generate synthetic data for demonstration
            np.random.seed(42)
            n_samples = 1000
            data = []
            for _ in range(n_samples):
                total_messages = np.random.randint(5, 50)
                total_tokens = np.random.randint(100, 5000)
                duration_minutes = np.random.uniform(1, 60)
                avg_response_time = np.random.uniform(0.5, 5.0)
                avg_message_quality = np.random.uniform(0.3, 1.0)
                
                # Synthetic quality score based on features
                quality_score = (
                    0.3 * min(total_messages / 20, 1.0) +
                    0.2 * min(total_tokens / 2000, 1.0) +
                    0.2 * (1 - min(duration_minutes / 30, 1.0)) +
                    0.1 * (1 - min(avg_response_time / 3, 1.0)) +
                    0.2 * avg_message_quality
                ) + np.random.normal(0, 0.1)
                quality_score = max(0, min(1, quality_score))
                
                data.append([total_messages, total_tokens, duration_minutes, quality_score, avg_response_time, avg_message_quality])
        
        # Convert to numpy arrays
        data = np.array(data)
        X = data[:, [0, 1, 2, 4, 5]]  # Features: messages, tokens, duration, response_time, message_quality
        y = data[:, 3]  # Target: quality_score
        
        return X, y
    
    def objective_function(self, trial: optuna.Trial, X: np.ndarray, y: np.ndarray) -> float:
        """Objective function for conversation quality optimization"""
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.model_selection import cross_val_score
        
        # Suggest hyperparameters
        n_estimators = trial.suggest_int('n_estimators', 50, 300)
        max_depth = trial.suggest_int('max_depth', 3, 15)
        min_samples_split = trial.suggest_int('min_samples_split', 2, 20)
        min_samples_leaf = trial.suggest_int('min_samples_leaf', 1, 10)
        max_features = trial.suggest_categorical('max_features', ['sqrt', 'log2'])
        
        # Create model with suggested parameters
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            max_features=max_features,
            random_state=42
        )
        
        # Evaluate using cross-validation
        scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_squared_error')
        return -scores.mean()  # Return negative MSE (higher is better)
    
    def optimize_model(self, n_trials: int = 100) -> OptimizationResult:
        """Optimize conversation quality model"""
        logger.info(f"Starting optimization for {self.model_type} model with {n_trials} trials")
        
        # Prepare data
        X, y = self.prepare_training_data()
        logger.info(f"Prepared training data: {X.shape[0]} samples, {X.shape[1]} features")
        
        # Create study
        study_name = f"{self.model_type}_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        study = optuna.create_study(
            direction='minimize',
            study_name=study_name,
            storage=f'sqlite:///{self.db_path}',
            load_if_exists=True
        )
        
        # Store study
        self.studies[study_name] = study
        
        # Save study info to database
        self.save_study_info(study_name, self.model_type, 'minimize')
        
        # Start optimization
        start_time = time.time()
        study.optimize(
            lambda trial: self.objective_function(trial, X, y),
            n_trials=n_trials,
            callbacks=[self.trial_callback]
        )
        optimization_time = time.time() - start_time
        
        # Create result
        result = OptimizationResult(
            study_name=study_name,
            best_params=study.best_params,
            best_value=study.best_value,
            n_trials=len(study.trials),
            optimization_time=optimization_time,
            timestamp=datetime.now(),
            model_type=self.model_type
        )
        
        # Save results
        self.save_optimization_result(result)
        self.optimization_results.append(result)
        
        logger.info(f"Optimization completed. Best value: {result.best_value:.4f}")
        logger.info(f"Best parameters: {result.best_params}")
        
        return result

class ResponseTimeOptimizer(ModelOptimizer):
    """Optimizer for response time prediction models"""
    
    def __init__(self, db_path: str = "conversations.db"):
        super().__init__(db_path)
        self.model_type = "response_time"
    
    def prepare_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for response time prediction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                LENGTH(content) as message_length,
                tokens,
                response_time
            FROM messages 
            WHERE response_time > 0 AND role = 'user'
        ''')
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            # Generate synthetic data
            np.random.seed(42)
            n_samples = 1000
            data = []
            for _ in range(n_samples):
                message_length = np.random.randint(10, 1000)
                tokens = np.random.randint(5, 200)
                
                # Response time based on message complexity
                base_time = 0.5 + (message_length / 1000) * 2 + (tokens / 200) * 1.5
                response_time = base_time + np.random.normal(0, 0.2)
                response_time = max(0.1, response_time)
                
                data.append([message_length, tokens, response_time])
        
        data = np.array(data)
        X = data[:, [0, 1]]  # Features: message_length, tokens
        y = data[:, 2]  # Target: response_time
        
        return X, y
    
    def objective_function(self, trial: optuna.Trial, X: np.ndarray, y: np.ndarray) -> float:
        """Objective function for response time optimization"""
        from sklearn.ensemble import GradientBoostingRegressor
        from sklearn.model_selection import cross_val_score
        
        # Suggest hyperparameters
        n_estimators = trial.suggest_int('n_estimators', 50, 200)
        max_depth = trial.suggest_int('max_depth', 3, 10)
        learning_rate = trial.suggest_float('learning_rate', 0.01, 0.3)
        subsample = trial.suggest_float('subsample', 0.6, 1.0)
        
        # Create model
        model = GradientBoostingRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=subsample,
            random_state=42
        )
        
        # Evaluate using cross-validation
        scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_squared_error')
        return -scores.mean()
    
    def optimize_model(self, n_trials: int = 100) -> OptimizationResult:
        """Optimize response time model"""
        logger.info(f"Starting optimization for {self.model_type} model")
        
        X, y = self.prepare_training_data()
        logger.info(f"Prepared training data: {X.shape[0]} samples")
        
        study_name = f"{self.model_type}_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        study = optuna.create_study(
            direction='minimize',
            study_name=study_name,
            storage=f'sqlite:///{self.db_path}',
            load_if_exists=True
        )
        
        self.studies[study_name] = study
        self.save_study_info(study_name, self.model_type, 'minimize')
        
        start_time = time.time()
        study.optimize(
            lambda trial: self.objective_function(trial, X, y),
            n_trials=n_trials,
            callbacks=[self.trial_callback]
        )
        optimization_time = time.time() - start_time
        
        result = OptimizationResult(
            study_name=study_name,
            best_params=study.best_params,
            best_value=study.best_value,
            n_trials=len(study.trials),
            optimization_time=optimization_time,
            timestamp=datetime.now(),
            model_type=self.model_type
        )
        
        self.save_optimization_result(result)
        self.optimization_results.append(result)
        
        logger.info(f"Response time optimization completed. Best MSE: {result.best_value:.4f}")
        
        return result

class OptimizationManager:
    """Manager for coordinating multiple optimization tasks"""
    
    def __init__(self, db_path: str = "conversations.db"):
        self.db_path = db_path
        self.optimizers = {
            'conversation_quality': ConversationQualityOptimizer(db_path),
            'response_time': ResponseTimeOptimizer(db_path)
        }
        self.optimization_history = []
    
    def run_optimization_suite(self, n_trials: int = 100) -> Dict[str, OptimizationResult]:
        """Run optimization for all available models"""
        results = {}
        
        logger.info("Starting optimization suite...")
        
        for name, optimizer in self.optimizers.items():
            logger.info(f"Optimizing {name} model...")
            try:
                result = optimizer.optimize_model(n_trials)
                results[name] = result
                logger.info(f"✓ {name} optimization completed")
            except Exception as e:
                logger.error(f"✗ {name} optimization failed: {e}")
                results[name] = None
        
        logger.info("Optimization suite completed!")
        return results
    
    def get_best_parameters(self, model_type: str) -> Optional[Dict[str, Any]]:
        """Get best parameters for a specific model type"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT parameters FROM best_parameters 
            WHERE model_type = ?
            ORDER BY performance_score DESC
            LIMIT 1
        ''', (model_type,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None
    
    def get_optimization_history(self) -> List[Dict[str, Any]]:
        """Get optimization history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                s.study_name,
                s.model_type,
                s.created_at,
                bp.performance_score,
                bp.parameters
            FROM optimization_studies s
            LEFT JOIN best_parameters bp ON s.study_name = bp.study_name
            ORDER BY s.created_at DESC
        ''')
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'study_name': row[0],
                'model_type': row[1],
                'created_at': row[2],
                'performance_score': row[3],
                'parameters': json.loads(row[4]) if row[4] else None
            })
        
        conn.close()
        return history
    
    def visualize_optimization_progress(self, study_name: str, save_path: str = None):
        """Visualize optimization progress"""
        if study_name not in self.optimizers:
            # Try to find the optimizer by study name
            for optimizer in self.optimizers.values():
                if study_name in optimizer.studies:
                    study = optimizer.studies[study_name]
                    break
            else:
                logger.error(f"Study {study_name} not found")
                return
        
        # Create visualization
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Plot optimization history
        values = [trial.value for trial in study.trials if trial.value is not None]
        axes[0, 0].plot(values)
        axes[0, 0].set_title('Optimization Progress')
        axes[0, 0].set_xlabel('Trial')
        axes[0, 0].set_ylabel('Objective Value')
        
        # Plot parameter importance
        if len(study.trials) > 10:
            importance = optuna.importance.get_param_importances(study)
            params = list(importance.keys())
            importances = list(importance.values())
            
            axes[0, 1].barh(params, importances)
            axes[0, 1].set_title('Parameter Importance')
            axes[0, 1].set_xlabel('Importance')
        
        # Plot parameter distribution for top parameter
        if len(study.trials) > 5:
            best_params = study.best_params
            if best_params:
                top_param = list(best_params.keys())[0]
                param_values = [trial.params.get(top_param) for trial in study.trials 
                              if trial.params.get(top_param) is not None]
                
                axes[1, 0].hist(param_values, bins=20)
                axes[1, 0].set_title(f'Distribution of {top_param}')
                axes[1, 0].set_xlabel(top_param)
                axes[1, 0].set_ylabel('Frequency')
        
        # Plot convergence
        best_values = []
        current_best = float('inf')
        for trial in study.trials:
            if trial.value is not None and trial.value < current_best:
                current_best = trial.value
            best_values.append(current_best)
        
        axes[1, 1].plot(best_values)
        axes[1, 1].set_title('Convergence')
        axes[1, 1].set_xlabel('Trial')
        axes[1, 1].set_ylabel('Best Value So Far')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Optimization visualization saved to {save_path}")
        
        plt.show()

def main():
    """Main function for testing optimization"""
    # Create optimization manager
    manager = OptimizationManager()
    
    # Run optimization suite
    results = manager.run_optimization_suite(n_trials=50)
    
    # Display results
    print("\n" + "="*50)
    print("OPTIMIZATION RESULTS")
    print("="*50)
    
    for model_type, result in results.items():
        if result:
            print(f"\n{model_type.upper()} MODEL:")
            print(f"  Best Score: {result.best_value:.4f}")
            print(f"  Best Parameters: {result.best_params}")
            print(f"  Optimization Time: {result.optimization_time:.2f}s")
            print(f"  Trials: {result.n_trials}")
    
    # Show optimization history
    print("\n" + "="*50)
    print("OPTIMIZATION HISTORY")
    print("="*50)
    
    history = manager.get_optimization_history()
    for entry in history[:5]:  # Show last 5 entries
        print(f"  {entry['study_name']}: {entry['performance_score']:.4f}")

if __name__ == "__main__":
    main()
