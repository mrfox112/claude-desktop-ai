"""
Test script for the AI Model Optimization System
Run this to test the Optuna-based hyperparameter tuning functionality
"""

import os
import sys
import time
import numpy as np
from datetime import datetime

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_optimization_system():
    """Test the optimization system"""
    print("🔧 Testing AI Model Optimization System")
    print("=" * 50)
    
    try:
        # Test imports
        print("1. Testing imports...")
        from model_optimizer import (
            OptimizationManager, 
            ConversationQualityOptimizer, 
            ResponseTimeOptimizer,
            OptimizationResult
        )
        print("   ✓ All imports successful")
        
        # Test database initialization
        print("2. Testing database initialization...")
        manager = OptimizationManager("test_optimization.db")
        print("   ✓ Database initialized successfully")
        
        # Test conversation quality optimizer
        print("3. Testing conversation quality optimizer...")
        quality_optimizer = ConversationQualityOptimizer("test_optimization.db")
        
        # Generate some test data
        print("   - Preparing test data...")
        X, y = quality_optimizer.prepare_training_data()
        print(f"   - Data shape: X={X.shape}, y={y.shape}")
        
        # Run a quick optimization with fewer trials
        print("   - Running optimization (10 trials)...")
        start_time = time.time()
        quality_result = quality_optimizer.optimize_model(n_trials=10)
        end_time = time.time()
        
        print(f"   ✓ Optimization completed in {end_time - start_time:.2f} seconds")
        print(f"   - Best value: {quality_result.best_value:.4f}")
        print(f"   - Best parameters: {quality_result.best_params}")
        
        # Test response time optimizer
        print("4. Testing response time optimizer...")
        response_optimizer = ResponseTimeOptimizer("test_optimization.db")
        
        print("   - Preparing test data...")
        X, y = response_optimizer.prepare_training_data()
        print(f"   - Data shape: X={X.shape}, y={y.shape}")
        
        print("   - Running optimization (10 trials)...")
        start_time = time.time()
        response_result = response_optimizer.optimize_model(n_trials=10)
        end_time = time.time()
        
        print(f"   ✓ Optimization completed in {end_time - start_time:.2f} seconds")
        print(f"   - Best value: {response_result.best_value:.4f}")
        print(f"   - Best parameters: {response_result.best_params}")
        
        # Test optimization manager
        print("5. Testing optimization manager...")
        
        # Test getting best parameters
        best_quality_params = manager.get_best_parameters('conversation_quality')
        best_response_params = manager.get_best_parameters('response_time')
        
        print(f"   - Best quality parameters: {best_quality_params}")
        print(f"   - Best response parameters: {best_response_params}")
        
        # Test optimization history
        history = manager.get_optimization_history()
        print(f"   - Optimization history entries: {len(history)}")
        
        # Test suite run (quick version)
        print("6. Testing optimization suite...")
        suite_results = manager.run_optimization_suite(n_trials=5)
        
        print("   Suite results:")
        for model_type, result in suite_results.items():
            if result:
                print(f"     - {model_type}: {result.best_value:.4f}")
            else:
                print(f"     - {model_type}: Failed")
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed successfully!")
        print("=" * 50)
        
        # Summary
        print(f"\nSUMMARY:")
        print(f"- Database: test_optimization.db")
        print(f"- Total optimization studies: {len(history)}")
        print(f"- Conversation quality best score: {quality_result.best_value:.4f}")
        print(f"- Response time best score: {response_result.best_value:.4f}")
        
        # Cleanup
        print("\n7. Cleaning up test database...")
        # Force cleanup of any remaining connections
        del manager
        del quality_optimizer
        del response_optimizer
        time.sleep(0.1)  # Give time for connections to close
        
        if os.path.exists("test_optimization.db"):
            try:
                os.remove("test_optimization.db")
                print("   ✓ Test database cleaned up")
            except PermissionError:
                print("   ⚠️  Test database still in use (this is normal on Windows)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install required packages: pip install optuna scikit-learn")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_with_claude():
    """Test integration with the main Claude application"""
    print("\n🤖 Testing integration with Claude Desktop...")
    print("=" * 50)
    
    try:
        # Test that the optimization system can be imported by the main app
        print("1. Testing integration imports...")
        from claude_desktop import OPTIMIZATION_AVAILABLE
        
        if OPTIMIZATION_AVAILABLE:
            print("   ✓ Optimization system is available in Claude Desktop")
            
            # Test creating OptimizationManager
            from claude_desktop import OptimizationManager
            manager = OptimizationManager("test_integration.db")
            print("   ✓ OptimizationManager created successfully")
            
            # Test accessing optimizers
            optimizers = manager.optimizers
            print(f"   ✓ Available optimizers: {list(optimizers.keys())}")
            
            # Cleanup
            if os.path.exists("test_integration.db"):
                os.remove("test_integration.db")
            
        else:
            print("   ⚠️  Optimization system is not available")
            print("   Please install: pip install optuna scikit-learn")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting AI Model Optimization Tests")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run main optimization tests
    success1 = test_optimization_system()
    
    # Run integration tests
    success2 = test_integration_with_claude()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED! 🎉")
        print("The optimization system is ready to use.")
    else:
        print("❌ Some tests failed. Please check the output above.")
        
    print(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
