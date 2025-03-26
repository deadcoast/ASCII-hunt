# HUNT DSL Syntax Specification

## 1. Introduction to HUNT DSL

The HUNT Domain Specific Language (DSL) is a custom language designed specifically for defining patterns to recognize UI elements in ASCII art. It uses a structured syntax based on the Cabin Brackets Hierarchical System (CBHS) which organizes code into nested levels of brackets, each with its own specific purpose and naming conventions.

## 2. Cabin Brackets Hierarchical System (CBHS)

The CBHS consists of four levels of brackets that structure the DSL code:

### 2.1 Alpha Brackets `< >`

Alpha brackets represent the top level of the hierarchy and typically contain command calls or modifiers.

**Naming Convention**: PascalCase

**Example**:

```hunt
< hunt:
    [INIT =
        {param =
            (val)
        }
    ]
><EXEC>
```

### 2.2 Beta Brackets `[ ]`

Beta brackets represent the second level and typically contain initialization commands.

**Naming Convention**: SCREAMING_SNAKE_CASE

**Example**:

```hunt
[INIT GATHER =
    {param tag:button =
        (val "[", "]")
    }
]
```

### 2.3 Gamma Brackets `{ }`

Gamma brackets represent the third level and typically contain parameter definitions.

**Naming Convention**: camelCase

**Example**:

```hunt
{param tag:checkbox =
    (val "□", "■", "☐", "☑", "[ ]", "[X]")
}
```

### 2.4 Delta Brackets `( )`

Delta brackets represent the fourth level and typically contain values for parameters.

**Naming Convention**: snake_case

**Example**:

```hunt
(val,
 top_left:(┌),
 top_right:(┐),
 bottom_left:(└),
 bottom_right:(┘),
 horizontal:(─),
 vertical:(│)
)
```

## 3. Detailed Syntax Rules

### 3.1 Command Syntax

Commands are the primary way to perform actions in the HUNT DSL. Each command has a specific syntax and purpose.

#### 3.1.1 hunt Command

The `hunt` command is the top-level command that defines a pattern or module.

**Syntax**:

```hunt
< hunt:
    [INIT =
        {param =
            (val)
        }
    ]
><EXEC>
```

#### 3.1.2 Track Command

The `Track` command is used to search and map the canvas for specific patterns.

**Syntax**:

```hunt
< hunt Track:
    [INIT GATHER =
        {param tag:component_type =
            (val pattern_elements)
        }
    ]
><EXEC>
```

**Example**:

```hunt
< hunt Track:
    [INIT GATHER =
        {param tag:button =
            (val "[", "]")
        }
        {param pluck:button_text =
            (val "\\[(.+?)\\]")
        }
    ]
><EXEC>
```

#### 3.1.3 GATHER/GET Command

The `GATHER` or `GET` command is used to extract character and coordinate data.

**Syntax**:

```hunt
[INIT GATHER =
    {param extraction_type:target =
        (val extraction_pattern)
    }
]
```

**Example**:

```hunt
[INIT GATHER =
    {param tag:checkbox =
        (val "□", "■", "☐", "☑", "[ ]", "[X]")
    }
    {param pluck:checkbox_state =
        (val "■|☑|\\[X\\]", "□|☐|\\[ \\]")
    }
]
```

#### 3.1.4 HARVEST/HARV Command

The `HARVEST` or `HARV` command is used to collect data from multiple regions.

**Syntax**:

```hunt
[INIT HARVEST =
    {param from:regions =
        (val region_names)
    }
]
```

**Example**:

```hunt
[INIT HARVEST =
    {param from:regions =
        (val "header", "body", "footer")
    }
]
```

### 3.2 Parameter Syntax

Parameters are defined in gamma brackets and specify the details of a command.

#### 3.2.1 tag Parameter

The `tag` parameter is used to organize and label components.

**Syntax**:

```hunt
{param tag:component_type =
    (val pattern_elements)
}
```

**Example**:

```hunt
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
```

#### 3.2.2 pluck Parameter

The `pluck` parameter is used to extract specific content from a component.

**Syntax**:

```hunt
{param pluck:target =
    (val pattern)
}
```

**Example**:

```hunt
{param pluck:title =
    (val "^(.+)$")
}
```

#### 3.2.3 trap Parameter

The `trap` parameter is used to define constraints or validation rules.

