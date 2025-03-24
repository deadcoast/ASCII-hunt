#### 1. Box and Container Patterns

```hunt
< hunt Track:
    [INIT GATHER =
        {param tag:window =
            (val
             top_left:(┌),
             top_right:(┐),
             bottom_left:(└),
             bottom_right:(┘),
             horizontal:(─),
             vertical:(│)
            )
        }
        {param pluck:title =
            (val "^(.+)$")  # First line of content
        }
    ]
><EXEC>

< hunt Track:
    [INIT GATHER =
        {param tag:panel =
            (val
             top_left:(╔),
             top_right:(╗),
             bottom_left:(╚),
             bottom_right:(╝),
             horizontal:(═),
             vertical:(║)
            )
        }
    ]
><EXEC>

< hunt Track:
    [INIT GATHER =
        {param tag:group_box =
            (val
             top_left:(┏),
             top_right:(┓),
             bottom_left:(┗),
             bottom_right:(┛),
             horizontal:(━),
             vertical:(┃)
            )
        }
        {param pluck:group_title =
            (val "^(.+)$")  # First line of content
        }
    ]
><EXEC>
```

#### 2. Control Patterns

```hunt
< hunt Track:
    [INIT GATHER =
        {param tag:button =
            (val "[", "]")
        }
        {param pluck:button_text =
            (val "\\[(.+?)\\]")  # Text between brackets
        }
    ]
><EXEC>

< hunt Track:
    [INIT GATHER =
        {param tag:checkbox =
            (val "□", "■", "☐", "☑", "[ ]", "[X]")
        }
        {param pluck:checkbox_state =
            (val "■|☑|\\[X\\]", "□|☐|\\[ \\]")
        }
        {param pluck:checkbox_label =
            (val "(?:■|□|☑|☐|\\[X\\]|\\[ \\])\\s*(.+)")  # Text after checkbox
        }
    ]
><EXEC>

< hunt Track:
    [INIT GATHER =
        {param tag:radio_button =
            (val "○", "●", "( )", "(•)")
        }
        {param pluck:radio_state =
            (val "●|\\(•\\)", "○|\\( \\)")
        }
        {param pluck:radio_label =
            (val "(?:●|○|\\(•\\)|\\( \\))\\s*(.+)")  # Text after radio button
        }
    ]
><EXEC>

< hunt Track:
    [INIT GATHER =
        {param tag:dropdown =
            (val "▼", "▶", "[▼]", "[▶]")
        }
        {param pluck:dropdown_state =
            (val "▼|\\[▼\\]", "▶|\\[▶\\]")
        }
        {param pluck:dropdown_label =
            (val "(.+?)\\s*(?:▼|▶|\\[▼\\]|\\[▶\\])")  # Text before dropdown
        }
    ]
><EXEC>
```

#### 3. Text and Input Patterns

```hunt
< hunt Track:
    [INIT GATHER =
        {param tag:text_field =
            (val "___", "...", "___________")
        }
        {param pluck:field_label =
            (val "(.+?):\\s*(?:___|\\.\\.\\.|_________)")  # Label before field
        }
        {param pluck:field_value =
            (val "(?:___|\\.\\.\\.|_________)(.*)")  # Text in field
        }
    ]
><EXEC>

< hunt Track:
    [INIT GATHER =
        {param tag:text_area =
            (val
             top_left:(┌),
             top_right:(┐),
             bottom_left:(└),
             bottom_right:(┘),
             horizontal:(─),
             vertical:(│)
            )
        }
        {param pluck:area_content =
            (val "(?s)(?<=\\n)(.+?)(?=\\n[└┘])")  # Content between borders
        }
    ]
><EXEC>

< hunt Track:
    [INIT GATHER =
        {param tag:label =
            (val ":", "=")
        }
        {param pluck:label_text =
            (val "(.+?)(?::|=)")  # Text before colon or equals
        }
        {param pluck:label_value =
            (val "(?::|=)\\s*(.+)")  # Text after colon or equals
        }
    ]
><EXEC>
```

#### 4. Relationship Patterns

```hunt
< hunt Track:
    [INIT GATHER =
        {param tag:contains =
            (val "contains", "inside")
        }
    ]
><EXEC>

< hunt Track:
    [INIT GATHER =
        {param tag:adjacent =
            (val "next_to", "adjacent")
        }
        {param pluck:direction =
            (val "right", "left", "above", "below")
        }
    ]
><EXEC>

< hunt Track:
    [INIT GATHER =
        {param tag:labeled_by =
            (val "labeled_by", "described_by")
        }
    ]
><EXEC>
```

