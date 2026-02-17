"""
Tests for secure configuration and JWT authentication setup.

These tests verify that:
1. Environment variable loading works correctly
2. SECRET_KEY validation catches insecure configurations
3. Fail-fast behavior works as expected
4. JWT utilities function properly when dependencies are available
"""

import os
import sys
import pytest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestEnvironmentConfiguration:
    """Test environment variable loading and configuration."""
    
    def test_env_file_exists(self):
        """Test that .env.example exists as a template."""
        env_example_path = Path(__file__).parent.parent / ".env.example"
        assert env_example_path.exists(), ".env.example file should exist"
        
        # Verify it contains SECRET_KEY documentation
        content = env_example_path.read_text()
        assert "SECRET_KEY" in content
        assert "security" in content.lower()
        assert "JWT" in content or "jwt" in content
    
    def test_gitignore_includes_env(self):
        """Test that .env is in .gitignore."""
        gitignore_path = Path(__file__).parent.parent / ".gitignore"
        assert gitignore_path.exists(), ".gitignore should exist"
        
        content = gitignore_path.read_text()
        assert ".env" in content, ".env should be in .gitignore"
    
    def test_config_settings_imports(self):
        """Test that config.settings can be imported."""
        from config import settings
        
        # Verify key constants exist
        assert hasattr(settings, 'APP_NAME')
        assert hasattr(settings, 'APP_VERSION')
        assert hasattr(settings, 'SECRET_KEY')
        assert hasattr(settings, 'JWT_ALGORITHM')
        assert hasattr(settings, 'JWT_EXPIRATION_MINUTES')
    
    def test_secret_key_none_by_default(self):
        """Test that SECRET_KEY is None when not set in environment."""
        # Clear any existing SECRET_KEY
        original_value = os.environ.pop('SECRET_KEY', None)
        
        try:
            # Force reload of settings module
            import importlib
            from config import settings
            importlib.reload(settings)
            
            # SECRET_KEY should be None when not set
            assert settings.SECRET_KEY is None or settings.SECRET_KEY == ""
        finally:
            # Restore original value
            if original_value:
                os.environ['SECRET_KEY'] = original_value


class TestSecretKeyValidation:
    """Test SECRET_KEY validation logic."""
    
    def test_validate_jwt_config_fails_without_secret(self):
        """Test that validation fails when SECRET_KEY is not set."""
        # Clear SECRET_KEY
        original_value = os.environ.pop('SECRET_KEY', None)
        
        try:
            # Force reload of settings
            import importlib
            from config import settings
            importlib.reload(settings)
            
            # Validation should fail
            with pytest.raises(ValueError, match="SECRET_KEY.*not set"):
                settings.validate_jwt_config()
        finally:
            if original_value:
                os.environ['SECRET_KEY'] = original_value
    
    def test_validate_jwt_config_fails_with_short_key(self):
        """Test that validation fails when SECRET_KEY is too short."""
        original_value = os.environ.get('SECRET_KEY')
        
        try:
            # Set a short key
            os.environ['SECRET_KEY'] = "short"
            
            # Force reload
            import importlib
            from config import settings
            importlib.reload(settings)
            
            # Validation should fail
            with pytest.raises(ValueError, match="too short"):
                settings.validate_jwt_config()
        finally:
            if original_value:
                os.environ['SECRET_KEY'] = original_value
            else:
                os.environ.pop('SECRET_KEY', None)
    
    def test_validate_jwt_config_fails_with_insecure_default(self):
        """Test that validation fails with insecure default values."""
        original_value = os.environ.get('SECRET_KEY')
        
        insecure_values = [
            "your-super-secret-jwt-key-change-this-in-production-min-32-chars",
            "change-this-secret-key-minimum-32-characters-required-here",
            "REPLACE_WITH_GENERATED_KEY_MINIMUM_32_CHARACTERS_REQUIRED",
            "this-is-a-test-key-for-testing-32-chars-minimum-required",
            "my-example-password-key-for-testing-32-chars-min",
        ]
        
        for insecure_key in insecure_values:
            try:
                os.environ['SECRET_KEY'] = insecure_key
                
                # Force reload
                import importlib
                from config import settings
                importlib.reload(settings)
                
                # Validation should fail with "insecure" in the error message
                with pytest.raises(ValueError, match="insecure"):
                    settings.validate_jwt_config()
            finally:
                if original_value:
                    os.environ['SECRET_KEY'] = original_value
                else:
                    os.environ.pop('SECRET_KEY', None)
    
    def test_validate_jwt_config_succeeds_with_valid_key(self):
        """Test that validation succeeds with a valid SECRET_KEY."""
        original_value = os.environ.get('SECRET_KEY')
        
        try:
            # Generate a valid key (32+ chars, random)
            import secrets
            valid_key = secrets.token_urlsafe(32)
            os.environ['SECRET_KEY'] = valid_key
            
            # Force reload
            import importlib
            from config import settings
            importlib.reload(settings)
            
            # Validation should succeed (no exception)
            settings.validate_jwt_config()
            
            # Should be able to get the key
            retrieved_key = settings.get_secret_key()
            assert retrieved_key == valid_key
        finally:
            if original_value:
                os.environ['SECRET_KEY'] = original_value
            else:
                os.environ.pop('SECRET_KEY', None)


