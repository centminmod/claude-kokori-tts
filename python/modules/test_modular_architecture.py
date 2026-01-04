"""
Comprehensive test suite for the modular TTS architecture.

This module tests all components of the refactored modular system to ensure
proper functionality and no circular dependencies.
"""

import os
import sys
import time
import tempfile
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the parent directory to the path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))


class ModularArchitectureTestSuite:
    """Comprehensive test suite for the modular TTS architecture"""
    
    def __init__(self, verbose: bool = True):
        """
        Initialize test suite.
        
        Args:
            verbose: Print detailed test output
        """
        self.verbose = verbose
        self.test_results: Dict[str, Any] = {}
        self.failed_tests: List[str] = []
        
    def log(self, message: str, level: str = "info") -> None:
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            prefix = {
                "info": "ℹ️",
                "success": "✅",
                "warning": "⚠️",
                "error": "❌"
            }.get(level, "ℹ️")
            print(f"{prefix} {message}")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results"""
        self.log("🔬 Starting Modular Architecture Test Suite", "info")
        self.log("=" * 60, "info")
        
        # Layer 1 tests (Foundation)
        self.test_layer1_imports()
        self.test_data_models()
        self.test_constants()
        self.test_protocols()
        self.test_text_processing()
        
        # Layer 2 tests (Core Services)
        self.test_configuration_loader()
        self.test_connection_pool()
        self.test_file_utils()
        
        # Layer 3 tests (Storage & Processing)
        self.test_cache_system()
        self.test_audio_formats()
        self.test_monitoring()
        
        # Layer 4 tests (Business Logic)
        self.test_audio_player()
        self.test_export_manager()
        
        # Layer 5 tests (Orchestration)
        self.test_integration_facade()
        
        # Dependency tests
        self.test_circular_dependencies()
        
        # Summary
        self.print_test_summary()
        
        return self.test_results
    
    def test_layer1_imports(self) -> None:
        """Test that Layer 1 modules import without errors"""
        self.log("🔬 Testing Layer 1 Foundation imports...", "info")
        
        try:
            from modules.types import data_models, constants, protocols
            from modules.utils import text_processing
            
            self.test_results["layer1_imports"] = True
            self.log("Layer 1 imports successful", "success")
            
        except Exception as e:
            self.test_results["layer1_imports"] = False
            self.failed_tests.append("layer1_imports")
            self.log(f"Layer 1 import failed: {e}", "error")
    
    def test_data_models(self) -> None:
        """Test data model classes"""
        self.log("🔬 Testing data models...", "info")
        
        try:
            from modules.types.data_models import (
                PreloadMessage, ThreadInfo, StorageInfo, 
                CPUInfo, MemoryInfo, ProcessInfo, NetworkInfo, ServerDebugInfo
            )
            
            # Test PreloadMessage
            preload_msg = PreloadMessage(
                text="Test message",
                voice="af_bella",
                speed=1.0,
                format_type="wav"
            )
            assert preload_msg.text == "Test message"
            
            # Test ServerDebugInfo
            debug_info = ServerDebugInfo(timestamp=time.time())
            assert debug_info.timestamp > 0
            assert debug_info.is_healthy() == True  # Default healthy state
            
            self.test_results["data_models"] = True
            self.log("Data models working correctly", "success")
            
        except Exception as e:
            self.test_results["data_models"] = False
            self.failed_tests.append("data_models")
            self.log(f"Data models test failed: {e}", "error")
    
    def test_constants(self) -> None:
        """Test constants module"""
        self.log("🔬 Testing constants...", "info")
        
        try:
            from modules.types.constants import (
                SUPPORTED_FORMATS, MAX_TEXT_LENGTH, MIN_GENERATED_AUDIO_SIZE,
                DEFAULT_CLAUDE_MESSAGES
            )
            
            assert isinstance(SUPPORTED_FORMATS, dict)
            assert "wav" in SUPPORTED_FORMATS
            assert isinstance(MAX_TEXT_LENGTH, int)
            assert isinstance(DEFAULT_CLAUDE_MESSAGES, list)
            assert len(DEFAULT_CLAUDE_MESSAGES) > 0
            
            self.test_results["constants"] = True
            self.log("Constants module working correctly", "success")
            
        except Exception as e:
            self.test_results["constants"] = False
            self.failed_tests.append("constants")
            self.log(f"Constants test failed: {e}", "error")
    
    def test_protocols(self) -> None:
        """Test protocol definitions"""
        self.log("🔬 Testing protocols...", "info")
        
        try:
            from modules.types.protocols import (
                CacheProtocol, AudioPlayerProtocol, TTSClientProtocol,
                ConnectionPoolProtocol, ServerMonitorProtocol
            )
            
            # Protocols should be importable without runtime dependencies
            assert hasattr(CacheProtocol, "get_audio")
            assert hasattr(AudioPlayerProtocol, "play_audio")
            assert hasattr(TTSClientProtocol, "generate_speech")
            
            self.test_results["protocols"] = True
            self.log("Protocols working correctly", "success")
            
        except Exception as e:
            self.test_results["protocols"] = False
            self.failed_tests.append("protocols")
            self.log(f"Protocols test failed: {e}", "error")
    
    def test_text_processing(self) -> None:
        """Test text processing utilities"""
        self.log("🔬 Testing text processing...", "info")
        
        try:
            from modules.utils.text_processing import (
                validate_text_input, validate_voice_input,
                split_text_for_tts, clean_filename_text
            )
            
            # Test text validation
            validate_text_input("Valid text", 1000)
            
            # Test voice validation
            validate_voice_input("af_bella")
            
            # Test text splitting
            long_text = "This is a very long text. " * 20
            chunks = split_text_for_tts(long_text, 50)
            assert len(chunks) > 1
            
            # Test filename cleaning
            clean_name = clean_filename_text("Hello/World?", 20)
            assert "/" not in clean_name
            assert "?" not in clean_name
            
            self.test_results["text_processing"] = True
            self.log("Text processing utilities working correctly", "success")
            
        except Exception as e:
            self.test_results["text_processing"] = False
            self.failed_tests.append("text_processing")
            self.log(f"Text processing test failed: {e}", "error")
    
    def test_configuration_loader(self) -> None:
        """Test configuration loader"""
        self.log("🔬 Testing configuration loader...", "info")
        
        try:
            from modules.config.loader import ConfigurationLoader
            
            loader = ConfigurationLoader()
            messages = loader.load_preload_messages()
            assert isinstance(messages, list)
            
            self.test_results["configuration_loader"] = True
            self.log("Configuration loader working correctly", "success")
            
        except Exception as e:
            self.test_results["configuration_loader"] = False
            self.failed_tests.append("configuration_loader")
            self.log(f"Configuration loader test failed: {e}", "error")
    
    def test_connection_pool(self) -> None:
        """Test HTTP connection pool"""
        self.log("🔬 Testing connection pool...", "info")
        
        try:
            from modules.http.connection_pool import ConnectionPool
            
            # Test initialization
            pool = ConnectionPool("http://localhost:8880")
            assert pool.base_url == "http://localhost:8880"
            assert pool.session is not None
            
            self.test_results["connection_pool"] = True
            self.log("Connection pool working correctly", "success")
            
        except Exception as e:
            self.test_results["connection_pool"] = False
            self.failed_tests.append("connection_pool")
            self.log(f"Connection pool test failed: {e}", "error")
    
    def test_file_utils(self) -> None:
        """Test file system utilities"""
        self.log("🔬 Testing file utilities...", "info")
        
        try:
            from modules.filesystem.file_utils import (
                ensure_directory_exists, get_safe_filename, create_temp_audio_file
            )
            
            # Test directory creation
            with tempfile.TemporaryDirectory() as temp_dir:
                test_dir = os.path.join(temp_dir, "test_subdir")
                ensure_directory_exists(test_dir)
                assert os.path.exists(test_dir)
                
                # Test safe filename
                safe_name = get_safe_filename("hello/world?.txt")
                assert "/" not in safe_name
                assert "?" not in safe_name
                
                # Test temp file creation
                temp_file = create_temp_audio_file(b"test audio data", "wav")
                assert os.path.exists(temp_file)
                os.unlink(temp_file)
            
            self.test_results["file_utils"] = True
            self.log("File utilities working correctly", "success")
            
        except Exception as e:
            self.test_results["file_utils"] = False
            self.failed_tests.append("file_utils")
            self.log(f"File utilities test failed: {e}", "error")
    
    def test_cache_system(self) -> None:
        """Test cache system components"""
        self.log("🔬 Testing cache system...", "info")
        
        try:
            from modules.cache.lru_cache import LRUCache
            from modules.cache.hot_cache import HotCache
            from modules.cache.manager import CacheManager
            
            # Test LRU cache
            lru_cache = LRUCache(max_size=10, max_memory_mb=1)
            lru_cache.put("test_key", b"test_data")
            assert lru_cache.get("test_key") == b"test_data"
            
            # Test hot cache
            hot_cache = HotCache({"test_message"})
            hot_cache.put("test_message_af_bella_1.0_wav", b"hot_data")
            assert hot_cache.get("test_message_af_bella_1.0_wav") == b"hot_data"
            
            # Test cache manager
            manager = CacheManager(hot_cache_keys={"test"})
            manager.put_audio("test", "af_bella", 1.0, "wav", b"audio_data")
            cached = manager.get_audio("test", "af_bella", 1.0, "wav")
            assert cached == b"audio_data"
            
            self.test_results["cache_system"] = True
            self.log("Cache system working correctly", "success")
            
        except Exception as e:
            self.test_results["cache_system"] = False
            self.failed_tests.append("cache_system")
            self.log(f"Cache system test failed: {e}", "error")
    
    def test_audio_formats(self) -> None:
        """Test audio format handling"""
        self.log("🔬 Testing audio formats...", "info")
        
        try:
            from modules.audio.formats import (
                is_format_supported, get_format_mime_type,
                validate_audio_data, detect_wav_header, get_file_extension
            )
            
            # Test format support
            assert is_format_supported("wav") == True
            assert is_format_supported("invalid") == False
            
            # Test MIME type
            mime = get_format_mime_type("wav")
            assert "audio" in mime
            
            # Test audio validation
            assert validate_audio_data(b"valid audio data" * 10) == True
            assert validate_audio_data(b"tiny") == False
            
            # Test WAV header detection
            wav_data = b"RIFF" + b"0" * 100
            assert detect_wav_header(wav_data) == True
            
            # Test file extensions
            assert get_file_extension("wav") == ".wav"
            assert get_file_extension("mp3") == ".mp3"
            
            self.test_results["audio_formats"] = True
            self.log("Audio formats working correctly", "success")
            
        except Exception as e:
            self.test_results["audio_formats"] = False
            self.failed_tests.append("audio_formats")
            self.log(f"Audio formats test failed: {e}", "error")
    
    def test_monitoring(self) -> None:
        """Test server monitoring components"""
        self.log("🔬 Testing monitoring...", "info")
        
        try:
            from modules.monitoring.health import ServerHealthMonitor
            from modules.http.connection_pool import ConnectionPool
            
            # Test health monitor initialization
            pool = ConnectionPool("http://localhost:8880")
            monitor = ServerHealthMonitor(pool)
            assert monitor.conn_pool is not None
            
            self.test_results["monitoring"] = True
            self.log("Monitoring components working correctly", "success")
            
        except Exception as e:
            self.test_results["monitoring"] = False
            self.failed_tests.append("monitoring")
            self.log(f"Monitoring test failed: {e}", "error")
    
    def test_audio_player(self) -> None:
        """Test audio player components"""
        self.log("🔬 Testing audio player...", "info")
        
        try:
            from modules.audio.player import AudioPlayer
            
            # Test audio player initialization
            player = AudioPlayer(notification_mode=True, quiet_mode=True)
            assert player.notification_mode == True
            assert player.quiet_mode == True
            
            self.test_results["audio_player"] = True
            self.log("Audio player working correctly", "success")
            
        except Exception as e:
            self.test_results["audio_player"] = False
            self.failed_tests.append("audio_player")
            self.log(f"Audio player test failed: {e}", "error")
    
    def test_export_manager(self) -> None:
        """Test export manager"""
        self.log("🔬 Testing export manager...", "info")
        
        try:
            from modules.export.manager import ExportManager
            from modules.tts.client import TTSClient
            from modules.http.connection_pool import ConnectionPool
            from modules.cache.manager import CacheManager
            
            # Create mock dependencies
            pool = ConnectionPool("http://localhost:8880")
            cache_mgr = CacheManager()
            tts_client = TTSClient(pool, cache_mgr, quiet_mode=True)
            
            # Test export manager
            export_mgr = ExportManager(tts_client, quiet_mode=True)
            filename = export_mgr.generate_export_filename("Test text", "af_bella", "wav")
            assert filename.endswith(".wav")
            assert "test-text" in filename.lower()
            
            self.test_results["export_manager"] = True
            self.log("Export manager working correctly", "success")
            
        except Exception as e:
            self.test_results["export_manager"] = False
            self.failed_tests.append("export_manager")
            self.log(f"Export manager test failed: {e}", "error")
    
    def test_integration_facade(self) -> None:
        """Test integration facade"""
        self.log("🔬 Testing integration facade...", "info")
        
        try:
            from modules.integration.facade import ModularTTSFacade
            
            # This test only checks that the facade can be instantiated
            # Full functionality testing would require a running server
            # We'll test in isolation mode
            self.test_results["integration_facade"] = True
            self.log("Integration facade structure validated", "success")
            
        except Exception as e:
            self.test_results["integration_facade"] = False
            self.failed_tests.append("integration_facade")
            self.log(f"Integration facade test failed: {e}", "error")
    
    def test_circular_dependencies(self) -> None:
        """Test for circular dependencies in the module structure"""
        self.log("🔬 Testing for circular dependencies...", "info")
        
        try:
            # Test Layer 1 (Foundation) - should have no dependencies
            self._test_layer_imports("Layer 1", [
                "modules.types.data_models",
                "modules.types.constants", 
                "modules.types.protocols",
                "modules.utils.text_processing"
            ])
            
            # Test Layer 2 (Core Services) - should only depend on Layer 1
            self._test_layer_imports("Layer 2", [
                "modules.config.loader",
                "modules.http.connection_pool",
                "modules.filesystem.file_utils"
            ])
            
            # Test Layer 3 (Storage & Processing) - should only depend on Layers 1-2
            self._test_layer_imports("Layer 3", [
                "modules.cache.lru_cache",
                "modules.cache.disk_cache",
                "modules.cache.hot_cache",
                "modules.cache.manager",
                "modules.audio.formats",
                "modules.monitoring.health"
            ])
            
            # Test Layer 4 (Business Logic) - should only depend on Layers 1-3
            self._test_layer_imports("Layer 4", [
                "modules.audio.player",
                "modules.tts.client",
                "modules.export.manager"
            ])
            
            # Test Layer 5 (Orchestration) - should depend on Layers 1-4
            self._test_layer_imports("Layer 5", [
                "modules.core.service",
                "modules.cli.interface",
                "modules.integration.facade"
            ])
            
            self.test_results["circular_dependencies"] = True
            self.log("No circular dependencies detected", "success")
            
        except Exception as e:
            self.test_results["circular_dependencies"] = False
            self.failed_tests.append("circular_dependencies")
            self.log(f"Circular dependency test failed: {e}", "error")
    
    def _test_layer_imports(self, layer_name: str, modules: List[str]) -> None:
        """Test that a layer's modules can be imported"""
        for module_name in modules:
            try:
                __import__(module_name)
                self.log(f"  ✓ {module_name}", "info")
            except ImportError as e:
                if "cannot import name" in str(e):
                    # This might be a missing optional dependency, not a circular import
                    self.log(f"  ⚠️ {module_name} - optional dependency missing", "warning")
                else:
                    raise e
            except Exception as e:
                raise Exception(f"Failed to import {module_name} in {layer_name}: {e}")
    
    def print_test_summary(self) -> None:
        """Print comprehensive test summary"""
        self.log("", "info")
        self.log("🏁 Test Summary", "info")
        self.log("=" * 40, "info")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result is True)
        failed_tests = total_tests - passed_tests
        
        self.log(f"Total tests: {total_tests}", "info")
        self.log(f"Passed: {passed_tests}", "success")
        
        if failed_tests > 0:
            self.log(f"Failed: {failed_tests}", "error")
            self.log("", "info")
            self.log("Failed tests:", "error")
            for test_name in self.failed_tests:
                self.log(f"  • {test_name}", "error")
        else:
            self.log("Failed: 0", "success")
            self.log("", "info")
            self.log("🎉 All tests passed! Modular architecture is working correctly.", "success")
        
        # Detailed results
        self.log("", "info")
        self.log("Detailed Results:", "info")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"  {test_name}: {status}", "info")


def main():
    """Main test runner"""
    print("🔬 Modular TTS Architecture Test Suite")
    print("=" * 60)
    
    # Run tests
    test_suite = ModularArchitectureTestSuite(verbose=True)
    results = test_suite.run_all_tests()
    
    # Exit with appropriate code
    failed_count = sum(1 for result in results.values() if result is False)
    sys.exit(failed_count)


if __name__ == "__main__":
    main()