## 7.2 Pattern Recognition DSL Specification

The pattern recognition DSL will be designed to allow declarative definition of ASCII UI patterns:

### Syntax and Semantics

1. **Top-Level Commands**:

   - `hunt`: Define a pattern or module
   - `Track`: Define a tracking pattern for UI elements
   - `GATHER`/`GET`: Extract characters and coordinates
   - `HARVEST`/`HARV`: Collect data from multiple regions
   - `RACK`: Preview pattern visualization
   - `COOK`: Generate code from recognized patterns

2. **Parameter Expressions**:

   - `tag`: Define pattern tags for classification
   - `pluck`: Extract specific content based on patterns
   - `trap`: Define constraints or validation rules
   - `skin`: Extract from partial matches
   - `log`: Control debugging and logging output

3. **Execution Controls**:
   - `EXEC`: Execute pattern processing
   - `req`: Make pattern requirements strict
   - `prohib`: Specify prohibited patterns
   - `config`: Configure processing options

### Pattern Definition Example

```hunt
< hunt Button:
    [INIT GATHER =
        {param tag:button =
            (val
             box_chars:(┌┐└┘│─),  # Optional box characters
             bracket_chars:("[", "]")  # Button can be in [] brackets
            )
        }
        {param pluck:button_text =
            (val
             bracket_pattern:"\\[(.+?)\\]",  # Extract text between []
             box_pattern:"(?<=\\n\\s*)(.+?)(?=\\s*\\n)"  # Extract text in box
            )
        }
        {param trap =
            (val "text must not be empty")  # Validation rule
        }
    ]
><EXEC>
```

### Pattern Matching Process

The pattern matching process will follow these steps:

1. **Parse HUNT Patterns**: Convert HUNT DSL code into an AST
2. **Register Patterns**: Store patterns in the pattern registry
3. **Apply Patterns**: Apply patterns to detected components from earlier pipeline stages
4. **Extract Properties**: Extract component properties based on pattern matches
5. **Determine Types**: Classify components based on best pattern matches
6. **Detect Relationships**: Apply relationship patterns to determine component hierarchies
7. **Validate Results**: Apply validation rules to ensure pattern integrity

### Integration with Component Model

The DSL will integrate with the component model through these mechanisms:

1. **Type Classification**: Determine the UI element type based on pattern matches
2. **Property Extraction**: Extract properties like labels, values, and states
3. **Relationship Detection**: Establish parent-child and logical relationships
4. **Validation Rules**: Ensure component integrity and completeness

### Extensibility Mechanisms

The DSL will support extensibility through:

1. **Custom Pattern Libraries**: Load user-defined pattern collections
2. **Pattern Inheritance**: Extend existing patterns with additional rules
3. **Plugin Architecture**: Register custom pattern matchers and extractors
4. **Configuration System**: Configure pattern matching behavior

## 7.3 Implementation Roadmap

The implementation of the HUNT DSL integration will follow this timeline:

### Phase 1: Core Parser and Interpreter (Weeks 1-3)

1. **Implement HUNT Parser**: Complete the lexer and parser for HUNT syntax
2. **Build AST Representation**: Create data structures for the abstract syntax tree
3. **Develop Basic Interpreter**: Implement core command interpretation
4. **Create Pattern Registry**: Build the pattern storage and retrieval system

### Phase 2: Pattern Matching System (Weeks 4-6)

1. **Implement Pattern Matchers**: Develop matchers for different pattern types
2. **Create Property Extractors**: Build extractors for component properties
3. **Develop Relationship Detectors**: Implement relationship detection logic
4. **Build Validation System**: Create the constraint validation system

### Phase 3: Integration with Framework (Weeks 7-9)

1. **Create Pipeline Processor**: Implement the HUNT recognition processor
2. **Develop Component Model Adapter**: Connect DSL to component model
3. **Build Command Line Interface**: Extend CLI for HUNT operations
4. **Implement Configuration System**: Create configuration management

### Phase 4: Pattern Library Development (Weeks 10-12)

1. **Create Basic Pattern Library**: Implement common UI element patterns
2. **Develop Relationship Patterns**: Create patterns for component relationships
3. **Build Complex Composite Patterns**: Implement patterns for composite components
4. **Create Pattern Testing Framework**: Develop tools for testing patterns

### Phase 5: Visualization and Debugging (Weeks 13-15)

1. **Implement Visualizer**: Create pattern match visualization tool
2. **Build Debugging Utilities**: Develop debugging and tracing tools
3. **Create Pattern Editor**: Build interactive pattern development environment
4. **Develop Documentation Generator**: Create tools for documenting patterns
