# V0 Validation — Structural Validation

## Overview

V0 validation проверяет **структурную корректность** проекта и сгенерированного analytical layout **до** геометрической валидации (V1) и функциональной проверки (V2).

**Важно:** V0 НЕ проверяет геометрию (пересечения, containment, forbidden zones). Это задача V1.

## Architecture
ProjectConfig (input requirements)
↓
Generator / Solver
↓
AnalyticalLayout (generated geometry)
↓
V0 Validation (structural)
↓
V1 Validation (geometry)
↓
V2 Validation (functional/access)


## Что проверяет V0

### 1. ProjectConfig Validation

| Rule ID | Описание | Severity |
|---------|----------|----------|
| `CONFIG-JSON-001` | Конфиг — валидный JSON-объект (dict) | ERROR |
| `CONFIG-SCHEMA-001` | Конфиг соответствует JSON Schema | ERROR |
| `CONFIG-PROFILE-001` | ConstraintProfile существует и валиден | ERROR |
| `CONFIG-BOUNDARY-001` | Boundary присутствует с width_mm и height_mm | ERROR |
| `CONFIG-MAXSIDE-001` | Max(boundary.width_mm, boundary.height_mm) ≤ 10000 | ERROR |
| `CONFIG-GRID-001` | Все значения кратны grid_quantum_mm (100) | ERROR (при reject) |
| `CONFIG-ROOMS-001` | Room programme не пустой | ERROR |
| `CONFIG-ID-001` | ID комнат уникальны | ERROR |

### 2. AnalyticalLayout Validation

| Rule ID | Описание | Severity |
|---------|----------|----------|
| `LAYOUT-JSON-001` | Layout — валидный JSON-объект | ERROR |
| `LAYOUT-ROOMS-001` | Rooms массив присутствует | ERROR |
| `LAYOUT-ROOM-FIELDS-001` | Каждая комната имеет x_mm, y_mm, width_mm, height_mm, declared_area_m2 | ERROR |
| `LAYOUT-ID-001` | ID комнат уникальны | ERROR |

## Единицы измерения

- **Координаты и размеры:** целые мм (int)
- **Площадь:** float м²
- **Grid quantum:** 100 мм (по умолчанию)
- **Rounding policy:** `reject` (некратные значения → ERROR)

## Как использовать

### Запуск валидации

```python
from braim_floorplan_generator.validation import (
    ValidationEngine,
    ConstraintProfile,
    ProjectConfig,
    AnalyticalLayout,
)

# Загрузка профиля
profile = ConstraintProfile.from_json("configs/constraints/mvp_concept_100.json")

# Загрузка проекта
project = ProjectConfig.from_json("path/to/project.json")

# Валидация ProjectConfig
report = ValidationEngine.validate_project_config(project, profile)

if report.status == "INVALID":
    print("Project config is invalid:")
    for issue in report.issues:
        print(f"  - {issue.rule_id}: {issue.description}")

# После генерации layout
layout = generate_layout(project, profile)  # твой генератор

# Валидация AnalyticalLayout
layout_report = ValidationEngine.validate_layout_structure(layout, profile)
```

### Проверка возможности IFC-экспорта

```python
if not report.can_export_ifc():
    print("IFC export blocked: status =", report.status)
    
# Принудительный экспорт (только для отладки)
if report.can_export_ifc(override=True):
    print("IFC export allowed with override")
```

### Экспорт отчёта

```python
# JSON
report.export_json("validation_report.json")

# SVG (визуализация проблем)
report.export_svg("validation_report.svg")
```

## Статусы валидации

| Статус | Условие |
|--------|---------|
| `VALID` | Нет ERROR и WARNING |
| `VALID_WITH_WARNINGS` | Нет ERROR, но есть WARNING |
| `INVALID` | Есть хотя бы один ERROR |

## Известные ограничения V0

- ❌ Не проверяется containment комнат внутри boundary (V1)
- ❌ Не проверяются пересечения комнат (V1)
- ❌ Не проверяются forbidden zones (V1)
- ❌ Не проверяется declared_area_m2 vs geometric area (V1)
- ❌ Не проверяются adjacency/connectivity (V2)
- ❌ Не проверяются двери и окна (V3)

## Запуск тестов

```bash
python -m pytest tests/test_validation_v0.py -v
```

Ожидаемый результат: **30 passed**

## Связанные документы

- `schemas/constraint_profile.schema.json` — JSON Schema для профиля
- `configs/constraints/mvp_concept_100.json` — пример профиля
- `docs/validation_v1_spec.md` — спецификация V1 (геометрия)