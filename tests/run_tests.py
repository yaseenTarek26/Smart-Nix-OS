#!/usr/bin/env python3
"""
Test runner for NixOS AI Assistant
"""

import os
import sys
import unittest
import subprocess
from pathlib import Path

def run_tests():
    """Run all tests"""
    # Add the project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / "ai"))
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_linting():
    """Run code linting"""
    print("Running code linting...")
    
    # Run flake8
    try:
        result = subprocess.run([
            'flake8', 'ai/', 'tests/',
            '--max-line-length=100',
            '--ignore=E203,W503'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("Flake8 issues found:")
            print(result.stdout)
            print(result.stderr)
            return False
        else:
            print("Flake8: No issues found")
    except FileNotFoundError:
        print("Flake8 not found, skipping linting")
    
    return True

def run_type_checking():
    """Run type checking with mypy"""
    print("Running type checking...")
    
    try:
        result = subprocess.run([
            'mypy', 'ai/',
            '--ignore-missing-imports',
            '--no-strict-optional'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("MyPy issues found:")
            print(result.stdout)
            print(result.stderr)
            return False
        else:
            print("MyPy: No issues found")
    except FileNotFoundError:
        print("MyPy not found, skipping type checking")
    
    return True

def main():
    """Main test runner"""
    print("NixOS AI Assistant - Test Suite")
    print("=" * 40)
    
    # Run linting
    lint_success = run_linting()
    print()
    
    # Run type checking
    type_success = run_type_checking()
    print()
    
    # Run unit tests
    print("Running unit tests...")
    test_success = run_tests()
    print()
    
    # Summary
    print("Test Summary:")
    print(f"  Linting: {'PASS' if lint_success else 'FAIL'}")
    print(f"  Type Checking: {'PASS' if type_success else 'FAIL'}")
    print(f"  Unit Tests: {'PASS' if test_success else 'FAIL'}")
    
    overall_success = lint_success and type_success and test_success
    print(f"\nOverall: {'PASS' if overall_success else 'FAIL'}")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())
