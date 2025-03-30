# File: namespace_extractor/performance.py
"""
Performance optimization module for namespace extractor.

This module provides performance enhancement capabilities for the namespace extractor,
including AST caching, parallel processing, incremental updates, memory optimization,
and tracking changes in files.
"""

import ast
import hashlib
import multiprocessing as mp
import os
import pickle
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from typing import Any

from tqdm import tqdm

from .config import ExtractorConfig


@dataclass
class CacheEntry:
    """Entry in the AST cache."""

    file_hash: str
    modification_time: float
    ast_data: ast.AST
    namespaces: list[dict[str, Any]]


class ASTCache:
    """Cache for parsed AST data to avoid reprocessing unchanged files."""

    def __init__(self, cache_dir: str | None = None) -> None:
        """
        Initialize the AST cache.

        Args:
            cache_dir: Directory to store cache (default: ~/.namespace_extractor/cache)
        """
        if cache_dir is None:
            cache_dir = os.path.join(
                os.path.expanduser("~"), ".namespace_extractor", "cache"
            )

        self.cache_dir = cache_dir
        self.cache: dict[str, CacheEntry] = {}
        self.enabled = True

        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)

        # Load cached data
        self._load_cache()

    def _load_cache(self) -> None:
        """Load the cache from disk."""
        cache_file = os.path.join(self.cache_dir, "ast_cache.pkl")

        if os.path.exists(cache_file):
            try:
                with open(cache_file, "rb") as f:
                    self.cache = pickle.load(f)
                print(f"Loaded AST cache with {len(self.cache)} entries")
            except Exception as e:
                print(f"Error loading AST cache: {e!s}")
                self.cache = {}

    def save_cache(self) -> None:
        """Save the cache to disk."""
        cache_file = os.path.join(self.cache_dir, "ast_cache.pkl")

        try:
            with open(cache_file, "wb") as f:
                pickle.dump(self.cache, f)
            print(f"Saved AST cache with {len(self.cache)} entries")
        except Exception as e:
            print(f"Error saving AST cache: {e!s}")

    def get(self, file_path: str) -> tuple[ast.AST, list[dict[str, Any]]] | None:
        """
        Get cached AST and namespaces for a file.

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (AST, namespaces) or None if not cached or cache is invalid
        """
        if not self.enabled:
            return None

        # Check if file exists and get modification time
        if not os.path.exists(file_path):
            return None

        modification_time = os.path.getmtime(file_path)

        # Check if file is in cache
        if file_path in self.cache:
            cache_entry = self.cache[file_path]

            # Check if file has been modified
            if cache_entry.modification_time == modification_time:
                # Verify file content using hash
                file_hash = self._compute_file_hash(file_path)
                if file_hash == cache_entry.file_hash:
                    return (cache_entry.ast_data, cache_entry.namespaces)

        return None

    def put(
        self, file_path: str, ast_data: ast.AST, namespaces: list[dict[str, Any]]
    ) -> None:
        """
        Store AST and namespaces in the cache.

        Args:
            file_path: Path to the file
            ast_data: Parsed AST
            namespaces: Extracted namespaces
        """
        if not self.enabled:
            return

        # Get file metadata
        modification_time = os.path.getmtime(file_path)
        file_hash = self._compute_file_hash(file_path)

        # Create cache entry
        self.cache[file_path] = CacheEntry(
            file_hash=file_hash,
            modification_time=modification_time,
            ast_data=ast_data,
            namespaces=namespaces,
        )

    def clear(self) -> None:
        """Clear the cache."""
        self.cache = {}

        # Remove cache file
        cache_file = os.path.join(self.cache_dir, "ast_cache.pkl")
        if os.path.exists(cache_file):
            os.remove(cache_file)

    def _compute_file_hash(self, file_path: str) -> str:
        """
        Compute a hash of the file content.

        Args:
            file_path: Path to the file

        Returns:
            Hash of the file content
        """
        hasher = hashlib.md5()

        with open(file_path, "rb") as f:
            buf = f.read(65536)  # Read in 64k chunks
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)

        return hasher.hexdigest()