**Syntax**:

```hunt
{param trap =
    (val constraint_message)
}
```

**Example**:

```hunt
{param trap =
    (val "window must have a title")
}
```

### 3.3 Controllers

Controllers are special syntax elements that modify how commands and parameters interact.

#### 3.3.1 Bridge Controller `:`

The Bridge Controller links commands or parameters together.

**Example**:

```hunt
< hunt Track:
    [INIT GATHER =
        {param tag:button}:{pluck:text =
            (val pattern)
        }
    ]
><EXEC>
```

#### 3.3.2 Chain Controller `@@`

The Chain Controller connects multiple commands in sequence.

**Example**:

```hunt
<
    [
        {
            ()
        }
    ]
><EXEC:req & config @@ {floop:1}>
```

#### 3.3.3 Assignment Marker `=`

The Assignment Marker associates a value with a parameter or command.

**Example**:

```hunt
[INIT =
    {param =
        (val)
    }
]
```

### 3.4 Execution Control

Execution control defines how the pattern is applied and validated.

#### 3.4.1 EXEC

The `EXEC` keyword executes the pattern with optional modifiers.

**Syntax**:

```hunt
><EXEC:modifiers>
```

**Example**:

```hunt
><EXEC:req & config @@ {floop:(val regex(1))}>
```

#### 3.4.2 req

The `req` modifier makes the pattern requirements strict.

**Example**:

```hunt
><EXEC:{req}>
```

#### 3.4.3 prohib

The `prohib` modifier specifies prohibited patterns.

**Example**:

```hunt
{param prohib:config =
    ()
}
```

## 4. Complete Pattern Examples

### 4.1 Button Pattern

```hunt
< hunt Track:
    [INIT GATHER =
        {param tag:button =
            (val "[", "]")
        }
        {param pluck:button_text =
            (val "\\[(.+?)\\]")
        }
    ]
><EXEC>
```

This pattern recognizes buttons enclosed in square brackets and extracts the button text.

### 4.2 Checkbox Pattern

```hunt
< hunt Track:
    [INIT GATHER =
        {param tag:checkbox =
            (val "□", "■", "☐", "☑", "[ ]", "[X]")
        }
        {param pluck:checkbox_state =
            (val "■|☑|\\[X\\]", "□|☐|\\[ \\]")
        }
        {param pluck:checkbox_label =
            (val "(?:■|□|☑|☐|\\[X\\]|\\[ \\])\\s*(.+)")
        }
    ]
><EXEC>
```

This pattern recognizes checkboxes in various forms and extracts their state and label.

### 4.3 Window Pattern

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
            (val "^(.+)$")
        }
    ]
><EXEC>
```

This pattern recognizes windows defined by box-drawing characters and extracts the window title.

### 4.4 Text Field Pattern

```hunt
< hunt Track:
    [INIT GATHER =
        {param tag:text_field =
            (val "___", "...", "___________")
        }
        {param pluck:field_label =
            (val "(.+?):\\s*(?:___|\\.\\.\\.|_________)")
        }
        {param pluck:field_value =
            (val "(?:___|\\.\\.\\.|_________)(.*)")
        }
    ]
><EXEC>
```

This pattern recognizes text fields represented by underscores or dots and extracts their label and value.

### 4.5 Advanced Pattern with Multiple Components

```hunt
< hunt UiForm:
    [INIT GATHER =
        {param tag:form =
            (val
             top_left:(┌),
             top_right:(┐),
             bottom_left:(└),
             bottom_right:(┘),
             horizontal:(─),
             vertical:(│)
            )
        }
    ]
    [INIT HARVEST =
        {param from:regions =
            (val "header", "body", "footer")
        }
    ]
    [INIT COOK =
        {param format:tkinter =
            (val
             template_style:"modern",
             include_validation:true
            )
        }
    ]
><EXEC:{req} & {config} @@ {floop:1}>
```

This advanced pattern defines a form with multiple regions and specifies how to generate Tkinter code with a modern style and validation.

### 4.6 Pattern with Constraints and Validation

```hunt
< hunt ValidatedInput:
    [INIT GATHER =
        {param tag:input =
            (val "___", "[ ]", "(...)")
        }
        {param pluck:input_label =
            (val "(.+?):")
        }
        {param trap =
            (val "input must have a label")
        }
    ]
    [INIT VALIDATE =
        {param required:true =
            (val)
        }
        {param pattern:"[A-Za-z0-9]+" =
            (val)
        }
    ]
