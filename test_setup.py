"""
Quick Setup Test Script
Run this to verify your installation before running the bot
"""

import sys

print("=" * 60)
print("NAS100 Bot - Setup Verification")
print("=" * 60)

# Test 1: Python Version
print("\n1. Checking Python version...")
python_version = sys.version_info
if python_version.major >= 3 and python_version.minor >= 8:
    print(f"   ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} - OK")
else:
    print(f"   ❌ Python version too old. Need 3.8+, you have {python_version.major}.{python_version.minor}")
    sys.exit(1)

# Test 2: Required Libraries
print("\n2. Checking required libraries...")
required_libs = ['MetaTrader5', 'pandas', 'numpy']
missing_libs = []

for lib in required_libs:
    try:
        __import__(lib)
        print(f"   ✅ {lib} - Installed")
    except ImportError:
        print(f"   ❌ {lib} - NOT FOUND")
        missing_libs.append(lib)

if missing_libs:
    print("\n   Install missing libraries with:")
    print(f"   pip install {' '.join(missing_libs)}")
    sys.exit(1)

# Test 3: MT5 Connection
print("\n3. Testing MT5 connection...")
try:
    import MetaTrader5 as mt5
    
    if not mt5.initialize():
        print("   ❌ MT5 initialization failed")
        print("   Make sure MT5 is installed and running")
        print("   Enable 'Allow automated trading' in MT5 settings")
    else:
        print("   ✅ MT5 connected successfully")
        
        # Get MT5 version info
        version = mt5.version()
        if version:
            print(f"   MT5 Build: {version[0]}")
            print(f"   Release Date: {version[1]}")
        
        mt5.shutdown()
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 4: Config File
print("\n4. Checking configuration file...")
try:
    import config
    print("   ✅ config.py found")
    
    # Check critical settings
    if hasattr(config, 'SYMBOL'):
        print(f"   Symbol: {config.SYMBOL}")
    if hasattr(config, 'LOT_SIZE'):
        print(f"   Lot Size: {config.LOT_SIZE}")
    
except ImportError:
    print("   ⚠️  config.py not found (will use defaults)")

# Test 5: Optional Libraries
print("\n5. Checking optional libraries...")
optional_libs = ['requests', 'matplotlib']

for lib in optional_libs:
    try:
        __import__(lib)
        print(f"   ✅ {lib} - Installed")
    except ImportError:
        print(f"   ⚠️  {lib} - Not installed (optional)")

# Final Summary
print("\n" + "=" * 60)
print("Setup Verification Complete!")
print("=" * 60)

if not missing_libs:
    print("\n✅ All requirements met! You're ready to run the bot.")
    print("\nNext steps:")
    print("1. Edit config.py with your MT5 credentials (use DEMO account!)")
    print("2. Verify your broker's symbol name for NAS100")
    print("3. Run: python nas100_breakout_bot.py")
    print("\n⚠️  IMPORTANT: Always test with DEMO account first!")
else:
    print("\n❌ Setup incomplete. Please install missing requirements.")
    print(f"\nRun: pip install {' '.join(missing_libs)}")

print("=" * 60)
