#!/usr/bin/env python3
"""
Accurate modularization of frontend/index.html
Maps all functions with exact boundaries and dependencies
"""

import os
import re
from pathlib import Path

class AccurateModularizer:
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
        
        # Find JS boundaries
        self.js_start = None
        self.js_end = None
        for i, line in enumerate(self.lines):
            if "<script>" in line and self.js_start is None:
                self.js_start = i + 1
            elif "</script>" in line and self.js_start is not None:
                self.js_end = i
                break
                
        self.js_lines = self.lines[self.js_start:self.js_end] if self.js_start and self.js_end else []

    def find_all_functions(self):
        """Find all functions with exact line boundaries"""
        functions = []
        i = 0
        
        while i < len(self.js_lines):
            line = self.js_lines[i].strip()
            
            # Match function declarations
            if (line.startswith('function ') or 
                line.startswith('const ') and ('= function' in line or '= (' in line or '= async' in line) or
                line.startswith('async function')):
                
                # Find function name
                if line.startswith('function '):
                    name = line.split('(')[0].replace('function ', '').strip()
                elif line.startswith('async function'):
                    name = line.split('(')[0].replace('async function ', '').strip()
                else:  # const
                    name = line.split('=')[0].replace('const ', '').strip()
                
                # Find function end by counting braces
                start_line = i
                brace_count = 0
                found_start = False
                
                for j in range(i, len(self.js_lines)):
                    current_line = self.js_lines[j]
                    
                    # Count opening braces
                    for char in current_line:
                        if char == '{':
                            brace_count += 1
                            found_start = True
                        elif char == '}' and found_start:
                            brace_count -= 1
                            
                    # Function ends when braces balance
                    if found_start and brace_count == 0:
                        end_line = j
                        
                        # Get full function code
                        func_lines = self.js_lines[start_line:end_line + 1]
                        code = '\n'.join(func_lines)
                        
                        functions.append({
                            'name': name,
                            'start': start_line,
                            'end': end_line,
                            'code': code,
                            'lines': func_lines
                        })
                        
                        i = end_line + 1
                        break
                else:
                    i += 1
            else:
                i += 1
                
        return functions

    def categorize_functions(self, functions):
        """Categorize functions by purpose"""
        categories = {
            'config': [],
            'auth': [],
            'utils': [],
            'navigation': [],
            'dashboard': [],
            'forms': [],
            'chat': [],
            'ui': []
        }
        
        # Categorization rules
        auth_patterns = ['signIn', 'signOut', 'Auth', 'Google', 'updateAuthButton']
        utils_patterns = ['showToast', 'showLoading', 'hideLoading', 'generateSessionId', 'formatTimestamp']
        nav_patterns = ['showPage', 'showDashboard', 'showCreateForm', 'showChat', 'navigation']
        dashboard_patterns = ['loadForms', 'renderForms', 'deleteForms', 'dashboard']
        form_patterns = ['renderQuestions', 'createQuestion', 'updateQuestion', 'toggleQuestion', 
                        'renderDemographics', 'createDemographic', 'toggleDemographic', 'addQuestion',
                        'deleteQuestion', 'saveForm', 'previewForm', 'getCurrentFormData', 'validateForm']
        chat_patterns = ['initializeChat', 'sendMessage', 'displayMessage', 'handleChat', 'chat']
        ui_patterns = ['render', 'display', 'show', 'hide', 'update', 'create']
        
        for func in functions:
            name = func['name'].lower()
            categorized = False
            
            # Check each category
            for pattern in auth_patterns:
                if pattern.lower() in name:
                    categories['auth'].append(func)
                    categorized = True
                    break
                    
            if not categorized:
                for pattern in utils_patterns:
                    if pattern.lower() in name:
                        categories['utils'].append(func)
                        categorized = True
                        break
                        
            if not categorized:
                for pattern in nav_patterns:
                    if pattern.lower() in name:
                        categories['navigation'].append(func)
                        categorized = True
                        break
                        
            if not categorized:
                for pattern in dashboard_patterns:
                    if pattern.lower() in name:
                        categories['dashboard'].append(func)
                        categorized = True
                        break
                        
            if not categorized:
                for pattern in form_patterns:
                    if pattern.lower() in name:
                        categories['forms'].append(func)
                        categorized = True
                        break
                        
            if not categorized:
                for pattern in chat_patterns:
                    if pattern.lower() in name:
                        categories['chat'].append(func)
                        categorized = True
                        break
                        
            if not categorized:
                categories['ui'].append(func)
                
        return categories

    def extract_non_function_code(self, functions):
        """Extract code that's not inside functions"""
        # Find all function line ranges
        function_ranges = []
        for func in functions:
            function_ranges.append((func['start'], func['end']))
        
        # Sort ranges
        function_ranges.sort()
        
        # Extract non-function code
        non_function_lines = []
        last_end = 0
        
        for start, end in function_ranges:
            # Add lines before this function
            if start > last_end:
                non_function_lines.extend(self.js_lines[last_end:start])
            last_end = end + 1
            
        # Add remaining lines after last function
        if last_end < len(self.js_lines):
            non_function_lines.extend(self.js_lines[last_end:])
            
        return non_function_lines

    def create_modules(self, categories, non_function_code):
        """Create modular JavaScript files"""
        
        # Create config module with Firebase setup
        config_lines = []
        for line in non_function_code:
            if ('firebase' in line.lower() or 
                'const auth' in line or 
                'const db' in line or 
                'const rtdb' in line or
                'firebaseConfig' in line):
                config_lines.append(line)
        
        if config_lines:
            (self.js_dir / "config.js").write_text('\n'.join(config_lines))
            print(f"✅ Created config.js ({len(config_lines)} lines)")
        
        # Create other modules
        module_map = {
            'auth.js': categories['auth'],
            'utils.js': categories['utils'], 
            'navigation.js': categories['navigation'],
            'dashboard.js': categories['dashboard'],
            'forms.js': categories['forms'],
            'chat.js': categories['chat'],
            'ui.js': categories['ui']
        }
        
        for filename, funcs in module_map.items():
            if funcs:
                codes = [func['code'] for func in funcs]
                content = '\n\n'.join(codes)
                (self.js_dir / filename).write_text(content)
                print(f"✅ Created {filename} ({len(funcs)} functions)")
        
        # Create initialization code
        init_code = []
        for line in non_function_code:
            if ('lucide.createIcons' in line or
                'DOMContentLoaded' in line or
                'addEventListener' in line):
                init_code.append(line)
        
        # Add manual initialization
        init_code.extend([
            "",
            "// Initialize application", 
            "document.addEventListener('DOMContentLoaded', function() {",
            "    lucide.createIcons();",
            "    updateAuthButton();",
            "    showPage('landingPage');",
            "});"
        ])
        
        (self.js_dir / "init.js").write_text('\n'.join(init_code))
        print(f"✅ Created init.js")

    def create_modular_index(self):
        """Create new modular index.html"""
        # Find head section
        head_start = None
        head_end = None
        body_start = None
        
        for i, line in enumerate(self.lines):
            if "<head>" in line:
                head_start = i
            elif "</head>" in line:
                head_end = i
            elif "<body" in line:
                body_start = i
                break
                
        if not all([head_start, head_end, body_start]):
            print("❌ Could not find HTML structure")
            return None
            
        # Build new index
        new_lines = []
        
        # Add head section
        new_lines.extend(self.lines[head_start:head_end])
        new_lines.append('</head>')
        
        # Add body with script imports
        new_lines.extend([
            '<body>',
            '    <!-- Dynamic content container -->',
            '    <div id="app-root"></div>',
            '',
            '    <!-- Firebase -->',
            '    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-app-compat.js"></script>',
            '    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-auth-compat.js"></script>',
            '    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-firestore-compat.js"></script>',
            '    <script src="https://www.gstatic.com/firebasejs/9.22.2/firebase-database-compat.js"></script>',
            '',
            '    <!-- Modular Scripts -->',
            '    <script src="js/config.js"></script>',
            '    <script src="js/utils.js"></script>',
            '    <script src="js/auth.js"></script>',
            '    <script src="js/navigation.js"></script>',
            '    <script src="js/dashboard.js"></script>',
            '    <script src="js/forms.js"></script>',
            '    <script src="js/chat.js"></script>',
            '    <script src="js/ui.js"></script>',
            '    <script src="js/init.js"></script>',
            '</body>',
            '</html>'
        ])
        
        # Add original HTML content in app-root via JavaScript
        html_content = self.lines[body_start + 1:self.js_start - 1]
        html_js = 'document.getElementById("app-root").innerHTML = `' + '\\n'.join(html_content).replace('`', '\\`') + '`;'
        
        (self.js_dir / "content.js").write_text(html_js)
        new_lines.insert(-3, '    <script src="js/content.js"></script>')
        
        # Write new index
        new_index = self.base_dir / "index-modular.html"
        new_index.write_text('\n'.join(new_lines))
        print(f"✅ Created index-modular.html ({len(new_lines)} lines)")
        
        return new_index

    def run(self):
        """Execute accurate modularization"""
        print("🚀 Starting accurate modularization...")
        
        if not self.js_lines:
            print("❌ Could not find JavaScript section")
            return
            
        # Find all functions
        functions = self.find_all_functions()
        print(f"📊 Found {len(functions)} functions")
        
        # Categorize functions
        categories = self.categorize_functions(functions)
        
        # Extract non-function code
        non_function_code = self.extract_non_function_code(functions)
        
        # Create modules
        self.create_modules(categories, non_function_code)
        
        # Create modular index
        new_index = self.create_modular_index()
        
        if new_index:
            original_size = self.input_file.stat().st_size
            new_size = new_index.stat().st_size
            reduction = ((original_size - new_size) / original_size) * 100
            print(f"📊 Size: {original_size//1024}KB → {new_size//1024}KB ({reduction:.1f}% reduction)")
        
        print("✅ Accurate modularization complete!")

if __name__ == "__main__":
    modularizer = AccurateModularizer()
    modularizer.run()