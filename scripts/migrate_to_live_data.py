#!/usr/bin/env python3
"""
🔄 Migration Script: Transition from Downloaded Data to Live API Data

This script helps you migrate from the old system (downloading large data chunks)
to the new live data system (on-demand API access with caching).
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import shutil
from datetime import datetime
from typing import Dict, Any
from utils.logger import trading_logger
from utils.live_data_manager import live_data_manager
from config import config

class LiveDataMigration:
    """Migration helper for transitioning to live data system"""

    def __init__(self):
        self.data_dir = "data"
        self.backup_dir = "data_backup"
        self.migration_log = []

    def analyze_current_storage(self) -> Dict[str, Any]:
        """Analyze current data storage"""
        print("📊 Analyzing Current Data Storage...")
        print("=" * 60)

        total_size = 0
        file_count = 0
        directories = []

        # Walk through data directory
        if os.path.exists(self.data_dir):
            for root, dirs, files in os.walk(self.data_dir):
                for file in files:
                    if file.endswith('.csv'):
                        filepath = os.path.join(root, file)
                        size = os.path.getsize(filepath)
                        total_size += size
                        file_count += 1

                for dir in dirs:
                    if dir not in directories:
                        directories.append(dir)

        total_size_mb = total_size / (1024 * 1024)

        print(f"\n📦 Current Storage Statistics:")
        print(f"   Total Size: {total_size_mb:.2f} MB")
        print(f"   CSV Files: {file_count}")
        print(f"   Directories: {len(directories)}")
        print(f"   Directories: {', '.join(directories)}")

        print(f"\n💡 With Live Data System:")
        print(f"   Disk Usage: ~0 MB (data cached in RAM)")
        print(f"   Potential Savings: {total_size_mb:.2f} MB")
        print(f"   Data Freshness: Always current (5min cache)")

        return {
            'total_size_mb': total_size_mb,
            'file_count': file_count,
            'directories': directories,
            'savings_mb': total_size_mb
        }

    def backup_existing_data(self) -> bool:
        """Create backup of existing data"""
        print(f"\n💾 Creating Backup...")
        print("=" * 60)

        try:
            if os.path.exists(self.data_dir):
                # Create backup with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{self.backup_dir}_{timestamp}"

                print(f"   Backing up {self.data_dir} to {backup_path}...")
                shutil.copytree(self.data_dir, backup_path)

                print(f"   ✅ Backup created: {backup_path}")
                self.migration_log.append(f"Backup created: {backup_path}")
                return True
            else:
                print(f"   ℹ️  No data directory found - nothing to backup")
                return True

        except Exception as e:
            print(f"   ❌ Backup failed: {e}")
            return False

    def test_live_data_access(self) -> bool:
        """Test live data API access"""
        print(f"\n🧪 Testing Live Data Access...")
        print("=" * 60)

        test_symbols = config.SYMBOLS[:3]  # Test with first 3 symbols
        print(f"   Testing with symbols: {', '.join(test_symbols)}")

        success_count = 0
        for symbol in test_symbols:
            try:
                print(f"\n   📊 Fetching {symbol}...", end=" ")
                df = live_data_manager.get_live_data(
                    symbol,
                    timeframe='1D',
                    lookback_bars=100,
                    force_refresh=True
                )

                if not df.empty:
                    print(f"✅ ({len(df)} bars)")
                    success_count += 1
                else:
                    print(f"❌ (no data)")

            except Exception as e:
                print(f"❌ Error: {e}")

        print(f"\n   Results: {success_count}/{len(test_symbols)} successful")

        if success_count == len(test_symbols):
            print(f"   ✅ Live data access working perfectly!")
            return True
        else:
            print(f"   ⚠️  Some symbols failed - check your API access")
            return False

    def update_configuration(self) -> bool:
        """Update configuration for live data"""
        print(f"\n⚙️  Updating Configuration...")
        print("=" * 60)

        try:
            env_file = ".env"

            # Check if .env exists
            if os.path.exists(env_file):
                print(f"   Found {env_file}")

                # Read current content
                with open(env_file, 'r') as f:
                    content = f.read()

                # Check if USE_LIVE_DATA already set
                if 'USE_LIVE_DATA' in content:
                    print(f"   ℹ️  USE_LIVE_DATA already configured")
                else:
                    # Append live data configuration
                    with open(env_file, 'a') as f:
                        f.write("\n# Live Data Configuration\n")
                        f.write("USE_LIVE_DATA=True\n")
                        f.write("LIVE_DATA_CACHE_SIZE=100\n")
                        f.write("LIVE_DATA_TTL_MINUTES=5\n")
                        f.write("USE_ALPACA_DATA=False\n")
                        f.write("DEFAULT_LOOKBACK_BARS=100\n")

                    print(f"   ✅ Added live data configuration to {env_file}")

            else:
                # Create new .env file
                with open(env_file, 'w') as f:
                    f.write("# Live Data Configuration\n")
                    f.write("USE_LIVE_DATA=True\n")
                    f.write("LIVE_DATA_CACHE_SIZE=100\n")
                    f.write("LIVE_DATA_TTL_MINUTES=5\n")
                    f.write("USE_ALPACA_DATA=False\n")
                    f.write("DEFAULT_LOOKBACK_BARS=100\n")

                print(f"   ✅ Created {env_file} with live data configuration")

            self.migration_log.append("Configuration updated")
            return True

        except Exception as e:
            print(f"   ❌ Configuration update failed: {e}")
            return False

    def cleanup_old_data(self, keep_backup: bool = True) -> bool:
        """Clean up old CSV data files"""
        print(f"\n🗑️  Cleaning Up Old Data...")
        print("=" * 60)

        try:
            if os.path.exists(self.data_dir):
                csv_files = []

                # Find all CSV files
                for root, dirs, files in os.walk(self.data_dir):
                    for file in files:
                        if file.endswith('.csv'):
                            csv_files.append(os.path.join(root, file))

                print(f"   Found {len(csv_files)} CSV files")

                if csv_files:
                    response = input(f"\n   ⚠️  Delete {len(csv_files)} CSV files? (yes/no): ").strip().lower()

                    if response == 'yes':
                        deleted_count = 0
                        for filepath in csv_files:
                            try:
                                os.remove(filepath)
                                deleted_count += 1
                            except Exception as e:
                                print(f"   ⚠️  Failed to delete {filepath}: {e}")

                        print(f"   ✅ Deleted {deleted_count} CSV files")

                        # Remove empty directories
                        for root, dirs, files in os.walk(self.data_dir, topdown=False):
                            for dir in dirs:
                                dirpath = os.path.join(root, dir)
                                if not os.listdir(dirpath):
                                    os.rmdir(dirpath)
                                    print(f"   🗑️  Removed empty directory: {dirpath}")

                        self.migration_log.append(f"Deleted {deleted_count} CSV files")
                        return True
                    else:
                        print(f"   ℹ️  Keeping CSV files (you can delete them manually later)")
                        return True
                else:
                    print(f"   ℹ️  No CSV files to clean up")
                    return True

            else:
                print(f"   ℹ️  Data directory doesn't exist")
                return True

        except Exception as e:
            print(f"   ❌ Cleanup failed: {e}")
            return False

    def show_cache_status(self):
        """Show current cache status"""
        print(f"\n📊 Live Data Cache Status:")
        print("=" * 60)

        status = live_data_manager.get_status()

        print(f"\n   Cache Statistics:")
        print(f"      Size: {status['cache']['size']}/{status['cache']['max_size']}")
        print(f"      Hit Rate: {status['cache']['hit_rate']:.1f}%")
        print(f"      Total Requests: {status['cache']['total_requests']}")

        print(f"\n   API Statistics:")
        print(f"      API Calls: {status['api_calls']}")
        print(f"      Data Fetched: {status['total_data_fetched_mb']} MB")

        print(f"\n   Data Sources:")
        print(f"      Alpaca: {'Enabled' if status['data_sources']['alpaca_enabled'] else 'Disabled'}")
        print(f"      yfinance: {'Enabled' if status['data_sources']['yfinance_enabled'] else 'Disabled'}")

    def run_full_migration(self):
        """Run complete migration process"""
        print("\n" + "=" * 60)
        print("🚀 MIGRATION TO LIVE DATA SYSTEM")
        print("=" * 60)

        print("\nThis migration will:")
        print("  1. Analyze your current data storage")
        print("  2. Create a backup of existing data")
        print("  3. Test live data API access")
        print("  4. Update configuration")
        print("  5. Optionally clean up old CSV files")

        response = input("\nProceed with migration? (yes/no): ").strip().lower()

        if response != 'yes':
            print("\n❌ Migration cancelled")
            return

        # Step 1: Analyze
        analysis = self.analyze_current_storage()

        # Step 2: Backup
        if not self.backup_existing_data():
            print("\n❌ Migration failed - backup unsuccessful")
            return

        # Step 3: Test
        if not self.test_live_data_access():
            print("\n⚠️  Warning: Some API tests failed")
            response = input("Continue anyway? (yes/no): ").strip().lower()
            if response != 'yes':
                print("\n❌ Migration cancelled")
                return

        # Step 4: Update config
        if not self.update_configuration():
            print("\n❌ Migration failed - configuration update unsuccessful")
            return

        # Step 5: Show cache status
        self.show_cache_status()

        # Step 6: Cleanup (optional)
        print("\n")
        response = input("Do you want to clean up old CSV files now? (yes/no): ").strip().lower()

        if response == 'yes':
            self.cleanup_old_data()
        else:
            print("\n   ℹ️  You can run cleanup later using this script")

        # Summary
        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETED!")
        print("=" * 60)

        print("\nMigration Summary:")
        for log_entry in self.migration_log:
            print(f"   ✅ {log_entry}")

        print("\n📝 Next Steps:")
        print("   1. Restart your trading bot")
        print("   2. Monitor cache performance with cache_status option")
        print("   3. Old data is backed up if you need to revert")

        print("\n💡 Benefits:")
        print(f"   • Saved {analysis['savings_mb']:.2f} MB of disk space")
        print(f"   • Data is now always fresh (5min cache)")
        print(f"   • Faster startup (no large data loads)")
        print(f"   • On-demand data fetching")


def main():
    """Main function"""
    migration = LiveDataMigration()

    print("\n📊 Live Data Migration Tool")
    print("=" * 60)
    print("\nOptions:")
    print("1. Run full migration")
    print("2. Analyze current storage only")
    print("3. Test live data access")
    print("4. Show cache status")
    print("5. Cleanup old data only")
    print("6. Exit")

    choice = input("\nSelect option (1-6): ").strip()

    if choice == '1':
        migration.run_full_migration()
    elif choice == '2':
        migration.analyze_current_storage()
    elif choice == '3':
        migration.test_live_data_access()
    elif choice == '4':
        migration.show_cache_status()
    elif choice == '5':
        migration.cleanup_old_data()
    elif choice == '6':
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()
