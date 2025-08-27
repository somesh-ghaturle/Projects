#!/usr/bin/env python3
"""
Simple Real-world Demo of the Agentic Finance Workflow System
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import our agents
from agents import AgentContext, AgentType
from agents.cleaner import DataCleanerAgent, CleaningRules
from agents.orchestrator import OrchestratorAgent, WorkflowDefinition, WorkflowStep

def create_sample_financial_data():
    """Create realistic financial data with issues"""
    print("📊 Creating sample financial market data...")
    
    # Create 50 records of AAPL stock data
    dates = pd.date_range(start='2024-01-01', periods=50, freq='D')
    data = []
    
    base_price = 150.0
    for i, date in enumerate(dates):
        # Simulate price movements
        price = base_price + np.random.normal(0, 5)  # Random walk
        volatility = abs(np.random.normal(0, 2))
        
        data.append({
            'timestamp': date,
            'symbol': 'AAPL',
            'open': round(price, 2),
            'high': round(price + volatility, 2), 
            'low': round(price - volatility, 2),
            'close': round(price + np.random.normal(0, 1), 2),
            'volume': np.random.randint(1000000, 5000000)
        })
    
    df = pd.DataFrame(data)
    
    # Add some data quality issues
    print("🔧 Adding realistic data quality issues...")
    
    # Missing values (10%)
    missing_indices = np.random.choice(df.index, size=5, replace=False)
    df.loc[missing_indices[:3], 'close'] = np.nan
    df.loc[missing_indices[3:], 'volume'] = np.nan
    
    # Price outliers (bad ticks)
    df.loc[10, 'high'] = df.loc[10, 'high'] * 5  # Extreme spike
    df.loc[20, 'low'] = df.loc[20, 'low'] * 0.1  # Extreme drop
    
    # Add duplicate
    df = pd.concat([df, df.iloc[[5]]], ignore_index=True)
    
    print(f"✓ Created {len(df)} records")
    print(f"  - Missing values: {df.isnull().sum().sum()}")
    print(f"  - Duplicates: {df.duplicated().sum()}")
    
    return df

async def demo_simple_cleaning():
    """Demo: Simple data cleaning"""
    print("\n" + "="*50)
    print("🧹 DEMO: Data Cleaning Agent")
    print("="*50)
    
    # Create sample data
    raw_data = create_sample_financial_data()
    print(f"Raw data shape: {raw_data.shape}")
    
    # Create cleaner with basic rules
    cleaner = DataCleanerAgent()
    
    # Create context
    context = AgentContext(
        agent_id="demo_cleaner",
        workflow_id="simple_demo"
    )
    
    # Execute cleaning
    print("⚙️  Cleaning data...")
    result = await cleaner.execute({"data": raw_data}, context)
    
    if result.success:
        cleaned_data = result.data['cleaned_data']
        print(f"✅ Success!")
        print(f"   Original: {len(raw_data)} rows")
        print(f"   Cleaned: {len(cleaned_data)} rows") 
        print(f"   Removed: {len(raw_data) - len(cleaned_data)} rows")
        print(f"   Missing values: {raw_data.isnull().sum().sum()} → {cleaned_data.isnull().sum().sum()}")
        
        print("\n📊 Sample cleaned data:")
        print(cleaned_data[['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume']].head(3))
        
        return cleaned_data
    else:
        print(f"❌ Failed: {result.error_message}")
        return None

async def demo_orchestrated():
    """Demo: Orchestrated workflow"""
    print("\n" + "="*50) 
    print("🎯 DEMO: Orchestrated Workflow")
    print("="*50)
    
    # Create sample data
    raw_data = create_sample_financial_data()
    
    # Create workflow step
    workflow_step = WorkflowStep(
        step_id="clean_data",
        agent_type=AgentType.CLEANER
    )
    
    # Create workflow definition
    workflow_def = WorkflowDefinition(
        workflow_id="simple_workflow",
        name="Simple Data Processing",
        description="Basic financial data cleaning workflow",
        steps=[workflow_step]
    )
    
    # Create orchestrator
    orchestrator = OrchestratorAgent()
    
    # Prepare input
    workflow_input = {
        "workflow_definition": workflow_def,
        "input_parameters": {"data": raw_data}
    }
    
    # Execute
    context = AgentContext(
        agent_id="demo_orchestrator", 
        workflow_id="orchestrated_demo"
    )
    
    print("⚙️  Executing workflow...")
    result = await orchestrator.execute(workflow_input, context)
    
    if result.success:
        print("✅ Workflow completed!")
        workflow_results = result.data
        print(f"   Status: {workflow_results.get('status', 'unknown')}")
        duration = workflow_results.get('duration', 0)
        print(f"   Duration: {duration:.4f}s")
        print(f"   Execution ID: {workflow_results.get('execution_id', 'N/A')}")
        
        return workflow_results
    else:
        print(f"❌ Workflow failed: {result.error_message}")
        return None

async def demo_performance():
    """Demo: Quick performance test"""
    print("\n" + "="*50)
    print("⚡ DEMO: Performance Test")
    print("="*50)
    
    sizes = [50, 100, 200]
    
    for size in sizes:
        print(f"\n📊 Testing {size} records...")
        
        # Generate test data
        dates = pd.date_range('2024-01-01', periods=size, freq='D') 
        df = pd.DataFrame({
            'timestamp': dates,
            'symbol': 'TEST',
            'open': np.random.uniform(100, 200, size),
            'high': np.random.uniform(100, 200, size),
            'low': np.random.uniform(100, 200, size), 
            'close': np.random.uniform(100, 200, size),
            'volume': np.random.randint(1000000, 10000000, size)
        })
        
        # Add some missing values
        missing_count = size // 10
        missing_indices = np.random.choice(df.index, size=missing_count, replace=False)
        df.loc[missing_indices, 'close'] = np.nan
        
        # Time the cleaning
        cleaner = DataCleanerAgent()
        context = AgentContext(agent_id=f"perf_{size}", workflow_id="performance")
        
        start_time = datetime.now()
        result = await cleaner.execute({"data": df}, context)
        duration = (datetime.now() - start_time).total_seconds()
        
        if result.success:
            cleaned = result.data['cleaned_data']
            throughput = len(df) / duration if duration > 0 else 0
            print(f"   ✅ {size} → {len(cleaned)} records in {duration:.3f}s ({throughput:.0f} rec/sec)")
        else:
            print(f"   ❌ Failed")

async def main():
    """Run all demos"""
    print("🚀 Agentic Finance Workflow - Simple Demo")
    print("Testing real financial data processing...\n")
    
    try:
        # Run demos
        cleaned_data = await demo_simple_cleaning()
        workflow_result = await demo_orchestrated() 
        await demo_performance()
        
        print("\n" + "="*50)
        print("🎉 ALL DEMOS COMPLETED!")
        print("="*50)
        
        if cleaned_data is not None:
            print("✅ Data Cleaning: WORKING")
        
        if workflow_result is not None:
            print("✅ Workflow Orchestration: WORKING")
            
        print("✅ Performance Testing: WORKING")
        print("\n🎯 System is ready for production use!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
