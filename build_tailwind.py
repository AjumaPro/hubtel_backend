#!/usr/bin/env python3
"""
Simple script to build Tailwind CSS
"""
import subprocess
import sys
import os

def build_tailwind():
    try:
        # Try to use npx tailwindcss
        cmd = [
            'npx', 'tailwindcss',
            '--input', './static/css/tailwind.css',
            '--output', './static/css/tailwind.output.css',
            '--minify'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Tailwind CSS built successfully!")
            print(f"Output: {result.stdout}")
        else:
            print("❌ Error building Tailwind CSS:")
            print(f"Error: {result.stderr}")
            
            # Fallback: create a basic CSS file
            print("Creating fallback CSS file...")
            create_fallback_css()
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        print("Creating fallback CSS file...")
        create_fallback_css()

def create_fallback_css():
    """Create a basic CSS file with essential styles"""
    css_content = """/* Fallback CSS - Tailwind build failed */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Basic reset */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f8fafc;
    color: #1e293b;
    line-height: 1.6;
    font-size: 14px;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Dashboard Header */
.dashboard-header {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: white;
    padding: 1.5rem 2rem;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
    position: relative;
    overflow: hidden;
}

.dashboard-header h1 {
    font-size: 2rem;
    font-weight: 800;
    margin-bottom: 0.25rem;
    position: relative;
    z-index: 1;
}

.dashboard-header .subtitle {
    opacity: 0.95;
    font-size: 1rem;
    font-weight: 500;
    position: relative;
    z-index: 1;
}

/* Navigation */
.dashboard-nav {
    background: white;
    border-bottom: 1px solid #e2e8f0;
    padding: 0 2rem;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    position: sticky;
    top: 0;
    z-index: 100;
}

.nav-tabs {
    display: flex;
    list-style: none;
    gap: 0;
}

.nav-tabs li {
    border-bottom: 3px solid transparent;
    transition: all 0.3s ease;
}

.nav-tabs li.active {
    border-bottom-color: #4f46e5;
}

.nav-tabs a {
    display: block;
    padding: 1.25rem 1.5rem;
    text-decoration: none;
    color: #64748b;
    font-weight: 600;
    font-size: 0.95rem;
    transition: all 0.3s ease;
}

.nav-tabs a:hover {
    background: #f8fafc;
    color: #4f46e5;
}

.nav-tabs li.active a {
    color: #4f46e5;
    font-weight: 700;
}

/* Main Content */
.dashboard-content {
    padding: 2rem;
    max-width: 1400px;
    margin: 0 auto;
}

/* Stats Grid */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: white;
    padding: 1.5rem;
    border-radius: 16px;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    border: 1px solid #f1f5f9;
    position: relative;
    overflow: hidden;
}

.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
}

.stat-card h3 {
    color: #64748b;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.75rem;
    font-weight: 600;
}

.stat-card .value {
    font-size: 2.25rem;
    font-weight: 800;
    color: #1e293b;
    margin-bottom: 0.5rem;
    line-height: 1;
}

.stat-card .change {
    font-size: 0.875rem;
    color: #10b981;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

/* Buttons */
.btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 600;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s ease;
}

.btn-primary {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: white;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
}

.btn-primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
}

.btn-success {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
}

.btn-success:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
}

.btn-outline {
    background: transparent;
    color: #4f46e5;
    border: 2px solid #4f46e5;
    font-weight: 600;
}

.btn-outline:hover {
    background: #4f46e5;
    color: white;
    transform: translateY(-1px);
}

.btn-sm {
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
}

/* Data Sections */
.data-section {
    background: white;
    border-radius: 16px;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;
    border: 1px solid #f1f5f9;
    overflow: hidden;
}

.section-header {
    padding: 1.5rem 2rem;
    border-bottom: 1px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #f8fafc;
}

.section-header h2 {
    color: #1e293b;
    font-size: 1.25rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.section-actions {
    display: flex;
    gap: 0.75rem;
    align-items: center;
}

/* Tables */
.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.875rem;
}

.data-table th,
.data-table td {
    padding: 1rem 1.5rem;
    text-align: left;
    border-bottom: 1px solid #f1f5f9;
}

.data-table th {
    background: #f8fafc;
    font-weight: 700;
    color: #1e293b;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    position: sticky;
    top: 0;
    z-index: 10;
}

.data-table tr:hover {
    background: #f8fafc;
}

.data-table .status {
    padding: 0.375rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
}

.status.success {
    background: #dcfce7;
    color: #059669;
}

.status.pending {
    background: #fef3c7;
    color: #d97706;
}

.status.failed {
    background: #fee2e2;
    color: #dc2626;
}

/* Responsive Design */
@media (max-width: 768px) {
    .dashboard-content {
        padding: 1rem;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
    }
    
    .nav-tabs {
        flex-direction: column;
    }
    
    .nav-tabs li {
        border-bottom: none;
        border-left: 3px solid transparent;
    }
    
    .nav-tabs li.active {
        border-left-color: #4f46e5;
        border-bottom-color: transparent;
    }
    
    .data-table {
        font-size: 0.8rem;
    }
    
    .data-table th,
    .data-table td {
        padding: 0.75rem;
    }
    
    .section-header {
        flex-direction: column;
        gap: 1rem;
        align-items: flex-start;
    }
    
    .section-actions {
        width: 100%;
        justify-content: flex-start;
        flex-wrap: wrap;
    }
}
"""
    
    with open('./static/css/tailwind.output.css', 'w') as f:
        f.write(css_content)
    
    print("✅ Fallback CSS file created successfully!")

if __name__ == "__main__":
    build_tailwind() 