class TestAuthModule:
    """Test core.auth module (if JWT libraries are available)."""
    
    def test_auth_module_exists(self):
        """Test that core.auth module exists."""
        auth_module_path = Path(__file__).parent.parent / "core" / "auth.py"
        assert auth_module_path.exists(), "core/auth.py should exist"
    
    def test_auth_module_imports(self):
        """Test that core.auth can be imported."""
        try:
            from core import auth
            
            # Verify expected functions exist
            assert hasattr(auth, 'create_access_token')
            assert hasattr(auth, 'verify_token')
            assert hasattr(auth, 'get_user_from_token')
            assert hasattr(auth, 'validate_jwt_config')
            
            # Verify exception classes exist
            assert hasattr(auth, 'AuthenticationError')
            assert hasattr(auth, 'TokenExpiredError')
            assert hasattr(auth, 'TokenInvalidError')
        except ImportError as e:
            pytest.skip(f"core.auth module could not be imported: {e}")
    
    def test_create_access_token_requires_secret(self):
        """Test that create_access_token validates SECRET_KEY."""
        try:
            from core.auth import create_access_token, JWT_AVAILABLE
            
            if not JWT_AVAILABLE:
                pytest.skip("python-jose not available")
        except ImportError:
            pytest.skip("core.auth module could not be imported")
        
        # Clear SECRET_KEY
        original_value = os.environ.pop('SECRET_KEY', None)
        
        try:
            # Force reload
            import importlib
            from config import settings
            importlib.reload(settings)
            
            # Should fail without SECRET_KEY (could be ValueError or RuntimeError)
            with pytest.raises((ValueError, RuntimeError)):
                create_access_token({"sub": "test"})
        finally:
            if original_value:
                os.environ['SECRET_KEY'] = original_value
    
    @pytest.mark.skipif(
        not os.environ.get('SECRET_KEY'),
        reason="SECRET_KEY not set in environment"
    )
    def test_token_creation_and_verification(self):
        """Test end-to-end token creation and verification."""
        try:
            from core.auth import create_access_token, verify_token
            import secrets
            
            # Set a valid key for testing
            original_value = os.environ.get('SECRET_KEY')
            test_key = secrets.token_urlsafe(32)
            os.environ['SECRET_KEY'] = test_key
            
            try:
                # Force reload
                import importlib
                from config import settings
                importlib.reload(settings)
                
                # Create a token
                test_data = {"sub": "user123", "role": "student"}
                token = create_access_token(test_data)
                
                assert isinstance(token, str)
                assert len(token) > 0
                
                # Verify the token
                payload = verify_token(token)
                assert payload["sub"] == "user123"
                assert payload["role"] == "student"
                assert "exp" in payload  # Expiration time
                assert "iat" in payload  # Issued at time
            finally:
                if original_value:
                    os.environ['SECRET_KEY'] = original_value
                else:
                    os.environ.pop('SECRET_KEY', None)
        except ImportError:
            pytest.skip("python-jose not available")


class TestDocumentation:
    """Test that security documentation is present."""
    
    def test_readme_has_security_section(self):
        """Test that README.md has security documentation."""
        readme_path = Path(__file__).parent.parent / "README.md"
        assert readme_path.exists(), "README.md should exist"
        
        content = readme_path.read_text()
        assert "Security" in content or "security" in content
        assert "SECRET_KEY" in content
        assert "environment" in content.lower() or "Environment" in content
    
    def test_setup_has_security_section(self):
        """Test that SETUP.md has security instructions."""
        setup_path = Path(__file__).parent.parent / "SETUP.md"
        assert setup_path.exists(), "SETUP.md should exist"
        
        content = setup_path.read_text()
        assert "Security" in content or "security" in content
        assert "SECRET_KEY" in content or ".env" in content
    
    def test_env_example_has_security_docs(self):
        """Test that .env.example has comprehensive security documentation."""
        env_example_path = Path(__file__).parent.parent / ".env.example"
        content = env_example_path.read_text()
        
        # Check for key security topics
        assert "SECRET_KEY" in content
        assert "security" in content.lower() or "Security" in content
        assert "32" in content  # Minimum length requirement
        assert "production" in content.lower()
        assert "never" in content.lower() and "commit" in content.lower()


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
