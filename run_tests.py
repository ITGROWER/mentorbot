#!/usr/bin/env python3
"""
Test runner script for MentorBot.

This script provides convenient commands for running different types of tests
and generating coverage reports.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command: list[str], description: str) -> int:
    """
    Run a command and return its exit code.
    
    Args:
        command: Command to run as list of strings
        description: Description of what the command does
        
    Returns:
        int: Exit code of the command
    """
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")
    
    result = subprocess.run(command, cwd=Path(__file__).parent)
    return result.returncode


def main():
    """Main function for the test runner."""
    parser = argparse.ArgumentParser(description="MentorBot Test Runner")
    parser.add_argument(
        "test_type",
        choices=["all", "unit", "integration", "coverage", "quick", "ci"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "--fail-fast", "-x",
        action="store_true",
        help="Stop on first failure"
    )
    parser.add_argument(
        "--coverage-html",
        action="store_true",
        help="Generate HTML coverage report"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    base_cmd = ["poetry", "run", "pytest"]
    
    # Add common options
    if args.verbose:
        base_cmd.append("-v")
    
    if args.fail_fast:
        base_cmd.append("-x")
    
    # Coverage options
    coverage_cmd = base_cmd + [
        "--cov=tgbot",
        "--cov-report=term-missing",
    ]
    
    if args.coverage_html:
        coverage_cmd.append("--cov-report=html")
    
    # Test type specific commands
    commands = {
        "all": base_cmd + ["tests/"],
        "unit": base_cmd + ["tests/unit/"],
        "integration": base_cmd + ["tests/integration/"],
        "coverage": coverage_cmd + ["tests/"],
        "quick": base_cmd + ["tests/unit/", "-m", "not slow"],
        "ci": base_cmd + [
            "tests/",
            "--tb=short",
            "--strict-markers",
            "--disable-warnings",
            "--durations=10"
        ]
    }
    
    # Run the appropriate command
    command = commands[args.test_type]
    exit_code = run_command(command, f"Running {args.test_type} tests")
    
    if exit_code == 0:
        print(f"\n✅ {args.test_type.title()} tests passed!")
    else:
        print(f"\n❌ {args.test_type.title()} tests failed!")
        sys.exit(exit_code)


if __name__ == "__main__":
    main()