class ChangeTracker:
    """Tracks changes in files for incremental updates."""

    def __init__(self, data_dir: str | None = None) -> None:
        """
        Initialize the change tracker.

        Args:
            data_dir: Directory to save data (default: ~/.namespace_extractor/data)
        """
        if data_dir is None:
            data_dir = os.path.join(
                os.path.expanduser("~"), ".namespace_extractor", "data"
            )

        self.data_dir = data_dir
        self.file_metadata: dict[str, dict[str, Any]] = {}

        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)

        # Load tracking data
        self._load_tracking_data()

    def _load_tracking_data(self) -> None:
        """Load tracking data from disk."""
        tracking_file = os.path.join(self.data_dir, "file_tracking.pkl")

        if os.path.exists(tracking_file):
            try:
                with open(tracking_file, "rb") as f:
                    self.file_metadata = pickle.load(f)
                print(
                    f"Loaded change tracking data for {len(self.file_metadata)} files"
                )
            except Exception as e:
                print(f"Error loading change tracking data: {e!s}")
                self.file_metadata = {}

    def save_tracking_data(self) -> None:
        """Save tracking data to disk."""
        tracking_file = os.path.join(self.data_dir, "file_tracking.pkl")

        try:
            with open(tracking_file, "wb") as f:
                pickle.dump(self.file_metadata, f)
            print(f"Saved change tracking data for {len(self.file_metadata)} files")
        except Exception as e:
            print(f"Error saving change tracking data: {e!s}")

    def find_changed_files(
        self, files: list[str]
    ) -> tuple[list[str], list[str], list[str]]:
        """
        Identify which files have changed, been added, or been removed.

        Args:
            files: List of current files

        Returns:
            Tuple of (changed files, new files, removed files)
        """
        changed_files = []
        new_files = []
        current_files = set(files)
        previous_files = set(self.file_metadata.keys())

        # Find removed files
        removed_files = list(previous_files - current_files)

        # Check for changed and new files
        for file_path in files:
            if not os.path.exists(file_path):
                continue

            if file_path in self.file_metadata:
                # Existing file - check if changed
                metadata = self.file_metadata[file_path]

                # Check modification time
                current_mtime = os.path.getmtime(file_path)
                if current_mtime != metadata.get("modification_time", 0):
                    changed_files.append(file_path)
            else:
                # New file
                new_files.append(file_path)

        return changed_files, new_files, removed_files

    def update_file_metadata(self, file_path: str) -> None:
        """
        Update metadata for a file.

        Args:
            file_path: Path to the file
        """
        if not os.path.exists(file_path):
            # Remove from metadata if the file no longer exists
            if file_path in self.file_metadata:
                del self.file_metadata[file_path]
            return

        # Update metadata
        self.file_metadata[file_path] = {
            "modification_time": os.path.getmtime(file_path),
            "size": os.path.getsize(file_path),
            "last_processed": time.time(),
        }


class ParallelProcessor:
    """Handles parallel processing for namespace extraction."""

    def __init__(self, config: ExtractorConfig, max_workers: int | None = None) -> None:
        """
        Initialize the parallel processor.

        Args:
            config: Extraction configuration
            max_workers: Maximum number of worker processes (default: CPU count)
        """
        self.config = config
        self.max_workers = max_workers or mp.cpu_count()

    def process_files(
        self, files: list[str], ast_cache: ASTCache | None = None
    ) -> list[tuple[str, str, list[dict[str, Any]]]]:
        """
        Process files in parallel.

        Args:
            files: List of files to process
            ast_cache: Optional AST cache

        Returns:
            List of extraction results
        """
        results = []

        # Set up process pool
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit tasks
            futures = [
                executor.submit(self._process_file, file_path, self.config, ast_cache)
                for file_path in files
            ]

            # Collect results with progress bar
            with tqdm(total=len(futures), desc="Processing files") as pbar:
                for future in futures:
                    try:
                        result = future.result()
                        if result is not None:
                            results.append(result)
                    except Exception as e:
                        print(f"Error in worker process: {e!s}")
                    finally:
                        pbar.update(1)

        return results

    @staticmethod
    def _process_file(
        file_path: str, config: ExtractorConfig, ast_cache: ASTCache | None = None
    ) -> tuple[str, str, list[dict[str, Any]]] | None:
        """
        Process a single file (intended to run in a worker process).

        Args:
            file_path: Path to the file
            config: Extraction configuration
            ast_cache: Optional AST cache

        Returns:
            Extraction result or None on error
        """
        try:
            # This import is necessary in the worker process
            from .parser import extract_namespaces

            return extract_namespaces(file_path, config)
        except Exception as e:
            print(f"Error processing file {file_path}: {e!s}")
            return None


