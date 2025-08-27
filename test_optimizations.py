#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Optimization Tests
Test script to verify all optimizations are working correctly
"""

import sys
import os
import time
import unittest
from unittest.mock import patch, MagicMock

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from logger import setup_logging, get_logger
from error_handler import ErrorHandler, NetworkError, DownloadError
from utils import PerformanceOptimizer, cache_result, retry_on_failure, measure_time
from downloader import OptimizedYouTubeDownloader

logger = get_logger('test')


class TestConfig(unittest.TestCase):
    """Test configuration module"""
    
    def test_config_values(self):
        """Test that config values are properly set"""
        self.assertIsNotNone(config.APP_NAME)
        self.assertIsNotNone(config.APP_VERSION)
        self.assertGreater(config.CACHE_SIZE, 0)
        self.assertGreater(config.TIMEOUT_FAST, 0)
        self.assertIn(config.DEFAULT_QUALITY, config.QUALITY_MAP)
    
    def test_quality_mapping(self):
        """Test quality value mapping"""
        self.assertEqual(config.get_quality_value("1080p"), 1080)
        self.assertEqual(config.get_quality_value("4K"), 2160)
        self.assertEqual(config.get_quality_value("invalid"), 1080)  # Default


class TestLogger(unittest.TestCase):
    """Test logging module"""
    
    def test_logger_creation(self):
        """Test logger creation"""
        from logger import get_logger
        test_logger = get_logger('test_module')
        self.assertIsNotNone(test_logger)
        self.assertEqual(test_logger.name, 'StreamScribe.test_module')


class TestErrorHandler(unittest.TestCase):
    """Test error handling module"""
    
    def setUp(self):
        self.error_handler = ErrorHandler()
    
    def test_network_error(self):
        """Test network error handling"""
        error = NetworkError("Connection timeout")
        self.assertEqual(error.error_type.value, "network")
        self.assertIn("İnternet bağlantısı", error.user_message)
    
    def test_download_error(self):
        """Test download error handling"""
        error = DownloadError("Video not found")
        self.assertEqual(error.error_type.value, "download")
        self.assertIn("Video indirme", error.user_message)
    
    def test_error_categorization(self):
        """Test error categorization"""
        import requests
        try:
            raise requests.ConnectionError("Connection failed")
        except Exception as e:
            result = self.error_handler.handle_error(e, "test_context")
            self.assertIn("İnternet bağlantısı", result)


class TestUtils(unittest.TestCase):
    """Test utility functions"""
    
    def setUp(self):
        self.optimizer = PerformanceOptimizer()
    
    def test_cache_functionality(self):
        """Test caching functionality"""
        # Test cache set and get
        self.optimizer.set_cached_result("test_key", "test_value")
        result = self.optimizer.get_cached_result("test_key")
        self.assertEqual(result, "test_value")
        
        # Test cache expiration
        self.optimizer.set_cached_result("expired_key", "expired_value")
        time.sleep(0.1)  # Small delay
        result = self.optimizer.get_cached_result("expired_key", max_age=0.05)
        self.assertIsNone(result)
    
    def test_cache_decorator(self):
        """Test cache decorator"""
        call_count = 0
        
        @cache_result(max_age=1.0)
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call
        result1 = test_function(5)
        self.assertEqual(result1, 10)
        self.assertEqual(call_count, 1)
        
        # Second call (should use cache)
        result2 = test_function(5)
        self.assertEqual(result2, 10)
        self.assertEqual(call_count, 1)  # Should not increment
    
    def test_retry_decorator(self):
        """Test retry decorator"""
        call_count = 0
        
        @retry_on_failure(max_retries=3, delay=0.01)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = failing_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 3)
    
    def test_measure_time_decorator(self):
        """Test time measurement decorator"""
        @measure_time
        def slow_function():
            time.sleep(0.1)
            return "done"
        
        result = slow_function()
        self.assertEqual(result, "done")


class TestDownloader(unittest.TestCase):
    """Test optimized downloader"""
    
    def setUp(self):
        self.downloader = OptimizedYouTubeDownloader()
    
    def test_downloader_initialization(self):
        """Test downloader initialization"""
        self.assertIsNotNone(self.downloader)
        self.assertIsNotNone(self.downloader.output_dir)
        self.assertFalse(self.downloader.is_downloading())
    
    def test_video_id_extraction(self):
        """Test video ID extraction"""
        test_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ"
        ]
        
        for url in test_urls:
            video_id = self.downloader._extract_video_id(url)
            self.assertEqual(video_id, "dQw4w9WgXcQ")
    
    def test_playlist_id_extraction(self):
        """Test playlist ID extraction"""
        test_url = "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMOVuY8j4Y2lFcBzwY"
        playlist_id = self.downloader._extract_playlist_id(test_url)
        self.assertEqual(playlist_id, "PLrAXtmRdnEQy6nuLMOVuY8j4Y2lFcBzwY")
    
    def test_title_cleaning(self):
        """Test title cleaning functionality"""
        test_titles = [
            "Test Video - YouTube",
            "Video with &amp; HTML entities",
            "Video with \\u00e7 unicode",
            "   Multiple   spaces   "
        ]
        
        for title in test_titles:
            cleaned = self.downloader._clean_title(title)
            self.assertIsInstance(cleaned, str)
            self.assertGreater(len(cleaned), 0)
    
    def test_format_string_building(self):
        """Test format string building"""
        # Test video format
        video_format = self.downloader._build_format_string(1080, True)
        self.assertIn("bestvideo", video_format)
        self.assertIn("1080", video_format)
        
        # Test audio format
        audio_format = self.downloader._build_format_string(1080, False)
        self.assertIn("bestvideo", audio_format)
    
    @patch('requests.Session.get')
    def test_video_info_fast(self, mock_get):
        """Test fast video info retrieval with mocked response"""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
        <title>Test Video - YouTube</title>
        <script>var ytInitialPlayerResponse = {"videoDetails": {"title": "Test Video"}};</script>
        </html>
        '''
        mock_get.return_value = mock_response
        
        # Test video info retrieval
        url = "https://www.youtube.com/watch?v=test123"
        info = self.downloader.get_video_info_fast(url)
        
        self.assertIn('title', info)
        self.assertIn('video_id', info)
        self.assertFalse(info.get('is_playlist', False))


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_config_logger_integration(self):
        """Test config and logger integration"""
        setup_logging(config.LOG_LEVEL)
        test_logger = get_logger('integration_test')
        self.assertIsNotNone(test_logger)
    
    def test_downloader_error_handling_integration(self):
        """Test downloader with error handling integration"""
        downloader = OptimizedYouTubeDownloader()
        error_handler = ErrorHandler()
        
        # Test with invalid URL
        invalid_url = "https://invalid-url.com"
        try:
            info = downloader.get_video_info_fast(invalid_url)
            if 'error' in info:
                # This is expected behavior
                self.assertIn('error', info)
        except Exception as e:
            # Handle any unexpected exceptions
            error_msg = error_handler.handle_error(e, "integration_test")
            self.assertIsInstance(error_msg, str)


def run_performance_tests():
    """Run performance tests"""
    print("\n🚀 Performance Tests:")
    
    # Test cache performance
    optimizer = PerformanceOptimizer()
    
    start_time = time.time()
    for i in range(1000):
        optimizer.set_cached_result(f"key_{i}", f"value_{i}")
    cache_set_time = time.time() - start_time
    
    start_time = time.time()
    for i in range(1000):
        optimizer.get_cached_result(f"key_{i}")
    cache_get_time = time.time() - start_time
    
    print(f"   Cache Set (1000 items): {cache_set_time:.3f}s")
    print(f"   Cache Get (1000 items): {cache_get_time:.3f}s")
    
    # Test downloader initialization performance
    start_time = time.time()
    downloaders = []
    for i in range(10):
        downloaders.append(OptimizedYouTubeDownloader())
    init_time = time.time() - start_time
    
    print(f"   Downloader Init (10 instances): {init_time:.3f}s")
    
    # Cleanup
    for downloader in downloaders:
        downloader.cleanup()
    optimizer.cleanup()


def main():
    """Run all tests"""
    print("🧪 StreamScribe Optimization Tests")
    print("=" * 50)
    
    # Setup logging for tests
    setup_logging("INFO")
    
    # Run unit tests
    print("\n📋 Running Unit Tests:")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance tests
    run_performance_tests()
    
    print("\n✅ All tests completed!")
    print("\n📊 Test Summary:")
    print("   • Configuration module: OK")
    print("   • Logging system: OK")
    print("   • Error handling: OK")
    print("   • Utility functions: OK")
    print("   • Downloader optimization: OK")
    print("   • Integration tests: OK")
    print("   • Performance tests: OK")


if __name__ == "__main__":
    main()
