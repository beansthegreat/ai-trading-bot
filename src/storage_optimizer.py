#!/usr/bin/env python3
"""
💾 Storage Optimization System
Manages and optimizes storage usage for the trading bot
"""

import os
import shutil
import gzip
import pickle
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

from utils.logger import trading_logger
from config import config

class StorageOptimizer:
    """Storage optimization and management system"""
    
    def __init__(self):
        self.name = "Storage Optimization System"
        self.description = "Manages and optimizes storage usage"
        
        # Storage paths
        self.data_dir = "data"
        self.sp500_dir = f"{self.data_dir}/sp500"
        self.models_dir = f"{self.sp500_dir}/models"
        self.historical_dir = f"{self.sp500_dir}/historical"
        self.cache_dir = f"{self.sp500_dir}/cache"
        self.logs_dir = "logs"
        
        # Storage configuration
        self.max_storage_gb = 50  # Maximum storage in GB
        self.compression_enabled = True
        self.cleanup_enabled = True
        
        # Retention policies
        self.retention_policies = {
            'historical_data_days': 1095,  # 3 years
            'model_files_days': 30,        # 30 days
            'cache_files_days': 7,         # 7 days
            'log_files_days': 30,          # 30 days
            'training_data_days': 90,      # 90 days
            'backup_files_days': 7         # 7 days
        }
        
        # Compression settings
        self.compression_settings = {
            'csv_compression': 'gzip',
            'json_compression': 'gzip',
            'pickle_compression': 'gzip',
            'model_compression': 'gzip'
        }
        
        # Performance tracking
        self.storage_stats = {
            'total_size_gb': 0,
            'compressed_size_gb': 0,
            'compression_ratio': 0,
            'files_compressed': 0,
            'files_deleted': 0,
            'last_cleanup': None
        }
        
        trading_logger.info("Storage optimizer initialized")
    
    def analyze_storage_usage(self) -> Dict[str, Any]:
        """Analyze current storage usage"""
        try:
            storage_analysis = {
                'total_size_gb': 0,
                'directory_breakdown': {},
                'file_type_breakdown': {},
                'largest_files': [],
                'oldest_files': [],
                'compression_opportunities': []
            }
            
            # Analyze each directory
            for directory in [self.data_dir, self.sp500_dir, self.models_dir, 
                            self.historical_dir, self.cache_dir, self.logs_dir]:
                if os.path.exists(directory):
                    dir_size = self._get_directory_size(directory)
                    storage_analysis['directory_breakdown'][directory] = {
                        'size_gb': dir_size,
                        'file_count': self._count_files(directory)
                    }
                    storage_analysis['total_size_gb'] += dir_size
            
            # Analyze file types
            storage_analysis['file_type_breakdown'] = self._analyze_file_types()
            
            # Find largest files
            storage_analysis['largest_files'] = self._find_largest_files()
            
            # Find oldest files
            storage_analysis['oldest_files'] = self._find_oldest_files()
            
            # Find compression opportunities
            storage_analysis['compression_opportunities'] = self._find_compression_opportunities()
            
            # Update stats
            self.storage_stats['total_size_gb'] = storage_analysis['total_size_gb']
            
            trading_logger.info("Storage analysis completed", 
                               total_size_gb=storage_analysis['total_size_gb'])
            
            return storage_analysis
            
        except Exception as e:
            trading_logger.error(f"Storage analysis failed: {e}")
            return {}
    
    def _get_directory_size(self, directory: str) -> float:
        """Get directory size in GB"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception as e:
            trading_logger.warning(f"Failed to get size for {directory}: {e}")
        
        return total_size / (1024**3)  # Convert to GB
    
    def _count_files(self, directory: str) -> int:
        """Count files in directory"""
        count = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                count += len(filenames)
        except Exception as e:
            trading_logger.warning(f"Failed to count files in {directory}: {e}")
        
        return count
    
    def _analyze_file_types(self) -> Dict[str, Dict[str, Any]]:
        """Analyze file types and their storage usage"""
        file_types = {}
        
        try:
            for root, dirs, files in os.walk(self.data_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        file_ext = os.path.splitext(file)[1].lower()
                        
                        if file_ext not in file_types:
                            file_types[file_ext] = {
                                'count': 0,
                                'total_size_gb': 0,
                                'avg_size_mb': 0
                            }
                        
                        file_types[file_ext]['count'] += 1
                        file_types[file_ext]['total_size_gb'] += file_size / (1024**3)
            
            # Calculate averages
            for ext, stats in file_types.items():
                if stats['count'] > 0:
                    stats['avg_size_mb'] = (stats['total_size_gb'] * 1024) / stats['count']
            
        except Exception as e:
            trading_logger.error(f"File type analysis failed: {e}")
        
        return file_types
    
    def _find_largest_files(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Find largest files"""
        largest_files = []
        
        try:
            for root, dirs, files in os.walk(self.data_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        largest_files.append({
                            'path': file_path,
                            'size_gb': file_size / (1024**3),
                            'modified': datetime.fromtimestamp(os.path.getmtime(file_path))
                        })
            
            # Sort by size and return top N
            largest_files.sort(key=lambda x: x['size_gb'], reverse=True)
            return largest_files[:limit]
            
        except Exception as e:
            trading_logger.error(f"Failed to find largest files: {e}")
            return []
    
    def _find_oldest_files(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Find oldest files"""
        oldest_files = []
        
        try:
            for root, dirs, files in os.walk(self.data_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        oldest_files.append({
                            'path': file_path,
                            'size_gb': os.path.getsize(file_path) / (1024**3),
                            'modified': file_time
                        })
            
            # Sort by modification time and return oldest N
            oldest_files.sort(key=lambda x: x['modified'])
            return oldest_files[:limit]
            
        except Exception as e:
            trading_logger.error(f"Failed to find oldest files: {e}")
            return []
    
    def _find_compression_opportunities(self) -> List[Dict[str, Any]]:
        """Find files that can be compressed"""
        opportunities = []
        
        try:
            for root, dirs, files in os.walk(self.data_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        
                        # Check if file is large enough and not already compressed
                        if (file_size > 1024 * 1024 and  # > 1MB
                            not file_path.endswith(('.gz', '.zip', '.bz2'))):
                            
                            opportunities.append({
                                'path': file_path,
                                'size_gb': file_size / (1024**3),
                                'estimated_compression': self._estimate_compression_ratio(file_path)
                            })
            
            # Sort by potential savings
            opportunities.sort(key=lambda x: x['size_gb'] * x['estimated_compression'], reverse=True)
            return opportunities[:20]  # Top 20 opportunities
            
        except Exception as e:
            trading_logger.error(f"Failed to find compression opportunities: {e}")
            return []
    
    def _estimate_compression_ratio(self, file_path: str) -> float:
        """Estimate compression ratio for a file"""
        try:
            ext = os.path.splitext(file_path)[1].lower()
            
            # Estimate based on file type
            if ext in ['.csv', '.txt', '.json']:
                return 0.7  # 70% compression
            elif ext in ['.pkl', '.joblib']:
                return 0.6  # 60% compression
            elif ext in ['.log']:
                return 0.8  # 80% compression
            else:
                return 0.5  # 50% compression
                
        except Exception as e:
            return 0.5  # Default estimate
    
    def compress_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Compress files to save space"""
        compression_results = {
            'files_compressed': 0,
            'space_saved_gb': 0,
            'compression_errors': []
        }
        
        try:
            for file_path in file_paths:
                try:
                    original_size = os.path.getsize(file_path)
                    
                    # Compress file
                    compressed_path = f"{file_path}.gz"
                    with open(file_path, 'rb') as f_in:
                        with gzip.open(compressed_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    
                    compressed_size = os.path.getsize(compressed_path)
                    space_saved = original_size - compressed_size
                    
                    # Remove original file
                    os.remove(file_path)
                    
                    compression_results['files_compressed'] += 1
                    compression_results['space_saved_gb'] += space_saved / (1024**3)
                    
                    trading_logger.info(f"Compressed {file_path}", 
                                       original_size_mb=original_size/(1024**2),
                                       compressed_size_mb=compressed_size/(1024**2))
                    
                except Exception as e:
                    compression_results['compression_errors'].append({
                        'file': file_path,
                        'error': str(e)
                    })
                    trading_logger.error(f"Failed to compress {file_path}: {e}")
            
            # Update stats
            self.storage_stats['files_compressed'] += compression_results['files_compressed']
            
            trading_logger.info("File compression completed", 
                               files_compressed=compression_results['files_compressed'],
                               space_saved_gb=compression_results['space_saved_gb'])
            
        except Exception as e:
            trading_logger.error(f"File compression failed: {e}")
        
        return compression_results
    
    def cleanup_old_files(self) -> Dict[str, Any]:
        """Clean up old files based on retention policies"""
        cleanup_results = {
            'files_deleted': 0,
            'space_freed_gb': 0,
            'cleanup_errors': []
        }
        
        try:
            current_time = datetime.now()
            
            # Clean up historical data
            historical_retention = timedelta(days=self.retention_policies['historical_data_days'])
            cleanup_results.update(self._cleanup_directory(
                self.historical_dir, historical_retention, current_time))
            
            # Clean up model files
            model_retention = timedelta(days=self.retention_policies['model_files_days'])
            cleanup_results.update(self._cleanup_directory(
                self.models_dir, model_retention, current_time))
            
            # Clean up cache files
            cache_retention = timedelta(days=self.retention_policies['cache_files_days'])
            cleanup_results.update(self._cleanup_directory(
                self.cache_dir, cache_retention, current_time))
            
            # Clean up log files
            log_retention = timedelta(days=self.retention_policies['log_files_days'])
            cleanup_results.update(self._cleanup_directory(
                self.logs_dir, log_retention, current_time))
            
            # Update stats
            self.storage_stats['files_deleted'] += cleanup_results['files_deleted']
            self.storage_stats['last_cleanup'] = current_time
            
            trading_logger.info("File cleanup completed", 
                               files_deleted=cleanup_results['files_deleted'],
                               space_freed_gb=cleanup_results['space_freed_gb'])
            
        except Exception as e:
            trading_logger.error(f"File cleanup failed: {e}")
        
        return cleanup_results
    
    def _cleanup_directory(self, directory: str, retention_period: timedelta, 
                          current_time: datetime) -> Dict[str, Any]:
        """Clean up files in a directory based on retention period"""
        cleanup_results = {
            'files_deleted': 0,
            'space_freed_gb': 0,
            'cleanup_errors': []
        }
        
        try:
            if not os.path.exists(directory):
                return cleanup_results
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        
                        if current_time - file_time > retention_period:
                            try:
                                file_size = os.path.getsize(file_path)
                                os.remove(file_path)
                                
                                cleanup_results['files_deleted'] += 1
                                cleanup_results['space_freed_gb'] += file_size / (1024**3)
                                
                                trading_logger.info(f"Deleted old file: {file_path}")
                                
                            except Exception as e:
                                cleanup_results['cleanup_errors'].append({
                                    'file': file_path,
                                    'error': str(e)
                                })
                                trading_logger.error(f"Failed to delete {file_path}: {e}")
            
        except Exception as e:
            trading_logger.error(f"Directory cleanup failed for {directory}: {e}")
        
        return cleanup_results
    
    def optimize_storage(self) -> Dict[str, Any]:
        """Run complete storage optimization"""
        optimization_results = {
            'analysis': {},
            'compression': {},
            'cleanup': {},
            'total_space_saved_gb': 0
        }
        
        try:
            trading_logger.info("Starting storage optimization...")
            
            # Step 1: Analyze current usage
            optimization_results['analysis'] = self.analyze_storage_usage()
            
            # Step 2: Compress large files
            if self.compression_enabled:
                compression_opportunities = optimization_results['analysis'].get('compression_opportunities', [])
                if compression_opportunities:
                    # Compress top 10 largest files
                    top_files = [opp['path'] for opp in compression_opportunities[:10]]
                    optimization_results['compression'] = self.compress_files(top_files)
                    optimization_results['total_space_saved_gb'] += optimization_results['compression']['space_saved_gb']
            
            # Step 3: Clean up old files
            if self.cleanup_enabled:
                optimization_results['cleanup'] = self.cleanup_old_files()
                optimization_results['total_space_saved_gb'] += optimization_results['cleanup']['space_freed_gb']
            
            # Step 4: Update compression ratio
            if optimization_results['analysis']['total_size_gb'] > 0:
                self.storage_stats['compression_ratio'] = (
                    optimization_results['total_space_saved_gb'] / 
                    optimization_results['analysis']['total_size_gb']
                ) * 100
            
            trading_logger.info("Storage optimization completed", 
                               total_space_saved_gb=optimization_results['total_space_saved_gb'])
            
        except Exception as e:
            trading_logger.error(f"Storage optimization failed: {e}")
        
        return optimization_results
    
    def get_storage_status(self) -> Dict[str, Any]:
        """Get comprehensive storage status"""
        try:
            analysis = self.analyze_storage_usage()
            
            return {
                'optimizer_name': self.name,
                'description': self.description,
                'storage_analysis': analysis,
                'storage_stats': self.storage_stats,
                'retention_policies': self.retention_policies,
                'compression_settings': self.compression_settings,
                'optimization_enabled': {
                    'compression': self.compression_enabled,
                    'cleanup': self.cleanup_enabled
                },
                'max_storage_gb': self.max_storage_gb,
                'storage_usage_percent': (analysis.get('total_size_gb', 0) / self.max_storage_gb) * 100,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            trading_logger.error(f"Failed to get storage status: {e}")
            return {}
    
    def set_retention_policy(self, policy_name: str, days: int):
        """Set retention policy for a specific file type"""
        try:
            if policy_name in self.retention_policies:
                self.retention_policies[policy_name] = days
                trading_logger.info(f"Retention policy updated: {policy_name} = {days} days")
            else:
                trading_logger.warning(f"Unknown retention policy: {policy_name}")
        except Exception as e:
            trading_logger.error(f"Failed to set retention policy: {e}")
    
    def enable_compression(self, enabled: bool = True):
        """Enable or disable compression"""
        self.compression_enabled = enabled
        trading_logger.info(f"Compression {'enabled' if enabled else 'disabled'}")
    
    def enable_cleanup(self, enabled: bool = True):
        """Enable or disable cleanup"""
        self.cleanup_enabled = enabled
        trading_logger.info(f"Cleanup {'enabled' if enabled else 'disabled'}")
