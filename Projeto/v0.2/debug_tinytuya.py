import tinytuya
import inspect

print("=== Inspecting tinytuya.deviceScan ===")
try:
    print(inspect.signature(tinytuya.deviceScan))
except Exception as e:
    print(f"Could not get signature: {e}")
    print(f"Docstring: {tinytuya.deviceScan.__doc__}")

print("\n=== Inspecting tinytuya.Cloud.getdevices ===")
try:
    print(inspect.signature(tinytuya.Cloud.getdevices))
except Exception as e:
    print(f"Could not get signature: {e}")
