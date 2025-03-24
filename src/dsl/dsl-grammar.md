## 3.4 Component Mapping DSL

### Mathematical Foundation

The Component Mapping DSL provides a declarative way to specify mappings between components and code templates. We can formalize this as follows:

Let $D$ be the language of the DSL, and $I : D \rightarrow (C \rightarrow S)$ be an interpretation function that maps DSL expressions to component transformation functions.

For a DSL expression $d \in D$, the interpretation generates a function $f_d = I(d)$ such that $f_d : C \rightarrow S$ maps components to source code.

DSL expressions can be composed through operations:

- Sequential composition: $(d_1 ; d_2)$ interpreted as $f_{d_1} \cdot f_{d_2}$
- Conditional application: $(d_1 \text{ if } p \text{ else } d_2)$ interpreted as $\lambda c . p(c) ? f_{d_1}(c) : f_{d_2}(c)$
- Repetition: $(d^*)$ interpreted as $\lambda c . \bigoplus_{c' \in children(c)} f_d(c')$

The DSL provides a concise way to specify complex transformations without writing general-purpose code.

### DSL Grammar

The Component Mapping DSL will use a syntax designed for readability and expressiveness:

```
# EBNF Grammar for Component Mapping DSL

mapping ::= "component" component_type ":" NEWLINE INDENT mappings DEDENT
mappings ::= (property_mapping | children_mapping | template)+
property_mapping ::= "property" property_name "=" expression
children_mapping ::= "children" ":" NEWLINE INDENT child_mappings DEDENT
child_mappings ::= (child_mapping)+
child_mapping ::= component_type "=>" expression
template ::= "template" ":" NEWLINE INDENT template_code DEDENT
expression ::= literal | reference | function_call | conditional
reference ::= "$" (property_name | "parent" "." property_name | "index" | "type")
function_call ::= function_name "(" [arguments] ")"
arguments ::= expression ("," expression)*
conditional ::= "if" condition "then" expression "else" expression
literal ::= STRING | NUMBER | "true" | "false" | "null"
```

Example DSL code:

```
component Button:
    property text = $text
    property enabled = $enabled
    property width = compute_width($text)
    property height = 30

    template:
        <button class="btn {if $enabled then 'active' else 'disabled'}"
                style="width: {$width}px; height: {$height}px;">
            {$text}
        </button>
```
