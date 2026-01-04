"""
Test operations and functionality tests for the TTS system.

This module provides comprehensive testing capabilities including basic tests,
quick tests, and full functionality tests.
Layer 5 - Orchestration: Depends on all other layers.
"""

import json
import time
from typing import Optional, List, Tuple

from modules.integration.facade import ModularTTSFacade


class TestRunner:
    """Handles all test operations for the TTS system"""
    
    def __init__(self, tts: ModularTTSFacade):
        """
        Initialize test runner.
        
        Args:
            tts: TTS facade instance
        """
        self.tts = tts
    
    def run_basic_test(self, voice: str, format: str, quiet: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Run basic system test.
        
        Args:
            voice: Voice to use for test
            format: Audio format
            quiet: Suppress output
            
        Returns:
            Tuple of (success, error_message)
        """
        if not quiet:
            print("🚀 Running enhanced system test...")
        
        success = self.tts.test_connection_with_retry()
        error_msg = None
        
        if success:
            try:
                test_audio = self.tts.generate_speech(
                    "Enhanced system test successful",
                    voice, 1.0, format
                )
                self.tts.play_audio(test_audio, format)
                if not quiet:
                    print("✅ All tests passed!")
            except Exception as e:
                success = False
                error_msg = str(e)
        
        return success, error_msg
    
    def run_quick_test(self, voice: str, format: str) -> int:
        """
        Run quick functionality tests.
        
        Args:
            voice: Voice to use
            format: Audio format
            
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        print("⚡ Running quick functionality tests...")
        test_results = []
        
        # Quick Test 1: Basic speech
        try:
            print("1️⃣ Basic speech...", end="", flush=True)
            self.tts.speak_text("Test", voice, 1.0, format)
            print(" ✅")
            test_results.append(("Basic speech", True, None))
        except Exception as e:
            print(" ❌")
            test_results.append(("Basic speech", False, str(e)))
        
        # Quick Test 2: Voice blending
        try:
            print("2️⃣ Voice blending...", end="", flush=True)
            self.tts.speak_text("Blend", "af_bella+af_sky", 1.0, format)
            print(" ✅")
            test_results.append(("Voice blending", True, None))
        except Exception as e:
            print(" ❌")
            test_results.append(("Voice blending", False, str(e)))
        
        # Quick Test 3: Caching
        try:
            print("3️⃣ Cache test...", end="", flush=True)
            cache_text = "This is a cache test message"
            start = time.time()
            self.tts.speak_text(cache_text, voice, 1.0, format)
            first_time = time.time() - start
            
            start = time.time()
            self.tts.speak_text(cache_text, voice, 1.0, format)
            cached_time = time.time() - start
            
            # Cache test - cached should be noticeably faster
            # Account for audio playback time which is constant
            if cached_time < first_time - 0.1:  # At least 100ms faster
                print(" ✅")
                test_results.append(("Caching", True, f"{cached_time:.2f}s vs {first_time:.2f}s"))
            else:
                print(" ❌")
                test_results.append(("Caching", False, f"Not faster enough: {cached_time:.2f}s vs {first_time:.2f}s"))
        except Exception as e:
            print(" ❌")
            test_results.append(("Caching", False, str(e)))
        
        # Quick Test 4: Notification mode
        try:
            print("4️⃣ Notification mode...", end="", flush=True)
            quick_tts = ModularTTSFacade(
                base_url=self.tts.base_url, notification_mode=True, quiet_mode=True, preload=False
            )
            quick_tts.speak_text("Quick", voice, 1.0, "wav")
            print(" ✅")
            test_results.append(("Notification mode", True, None))
        except Exception as e:
            print(" ❌")
            test_results.append(("Notification mode", False, str(e)))
        
        # Summary
        passed = sum(1 for _, success, _ in test_results if success)
        failed = len(test_results) - passed
        
        print(f"\n{'='*40}")
        print(f"Quick Test Summary: {passed} passed, {failed} failed")
        
        if failed > 0:
            print("\nFailed tests:")
            for name, success, details in test_results:
                if not success:
                    print(f"  ❌ {name}: {details}")
        
        return 0 if failed == 0 else 1
    
    def run_comprehensive_test(self, voice: str, format: str) -> int:
        """
        Run comprehensive functionality tests.
        
        Args:
            voice: Voice to use
            format: Audio format
            
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        print("🧪 Running comprehensive functionality tests...")
        test_results = []
        
        # Test 1: Basic speech
        try:
            print("\n1️⃣ Testing basic speech...")
            self.tts.speak_text("Test", voice, 1.0, format)
            test_results.append(("Basic speech", True, None))
        except Exception as e:
            test_results.append(("Basic speech", False, str(e)))
        
        # Test 2: Voice blending
        try:
            print("\n2️⃣ Testing voice blending...")
            self.tts.speak_text("Blend", "af_bella+af_sky", 1.0, format)
            test_results.append(("Voice blending", True, None))
        except Exception as e:
            test_results.append(("Voice blending", False, str(e)))
        
        # Test 3: Weighted voice blending
        try:
            print("\n3️⃣ Testing weighted voice blending...")
            self.tts.speak_text("Weight", "af_bella(2)+af_sky(1)", 1.0, format)
            test_results.append(("Weighted blending", True, None))
        except Exception as e:
            test_results.append(("Weighted blending", False, str(e)))
        
        # Test 4: Different speeds
        try:
            print("\n4️⃣ Testing different speeds...")
            self.tts.speak_text("Slow", voice, 0.7, format)
            self.tts.speak_text("Fast", voice, 1.5, format)
            test_results.append(("Speed variations", True, None))
        except Exception as e:
            test_results.append(("Speed variations", False, str(e)))
        
        # Test 5: Different formats
        try:
            print("\n5️⃣ Testing different formats...")
            for fmt in ["wav", "mp3", "pcm"]:
                self.tts.speak_text("Format", voice, 1.0, fmt)
            test_results.append(("Format variations", True, None))
        except Exception as e:
            test_results.append(("Format variations", False, str(e)))
        
        # Test 6: Notification mode
        try:
            print("\n6️⃣ Testing notification mode...")
            quick_tts = ModularTTSFacade(
                base_url=self.tts.base_url, notification_mode=True, quiet_mode=True, preload=False
            )
            quick_tts.speak_text("Quick", voice, 1.0, "wav")
            test_results.append(("Notification mode", True, None))
        except Exception as e:
            test_results.append(("Notification mode", False, str(e)))
        
        # Test 7: Caching
        try:
            print("\n7️⃣ Testing cache functionality...")
            # Use generate_speech (no playback) to measure actual cache performance
            # First call - generates audio from API
            start = time.time()
            self.tts.generate_speech("Cache test", voice, 1.0, format)
            first_time = time.time() - start

            # Second call - should hit cache (much faster)
            start = time.time()
            self.tts.generate_speech("Cache test", voice, 1.0, format)
            cached_time = time.time() - start

            # Cache is working if:
            # 1. Both times < 50ms (cache was already warm from previous run), OR
            # 2. Cached time is significantly faster than first time
            if first_time < 0.05 and cached_time < 0.05:
                cache_working = True  # Already cached = cache is working
                cache_detail = f"Already cached: {first_time:.2f}s, {cached_time:.2f}s"
            else:
                cache_working = cached_time < first_time * 0.5
                cache_detail = f"First: {first_time:.2f}s, Cached: {cached_time:.2f}s"
            test_results.append(("Cache functionality", cache_working, cache_detail))
        except Exception as e:
            test_results.append(("Cache functionality", False, str(e)))
        
        # Test 8: Phonemes
        try:
            print("\n8️⃣ Testing phoneme generation...")
            phonemes, tokens = self.tts.get_phonemes("Hello world")
            test_results.append(("Phoneme generation", True, f"Phonemes: {phonemes[:20]}..."))
        except Exception as e:
            test_results.append(("Phoneme generation", False, str(e)))
        
        # Test 9: Long text chunking
        try:
            print("\n9️⃣ Testing long text chunking...")
            long_text = "This is a test of the text chunking system. It should split this text into multiple chunks if it exceeds the maximum length. " * 3
            self.tts.speak_text(long_text, voice, 1.0, format)
            test_results.append(("Long text chunking", True, None))
        except Exception as e:
            test_results.append(("Long text chunking", False, str(e)))
        
        # Test 10: Background playback
        try:
            print("\n🔟 Testing background playback...")
            self.tts.speak_text("Background", voice, 1.0, format, background=True)
            time.sleep(0.5)  # Give it time to play
            test_results.append(("Background playback", True, None))
        except Exception as e:
            test_results.append(("Background playback", False, str(e)))
        
        # Print results
        print("\n" + "="*60)
        print("📊 TEST RESULTS:")
        print("="*60)
        
        passed = 0
        failed = 0
        
        for test_name, success, details in test_results:
            if success:
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED - {details}")
                failed += 1
            if details and success:
                print(f"   Details: {details}")
        
        print("="*60)
        print(f"Summary: {passed} passed, {failed} failed")
        
        # Show cache stats
        stats = self.tts.get_stats()
        print(f"\n📈 Final Cache Stats:")
        print(f"   Items: {stats['cache']['size']}")
        print(f"   Memory: {stats['cache']['memory_mb']:.1f}MB")
        print(f"   Hit Rate: {stats['cache']['hit_rate']:.1%}")
        
        return 0 if failed == 0 else 1


def run_tests(
    tts: ModularTTSFacade,
    test_type: str,
    voice: str,
    format: str,
    server: str,
    quiet: bool,
    json_output: bool
) -> Optional[int]:
    """
    Run test operations.
    
    Args:
        tts: TTS instance
        test_type: Type of test ('basic', 'quick', 'all')
        voice: Voice to use
        format: Audio format
        server: Server URL
        quiet: Quiet mode
        json_output: Output in JSON format
        
    Returns:
        Exit code or None if no test was run
    """
    if test_type == 'basic':
        # Create a consistent test instance for all test modes
        test_tts = ModularTTSFacade(
            base_url=server, notification_mode=False, quiet_mode=True, preload=False
        )
        runner = TestRunner(test_tts)
        
        success, error_msg = runner.run_basic_test(voice, format, quiet)
        
        if json_output:
            result = {
                "success": success,
                "message": "All tests passed" if success else "Audio test failed",
                "error": error_msg
            }
            print(json.dumps(result))
        return 0 if success else 1
    
    elif test_type == 'quick':
        # Create a quieter TTS instance for testing
        test_tts = ModularTTSFacade(
            base_url=server, notification_mode=False, quiet_mode=True, preload=False
        )
        runner = TestRunner(test_tts)
        return runner.run_quick_test(voice, format)
    
    elif test_type == 'all':
        # Create a quieter TTS instance for testing
        test_tts = ModularTTSFacade(
            base_url=server, notification_mode=False, quiet_mode=True, preload=False
        )
        runner = TestRunner(test_tts)
        return runner.run_comprehensive_test(voice, format)
    
    return None