@echo off
cd /d "D:\Desktop4\Obsidian Vault"
python test_system.py > test_output.txt 2>&1
type test_output.txt | findstr /C:"✅" /C:"❌" /C:"TEST RESULTS" /C:"Tests Passed" /C:"ALL TESTS"
