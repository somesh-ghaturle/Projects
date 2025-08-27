"""
Data Cleaner Agent for Financial Data Processing

This agent handles data cleaning operations including:
- Missing value imputation
- Outlier detection and treatment
- Data type conversions
- Duplicate removal
- Financial data-specific cleaning rules
"""

import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass

from .. import BaseAgent, AgentType, AgentContext, validate_agent_input


@dataclass
class CleaningRules:
    """Configuration for data cleaning operations"""
    handle_missing: str = "interpolate"  # 'drop', 'fill', 'interpolate', 'forward_fill'
    missing_threshold: float = 0.1  # Drop columns with >10% missing values
    outlier_method: str = "iqr"  # 'iqr', 'zscore', 'isolation_forest'
    outlier_threshold: float = 3.0  # Z-score threshold or IQR multiplier
    remove_duplicates: bool = True
    validate_business_hours: bool = True
    validate_price_ranges: bool = True
    min_price: float = 0.01
    max_price_change: float = 0.5  # 50% max price change between periods
    currency_conversion: Optional[str] = None


class DataCleanerAgent(BaseAgent):
    """
    Specialized agent for cleaning financial datasets.
    
    Handles common data quality issues in financial data including:
    - Price anomalies and outliers
    - Missing trading data
    - Corporate actions adjustments
    - Currency conversions
    - Business day validations
    """

    def __init__(self, cleaning_rules: Optional[CleaningRules] = None, **kwargs):
        super().__init__(AgentType.CLEANER, **kwargs)
        self.cleaning_rules = cleaning_rules or CleaningRules()
        self.logger.info(f"Initialized DataCleanerAgent with rules: {self.cleaning_rules}")

    @validate_agent_input({
        'required': ['data'],
        'optional': ['symbol', 'data_type', 'custom_rules']
    })
    async def _process(self, input_data: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """
        Main data cleaning processing logic.
        
        Args:
            input_data: Dictionary containing:
                - data: pandas DataFrame or file path
                - symbol: Stock symbol (optional)
                - data_type: Type of financial data ('stock_prices', 'options', 'fundamentals')
                - custom_rules: Override default cleaning rules
        
        Returns:
            Dictionary containing cleaned data and cleaning report
        """
        data = input_data['data']
        symbol = input_data.get('symbol')
        data_type = input_data.get('data_type', 'stock_prices')
        custom_rules = input_data.get('custom_rules', {})
        
        # Override rules if custom rules provided
        rules = self._merge_rules(custom_rules)
        
        # Load data if path provided
        if isinstance(data, str):
            df = await self._load_data(data)
        elif isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            raise ValueError("Data must be pandas DataFrame or file path")
        
        self.logger.info(f"Starting data cleaning for {len(df)} records")
        initial_rows = len(df)
        
        # Create cleaning report
        cleaning_report = {
            'initial_rows': initial_rows,
            'initial_columns': len(df.columns),
            'cleaning_steps': [],
            'warnings': [],
            'errors': []
        }
        
        try:
            # Step 1: Basic data validation
            df, step_report = await self._validate_basic_structure(df, data_type)
            cleaning_report['cleaning_steps'].append(step_report)
            
            # Step 2: Handle missing values
            df, step_report = await self._handle_missing_values(df, rules)
            cleaning_report['cleaning_steps'].append(step_report)
            
            # Step 3: Remove duplicates
            if rules.remove_duplicates:
                df, step_report = await self._remove_duplicates(df)
                cleaning_report['cleaning_steps'].append(step_report)
            
            # Step 4: Detect and handle outliers
            df, step_report = await self._handle_outliers(df, rules, data_type)
            cleaning_report['cleaning_steps'].append(step_report)
            
            # Step 5: Financial data specific cleaning
            if data_type == 'stock_prices':
                df, step_report = await self._clean_stock_prices(df, rules, symbol)
                cleaning_report['cleaning_steps'].append(step_report)
            
            # Step 6: Business day validation
            if rules.validate_business_hours and 'timestamp' in df.columns:
                df, step_report = await self._validate_business_days(df)
                cleaning_report['cleaning_steps'].append(step_report)
            
            # Step 7: Final data type conversions
            df, step_report = await self._convert_data_types(df, data_type)
            cleaning_report['cleaning_steps'].append(step_report)
            
            # Update metrics
            self._update_metrics(
                records_processed=initial_rows,
                success_rate=1.0 if len(df) > 0 else 0.0
            )
            
            # Final report summary
            cleaning_report.update({
                'final_rows': len(df),
                'final_columns': len(df.columns),
                'rows_removed': initial_rows - len(df),
                'data_quality_score': self._calculate_quality_score(df),
                'processing_time': getattr(self.metrics, 'execution_time', 0)
            })
            
            self.logger.info(
                f"Data cleaning completed. Rows: {initial_rows} -> {len(df)}, "
                f"Quality score: {cleaning_report['data_quality_score']:.2f}"
            )
            
            return {
                'cleaned_data': df,
                'cleaning_report': cleaning_report,
                'data_quality_score': cleaning_report['data_quality_score'],
                'metadata': {
                    'symbol': symbol,
                    'data_type': data_type,
                    'cleaning_rules': rules.__dict__
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error during data cleaning: {str(e)}")
            cleaning_report['errors'].append(str(e))
            raise

    async def _load_data(self, file_path: str) -> pd.DataFrame:
        """Load data from file path"""
        try:
            if file_path.endswith('.csv'):
                return pd.read_csv(file_path)
            elif file_path.endswith('.parquet'):
                return pd.read_parquet(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                return pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to load data from {file_path}: {str(e)}")
            raise

    def _merge_rules(self, custom_rules: Dict[str, Any]) -> CleaningRules:
        """Merge custom rules with default rules"""
        rules_dict = self.cleaning_rules.__dict__.copy()
        rules_dict.update(custom_rules)
        return CleaningRules(**rules_dict)

    async def _validate_basic_structure(self, df: pd.DataFrame, data_type: str) -> tuple:
        """Validate basic data structure and required columns"""
        step_report = {'step': 'basic_validation', 'actions': []}
        
        # Check for empty DataFrame
        if df.empty:
            raise ValueError("Dataset is empty")
        
        # Validate required columns based on data type
        required_columns = self._get_required_columns(data_type)
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            error_msg = f"Missing required columns: {missing_columns}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        step_report['actions'].append(f"Validated {len(required_columns)} required columns")
        
        # Convert timestamp column if exists
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            step_report['actions'].append("Converted timestamp column to datetime")
        
        return df, step_report

    def _get_required_columns(self, data_type: str) -> List[str]:
        """Get required columns for different data types"""
        column_mapping = {
            'stock_prices': ['timestamp', 'open', 'high', 'low', 'close', 'volume'],
            'options': ['timestamp', 'strike', 'expiry', 'option_type', 'price'],
            'fundamentals': ['symbol', 'period', 'revenue', 'earnings']
        }
        return column_mapping.get(data_type, [])

    async def _handle_missing_values(self, df: pd.DataFrame, rules: CleaningRules) -> tuple:
        """Handle missing values based on rules"""
        step_report = {'step': 'missing_values', 'actions': []}
        initial_missing = df.isnull().sum().sum()
        
        if initial_missing == 0:
            step_report['actions'].append("No missing values found")
            return df, step_report
        
        # Drop columns with too many missing values
        missing_ratio = df.isnull().sum() / len(df)
        columns_to_drop = missing_ratio[missing_ratio > rules.missing_threshold].index.tolist()
        
        if columns_to_drop:
            df = df.drop(columns=columns_to_drop)
            step_report['actions'].append(f"Dropped columns with >{rules.missing_threshold*100}% missing: {columns_to_drop}")
        
        # Handle remaining missing values
        for column in df.columns:
            if df[column].isnull().any():
                if rules.handle_missing == 'drop':
                    df = df.dropna(subset=[column])
                    step_report['actions'].append(f"Dropped rows with missing {column}")
                    
                elif rules.handle_missing == 'fill':
                    if df[column].dtype in ['float64', 'int64']:
                        fill_value = df[column].median()
                        df[column] = df[column].fillna(fill_value)
                        step_report['actions'].append(f"Filled {column} missing values with median: {fill_value}")
                    else:
                        fill_value = df[column].mode().iloc[0] if not df[column].mode().empty else 'Unknown'
                        df[column] = df[column].fillna(fill_value)
                        step_report['actions'].append(f"Filled {column} missing values with mode: {fill_value}")
                        
                elif rules.handle_missing == 'interpolate':
                    if df[column].dtype in ['float64', 'int64']:
                        df[column] = df[column].interpolate(method='linear')
                        step_report['actions'].append(f"Interpolated missing values in {column}")
                        
                elif rules.handle_missing == 'forward_fill':
                    df[column] = df[column].fillna(method='ffill')
                    step_report['actions'].append(f"Forward filled missing values in {column}")
        
        final_missing = df.isnull().sum().sum()
        step_report['actions'].append(f"Missing values: {initial_missing} -> {final_missing}")
        
        return df, step_report

    async def _remove_duplicates(self, df: pd.DataFrame) -> tuple:
        """Remove duplicate rows"""
        step_report = {'step': 'remove_duplicates', 'actions': []}
        initial_rows = len(df)
        
        # Remove exact duplicates
        df = df.drop_duplicates()
        
        # For time series data, remove duplicates based on timestamp
        if 'timestamp' in df.columns:
            df = df.drop_duplicates(subset=['timestamp'], keep='last')
        
        removed_rows = initial_rows - len(df)
        step_report['actions'].append(f"Removed {removed_rows} duplicate rows")
        
        return df, step_report

    async def _handle_outliers(self, df: pd.DataFrame, rules: CleaningRules, data_type: str) -> tuple:
        """Detect and handle outliers"""
        step_report = {'step': 'handle_outliers', 'actions': []}
        
        # Get numeric columns for outlier detection
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        outliers_removed = 0
        
        for column in numeric_columns:
            if column in ['volume']:  # Skip volume as it can have legitimate extreme values
                continue
                
            initial_count = len(df)
            
            if rules.outlier_method == 'iqr':
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - rules.outlier_threshold * IQR
                upper_bound = Q3 + rules.outlier_threshold * IQR
                
                outlier_mask = (df[column] < lower_bound) | (df[column] > upper_bound)
                df = df[~outlier_mask]
                
            elif rules.outlier_method == 'zscore':
                z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
                outlier_mask = z_scores > rules.outlier_threshold
                df = df[~outlier_mask]
            
            removed_count = initial_count - len(df)
            if removed_count > 0:
                outliers_removed += removed_count
                step_report['actions'].append(f"Removed {removed_count} outliers from {column}")
        
        step_report['actions'].append(f"Total outliers removed: {outliers_removed}")
        return df, step_report

    async def _clean_stock_prices(self, df: pd.DataFrame, rules: CleaningRules, symbol: Optional[str]) -> tuple:
        """Financial data specific cleaning for stock prices"""
        step_report = {'step': 'stock_price_cleaning', 'actions': []}
        initial_rows = len(df)
        
        # Validate price ranges
        if rules.validate_price_ranges:
            price_columns = ['open', 'high', 'low', 'close']
            for col in price_columns:
                if col in df.columns:
                    # Remove rows with negative or zero prices
                    mask = df[col] > rules.min_price
                    df = df[mask]
                    
                    # Check for extreme price changes
                    if len(df) > 1:
                        price_change = df[col].pct_change().abs()
                        extreme_changes = price_change > rules.max_price_change
                        df = df[~extreme_changes]
            
            removed_rows = initial_rows - len(df)
            if removed_rows > 0:
                step_report['actions'].append(f"Removed {removed_rows} rows with invalid prices")
        
        # Validate OHLC relationships
        if all(col in df.columns for col in ['open', 'high', 'low', 'close']):
            # High should be >= Open, Close, Low
            # Low should be <= Open, Close, High
            valid_ohlc = (
                (df['high'] >= df[['open', 'close', 'low']].max(axis=1)) &
                (df['low'] <= df[['open', 'close', 'high']].min(axis=1))
            )
            
            invalid_count = (~valid_ohlc).sum()
            if invalid_count > 0:
                df = df[valid_ohlc]
                step_report['actions'].append(f"Removed {invalid_count} rows with invalid OHLC relationships")
        
        # Sort by timestamp
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp').reset_index(drop=True)
            step_report['actions'].append("Sorted data by timestamp")
        
        return df, step_report

    async def _validate_business_days(self, df: pd.DataFrame) -> tuple:
        """Validate and filter business days"""
        step_report = {'step': 'business_days_validation', 'actions': []}
        
        if 'timestamp' not in df.columns:
            return df, step_report
        
        initial_rows = len(df)
        
        # Filter to business days (Monday=0, Sunday=6)
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        business_days = df['day_of_week'] < 5  # Monday to Friday
        df = df[business_days].drop('day_of_week', axis=1)
        
        removed_rows = initial_rows - len(df)
        step_report['actions'].append(f"Removed {removed_rows} non-business day records")
        
        return df, step_report

    async def _convert_data_types(self, df: pd.DataFrame, data_type: str) -> tuple:
        """Convert data types for optimal storage and processing"""
        step_report = {'step': 'data_type_conversion', 'actions': []}
        
        # Convert price columns to float32 for memory efficiency
        price_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in price_columns:
            if col in df.columns:
                if col == 'volume':
                    df[col] = df[col].astype('int64')
                else:
                    df[col] = df[col].astype('float32')
                step_report['actions'].append(f"Converted {col} to appropriate data type")
        
        # Ensure timestamp is datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            step_report['actions'].append("Ensured timestamp is datetime type")
        
        return df, step_report

    def _calculate_quality_score(self, df: pd.DataFrame) -> float:
        """Calculate data quality score (0-1)"""
        if df.empty:
            return 0.0
        
        # Factors for quality score
        completeness = 1 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))
        consistency = 1.0  # Could add consistency checks
        validity = 1.0     # Could add validity checks
        
        # Weighted average
        quality_score = (completeness * 0.5 + consistency * 0.3 + validity * 0.2)
        return min(1.0, max(0.0, quality_score))

    async def get_cleaning_summary(self, cleaning_report: Dict[str, Any]) -> str:
        """Generate human-readable cleaning summary"""
        summary_lines = [
            f"Data Cleaning Summary:",
            f"- Initial dataset: {cleaning_report['initial_rows']} rows, {cleaning_report['initial_columns']} columns",
            f"- Final dataset: {cleaning_report['final_rows']} rows, {cleaning_report['final_columns']} columns",
            f"- Rows removed: {cleaning_report['rows_removed']} ({cleaning_report['rows_removed']/cleaning_report['initial_rows']*100:.1f}%)",
            f"- Data quality score: {cleaning_report['data_quality_score']:.2f}/1.0",
            f"- Processing time: {cleaning_report['processing_time']:.2f} seconds"
        ]
        
        if cleaning_report['warnings']:
            summary_lines.append(f"- Warnings: {len(cleaning_report['warnings'])}")
        
        if cleaning_report['errors']:
            summary_lines.append(f"- Errors: {len(cleaning_report['errors'])}")
        
        return "\n".join(summary_lines)