class MemoryOptimizer:
    """Optimizes memory usage for large projects."""

    def __init__(self, config: ExtractorConfig) -> None:
        """
        Initialize the memory optimizer.

        Args:
            config: Extraction configuration
        """
        self.config = config
        self.memory_threshold_mb = 1024  # Default 1GB threshold
        self.batch_size = 100  # Default batch size

    def set_memory_threshold(self, threshold_mb: int) -> None:
        """
        Set the memory threshold for optimization.

        Args:
            threshold_mb: Memory threshold in megabytes
        """
        self.memory_threshold_mb = threshold_mb

    def set_batch_size(self, batch_size: int) -> None:
        """
        Set the batch size for processing.

        Args:
            batch_size: Number of files to process in one batch
        """
        self.batch_size = batch_size

    def process_in_batches(
        self,
        files: list[str],
        processor: ParallelProcessor,
        ast_cache: ASTCache | None = None,
    ) -> list[tuple[str, str, list[dict[str, Any]]]]:
        """
        Process files in batches to optimize memory usage.

        Args:
            files: List of files to process
            processor: Parallel processor instance
            ast_cache: Optional AST cache

        Returns:
            List of extraction results
        """
        results = []
        file_count = len(files)

        # Determine batch size based on file count and system memory
        if file_count > 1000:
            # For very large projects, use smaller batches
            actual_batch_size = min(self.batch_size, 50)
        else:
            actual_batch_size = self.batch_size

        # Process in batches
        for i in range(0, file_count, actual_batch_size):
            batch = files[i : i + actual_batch_size]

            print(
                f"Processing batch {i // actual_batch_size + 1}/{(file_count + actual_batch_size - 1) // actual_batch_size}"
            )

            # Process the batch
            batch_results = processor.process_files(batch, ast_cache)
            results.extend(batch_results)

            # Memory cleanup after each batch
            self._cleanup_memory()

        return results

    def _cleanup_memory(self) -> None:
        """Perform memory cleanup."""
        # Force garbage collection
        import gc

        gc.collect()


