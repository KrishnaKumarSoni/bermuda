#!/usr/bin/env python3
"""
Modularize frontend/index.html into separate files
Extracts HTML sections, JavaScript modules, and CSS components
"""

import os
import re
from pathlib import Path

class FrontendModularizer:
    def __init__(self, input_file="frontend/index.html"):
        self.input_file = Path(input_file)
        self.content = self.input_file.read_text()
        self.lines = self.content.split('\n')
        
        # Create output directories
        self.base_dir = self.input_file.parent
        self.js_dir = self.base_dir / "js"
        self.pages_dir = self.base_dir / "pages"
        self.css_dir = self.base_dir / "css"
        
        for dir_path in [self.js_dir, self.pages_dir, self.css_dir]:
            dir_path.mkdir(exist_ok=True)
            
        # Create subdirectories for JS modules
        for subdir in ["config", "auth", "dashboard", "forms", "chat", "utils"]:
            (self.js_dir / subdir).mkdir(exist_ok=True)

    def find_section_bounds(self, start_pattern, end_pattern):
        """Find start and end line numbers for a section"""
        start_idx = None
        end_idx = None
        
        for i, line in enumerate(self.lines):
            if start_pattern in line and start_idx is None:
                start_idx = i
            elif end_pattern in line and start_idx is not None:
                end_idx = i
                break
                
        return (start_idx, end_idx) if start_idx and end_idx else None

    def extract_html_sections(self):
        """Extract major HTML page sections"""
        sections = {
            "landing": ("<!-- Landing Page -->", "<!-- Dashboard Page -->"),
            "dashboard": ("<!-- Dashboard Page -->", "<!-- Create Form Page -->"),
            "create-form": ("<!-- Create Form Page -->", "<!-- Chat Interface Page -->"),
            "chat": ("<!-- Chat Interface Page -->", "<script>")
        }
        
        extracted_sections = {}
        
        for name, (start_marker, end_marker) in sections.items():
            bounds = self.find_section_bounds(start_marker, end_marker)
            if bounds:
                start_idx, end_idx = bounds
                # Get the content between markers (excluding the end marker line)
                section_lines = self.lines[start_idx:end_idx]
                extracted_sections[name] = '\n'.join(section_lines)
                
                # Write to separate file
                output_file = self.pages_dir / f"{name}.html"
                output_file.write_text('\n'.join(section_lines))
                print(f"✅ Extracted {name}.html ({len(section_lines)} lines)")
        
        return extracted_sections

    def extract_css_styles(self):
        """Extract embedded CSS styles"""
        style_bounds = self.find_section_bounds("<style>", "</style>")
        if style_bounds:
            start_idx, end_idx = style_bounds
            css_lines = self.lines[start_idx+1:end_idx]  # Exclude <style> tags
            css_content = '\n'.join(css_lines)
            
            output_file = self.css_dir / "components.css"
            output_file.write_text(css_content)
            print(f"✅ Extracted components.css ({len(css_lines)} lines)")
            return css_content
        return None

    def extract_javascript_modules(self):
        """Extract and categorize JavaScript functions"""
        script_bounds = self.find_section_bounds("<script>", "</script>")
        if not script_bounds:
            print("❌ Could not find JavaScript section")
            return
            
        start_idx, end_idx = script_bounds
        js_lines = self.lines[start_idx+1:end_idx]  # Exclude <script> tags
        js_content = '\n'.join(js_lines)
        
        # Define function categories with patterns
        modules = {
            "config/firebase.js": [
                r"// Firebase Configuration.*?const rtdb = firebase\.database\(\);",
            ],
            "auth/auth.js": [
                r"// Auth state observer.*?}\);",
                r"function signIn.*?^\}",
                r"function signOut.*?^\}",
                r"function showAuthModal.*?^\}",
                r"function hideAuthModal.*?^\}",
                r"function showSignUp.*?^\}",
            ],
            "utils/helpers.js": [
                r"// Utility functions.*?^\}",
                r"function showToast.*?^\}",
                r"function showLoading.*?^\}",
                r"function hideLoading.*?^\}",
                r"function generateSessionId.*?^\}",
                r"function formatTimestamp.*?^\}",
            ],
            "dashboard/dashboard.js": [
                r"// Navigation functions.*?^\}",
                r"function showPage.*?^\}",
                r"function showDashboard.*?^\}",
                r"function loadForms.*?^\}",
                r"function renderForms.*?^\}",
                r"function deleteForms.*?^\}",
            ],
            "forms/form-builder.js": [
                r"// Form creation.*?^\}",
                r"function showCreateForm.*?^\}",
                r"function displayFormBuilder.*?^\}",
                r"function renderQuestions.*?^\}",
                r"function renderDemographics.*?^\}",
                r"function addQuestion.*?^\}",
                r"function deleteQuestion.*?^\}",
                r"function updateQuestion.*?^\}",
            ],
            "forms/form-preview.js": [
                r"function previewForm.*?^\}",
                r"function getCurrentFormData.*?^\}",
                r"function validateFormData.*?^\}",
            ],
            "chat/chat.js": [
                r"// Chat functionality.*?^\}",
                r"function initializeChat.*?^\}",
                r"function sendMessage.*?^\}",
                r"function displayMessage.*?^\}",
                r"function handleChatMessage.*?^\}",
            ]
        }
        
        # Extract each module
        extracted_functions = set()
        
        for module_path, patterns in modules.items():
            module_content = []
            
            for pattern in patterns:
                matches = re.finditer(pattern, js_content, re.MULTILINE | re.DOTALL)
                for match in matches:
                    function_code = match.group(0)
                    if function_code not in extracted_functions:
                        module_content.append(function_code)
                        extracted_functions.add(function_code)
            
            if module_content:
                output_file = self.js_dir / module_path
                output_file.write_text('\n\n'.join(module_content))
                print(f"✅ Extracted {module_path} ({len(module_content)} functions)")

        # Create main.js with initialization code
        main_js_content = '''// Main application initialization
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Lucide icons
    lucide.createIcons();
    
    // Initialize authentication observer
    if (typeof initAuthObserver === 'function') {
        initAuthObserver();
    }
    
    // Show initial page
    showPage('landingPage');
});
'''
        (self.js_dir / "main.js").write_text(main_js_content)
        print("✅ Created main.js")

    def create_modular_index(self):
        """Create new modular index.html"""
        head_end = None
        body_start = None
        
        for i, line in enumerate(self.lines):
            if "</head>" in line:
                head_end = i
            elif "<body" in line:
                body_start = i
                break
        
        if not (head_end and body_start):
            print("❌ Could not find head/body boundaries")
            return
            
        # Build new index.html
        new_content = []
        
        # Keep head section but add new CSS link
        head_lines = self.lines[:head_end]
        # Add modular CSS before closing head
        head_lines.insert(-1, '    <link rel="stylesheet" href="css/components.css">')
        new_content.extend(head_lines)
        new_content.append('</head>')
        
        # Minimal body with page containers
        new_content.extend([
            '<body>',
            '    <!-- Page content will be loaded dynamically -->',
            '    <div id="app-container">',
            '        <div id="landingPage"></div>',
            '        <div id="dashboardPage" class="hidden"></div>',
            '        <div id="createFormPage" class="hidden"></div>',
            '        <div id="chatPage" class="hidden"></div>',
            '    </div>',
            '',
            '    <!-- Firebase -->',
            '    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-app-compat.js"></script>',
            '    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-auth-compat.js"></script>',
            '    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-firestore-compat.js"></script>',
            '    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-database-compat.js"></script>',
            '    ',
            '    <!-- Modular JavaScript -->',
            '    <script src="js/config/firebase.js"></script>',
            '    <script src="js/utils/helpers.js"></script>',
            '    <script src="js/auth/auth.js"></script>',
            '    <script src="js/dashboard/dashboard.js"></script>',
            '    <script src="js/forms/form-builder.js"></script>',
            '    <script src="js/forms/form-preview.js"></script>',
            '    <script src="js/chat/chat.js"></script>',
            '    <script src="js/main.js"></script>',
            '</body>',
            '</html>'
        ])
        
        # Write new index.html
        new_index_path = self.base_dir / "index-modular.html"
        new_index_path.write_text('\n'.join(new_content))
        print(f"✅ Created index-modular.html ({len(new_content)} lines)")
        
        return new_index_path

    def run(self):
        """Execute the modularization process"""
        print("🚀 Starting frontend modularization...")
        print(f"📄 Input: {self.input_file} ({len(self.lines)} lines)")
        
        # Extract components
        self.extract_css_styles()
        self.extract_html_sections()
        self.extract_javascript_modules()
        
        # Create new modular index
        new_index = self.create_modular_index()
        
        # Calculate size reduction
        original_size = self.input_file.stat().st_size
        if new_index and new_index.exists():
            new_size = new_index.stat().st_size
            reduction = ((original_size - new_size) / original_size) * 100
            print(f"📊 Size reduction: {original_size//1024}KB → {new_size//1024}KB ({reduction:.1f}% smaller)")
        
        print("✅ Modularization complete!")
        print(f"📁 Files created in: {self.base_dir}")

if __name__ == "__main__":
    modularizer = FrontendModularizer()
    modularizer.run()