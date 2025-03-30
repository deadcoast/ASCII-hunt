# CONTEXT AND REFERENCING FORMAT

Please help me create an optimized, creative and enhanced context and referencing format to provide context to my Agent LLM in the Cursor IDE.

Im trying to use my documents to create an optimized format that will allow the Agent in the Cursor IDE to Keep optimized context when coding. The format must be:
Simple enough for large codebases, but detailed enough that the Agent does not have to sort through large files to find its context.

## PAST ATTEMPTS

- I keep the documents in my codebase, and have the agent reference specific ones when i make a request. I need to try new, experimental ways of creating accessible context to the agent for codebases with 100+ code files/modules, balancing essential information with a concise triggering / referencing system. I have tried many things in the past as follow:

{[1.](Ineffecient Token Usage)}: I tried using index files, that did not work out well. The Agent was finding the files properly, but instead of going to the line the index referenced, it would search the entire file eating up tokens.
{[2.](Ineffective Agent Binding)}: I tried creating Mermaid infrastructure for each module in the codebase, the Agent didnt seem to follow them at all.
{[3.](No Contextual Awareness)}: I tried keeping class name and function definitions in a seperate file for a quick reference for naming spaces, but the Agent did not know what the files were, there wasnt enough context.
{[4.](Unclear or Confusing to Agent)}: I tried creating a large directory tree in the root, to reference the entire code base module naming, and in each subfolder i created its pertaining smaller directory tree of the files inside the subdirectory. Each directory file name had a markdown style task list box on it, to mark off when it was complete working on that file. I had hopes to achieve providing some sort of contextual memory or timeline, but I found the agent just completely ignored this. Or tried to update the entire directory tree at one.
{[5.](Constant Intervention)}: I tried creating a new, optimized format syntax of prompting i called `huntPrompt`, I designed it as a modified version of the native back end language of the LLM that they sometimes leak. I took examples from their hallucinations and used a hybrid of database syntax such as xml for the `< >` and json for the `{ }`. I found some sucess with this format, but still found it was not enough to justify the time each prompt and command took me to write out. I found the agent would use this sometimes, and others not. I will paste an example below:

```huntPrompt
<assistant>
  <!-- INIT sequentialthought -->
  <tool>
    Tool: read_file
    Arguments: {"STEP-1":"{target_file}", "should_read_entire_file":true}
    <result></result>
  </tool>
  <tool>
    Tool: edit_file
    Arguments: {"STEP-2":"{target_file}":"instructions":"Write your comprehensive "{DIAGNOSTIC-REPORT}", "code_edit":"""}
    <result></result>
  </tool>
  <tool>
    Tool: edit_file
    Arguments:{"STEP-3":"instructions":"When complete, prompt the user for approval to mark the "{DIAGNOSIS-TREE}" Task complete", "code_edit":""} 
    <results></results>
  </tool>
</assistant>
```

## NEW APPROACH

We need to formulate a new, optimized approach. Our approach should be creative, concise, and effective. It should balance Token Usage, Scalability, and Contextual awareness.

- The main purpose of this new, experimental and creative approach is to context focused.

It should be:

- Simple enough for large codebases {[3.]}, but detailed enough that the Agent does not have to sort through large files to find its context {[1.]}.
- Structured and Organized enough so that it does not require constant intervention from the user {[5.]}.
- Effectively and Accurately reference specific files, and specific lines of code within those files {[6.]}.
- Easily referenced by both the user and the Agent {[4.]}. When necessary, user should be able to point the Agent to the specific file, and the Agent should be able to reference it without confusion, heavy token usage, or limited context.
- Provide Two main Interaction points:
  - Documentation Archive for both the user and the Agent to reference.
  - An organized, easy to reference mapping system attached to the Documentation Archive,that can point to adequate context.
