"""Utility helper functions"""

def format_output(title, data):
    """Format output nicely"""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")
    if isinstance(data, dict):
        for key, value in data.items():
            print(f"  {key}: {value}")
    else:
        print(f"  {data}")
    print(f"{'='*50}\n")
