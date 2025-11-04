#!/usr/bin/env python3
"""
Analisa código não coberto e sugere casos de teste automaticamente
"""
import json
import ast
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional


class TestSuggester:
    def __init__(self):
        self.coverage_data = None
        self.suggestions = []
        
    def load_coverage(self) -> Optional[Dict]:
        """Carrega dados de cobertura do coverage.json"""
        try:
            with open('coverage.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ coverage.json not found. Run: pytest --cov=. --cov-report=json")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing coverage.json: {e}")
            return None
    
    def find_uncovered_functions(self, file_path: str, missing_lines: List[int]) -> List[Dict]:
        """Encontra funções não cobertas no arquivo"""
        suggestions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Verifica se a função tem linhas não cobertas
                    if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                        func_lines = set(range(node.lineno, node.end_lineno + 1))
                        uncovered = func_lines.intersection(set(missing_lines))
                        
                        if uncovered:
                            suggestions.append({
                                'file': file_path,
                                'function': node.name,
                                'line_start': node.lineno,
                                'line_end': node.end_lineno,
                                'uncovered_lines': sorted(list(uncovered)),
                                'complexity': self.estimate_complexity(node),
                                'has_docstring': ast.get_docstring(node) is not None
                            })
        except SyntaxError as e:
            print(f"⚠️  Syntax error in {file_path}: {e}")
        except Exception as e:
            print(f"⚠️  Error parsing {file_path}: {e}")
        
        return suggestions
    
    def estimate_complexity(self, node: ast.FunctionDef) -> str:
        """Estima complexidade da função baseada em tamanho"""
        if not hasattr(node, 'end_lineno'):
            return "unknown"
        
        lines = node.end_lineno - node.lineno
        
        if lines < 5:
            return "simple"
        elif lines < 20:
            return "medium"
        else:
            return "complex"
    
    def generate_test_template(self, func_info: Dict) -> str:
        """Gera template de teste para a função"""
        func_name = func_info['function']
        file_name = Path(func_info['file']).stem
        complexity = func_info['complexity']
        
        # Template baseado em complexidade
        if complexity == "simple":
            template = f'''def test_{func_name}():
    """Test {func_name} from {file_name}.py"""
    # Arrange
    # TODO: Setup test data
    
    # Act
    # result = {func_name}(...)
    
    # Assert
    # assert result == expected
    pass
'''
        else:
            template = f'''def test_{func_name}():
    """Test {func_name} from {file_name}.py - {complexity} function"""
    # Location: {func_info['file']}:{func_info['line_start']}
    # Uncovered lines: {len(func_info['uncovered_lines'])}
    
    # Test 1: Happy path
    # TODO: Test normal execution
    
    # Test 2: Edge cases
    # TODO: Test boundary conditions
    
    # Test 3: Error handling
    # TODO: Test exception cases
    pass

def test_{func_name}_error_handling():
    """Test {func_name} error cases"""
    # TODO: Test invalid inputs
    # TODO: Test exception raising
    pass
'''
        
        return template
    
    def calculate_priority(self, func: Dict, file_coverage: float) -> tuple:
        """Calcula prioridade do teste (para ordenação)"""
        # Prioridade: quanto menor coverage e mais complexa, maior prioridade
        priority_score = (100 - file_coverage) * 10
        
        if func['complexity'] == 'complex':
            priority_score += 30
        elif func['complexity'] == 'medium':
            priority_score += 15
        
        if not func['has_docstring']:
            priority_score += 5
        
        # Converte para categoria
        if priority_score > 700:
            return (1, "🔴 HIGH")
        elif priority_score > 400:
            return (2, "🟡 MEDIUM")
        else:
            return (3, "🟢 LOW")
    
    def analyze(self):
        """Analisa todos os arquivos e gera sugestões"""
        self.coverage_data = self.load_coverage()
        
        if not self.coverage_data:
            return []
        
        files = self.coverage_data.get('files', {})
        
        for file_path, data in files.items():
            # Skip test files and non-Python files
            if file_path.startswith('test_') or not file_path.endswith('.py'):
                continue
            
            # Skip if file doesn't exist
            if not os.path.exists(file_path):
                continue
            
            missing_lines = data.get('missing_lines', [])
            if not missing_lines:
                continue
            
            coverage_pct = data.get('summary', {}).get('percent_covered', 0)
            
            # Only suggest tests for files with < 80% coverage
            if coverage_pct < 80:
                funcs = self.find_uncovered_functions(file_path, missing_lines)
                
                for func in funcs:
                    priority_num, priority_label = self.calculate_priority(func, coverage_pct)
                    
                    self.suggestions.append({
                        'priority_num': priority_num,
                        'priority': priority_label,
                        'file': file_path,
                        'function': func['function'],
                        'coverage': coverage_pct,
                        'complexity': func['complexity'],
                        'uncovered_lines': len(func['uncovered_lines']),
                        'template': self.generate_test_template(func),
                        'location': f"{file_path}:{func['line_start']}"
                    })
        
        return self.suggestions
    
    def print_report(self):
        """Imprime relatório de sugestões"""
        suggestions = self.analyze()
        
        if not suggestions:
            print("✅ All code is well tested! (>80% coverage on all files)")
            return
        
        print(f"\n🧪 Found {len(suggestions)} functions needing tests:\n")
        print("=" * 80)
        
        # Sort by priority
        suggestions.sort(key=lambda x: (x['priority_num'], -x['coverage']))
        
        for idx, sugg in enumerate(suggestions, 1):
            print(f"\n{idx}. {sugg['priority']} {sugg['file']}::{sugg['function']}")
            print(f"   Coverage: {sugg['coverage']:.1f}% | Complexity: {sugg['complexity']}")
            print(f"   Location: {sugg['location']}")
            print(f"   Missing: {sugg['uncovered_lines']} lines")
            print(f"\n   Test Template:")
            print("   " + "\n   ".join(sugg['template'].split('\n')))
        
        print("\n" + "=" * 80)
        
        # Save to file
        output_file = 'suggested_tests.py'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Auto-generated test suggestions\n")
            f.write("# Review and adapt before using\n")
            f.write("# Generated by: .github/scripts/suggest_tests.py\n\n")
            f.write("import pytest\n\n")
            
            for sugg in suggestions:
                f.write(f"# Priority: {sugg['priority']} | Coverage: {sugg['coverage']:.1f}%\n")
                f.write(f"# File: {sugg['location']}\n")
                f.write(sugg['template'])
                f.write("\n\n")
        
        print(f"\n💾 Test templates saved to: {output_file}")
        print(f"📋 Review and copy to appropriate test file\n")
        
        # Summary statistics
        high_priority = sum(1 for s in suggestions if s['priority_num'] == 1)
        medium_priority = sum(1 for s in suggestions if s['priority_num'] == 2)
        low_priority = sum(1 for s in suggestions if s['priority_num'] == 3)
        
        print("📊 Summary:")
        print(f"   🔴 High Priority:   {high_priority}")
        print(f"   🟡 Medium Priority: {medium_priority}")
        print(f"   🟢 Low Priority:    {low_priority}")
        print(f"   📝 Total:           {len(suggestions)}\n")


def main():
    """Main entry point"""
    print("🔍 Analyzing test coverage and generating suggestions...\n")
    
    suggester = TestSuggester()
    suggester.print_report()
    
    # Return exit code based on findings
    if suggester.suggestions:
        high_priority = sum(1 for s in suggester.suggestions if s['priority_num'] == 1)
        if high_priority > 0:
            print(f"⚠️  Found {high_priority} high priority items requiring tests")
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