class IncrementalExtractor:
    """Handles incremental updates to extract only changed files."""

    def __init__(
        self,
        config: ExtractorConfig,
        ast_cache: ASTCache | None = None,
        change_tracker: ChangeTracker | None = None,
    ) -> None:
        """
        Initialize the incremental extractor.

        Args:
            config: Extraction configuration
            ast_cache: Optional AST cache
            change_tracker: Optional change tracker
        """
        self.config = config
        self.ast_cache = ast_cache or ASTCache()
        self.change_tracker = change_tracker or ChangeTracker()
        self.processor = ParallelProcessor(config)
        self.memory_optimizer = MemoryOptimizer(config)
        self.previous_results: dict[str, tuple[str, str, list[dict[str, Any]]]] = {}

    def extract(
        self, files: list[str], force_full: bool = False
    ) -> list[tuple[str, str, list[dict[str, Any]]]]:
        """
        Perform extraction, processing only changed files when possible.

        Args:
            files: List of files to process
            force_full: Force full extraction even if incremental is possible

        Returns:
            List of extraction results
        """
        if force_full:
            # Perform full extraction
            print("Performing full extraction (forced)")
            return self._full_extraction(files)

        # Check which files have changed
        changed_files, new_files, removed_files = (
            self.change_tracker.find_changed_files(files)
        )

        # If no previous results, or too many changes, do full extraction
        change_ratio = (len(changed_files) + len(new_files) + len(removed_files)) / max(
            1, len(files)
        )

        if not self.previous_results or change_ratio > 0.5:
            print(f"Performing full extraction (change ratio: {change_ratio:.2f})")
            return self._full_extraction(files)

        # Perform incremental extraction
        print("Performing incremental extraction:")
        print(f"  Changed files: {len(changed_files)}")
        print(f"  New files: {len(new_files)}")
        print(f"  Removed files: {len(removed_files)}")

        if files_to_process := changed_files + new_files:
            # Process files in batches to optimize memory
            new_results = self.memory_optimizer.process_in_batches(
                files_to_process, self.processor, self.ast_cache
            )

            # Update tracker for processed files
            for file_path in files_to_process:
                self.change_tracker.update_file_metadata(file_path)
        else:
            new_results = []

        # Merge with previous results
        return self._merge_results(new_results, changed_files, new_files, removed_files)

    def _full_extraction(
        self, files: list[str]
    ) -> list[tuple[str, str, list[dict[str, Any]]]]:
        """
        Perform full extraction of all files.

        Args:
            files: List of files to process

        Returns:
            List of extraction results
        """
        # Process all files in batches to optimize memory
        results = self.memory_optimizer.process_in_batches(
            files, self.processor, self.ast_cache
        )

        # Update previous results
        self.previous_results = {}
        for directory, filename, namespaces in results:
            file_path = os.path.join(directory, filename)
            self.previous_results[file_path] = (directory, filename, namespaces)

        # Update trackers for all files
        for file_path in files:
            self.change_tracker.update_file_metadata(file_path)

        return self._save_data(results)

    def _merge_results(
        self,
        new_results: list[tuple[str, str, list[dict[str, Any]]]],
        changed_files: list[str],
        new_files: list[str],
        removed_files: list[str],
    ) -> list[tuple[str, str, list[dict[str, Any]]]]:
        """
        Merge new results with previous results.

        Args:
            new_results: Results from changed and new files
            changed_files: List of changed files
            new_files: List of new files
            removed_files: List of removed files

        Returns:
            Merged results
        """
        # Convert new results to dictionary for easier lookup
        new_results_dict = {}
        for directory, filename, namespaces in new_results:
            file_path = os.path.join(directory, filename)
            new_results_dict[file_path] = (directory, filename, namespaces)

            # Update previous results
            self.previous_results[file_path] = (directory, filename, namespaces)

        # Remove processed entries for removed files
        for file_path in removed_files:
            if file_path in self.previous_results:
                del self.previous_results[file_path]

        # Merge results
        merged_results = list(self.previous_results.values())

        return self._save_data(merged_results)

    def _save_data(
        self, results: list[tuple[str, str, list[dict[str, Any]]]]
    ) -> list[tuple[str, str, list[dict[str, Any]]]]:
        """
        Save cache and tracking data.

        Args:
            results: Results to save

        Returns:
            Results
        """
        self.ast_cache.save_cache()
        self.change_tracker.save_tracking_data()

        return results


# Enhanced extraction function using performance optimizations
def extract_with_optimizations(
    files: list[str],
    config: ExtractorConfig,
    incremental: bool = True,
    parallel: bool = True,
    optimize_memory: bool = True,
    force_full: bool = False,
) -> list[tuple[str, str, list[dict[str, Any]]]]:
    """
    Extract namespaces with performance optimizations.

    Args:
        files: List of files to process
        config: Extraction configuration
        incremental: Whether to use incremental extraction
        parallel: Whether to use parallel processing
        optimize_memory: Whether to optimize memory usage
        force_full: Force full extraction even if incremental is possible

    Returns:
        List of extraction results
    """
    if incremental:
        # Use incremental extractor
        ast_cache = ASTCache()
        change_tracker = ChangeTracker()
        processor = ParallelProcessor(config) if parallel else None
        memory_optimizer = MemoryOptimizer(config) if optimize_memory else None

        extractor = IncrementalExtractor(
            config, ast_cache=ast_cache, change_tracker=change_tracker
        )

        # Set processor if provided
        if processor:
            extractor.processor = processor

        # Set memory optimizer if provided
        if memory_optimizer:
            extractor.memory_optimizer = memory_optimizer

        return extractor.extract(files, force_full=force_full)

    elif parallel:
        # Use parallel processing without incremental
        processor = ParallelProcessor(config)

        if optimize_memory:
            # Use memory optimization
            memory_optimizer = MemoryOptimizer(config)
            return memory_optimizer.process_in_batches(files, processor)
        else:
            # Simple parallel processing
            return processor.process_files(files)

    else:
        # Fallback to basic processing
        from .parser import extract_namespaces

        results = []
        with tqdm(total=len(files), desc="Processing files") as pbar:
            for file_path in files:
                try:
                    result = extract_namespaces(file_path, config)
                    results.append(result)
                except Exception as e:
                    print(f"Error processing file {file_path}: {e!s}")
                finally:
                    pbar.update(1)

        return results
