#!/usr/bin/env python3
"""
Demonstration script for JWT Secret Key configuration and validation.

This script demonstrates:
1. How to generate a secure SECRET_KEY
2. How validation works (fail-fast behavior)
3. Best practices for environment variable configuration

Usage:
    python demo_jwt_config.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def demo_generate_secret_key() -> str:
    """Demonstrate how to generate a secure secret key."""
    print_section("1. Generating a Secure SECRET_KEY")
    
    import secrets
    secret_key = secrets.token_urlsafe(32)
    
    print("\n✓ Generated a cryptographically secure random key:")
    print(f"  {secret_key}")
    print("\nCommand to generate your own:")
    print('  python -c "import secrets; print(secrets.token_urlsafe(32))"')
    
    return secret_key


def demo_validation_without_key() -> None:
    """Demonstrate fail-fast validation when SECRET_KEY is missing."""
    print_section("2. Validation Without SECRET_KEY (Fail-Fast)")
    
    # Clear SECRET_KEY if set
    os.environ.pop('SECRET_KEY', None)
    
    # Force reload to clear any cached values
    import importlib
    import config.settings
    importlib.reload(config.settings)
    
    print("\n✗ Attempting validation without SECRET_KEY...")
    try:
        config.settings.validate_jwt_config()
        print("  ERROR: Should have failed!")
    except ValueError as e:
        print("✓ Validation correctly failed with clear error message:")
        error_lines = str(e).split('\n')
        for line in error_lines[:5]:  # Show first 5 lines
            print(f"  {line}")
        print("  ...")


def demo_validation_with_insecure_key() -> None:
    """Demonstrate validation rejection of insecure keys."""
    print_section("3. Validation With Insecure Key")
    
    insecure_key = "this-is-a-test-key-for-testing-32-chars-minimum-required"
    os.environ['SECRET_KEY'] = insecure_key
    
    # Force reload
    import importlib
    import config.settings
    importlib.reload(config.settings)
    
    print(f"\n✗ Attempting validation with insecure key:")
    print(f"  {insecure_key[:40]}...")
    try:
        config.settings.validate_jwt_config()
        print("  ERROR: Should have failed!")
    except ValueError as e:
        print("✓ Validation correctly rejected insecure default:")
        error_lines = str(e).split('\n')
        for line in error_lines[:4]:
            print(f"  {line}")


def demo_validation_with_valid_key(secret_key: str) -> None:
    """Demonstrate successful validation with valid key."""
    print_section("4. Validation With Valid Key")
    
    os.environ['SECRET_KEY'] = secret_key
    
    # Force reload
    import importlib
    import config.settings
    importlib.reload(config.settings)
    
    print(f"\n✓ Setting SECRET_KEY: {secret_key[:20]}...{secret_key[-10:]}")
    try:
        config.settings.validate_jwt_config()
        print("✓ Validation passed successfully!")
        print(f"✓ Key length: {len(secret_key)} characters")
        print(f"✓ Algorithm: {config.settings.JWT_ALGORITHM}")
        print(f"✓ Token expiration: {config.settings.JWT_EXPIRATION_MINUTES} minutes")
    except ValueError as e:
        print(f"✗ Unexpected error: {e}")


def demo_env_file_setup() -> None:
    """Demonstrate .env file setup."""
    print_section("5. Setting Up .env File")
    
    print("\n1. Copy the example file:")
    print("   cp .env.example .env")
    
    print("\n2. Generate a secure key:")
    print('   python -c "import secrets; print(secrets.token_urlsafe(32))"')
    
    print("\n3. Edit .env and set SECRET_KEY:")
    print("   # Open .env in your favorite editor")
    print("   # Set: SECRET_KEY=your-generated-key-here")
    
    print("\n4. Verify .env is in .gitignore:")
    print("   grep '.env' .gitignore")
    
    print("\n5. Never commit .env to version control!")


def demo_auth_utilities() -> None:
    """Demonstrate JWT auth utilities (if available)."""
    print_section("6. JWT Token Creation & Verification (Optional)")
    
    try:
        from core.auth import create_access_token, verify_token, JWT_AVAILABLE
        
        if not JWT_AVAILABLE:
            print("\n⚠ python-jose not installed")
            print("  To enable JWT features:")
            print("    pip install python-jose[cryptography]")
            return
        
        # Generate and set a valid key
        import secrets
        os.environ['SECRET_KEY'] = secrets.token_urlsafe(32)
        
        # Force reload
        import importlib
        import config.settings
        importlib.reload(config.settings)
        
        print("\n✓ Creating JWT token...")
        token_data = {"sub": "user123", "role": "student", "name": "Demo User"}
        token = create_access_token(token_data)
        print(f"  Token: {token[:30]}...{token[-20:]}")
        
        print("\n✓ Verifying token...")
        payload = verify_token(token)
        print(f"  User ID: {payload.get('sub')}")
        print(f"  Role: {payload.get('role')}")
        print(f"  Name: {payload.get('name')}")
        print(f"  Expires: {payload.get('exp')}")
        
    except ImportError as e:
        print(f"\n⚠ JWT features not available: {e}")
        print("  To enable: pip install python-jose[cryptography]")


def main():
    """Run all demonstrations."""
    print("\n" + "="*70)
    print("  JWT SECRET_KEY Configuration Demonstration")
    print("  SchedularV3 Security Features")
    print("="*70)
    
    # Generate a key for demonstrations
    secret_key = demo_generate_secret_key()
    
    # Demonstrate validation scenarios
    demo_validation_without_key()
    demo_validation_with_insecure_key()
    demo_validation_with_valid_key(secret_key)
    
    # Show setup instructions
    demo_env_file_setup()
    
    # Demonstrate auth utilities if available
    demo_auth_utilities()
    
    # Final summary
    print_section("Summary")
    print("\n✅ Security features implemented:")
    print("  • No hardcoded secrets in source code")
    print("  • Environment variable-based configuration")
    print("  • Fail-fast validation at startup")
    print("  • Minimum 32-character key requirement")
    print("  • Insecure default value detection")
    print("  • Comprehensive documentation")
    print("  • .env excluded from version control")
    
    print("\n📚 Next steps:")
    print("  • Review .env.example for all configuration options")
    print("  • Read Security section in README.md")
    print("  • Run tests: pytest tests/test_security_config.py")
    print("  • See core/auth.py for JWT implementation examples")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
