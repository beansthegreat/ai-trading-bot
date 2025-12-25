#!/usr/bin/env python3
"""
🧹 Cleanup Script: Remove Obsolete Files from Old Data System

This script removes files that are no longer needed after migrating
to the live data system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import shutil
from datetime import datetime
from pathlib import Path

class SystemCleanup:
    """Cleanup obsolete files from old data download system"""

    def __init__(self):
        self.root_dir = Path("/home/user/ai-trading-bot")
        self.removed_files = []
        self.removed_dirs = []
        self.saved_space_mb = 0

    def analyze_cleanup(self):
        """Analyze what will be removed"""
        print("\n🔍 CLEANUP ANALYSIS")
        print("=" * 70)

        # Obsolete scripts
        obsolete_scripts = [
            "scripts/collect_historical_data.py",
            "scripts/sp500_data_collector.py",
            "scripts/train_historical_models.py",
            "scripts/sp500_training_system.py",
            "scripts/run_complete_training.py",
        ]

        # Obsolete utilities
        obsolete_utils = [
            "utils/historical_trainer.py",
            "utils/data_enhancer.py",
        ]

        # Data directories to clean
        data_dirs_to_clean = [
            "data/historical",
            "data/cache",
            "data/sp500/historical",
            "data/sp500/cache",
        ]

        print("\n📝 Obsolete Scripts (will be removed):")
        for script in obsolete_scripts:
            path = self.root_dir / script
            if path.exists():
                size_kb = path.stat().st_size / 1024
                print(f"   ❌ {script} ({size_kb:.1f} KB)")
            else:
                print(f"   ⚠️  {script} (not found)")

        print("\n📝 Obsolete Utilities (will be removed):")
        for util in obsolete_utils:
            path = self.root_dir / util
            if path.exists():
                size_kb = path.stat().st_size / 1024
                print(f"   ❌ {util} ({size_kb:.1f} KB)")
            else:
                print(f"   ⚠️  {util} (not found)")

        print("\n📁 Data Directories (CSV files will be removed):")
        total_csv_size = 0
        total_csv_count = 0

        for dir_path in data_dirs_to_clean:
            full_path = self.root_dir / dir_path
            if full_path.exists():
                csv_files = list(full_path.glob("*.csv"))
                dir_size = sum(f.stat().st_size for f in csv_files)
                total_csv_size += dir_size
                total_csv_count += len(csv_files)

                if csv_files:
                    print(f"   🗑️  {dir_path}: {len(csv_files)} CSV files ({dir_size / (1024*1024):.2f} MB)")
                else:
                    print(f"   ✓  {dir_path}: empty")
            else:
                print(f"   ⚠️  {dir_path}: not found")

        print(f"\n💾 Total Space to Recover:")
        print(f"   CSV Files: {total_csv_count} files, {total_csv_size / (1024*1024):.2f} MB")

        print(f"\n✅ Will Keep:")
        print(f"   ✓ All model files (data/models/)")
        print(f"   ✓ All starter scripts (start_*.py)")
        print(f"   ✓ All monitoring scripts (*_monitor.py)")
        print(f"   ✓ Migration script (migrate_to_live_data.py)")
        print(f"   ✓ Backtesting and utility scripts")

        return total_csv_size / (1024*1024)

    def remove_obsolete_scripts(self):
        """Remove obsolete data collection scripts"""
        print("\n🗑️  Removing Obsolete Scripts...")
        print("=" * 70)

        obsolete_files = [
            "scripts/collect_historical_data.py",
            "scripts/sp500_data_collector.py",
            "scripts/train_historical_models.py",
            "scripts/sp500_training_system.py",
            "scripts/run_complete_training.py",
            "utils/historical_trainer.py",
            "utils/data_enhancer.py",
        ]

        for file_path in obsolete_files:
            full_path = self.root_dir / file_path
            if full_path.exists():
                size_kb = full_path.stat().st_size / 1024
                try:
                    full_path.unlink()
                    self.removed_files.append(str(file_path))
                    print(f"   ✅ Removed: {file_path} ({size_kb:.1f} KB)")
                except Exception as e:
                    print(f"   ❌ Failed to remove {file_path}: {e}")
            else:
                print(f"   ⚠️  Not found: {file_path}")

    def clean_data_directories(self):
        """Clean CSV files from data directories"""
        print("\n🗑️  Cleaning Data Directories...")
        print("=" * 70)

        data_dirs = [
            "data/historical",
            "data/cache",
            "data/sp500/historical",
            "data/sp500/cache",
        ]

        total_removed = 0
        total_size = 0

        for dir_path in data_dirs:
            full_path = self.root_dir / dir_path
            if full_path.exists():
                csv_files = list(full_path.glob("*.csv"))

                if csv_files:
                    print(f"\n   📁 {dir_path}:")
                    for csv_file in csv_files:
                        size_mb = csv_file.stat().st_size / (1024 * 1024)
                        try:
                            csv_file.unlink()
                            total_removed += 1
                            total_size += size_mb
                            print(f"      ✅ Removed: {csv_file.name} ({size_mb:.2f} MB)")
                        except Exception as e:
                            print(f"      ❌ Failed: {csv_file.name}: {e}")
                else:
                    print(f"   ✓ {dir_path}: already clean")

        self.saved_space_mb = total_size
        print(f"\n   💾 Total: Removed {total_removed} CSV files, saved {total_size:.2f} MB")

    def remove_empty_directories(self):
        """Remove empty data directories"""
        print("\n🗑️  Removing Empty Directories...")
        print("=" * 70)

        dirs_to_check = [
            "data/historical",
            "data/cache",
            "data/sp500/historical",
            "data/sp500/cache",
        ]

        for dir_path in dirs_to_check:
            full_path = self.root_dir / dir_path
            if full_path.exists() and not any(full_path.iterdir()):
                try:
                    full_path.rmdir()
                    self.removed_dirs.append(str(dir_path))
                    print(f"   ✅ Removed empty directory: {dir_path}")
                except Exception as e:
                    print(f"   ⚠️  Could not remove {dir_path}: {e}")

    def update_gitignore(self):
        """Update .gitignore to reflect new structure"""
        print("\n📝 Updating .gitignore...")
        print("=" * 70)

        gitignore_path = self.root_dir / ".gitignore"

        # Lines to add
        new_lines = [
            "\n# Old data system (obsolete after live data migration)",
            "data/historical/",
            "data/cache/",
            "data/sp500/historical/",
            "data/sp500/cache/",
            "historical_training_data/",
            "training_cache/",
            "\n# Keep models but ignore large files",
            "data/models/*.joblib",
            "*.pkl",
        ]

        try:
            if gitignore_path.exists():
                with open(gitignore_path, 'r') as f:
                    content = f.read()

                # Check if already updated
                if "Old data system" not in content:
                    with open(gitignore_path, 'a') as f:
                        f.write('\n'.join(new_lines))
                    print("   ✅ Updated .gitignore")
                else:
                    print("   ✓ .gitignore already updated")
            else:
                with open(gitignore_path, 'w') as f:
                    f.write('\n'.join(new_lines))
                print("   ✅ Created .gitignore")

        except Exception as e:
            print(f"   ⚠️  Failed to update .gitignore: {e}")

    def create_cleanup_summary(self):
        """Create summary of cleanup"""
        print("\n" + "=" * 70)
        print("📊 CLEANUP SUMMARY")
        print("=" * 70)

        print(f"\n✅ Files Removed: {len(self.removed_files)}")
        for f in self.removed_files:
            print(f"   • {f}")

        if self.removed_dirs:
            print(f"\n✅ Directories Removed: {len(self.removed_dirs)}")
            for d in self.removed_dirs:
                print(f"   • {d}")

        print(f"\n💾 Space Saved: {self.saved_space_mb:.2f} MB")

        print("\n✨ Your bot is now clean and optimized!")
        print("   • No more bulk data downloads")
        print("   • Only essential files remain")
        print("   • Live data system active")

    def run_cleanup(self):
        """Run complete cleanup process"""
        print("\n" + "=" * 70)
        print("🧹 SYSTEM CLEANUP - Old Data Download System")
        print("=" * 70)
        print("\nThis will remove obsolete files from the old data system.")
        print("All files will be permanently deleted.")

        # Analyze first
        space_to_save = self.analyze_cleanup()

        print(f"\n⚠️  Total space to recover: {space_to_save:.2f} MB")
        response = input("\nProceed with cleanup? (yes/no): ").strip().lower()

        if response != 'yes':
            print("\n❌ Cleanup cancelled")
            return

        # Execute cleanup
        self.remove_obsolete_scripts()
        self.clean_data_directories()
        self.remove_empty_directories()
        self.update_gitignore()
        self.create_cleanup_summary()

        print("\n✅ Cleanup completed successfully!")


def main():
    """Main function"""
    cleanup = SystemCleanup()

    print("\n🧹 System Cleanup Tool")
    print("=" * 70)
    print("\nOptions:")
    print("1. Run full cleanup (recommended)")
    print("2. Analyze only (no changes)")
    print("3. Remove scripts only")
    print("4. Clean data only")
    print("5. Exit")

    choice = input("\nSelect option (1-5): ").strip()

    if choice == '1':
        cleanup.run_cleanup()
    elif choice == '2':
        cleanup.analyze_cleanup()
    elif choice == '3':
        cleanup.remove_obsolete_scripts()
        cleanup.create_cleanup_summary()
    elif choice == '4':
        cleanup.clean_data_directories()
        cleanup.remove_empty_directories()
        cleanup.create_cleanup_summary()
    elif choice == '5':
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()
