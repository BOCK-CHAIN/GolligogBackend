#!/usr/bin/env python3
"""
Script to configure SearXNG to only use Google engines
"""

import yaml
import sys

def configure_google_only():
    settings_file = '/home/kali/search_engine/searxng/searx/settings.yml'
    
    # Google engines to keep enabled
    google_engines = {
        'google',
        'google images', 
        'google news',
        'google videos',
        'google scholar'
    }
    
    try:
        # Read the current settings
        with open(settings_file, 'r') as f:
            settings = yaml.safe_load(f)
        
        # Disable all engines except Google ones
        for engine in settings.get('engines', []):
            engine_name = engine.get('name', '')
            if engine_name in google_engines:
                # Enable Google engines
                engine['disabled'] = False
                print(f"Enabled: {engine_name}")
            else:
                # Disable all other engines
                engine['disabled'] = True
                if not engine_name.startswith('google'):
                    print(f"Disabled: {engine_name}")
        
        # Write back the modified settings
        with open(settings_file, 'w') as f:
            yaml.dump(settings, f, default_flow_style=False, sort_keys=False)
        
        print(f"\nSuccessfully configured SearXNG to use only Google engines.")
        print("Enabled engines:")
        for engine in google_engines:
            print(f"  - {engine}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    configure_google_only()
