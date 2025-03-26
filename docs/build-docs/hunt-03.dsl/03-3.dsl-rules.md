# 6.2 `Terms / Modules`- Commands Dictionary & Namespaces

## 6.2.1 Aliases & DSL Usage Examples

### Naming Conventions

1. `< AlphaBracket >` - Top Tier Cabin Bracket
   - PascalCase Naming Convention
2. `[BETA_BRACKET]` - Second Tier Cabin Bracket
   - SCREAMING_SNAKE_CASE Naming Convention
3. `{gammaBracket}` - Third Tier Cabin Bracket
   - camelCase Naming Convention
4. `(delta_brackets)` - Fourth Tier Cabin Bracket
   - snake_case Naming Convention

## 6.2.2 hunt CABIN BRACKET HIERARCHAL SYSTEM [Tag:hunt](#cbhs)

### AlphaBracket Type Rules

[Tag:hunt](#cbhs-A)

`< AlphaBrackets >`

- AlphaBracket Rules

  -

  - < AlphaBrackets > must align vertically, cannot be unreachable

- [hunt:rule](#A01): All huntSyntax statements and [CBHS] must start, and end with AlphaBrackets
- [hunt:rule](#A02): Utilizes the PascalCase Naming Structure.
- [hunt:rule](#A05): Always suffixed with a `:` operator
- [hunt:rule](#A06): Alpha brackets always begin with hunt
- [hunt:rule](#A07): defines the class operator, prefixed by hunt `< hunt: Class >`

### BetaBracket Type Rules

[Tag:hunt](#cbhs-B)

`[BETA_BRACKET]`

- [hunt:rule](#B01): Second Tier of the hunt Cabin Bracket System
- [hunt:rule](#B02): Utilizes the SCREAMING_SNAKE_CASE Naming Structure
- [hunt:rule](#B03): Utilizes the initiate `INIT` Command
- [hunt:rule](#B04): Beta brackets must adhere to [CBHS] Vertical Hierarchy, cannot be unreachable, cannot nest.
- [hunt:rule](#B05): Encapsulates the {gammaBracket} paramater and (delta_bracket) values

### gammaBracket Type Rules

[Tag:hunt](#cbhs-G)

`{gammaBracket}`

- [hunt:rule](#G01): {gammaBracket} is the Third Tier Bracket, cannot be called into or by Fourth Tier (delta_bracket)
- [hunt:rule](#G02): Utilizes the camelCase Naming Convention
- [hunt:rule](#G03): {gammaBracket} paramater must be closed before beginning a new one.
- [hunt:rule](#G04): does not have to adhere to [CBHS] Vertical Hierarchy
- [hunt:rule](#B06): Can call all three joining operators `&`, `@@`, `=`

### (delta_bracket) TypeRules

[Tag:hunt](#cbhs-D)

`(delta_bracket)`

- (delta_bracket) can close while aligning vertically
- (delta_bracket) may close without aligning vertically

- [hunt:rule](#D01): values must be encased in (delta_bracket)
- [hunt:rule](#D02): values must be assigned by a {Parameter} Function
- [hunt:rule](#D03): (delta_bracket) may close without Vertical Hierarchy enforcement
- [hunt:rule](#D04): values cannot traverse `& Link Director` or `@@ Chain Operator`
- [hunt:rule](#D05): (delta_bracket:(delta_bracket)) can encapsulate another with `:` Operator

## 6.2.3 Controllers [Tag:hunt](#huntcon)

### Assignment Marker Rules

[Tag:hunt](#huntcon-as)

`=` Assignment Marker

- [hunt:rule](#as01): Cannot be followed by any opening bracket
- [hunt:rule](#as02): Almost always followed by a new line
- [hunt:rule](#as03): May be followed only by a closing bracket of (delta_bracket)

### Bridge Controller Rules

[Tag:hunt](#huntcon-br)

`:` Bridge Commands Together

- [hunt:rule](#br01): Always used after hunt is defined at the top of code block, to bridge the rest of the huntCBHS
- [hunt:rule](#br02): Used to Bridge Commands, Parameters, and values Together
- [hunt:rule](#br03): Cannot be used more than once per line, UNLESS followed by a Chain Sequencer @@

### Link Director Rules

[Tag:hunt](#huntcon-lk)

`&` Directs functions, methods, or commands on the same line to link together

- [hunt:rule](#lk01): Can only be used after the `:` Bridge Controller and before the `@@` Chain method

### Chain Rules

[Tag:hunt](#huntcon-ch)

`@@` Chain Command Sequence

- [hunt:rule](#ch01): Used to chain `{param}:(value) & {param}:(value)` commands sequences together
- [hunt:rule](#ch02): can only be called after `:` Bridge Controller and `&` Link Director

### Comma Rules

[Tag:hunt](#huntcon-cm)

`,` Passes multiple values in a string or a list

- [hunt:rule](#cm01): Cannot be followed by any opening bracket
- [hunt:rule](#cm02): Almost always followed by a new line
- [hunt:rule](#cm03): May be followed only by a closing bracket of (delta_bracket)

## 6.2.4 Docstring Rules [Tag:hunt](#huntdoc)

### Global Docstring Character Rules

[Tag:hunt](#huntdoc-gd)

# Global Documenting Character

`#`

- [hunt:rule](#gd01): Documenting Character for single file documentation
- [hunt:rule](#gd02): The Single Docstring Characters can be placed Anywhere in the code

### Code Block Docstring Rules

[Tag:hunt](#huntdoc-ds)

`##--#` Docstring Opening Sequence
`#--##` Docstring Closing Sequence

- [hunt:rule](#ds01): Docstring Sequences are used when a more verbose code tagging is needed
- [hunt:rule](#ds02): Docstring sequences can ONLY be placed Directly Above an AlphaBracket
- [hunt:rule](#ds03): Content inside docstring must be prefixed with a global docstring character `#`

## 6.2.5 Command Type Rules [Tag:hunt](#huntctr)

### hunt Rules

[Tag:hunt](#huntctr-hunt)

hunt: Main Command Call

- [hunt:rule](#hunt01): Universal Code Block Unifier Command
- [hunt:rule](#hunt02): Must be placed after an opening Alpha Bracket unless Class is present
- [hunt:rule](#hunt03): Utilizes < alphaBracket >

### INIT Rules

[Tag:hunt](#huntctr-in)

INIT: Initiate Command Call for Parameters

- [hunt:rule](#in01): Initiate Command Call for Parameters
- [hunt:rule](#in02): Must be ALL CAPS
- [hunt:rule](#in03): Utilizes [BETA_BRACKET] SCREAMING_SNAKE_CASE

### PARAM Rules

[Tag:hunt](#huntctr-pr)

param: Initiate Command Call for values

- [hunt:rule](#pr01): Initiate Command Call for values
- [hunt:rule](#pr02): Must be all lowercase
- [hunt:rule](#pr03): Utilizes gammaBracket

### true Rules

[Tag:hunt](#huntctr-tr)

true: Return EXEC

- [hunt:rule](#tr01): Confirms the Return EXEC
- [hunt:rule](#tr02): Utilizes (delta_bracket)
- [hunt:rule](#tr03): Must be lowercase

### false Rules

[Tag:hunt](#huntctr-fl)

false: Passes the Return EXEC

- [hunt:rule](#fl01): Passes the Return EXEC
- [hunt:rule](#fl02): Utilizes (delta_bracket)
- [hunt:rule](#fl03): Must be lowercase

### EXEC Rules

[Tag:hunt](#huntctr-ex)

EXEC

- [hunt:rule](#ex01): All EXEC functions must start a new < AlphaBracket > directly after and attached to the closing AlphaBracket
- [hunt:rule](#ex02): The EXEC functions must have their own open and closed EpsilonBracket
- [hunt:rule](#ex03): The EXEC function must encase all modifiers and parameters in < AlphaBracket > at the end of the code block

### floop Rules

[Tag:hunt](#huntctr-flo)

floop

- [hunt:rule](#flo01): huntCBHS: {gammaBracket}
- [hunt:rule](#flo02): Parameter modifier for looping code blocks with EXEC, Commands, Parameters and values with huntCabin Brackets
- [hunt:rule](#flo03): Requires a numeric value, if specifying target functions, use floop = (variable):(numeric_value)
- [hunt:rule](#flo04): Loop command, takes numerical variations
- [hunt:rule](#flo05): If used after @@ Chain, requires {gammaBracket}

### req Rules

[Tag:hunt](#huntctr-req)

req

- [hunt:rule](#req01): huntCBHS: {gammaBracket}
- [hunt:rule](#req02): Used to Specify the lines, huntB, or functions when entire code block Execution is not desired
- [hunt:rule](#req03): To specify variable requirements, use req:(variable)
- [hunt:rule](#req04): If used after @@ Chain, requires {gammaBracket}

### prohib Rules

[Tag:hunt](#huntctr-pro)

`prohib`

- [hunt:rule](#pro01): huntCBHS: {gammaBracket}
- [hunt:rule](#pro02): Requirement, unskippable. Forces the code to run this variable, if not found, code exits
- [hunt:rule](#pro03): Used to reinforce restrictive commands, values, initiations or parameters
- [hunt:rule](#pro04): Can be used as a cancel command or with values in a loop
- [hunt:rule](#pro05): If used after @@ Chain, requires {gammaBracket}
