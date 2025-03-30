# COMPREHENSIVE SCRIPT REVISIONS

I would like to add revisions to the script to make it more robust and informative. These revisions ARE NOT for effeciency, they are for clarity and to provide a more detailed report. The revisions should be EXACTLY as I specified below.

## OVERVIEW OF REVISIONS

- Use Rich library for aesthetic formatting and a more comprehensive reporting system.

1. 'sys_INPUTS' LIST ALL INPUTS FROM THE MODULES
2. 'sys_OUTPUTS' LIST ALL OUTPUTS TO THE COMBINED FILE,
3. 'sys_VALIDATION' LIST RESULTS SIDE BY SIDE THEM SIDE BY SIDE TO PROVIDE A VISUAL FORMAT OF VALIDATION.
4. 'sys_REPORTS' TOTAL NUMBER OF VALIDATED AND FAILED MODULES. THEN LIST ALL OF THE FAILEDMODULES THAT HAD NO OUTPUTS.

## SCRIPT FUNCTIONALITY AND AESTHETICS

EACH STEP OF THE SCRIPT HAS AN ASCII BORDER STYLE AESTHETIC THAT IS TO BE LINED UP WITH THE TITLE.
THE TOP AND BOTTOM ARE THE SAME.
THE MIDDLE SECTION OF THE BORDER STARTS WITH HASHTAG (#) BEFORE THE TITLE, AND ENDS WITH ASTERISKS (\*) AFTER THE TITLE. THE TOP AND BOTTOM SHOULD LINE UP WITH THE MIDDLE SECTION.

TOP - '# ----------------'
MIDDLE - '# TITLE_EXAMPLE \*
BOTTOM - '# ----------------'

DYNAMIC SEPERATOR: '<:---:>' - is used to separate the sections of the script. For brevity, in the '### TERMINAL WORKFLOW' section I have included it small, but in the working script it should span the length of the terminal and adjust to its size.

### STATIC VALUES:

[IN] - STATIC: Visual label and aesthetic for the input.
[OUT] - STATIC: Visual label and aesthetic for the output.
[VALIDATED] - STATIC: The aesthetic render of {PASS}.
[--- NULL ---] - STATIC: The aesthetic render of {FAIL}.

### DYNAMIC VALUES:

{input_module} - DYNAMIC: title of component from the modulated mermaid diagrams.
{output_module} - DYNAMIC: title of componenet from the output of the combine_diagram.py script..
{STATUS} - DYNAMIC: The status of the module {✅ | ❌}
{RESULT} - DYNAMIC: The result of the module {PASS | FAIL}
{PASS} - DYNAMIC: Provides the aesthetic render [VALIDATED]
{FAIL} - DYNAMIC: Provides the aesthetic render [--- NULL ---]
{num_validated} - DYNAMIC: Total number of validated modules.
{num_failed} - DYNAMIC: Total number of null modules.
{list_all_null_modules} - DYNAMIC: List of all module namesthat had NULL output.

### HIDDEN COMMENTS

I HAVE INCLUDED HIDDEN COMMENTS FOR YOUR CONTEXT (<!-- THIS IS AHIDDEN COMMENT -->)

## TERMINAL EXAMPLE:

```
<:----------------------------------------------------------------------------:>

# -----------------
# > sys.INPUT[IN] *
# -----------------

> sys.INPUT[IN]: {input_module} | [OUT]: {output_module} {STATUS} -> {RESULT}

<:----------------------------------------------------------------------------:>
```

### TERMINAL WORKFLOW

<!-- Step 1. BEFORE the combine_diagrams.py script is run, count total number of inputs in the MODULATED versions of the mermaid diagrams -->

# -----------------

# > sys.INPUT[IN] \*

# -----------------

<!-- Complete list of components that input from the modulated mermaid diagrams -->

> sys.[IN]: {name_of_module}

<:---:>

<!-- Step 2. Run the combine_diagrams.py script and list all modules that output. -->

# -------------------

# > sys.OUTPUT[OUT] \*

# -------------------

<!-- Complete list of modules that output from the combine_diagrams.py script -->

> sys.[OUT]: {name_of_module}

<:---:>

<!-- Step 3. Compare input and output lists, REPORT VALIDATION RESULTS IN THIS FORMAT -->

> sys.[IN]: {name_of_module} | [OUT]: {name_of_module} {STATUS} -> {RESULT}

<!-- THE FORMAT ABOVE SHOULD RENDER AS THE EXAMPLES BELOW DEPENDING ON THE OUTPUTS -->

# ------------------

# > sys.VALIDATION \*

# ------------------

<!-- VALIDATED EXAMPLE -->

> sys.[IN]: {name_of_module} | [OUT]: {name_of_module} {✅} -> {VALIDATED}

<!-- FAILED EXAMPLE -->

> sys.[IN]: {name_of_module} | [OUT]:--- NULL ---{❌} -> {FAILED}

<:---:>

# ---------------

# > sys.REPORTS \*

# ---------------

<!-- REPORT NUMERICAL RESULTS -->

> sys.[✅]: {num_validated}
> sys.[❌]: {num_failed}

<!-- REPORT VALIDATION RESULTS IN THIS FORMAT -->

> sys.report: init == [---NULL OUTPUTS---]

{list_all_NULL_modules}

<:---:>
cursor:extension/Early-AI.EarlyAI
