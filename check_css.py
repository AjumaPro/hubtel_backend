#!/usr/bin/env python3
"""
Script to check for broken CSS classes in the dashboard template
"""

import re
import os

def extract_css_classes_from_html(html_content):
    """Extract all CSS classes from HTML content"""
    # Pattern to match class attributes
    class_pattern = r'class=["\']([^"\']*)["\']'
    classes = []
    
    for match in re.findall(class_pattern, html_content):
        # Split multiple classes
        class_list = match.split()
        classes.extend(class_list)
    
    return list(set(classes))  # Remove duplicates

def extract_css_classes_from_css(css_content):
    """Extract all CSS class selectors from CSS content"""
    # Pattern to match CSS class selectors
    selector_pattern = r'\.([a-zA-Z][a-zA-Z0-9_-]*(?:-[a-zA-Z0-9_-]*)*)'
    classes = []
    
    for match in re.findall(selector_pattern, css_content):
        classes.append(match)
    
    return list(set(classes))  # Remove duplicates

def check_missing_classes():
    """Check for missing CSS classes"""
    
    # Read the dashboard template
    template_path = 'dashboard/templates/dashboard/dashboard.html'
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        html_classes = extract_css_classes_from_html(html_content)
        print(f"Found {len(html_classes)} unique CSS classes in HTML template")
        
        # Read the CSS file
        css_path = 'static/css/tailwind.output.css'
        if os.path.exists(css_path):
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            css_classes = extract_css_classes_from_css(css_content)
            print(f"Found {len(css_classes)} unique CSS classes in CSS file")
            
            # Find missing classes
            missing_classes = []
            for html_class in html_classes:
                if html_class not in css_classes:
                    missing_classes.append(html_class)
            
            if missing_classes:
                print(f"\nMissing CSS classes ({len(missing_classes)}):")
                for cls in sorted(missing_classes):
                    print(f"  - {cls}")
            else:
                print("\nAll CSS classes are defined!")
                
            # Find unused classes
            unused_classes = []
            for css_class in css_classes:
                if css_class not in html_classes:
                    unused_classes.append(css_class)
            
            if unused_classes:
                print(f"\nUnused CSS classes ({len(unused_classes)}):")
                for cls in sorted(unused_classes)[:20]:  # Show first 20
                    print(f"  - {cls}")
                if len(unused_classes) > 20:
                    print(f"  ... and {len(unused_classes) - 20} more")
        else:
            print(f"CSS file not found: {css_path}")
    else:
        print(f"Template file not found: {template_path}")

if __name__ == "__main__":
    check_missing_classes() 