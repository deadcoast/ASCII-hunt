## TEMPLATE USAGE INSTRUCTIONS

1. Replace all placeholders marked with {CURLY_BRACES} with your project-specific information.
2. Customize component names, IDs, and responsibilities to match your project's architecture.
3. Update implementation statuses to reflect the current state of your project.
4. Define connection patterns that align with your project's architectural patterns and technology stack.
5. Add project-specific processes, optimizations, and integration strategies.
6. Document actual issues, missing connections, and priorities for your project.
7. Extend or modify the component categories and connection types as needed for your architecture.
8. This template is designed to be used alongside the System_Architecture.md template to provide a comprehensive architectural documentation for your project.
9. Parse all JSON objects and TypeScript interfaces as structured specifications that define the intended implementation
10. When implementing a component, first analyze the relevant codebase files to understand current implementation status
11. Fill in any placeholder values in the interfaces with concrete code implementations that align with architectural standards

## IMPLEMENTATION GUIDANCE FOR AI

When implementing this architecture:

1. Component Analysis - First analyze each component to understand its responsibilities and connections.
2. Connection Implementation - Focus on implementing missing connections between components following these patterns:

   - UI → Context: Use React hooks
   - Context → Manager: Use middleware pattern
   - Manager → Event: Use event emission pattern
   - Event → UI: Use subscription pattern

3. System Integration - Focus first on these critical integration points:

   - {MANAGER_1} → {CONTEXT_1} → {UI_COMPONENT_2} chain
   - {MANAGER_2} → {CONTEXT_4} → module UI components
   - Event system subscription for UI components
   - {SYSTEM_COMPONENT_1} integration with manager update methods

4. Consistent Patterns - Implement these architectural patterns consistently:

   - State management: Single source of truth with clear update flows
   - Event handling: Consistent subscription and emission patterns
   - Initialization: Proper dependency resolution and readiness checks
   - UI updates: Consistent data flow from managers to UI

5. Implementation Sequence - Follow this sequence for implementation:
   1. Core infrastructure ({SYSTEM_COMPONENT_1}, {EVENT_SYSTEM_ID})
   2. Manager standardization
   3. Context-Manager connections
   4. UI-Context connections
   5. Performance optimizations