><EXEC:req>
```

This pattern defines an input field with validation constraints, requiring the input to match a specific pattern.

## 5. DSL Integration Examples

### 5.1 Combining Multiple Patterns

```hunt
##-#
# Define a complete dialog box pattern
#-##

< hunt Dialog:
    [INIT GATHER =
        {param tag:dialog =
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
            (val "^(.+)$")
        }
    ]
    [INIT HARVEST =
        {param from:patterns =
            (val "Button", "Checkbox", "TextField")
        }
    ]
    [INIT RACK =
        {param view:ascii =
            (val highlight:true)
        }
    ]
><EXEC>
```

This example combines multiple patterns to recognize a complete dialog box with different types of controls.

### 5.2 Custom Component Definition

```hunt
< hunt Slot:
    [INIT ASSIGN =
        {param custom_dropdown:{component} =
            (val
             pattern:"▼|▶|[▼]|[▶]",
             label_pattern:"(.+?)\\s*(?:▼|▶|\\[▼\\]|\\[▶\\])",
             state_mapping:{
                "▼": "expanded",
                "▶": "collapsed",
                "[▼]": "expanded",
                "[▶]": "collapsed"
             }
            )
        }
    ]
><EXEC>

< hunt Track:
    [INIT GATHER =
        {param tag:dropdown =
            (val custom_dropdown)
        }
    ]
><EXEC>
```

This example defines a custom dropdown component and then uses it in a tracking pattern.

### 5.3 Pattern with Advanced Code Generation

```hunt
< hunt ButtonGroup:
    [INIT GATHER =
        {param tag:button_group =
            (val
             top_left:(┌),
             top_right:(┐),
             bottom_left:(└),
             bottom_right:(┘),
             horizontal:(─),
             vertical:(│)
            )
        }
        {param pluck:group_title =
            (val "^(.+)$")
        }
    ]
    [INIT HARVEST =
        {param from:patterns =
            (val "Button")
        }
    ]
    [INIT COOK =
        {param format:tkinter =
            (val
             template:"""
             # {$group_title} Button Group
             {$group_var} = tk.LabelFrame(root, text="{$group_title}")
             {$group_var}.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

             {$buttons}
             """
            )
        }
    ]
><EXEC>
```

This example defines a button group with a custom code generation template for Tkinter.

## 6. DSL Syntax Extensions

### 6.1 Custom Command Definition

```hunt
< hunt Slot:
    [INIT ASSIGN =
        {param ANALYZE:{command} =
            (val
             syntax:"[INIT ANALYZE = {param} ]",
             handler:"analyze_components",
             description:"Performs detailed analysis of component relationships"
            )
        }
    ]
><EXEC>

< hunt Track:
    [INIT ANALYZE =
        {param relationship:contains =
            (val tolerance:5)
        }
    ]
><EXEC>
```

This example defines a custom ANALYZE command and then uses it in a pattern.

### 6.2 Pattern Inheritance

```hunt
< hunt Slot:
    [INIT ASSIGN =
        {param BaseButton:{pattern} =
            (val
             tag:"button",
             pattern:"\\[(.+?)\\]"
            )
        }
    ]
><EXEC>

< hunt Track:
    [INIT GATHER =
        {param tag:submit_button =
            (val
             inherit:BaseButton,
             pattern_filter:"\\[(Submit|OK|Save)\\]"
            )
        }
    ]
><EXEC>
```

This example defines a base button pattern and then creates a specialized submit button pattern that inherits from it.

### 6.3 Advanced Constraint Definition

```hunt
< hunt Slot:
    [INIT ASSIGN =
        {param layout_constraints:{constraints} =
            (val
             min_spacing:1,
             max_depth:5,
             alignment:"strict"
            )
        }
    ]
><EXEC>

< hunt Track:
    [INIT GATHER =
        {param tag:form =
            (val
             top_left:(┌),
             top_right:(┐),
             bottom_left:(└),
             bottom_right:(┘)
            )
        }
        {param trap:layout =
            (val layout_constraints)
        }
    ]
><EXEC>
```

This example defines custom layout constraints and then applies them in a form pattern.
