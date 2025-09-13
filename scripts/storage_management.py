#!/usr/bin/env python3
"""
💾 Storage Management Script
Manage and optimize storage usage for the trading bot
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage_optimizer import StorageOptimizer
from utils.logger import trading_logger

def main():
    """Main storage management function"""
    print("💾 Storage Management System")
    print("=" * 50)
    
    optimizer = StorageOptimizer()
    
    while True:
        print("\nSelect operation:")
        print("1. Analyze storage usage")
        print("2. Run storage optimization")
        print("3. Clean up old files")
        print("4. Compress large files")
        print("5. Set retention policies")
        print("6. Show storage status")
        print("7. Exit")
        
        choice = input("\nEnter choice (1-7): ").strip()
        
        if choice == '1':
            print("\n📊 Analyzing storage usage...")
            analysis = optimizer.analyze_storage_usage()
            
            print(f"\n📈 Storage Analysis Results:")
            print(f"   Total Size: {analysis.get('total_size_gb', 0):.2f} GB")
            print(f"   Max Storage: {optimizer.max_storage_gb} GB")
            print(f"   Usage: {(analysis.get('total_size_gb', 0) / optimizer.max_storage_gb) * 100:.1f}%")
            
            print(f"\n📁 Directory Breakdown:")
            for directory, stats in analysis.get('directory_breakdown', {}).items():
                print(f"   {directory}: {stats['size_gb']:.2f} GB ({stats['file_count']} files)")
            
            print(f"\n📄 File Type Breakdown:")
            for ext, stats in analysis.get('file_type_breakdown', {}).items():
                print(f"   {ext}: {stats['count']} files, {stats['total_size_gb']:.2f} GB")
            
            print(f"\n🔍 Largest Files:")
            for file_info in analysis.get('largest_files', [])[:5]:
                print(f"   {file_info['path']}: {file_info['size_gb']:.2f} GB")
            
            print(f"\n💡 Compression Opportunities:")
            for opp in analysis.get('compression_opportunities', [])[:5]:
                estimated_savings = opp['size_gb'] * opp['estimated_compression']
                print(f"   {opp['path']}: {estimated_savings:.2f} GB savings")
        
        elif choice == '2':
            print("\n🔄 Running complete storage optimization...")
            results = optimizer.optimize_storage()
            
            print(f"\n✅ Optimization Results:")
            print(f"   Total Space Saved: {results['total_space_saved_gb']:.2f} GB")
            print(f"   Files Compressed: {results['compression'].get('files_compressed', 0)}")
            print(f"   Files Deleted: {results['cleanup'].get('files_deleted', 0)}")
            print(f"   Compression Errors: {len(results['compression'].get('compression_errors', []))}")
            print(f"   Cleanup Errors: {len(results['cleanup'].get('cleanup_errors', []))}")
        
        elif choice == '3':
            print("\n🗑️ Cleaning up old files...")
            results = optimizer.cleanup_old_files()
            
            print(f"\n✅ Cleanup Results:")
            print(f"   Files Deleted: {results['files_deleted']}")
            print(f"   Space Freed: {results['space_freed_gb']:.2f} GB")
            print(f"   Errors: {len(results['cleanup_errors'])}")
        
        elif choice == '4':
            print("\n📦 Compressing large files...")
            
            # Get compression opportunities
            analysis = optimizer.analyze_storage_usage()
            opportunities = analysis.get('compression_opportunities', [])
            
            if opportunities:
                print(f"   Found {len(opportunities)} compression opportunities")
                
                # Compress top 10 largest files
                top_files = [opp['path'] for opp in opportunities[:10]]
                results = optimizer.compress_files(top_files)
                
                print(f"\n✅ Compression Results:")
                print(f"   Files Compressed: {results['files_compressed']}")
                print(f"   Space Saved: {results['space_saved_gb']:.2f} GB")
                print(f"   Errors: {len(results['compression_errors'])}")
            else:
                print("   No compression opportunities found")
        
        elif choice == '5':
            print("\n⚙️ Current Retention Policies:")
            for policy, days in optimizer.retention_policies.items():
                print(f"   {policy}: {days} days")
            
            print("\nSet new retention policy:")
            policy_name = input("   Policy name: ").strip()
            try:
                days = int(input("   Days: ").strip())
                optimizer.set_retention_policy(policy_name, days)
                print(f"   ✅ Policy updated: {policy_name} = {days} days")
            except ValueError:
                print("   ❌ Invalid number of days")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        elif choice == '6':
            print("\n📊 Storage Status:")
            status = optimizer.get_storage_status()
            
            print(f"   Total Size: {status['storage_analysis'].get('total_size_gb', 0):.2f} GB")
            print(f"   Max Storage: {status['max_storage_gb']} GB")
            print(f"   Usage: {status['storage_usage_percent']:.1f}%")
            print(f"   Compression Enabled: {status['optimization_enabled']['compression']}")
            print(f"   Cleanup Enabled: {status['optimization_enabled']['cleanup']}")
            print(f"   Files Compressed: {status['storage_stats']['files_compressed']}")
            print(f"   Files Deleted: {status['storage_stats']['files_deleted']}")
            print(f"   Last Cleanup: {status['storage_stats']['last_cleanup']}")
        
        elif choice == '7':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
