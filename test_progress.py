#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Progress Bar Test Script
Test the progress bar functionality with simulated download data
"""

import time
import threading
from gui import StreamScribeOptimizedGUI

def test_progress_bar():
    """Test progress bar with simulated data"""
    print("🚀 Progress bar test başlatılıyor...")
    
    # GUI'yi başlat
    app = StreamScribeOptimizedGUI()
    
    # Simüle edilmiş progress data
    test_data = [
        {'status': 'downloading', '_percent_str': '10%', 'speed': 1024*1024, 'eta': 30, 'downloaded_bytes': 10*1024*1024, 'total_bytes': 100*1024*1024},
        {'status': 'downloading', '_percent_str': '25%', 'speed': 1024*1024, 'eta': 25, 'downloaded_bytes': 25*1024*1024, 'total_bytes': 100*1024*1024},
        {'status': 'downloading', '_percent_str': '50%', 'speed': 1024*1024, 'eta': 20, 'downloaded_bytes': 50*1024*1024, 'total_bytes': 100*1024*1024},
        {'status': 'downloading', '_percent_str': '75%', 'speed': 1024*1024, 'eta': 10, 'downloaded_bytes': 75*1024*1024, 'total_bytes': 100*1024*1024},
        {'status': 'downloading', '_percent_str': '90%', 'speed': 1024*1024, 'eta': 5, 'downloaded_bytes': 90*1024*1024, 'total_bytes': 100*1024*1024},
        {'status': 'finished', '_percent_str': '100%', 'speed': 0, 'eta': 0, 'downloaded_bytes': 100*1024*1024, 'total_bytes': 100*1024*1024},
    ]
    
    def simulate_progress():
        """Simulate progress updates"""
        for i, data in enumerate(test_data):
            print(f"📊 Progress update {i+1}: {data}")
            app._progress_callback(data)
            time.sleep(2)  # 2 saniye bekle
        
        print("✅ Progress test tamamlandı!")
    
    # Progress simulation'ı ayrı thread'de başlat
    progress_thread = threading.Thread(target=simulate_progress, daemon=True)
    progress_thread.start()
    
    # GUI'yi çalıştır
    app.run()

if __name__ == "__main__":
    test_progress_bar()
