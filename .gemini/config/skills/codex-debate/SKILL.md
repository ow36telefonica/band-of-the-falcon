---
name: codex-debate
description: Activate this skill when the user wants Gemini and Codex to debate or discuss a specific topic, codebase design, or refactoring strategy. This skill guides the agent to automatically run a 2-turn debate using `codex exec` and output the final consensus as a beautiful markdown report.
---

# Codex Debate Skill Instructions

When the user asks to "debate with Codex", "discuss with Codex", or says "〇〇についてCodexと議論して", follow this workflow to execute a structured, resource-efficient debate.

## Debate Rules & Constraints (Eco Mode)
To protect the user's ChatGPT Free limits, you MUST enforce the following constraints:
1. **Short Responses**: Limit both Gemini's and Codex's responses to **500 characters** per turn.
2. **Piped Input**: Always pipe an empty string `"" |` to the `codex.cmd` command to prevent it from waiting for stdin.
3. **Skip Checks**: Always use the `--skip-git-repo-check` option.
4. **2-Turn Limit**: Perform exactly 2 turns of debate (Turn 1: Gemini -> Codex -> Turn 2: Gemini -> Codex) and then summarize.

## Step-by-Step Workflow

### Step 1: Identify the Topic
Extract the debate topic or question from the user's request. If not specified, ask the user for a topic.

### Step 2: Turn 1 - Gemini's Thesis & Codex's Anti-Thesis
1. Formulate Gemini's opening argument (under 500 characters) based on the topic.
2. Run the first `codex exec` command.
   * Command template:
     ```powershell
     "" | C:\Users\xanth\AppData\Roaming\npm\codex.cmd exec --skip-git-repo-check "討論テーマ：『[TOPIC]』。ルール：500文字以内で要点のみ簡潔に反論または対案を述べてください。 Geminiの意見：『[GEMINI_OPINION_1]』"
     ```
3. Capture the stdout of Codex.

### Step 3: Turn 2 - Gemini's Rebuttal & Codex's Synthesis
1. Read Codex's response, and formulate Gemini's rebuttal (under 500 characters), conceding reasonable points but pushing for a synthesis or highlighting logical gaps.
2. Run the second `codex exec` command.
   * Command template:
     ```powershell
     "" | C:\Users\xanth\AppData\Roaming\npm\codex.cmd exec --skip-git-repo-check "討論テーマ：『[TOPIC]』。ルール：500文字以内で要点のみ簡潔に反論または対案を述べてください。 討論の経緯：1. Geminiは『[GEMINI_OPINION_1]』と主張。 2. Codexは『[CODEX_RESPONSE_1]』と反論。 3. Geminiの最新意見：『[GEMINI_REBUTTAL]』。 このGeminiの最新意見に対する、あなたの再反論または合意点を述べてください。"
     ```

3. Capture the final stdout of Codex.

### Step 4: Generate Report & Summary
1. Create a new report file under `C:\Users\xanth\Dropbox\debate_report\[THEME_NAME]YYYYMMDD.md` (e.g., `C:\Users\xanth\Dropbox\debate_report\投資を効率よく始めるには20260709.md`).
   * Note: Do NOT specify `ArtifactMetadata` when writing to this external directory, as it is outside the default artifact sandbox.
2. Format the report using the following structure:
   * Theme/Topic
   * Timeline / Debate Log (with emojis 🤖 for Gemini, 💻 for Codex)
   * A Mermaid diagram visualizing the consensus or final workflow
   * Practical conclusions or action items for the user
3. Inform the user that the debate is complete and link them to the newly created report file. Do not summarize the report in the chat response.
