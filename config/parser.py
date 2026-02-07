"""
YAML Parser for Orchestration

Parses workflow definitions with effects, configurations, and context.
"""

import yaml
from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass
from effect import Effect


@dataclass
class EffectDefinition:
    """Parsed effect definition"""
    name: str
    effect_class: str
    config: Dict[str, Any]

    def __repr__(self):
        return f"EffectDef({self.name}, {self.effect_class}, config={self.config})"


@dataclass
class WorkflowDefinition:
    """Complete workflow definition"""
    name: str
    effects: List[EffectDefinition]
    context: Dict[str, Any]
    
    def __repr__(self):
        return f"Workflow({self.name}, effects={len(self.effects)}, context keys={list(self.context.keys())})"


class YAMLParser:
    """Parse YAML workflow definitions"""
    
    def __init__(self, effect_registry: Optional[Dict[str, Type[Effect]]] = None):
        """
        Initialize parser
        
        Args:
            effect_registry: Dict mapping effect class names to Effect subclasses
        """
        self.effect_registry = effect_registry or {}
    
    def register_effect(self, name: str, effect_class: Type[Effect]) -> None:
        """Register an effect class"""
        self.effect_registry[name] = effect_class
    
    def parse_file(self, filepath: str) -> WorkflowDefinition:
        """Parse YAML file"""
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        return self.parse(data)
    
    def parse(self, data: Dict[str, Any]) -> WorkflowDefinition:
        """
        Parse workflow definition dict
        
        Expected structure:
        ```yaml
        workflow:
          name: my_workflow
          context:
            key1: value1
            key2: value2
          effects:
            - name: effect1
              class: ClassName
              config:
                param1: value1
                param2: value2
            - name: effect2
              class: ClassName
              config:
                param3: value3
        ```
        """
        if 'workflow' not in data:
            raise ValueError("YAML must contain 'workflow' key")
        
        workflow_data = data['workflow']
        
        # Parse metadata
        name = workflow_data.get('name', 'unnamed_workflow')
        context = workflow_data.get('context', {})
        
        # Parse effects
        effects_data = workflow_data.get('effects', [])
        effects = [self._parse_effect(e) for e in effects_data]
        
        return WorkflowDefinition(
            name=name,
            effects=effects,
            context=context
        )
    
    def _parse_effect(self, effect_data: Dict[str, Any]) -> EffectDefinition:
        """Parse single effect definition"""
        name = effect_data.get('name')
        effect_class = effect_data.get('class')
        config = effect_data.get('config', {})
        
        if not name:
            raise ValueError("Effect must have 'name'")
        if not effect_class:
            raise ValueError(f"Effect '{name}' must have 'class'")
        
        return EffectDefinition(
            name=name,
            effect_class=effect_class,
            config=config
        )
    
    def instantiate_effect(self, effect_def: EffectDefinition) -> Effect:
        """
        Create effect instance from definition
        
        Args:
            effect_def: EffectDefinition with class name and config
        
        Returns:
            Effect instance
        
        Raises:
            ValueError: If effect class not registered
        """
        class_name = effect_def.effect_class
        
        if class_name not in self.effect_registry:
            raise ValueError(
                f"Effect class '{class_name}' not registered. "
                f"Available: {list(self.effect_registry.keys())}"
            )
        
        effect_class = self.effect_registry[class_name]
        return effect_class(**effect_def.config)
    
    def instantiate_workflow(self, workflow_def: WorkflowDefinition) -> tuple[List[Effect], Dict[str, Any]]:
        """
        Create all effect instances and return with context
        
        Args:
            workflow_def: WorkflowDefinition
        
        Returns:
            Tuple of (effects list, context dict)
        """
        effects = [self.instantiate_effect(e) for e in workflow_def.effects]
        return effects, workflow_def.context


class WorkflowBuilder:
    """Fluent builder for workflow definitions"""
    
    def __init__(self, name: str):
        self.name = name
        self.effects: List[EffectDefinition] = []
        self.context: Dict[str, Any] = {}
    
    def add_effect(self, name: str, effect_class: str, **config) -> 'WorkflowBuilder':
        """Add an effect to workflow"""
        self.effects.append(
            EffectDefinition(name=name, effect_class=effect_class, config=config)
        )
        return self
    
    def set_context(self, **context) -> 'WorkflowBuilder':
        """Set workflow context"""
        self.context.update(context)
        return self
    
    def add_context(self, key: str, value: Any) -> 'WorkflowBuilder':
        """Add context value"""
        self.context[key] = value
        return self
    
    def build(self) -> WorkflowDefinition:
        """Build workflow definition"""
        return WorkflowDefinition(
            name=self.name,
            effects=self.effects,
            context=self.context
        )
    
    def to_yaml(self) -> str:
        """Convert to YAML string"""
        workflow_def = self.build()
        data = {
            'workflow': {
                'name': workflow_def.name,
                'context': workflow_def.context,
                'effects': [
                    {
                        'name': e.name,
                        'class': e.effect_class,
                        'config': e.config
                    }
                    for e in workflow_def.effects
                ]
            }
        }
        return yaml.dump(data, default_flow_style=False, sort_keys=False)


# ============================================================================
# INTEGRATION WITH EXECUTOR
# ============================================================================

class WorkflowExecutor:
    """Execute parsed workflows"""
    
    def __init__(self, parser: YAMLParser):
        self.parser = parser
    
    def execute_from_file(self, filepath: str, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Load and execute workflow from YAML file
        
        Args:
            filepath: Path to YAML file
            initial_context: Additional context to merge
        
        Returns:
            Final context dict
        """
        workflow_def = self.parser.parse_file(filepath)
        return self.execute(workflow_def, initial_context)
    
    def execute(self, workflow_def: WorkflowDefinition, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute workflow definition
        
        Args:
            workflow_def: WorkflowDefinition to execute
            initial_context: Additional context to merge
        
        Returns:
            Final context dict
        """
        effects, context = self.parser.instantiate_workflow(workflow_def)
        
        # Merge initial context
        if initial_context:
            context.update(initial_context)
        
        # Execute effects in sequence
        for effect in effects:
            context = effect.execute(context)
        
        return context