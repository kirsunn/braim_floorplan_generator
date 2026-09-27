"""
IDS-валидация планировки.

Класс PlanValidator позволяет:
- Добавлять правила вида «комната X должна иметь NetFloorArea ≥ Y»
- validate_ifc() возвращает сводку (pass/fail)
- export_bcf() — выгрузку замечаний в формате BCF
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import ifctester
import ifctester.ids
from .generator import Layout


@dataclass
class ValidationReport:
    """Отчёт о валидации."""
    passed: bool
    total_rules: int
    passed_rules: int
    failed_rules: int
    issues: List[Dict[str, Any]]
    
    def summary(self) -> str:
        status = "✓ PASS" if self.passed else "✗ FAIL"
        return f"{status}: {self.passed_rules}/{self.total_rules} правил пройдено"
    
    def to_dict(self) -> Dict:
        return {
            "passed": self.passed,
            "total_rules": self.total_rules,
            "passed_rules": self.passed_rules,
            "failed_rules": self.failed_rules,
            "issues": self.issues,
        }


class PlanValidator:
    """Валидатор планировок через IDS."""
    
    def __init__(self):
        self.rules = []
    
    def add_rule(self, rule: Dict[str, Any]) -> None:
        self.rules.append(rule)
    
    def validate_layout(self, layout: Layout) -> ValidationReport:
        issues = []
        passed_rules = 0
        
        for rule in self.rules:
            rule_passed = self._check_rule(layout, rule)
            
            if rule_passed:
                passed_rules += 1
            else:
                issues.append({
                    "rule": rule.get("name", "Unnamed rule"),
                    "description": f"Rule failed: {rule}",
                })
        
        total_rules = len(self.rules)
        failed_rules = total_rules - passed_rules
        
        return ValidationReport(
            passed=(failed_rules == 0),
            total_rules=total_rules,
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            issues=issues,
        )
    
    def _check_rule(self, layout: Layout, rule: Dict[str, Any]) -> bool:
        entity = rule.get("entity", "IfcSpace")
        prop = rule.get("property", "")
        operator = rule.get("operator", ">=")
        value = rule.get("value", 0.0)
        filter_spec = rule.get("filter", {})
        
        if entity != "IfcSpace":
            return True
        
        filter_type = filter_spec.get("type")
        
        for room in layout.rooms:
            if filter_type and room.type != filter_type:
                continue
            
            if prop == "Pset_SpaceCommon.NetFloorArea":
                actual_value = room.area
            else:
                continue
            
            if operator == ">=":
                if actual_value < value:
                    return False
            elif operator == ">":
                if actual_value <= value:
                    return False
            elif operator == "<=":
                if actual_value > value:
                    return False
            elif operator == "<":
                if actual_value >= value:
                    return False
            elif operator == "==":
                if actual_value != value:
                    return False
        
        return True
    
    def validate_ifc(self, ifc_filepath: str, ids_filepath: str) -> ValidationReport:
        ids_file = ifctester.ids.open(ids_filepath)
        
        import ifcopenshell
        ifc_file = ifcopenshell.open(ifc_filepath)
        
        results = ifctester.validate(ids_file, ifc_file)
        
        total_rules = len(ids_file.specifications)
        passed_rules = sum(1 for spec in ids_file.specifications if spec.id in results and results[spec.id].passing)
        failed_rules = total_rules - passed_rules
        
        issues = []
        for spec in ids_file.specifications:
            if spec.id in results and not results[spec.id].passing:
                for fail in results[spec.id].fails:
                    issues.append({
                        "rule": spec.name or spec.id,
                        "element": str(fail.element),
                        "description": fail.reason,
                    })
        
        return ValidationReport(
            passed=(failed_rules == 0),
            total_rules=total_rules,
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            issues=issues,
        )
    
    def export_bcf(self, report: ValidationReport, filepath: str) -> None:
        bcf_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<Markup>
  <Header>
    <Project>
      <Name>BRAIM Floorplan Validation</Name>
    </Project>
  </Header>
  <Topic>
    <Title>Floorplan Validation Report</Title>
    <Status>Active</Status>
  </Topic>
"""
        
        for i, issue in enumerate(report.issues, 1):
            bcf_content += f"""  <Comment>
    <Date>2026-09-27T12:00:00</Date>
    <Comment>Issue {i}: {issue.get('rule', 'Unknown rule')}</Comment>
    <Status>Active</Status>
  </Comment>
"""
        
        bcf_content += "</Markup>"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(bcf_content)
