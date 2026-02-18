const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, BorderStyle } = require("docx");
const fs = require("fs");

// Create Document
const doc = new Document({
    sections: [{
        properties: {},
        children: [
            // TITLE
            new Paragraph({
                text: "AMIR ALI'S COMPLETE WRITING BIBLE",
                heading: HeadingLevel.TITLE,
                alignment: AlignmentType.CENTER,
            }),
            new Paragraph({ text: "" }), // spacing

            new Paragraph({
                text: "Priority: ABSOLUTE | Date: 2026-02-15",
                alignment: AlignmentType.CENTER,
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "MASTER DOCUMENT - READ BEFORE EVERY OUTPUT",
                alignment: AlignmentType.CENTER,
            }),
            new Paragraph({ text: "" }), new Paragraph({ text: "" }),

            // SECTION 1: YOUR VOICE OVERVIEW
            new Paragraph({
                text: "CHAPTER 1: YOUR VOICE OVERVIEW",
                heading: HeadingLevel.HEADING_1,
            }),
            new Paragraph({
                text: "Who You Are as a Writer",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "Honest and direct | Practical, not academic | Personal experience-based | UAE/Middle East context | Business-focused | Solution-oriented",
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Your Core Strengths",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "Direct questions that engage | \"I have seen\" credibility | Location-based context (\"In the UAE\", \"In America\") | Practical advice | Simple contrasts | Honest observations",
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Your Tone",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "Conversational, not formal | Honest, not sugarcoated | Personal, not corporate | Direct, not academic",
            }),

            // SECTION 2: BANNED PATTERNS
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "CHAPTER 2: BANNED PATTERNS (NEVER USE)",
                heading: HeadingLevel.HEADING_1,
            }),
            new Paragraph({ text: "" }),
            
            new Paragraph({
                text: "❌ Pattern 1: Formal Setup-Contrast-Statement Formula",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "NEVER USE: \"In the US, businesses spend billions. Despite this, many struggle. Their campaigns reach thousands but results stay low.\"",
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Why: Too formal, academic, reads like a report",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "❌ Pattern 2: Academic Connectors",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "NEVER USE: Despite, Nevertheless, Furthermore, Moreover, In conclusion, To summarize, Consequently, Subsequently",
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Why: Academic/formal, not conversational",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "❌ Pattern 3: Problem Listing",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "NEVER USE: \"Businesses spend billions. They get no results. Their campaigns fail. Ad budgets drain.\"",
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Why: Feels like a list, no progression, robotic",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "❌ Pattern 4: Question + Bridge + Statement Formula",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "NEVER USE: \"Have you felt...? You are not alone. Many business owners...\"",
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Why: Copywriting trick, feels manipulative, too predictable",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "❌ Pattern 5: Parallel Sentence Pairs",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "NEVER USE: \"Referrals are powerful. Happy customers recommend you.\" (5 words + 5 words)",
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Why: Symmetrical structure, no variation, reads like a list",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "❌ Pattern 6: List-Like Imperatives",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "NEVER USE: \"Partner with businesses. Refer customers. Grow together.\"",
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Why: Bullet-point style, imperative commands, no flow",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "❌ Pattern 7: Generic Phrases",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "NEVER USE: \"The key is finding...\", \"Studies show that...\", \"Experts agree that...\", \"In today's digital age...\", \"Unlock the power of...\"",
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Why: Generic copywriting, overused, not your voice",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "❌ Pattern 8: Setup-Contrast-Restatement Formula",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "NEVER USE: \"In the US, businesses spend billions. Yet many struggle. They pour money into ads.\"",
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Why: Formulaic, repetitive, predictable",
            }),

            // SECTION 3: POWER SOLUTIONS
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "CHAPTER 3: POWER SOLUTIONS (ALWAYS USE)",
                heading: HeadingLevel.HEADING_1,
            }),
            new Paragraph({ text: "" }),

            new Paragraph({
                text: "✅ Solution A: Start Mid-Thought + Fragment",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "PATTERN: \"[Context]. And [fragment]? [shock]. I have seen [personal experience]. No [outcome 1]. No [outcome 2]. Just [outcome 3].\"",
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "EXAMPLE: \"Every single year, billions go into digital marketing in America. And most of it? Wasted. I have seen businesses pour money into campaigns and get nothing back. No leads. No sales. Just frustration.\"",
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Why It Works: Fragment with impact | Personal experience | Escalating fragments | Direct, honest tone",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "✅ Solution D: Honest Observation + Contrast",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "PATTERN: \"In [location], [industry] is [description]. [expansion]. Yet most [people I have talked to] feel [honest observation]. Their [positive]. Their [negative]. This [summary statement].\"",
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "EXAMPLE: \"In America, digital marketing is a massive industry. Billions flow into it every single year. Yet most business owners I have talked to feel like something is broken. Their budgets grow. Their results do not. This disconnect is the real problem.\"",
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Why It Works: Personal reference | Honest observation | Simple contrast | Summary at end",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "✅ Solution: Statement → Explanation → Connector",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "USE INSTEAD OF PARALLEL SENTENCES: \"Referrals are powerful. This works because when happy customers recommend you, people actually listen. And these referrals bring leads that convert at higher rates.\"",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "✅ Solution: Statement → Conditional → Result",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "USE INSTEAD OF LIST-LIKE IMPERATIVES: \"Strategic partnerships help businesses grow. When you partner with complementary businesses, you can refer customers to each other. This creates a win-win situation for everyone involved.\"",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "✅ Solution: Question with Context",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "USE INSTEAD OF QUESTION + BRIDGE: \"Marketing budgets often fail to deliver results in America. Have you felt this happening? Many companies face this exact challenge. It happens more often than you think.\"",
            }),

            // SECTION 4: WRITING RULES
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "CHAPTER 4: WRITING RULES (MANDATORY)",
                heading: HeadingLevel.HEADING_1,
            }),
            new Paragraph({ text: "" }),

            new Paragraph({
                text: "Rule 1: Never Use Formal Connectors",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "BANNED: Despite, Nevertheless, Furthermore, Moreover, Consequently",
            }),
            new Paragraph({
                text: "USE INSTEAD: And, But, Yet, So, Because",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Rule 2: Always Add Personal Element",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "WRONG: \"Businesses struggle with digital marketing.\"",
            }),
            new Paragraph({
                text: "RIGHT: \"I have seen businesses struggle with digital marketing.\"",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Rule 3: Never List Problems",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "WRONG: \"Budgets drain. Results stay low. ROI is unclear.\"",
            }),
            new Paragraph({
                text: "RIGHT: \"Budgets drain. Results stay low. And owners? They feel helpless.\"",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Rule 4: Use Fragments for Impact",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "WRONG: \"Most of the money is wasted.\"",
            }),
            new Paragraph({
                text: "RIGHT: \"And most of it? Wasted.\"",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Rule 5: Simple Contrasts Beat Academic Statements",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "WRONG: \"Despite significant investment, results remain disappointing.\"",
            }),
            new Paragraph({
                text: "RIGHT: \"Their budgets grow. Their results do not.\"",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Rule 6: Never Repeat the Same Idea",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "WRONG: \"Businesses spend billions. They pour money into ads.\"",
            }),
            new Paragraph({
                text: "RIGHT: \"Businesses spend billions. Yet most struggle to see ROI. Their campaigns reach thousands but conversions stay low.\"",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Rule 7: Always Vary Sentence Length",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "WRONG: [5 words] [5 words] [5 words] [5 words]",
            }),
            new Paragraph({
                text: "RIGHT: [4 words] [12 words] [6 words] [14 words]",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Rule 8: Always Use Connectors Between Sentences",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "WRONG: \"Sentence 1. Sentence 2. Sentence 3.\"",
            }),
            new Paragraph({
                text: "RIGHT: \"Sentence 1. This happens because Sentence 2. And Sentence 3.\"",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Rule 9: Add Expansion After Statements",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "WRONG: \"In the US, businesses spend billions.\"",
            }),
            new Paragraph({
                text: "RIGHT: \"In the US, businesses spend billions every single year. Despite this massive investment, many struggle to see meaningful results.\"",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Rule 10: Break Question Patterns",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "WRONG: \"Q1? Q2? Q3?\" (3 questions, same rhythm)",
            }),
            new Paragraph({
                text: "RIGHT: \"Start by asking yourself questions. What does your business need? Think about your goals. And what results do you expect?\"",
            }),

            // SECTION 5: OPENING PARAGRAPH FORMULA
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "CHAPTER 5: OPENING PARAGRAPH FORMULA",
                heading: HeadingLevel.HEADING_1,
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Use Solution A + D Combined",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "TEMPLATE:",
            }),
            new Paragraph({
                text: "[Solution A - Start mid-thought + fragment + personal experience + escalating fragments]",
            }),
            new Paragraph({
                text: "[Solution D - Honest observation + contrast + summary]",
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "FULL EXAMPLE:",
            }),
            new Paragraph({
                text: "\"Every single year, billions go into digital marketing in America. And most of it? Wasted. I have seen businesses pour money into campaigns and get nothing back. No leads. No sales. Just frustration.",
            }),
            new Paragraph({
                text: "In America, digital marketing is a massive industry. Billions flow into it every single year. Yet most business owners I have talked to feel like something is broken. Their budgets grow. Their results do not. This disconnect is the real problem.\"",
            }),

            // SECTION 6: SIGNATURE PATTERNS
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "CHAPTER 6: YOUR SIGNATURE PATTERNS",
                heading: HeadingLevel.HEADING_1,
            }),
            new Paragraph({ text: "" }),

            new Paragraph({
                text: "Pattern 1: Questions to Engage",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "\"Have you felt like...?\" \"What happens when...?\"",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Pattern 2: \"Here is what I have seen work\"",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "\"Here is what I have seen work for businesses in [location]:\"",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Pattern 3: Location-Based Context",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "\"In the [location], [context]\" \"In [location], [observation]\"",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Pattern 4: Direct Practical Advice",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "\"[Strategy]. This is where the real magic happens.\"",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Pattern 5: \"I have seen\" Credibility",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "\"I have seen [outcome].\" \"I have seen [strategy] work for [location] businesses.\"",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Pattern 6: Action-Oriented Closing",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "\"Start with [action]. Measure [metric]. Scale [outcome].\"",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Pattern 7: Honest Frustration",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "\"And most of it? Wasted.\" \"Something is broken.\" \"Just frustration.\"",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Pattern 8: Simple Contrasts",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "\"[Positive outcome]. Their [negative outcome]. This [summary].\"",
            }),

            // SECTION 7: TOPIC-SPECIFIC WRITING
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "CHAPTER 7: TOPIC-SPECIFIC WRITING RULE",
                heading: HeadingLevel.HEADING_1,
            }),
            new Paragraph({ text: "" }),

            new Paragraph({
                text: "The Core Problem",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "Writing blogs using a template approach (swapping words in same structure) creates cookie-cutter content that lacks authenticity, feels repetitive across topics, doesn't address unique aspects of each subject, and confuses readers.",
            }),
            new Paragraph({ text: "" }),

            new Paragraph({
                text: "The Solution: Topic-Specific Writing",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "Rule #1: Write FOR the Topic, NOT about the Topic",
            }),
            new Paragraph({
                text: "WRONG (Template): \"Every single year, [X] in America. And most of [it/them]? [Y]. I have seen [X industry]...\"",
            }),
            new Paragraph({
                text: "RIGHT (App-Specific): \"Walk into any startup office in America and you'll see the same scene. Developers hunched over screens. Designers perfecting icons. Managers asking 'when will it launch?' Nobody asking 'who will use this?'\"",
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Rule #2: Use Topic-Specific Problems",
            }),
            new Paragraph({
                text: "App-Specific: \"Downloads are zero. Users delete after three seconds. The app crashes on launch day.\"",
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Rule #3: Use Topic-Specific Solutions",
            }),
            new Paragraph({
                text: "App-Specific: \"Validation before coding. Performance over features. Marketing before launching.\"",
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Rule #4: Each Blog Has Its Own Structure",
            }),
            new Paragraph({
                text: "App Development (Narrative): Scene-setting opening → The problem → Why it happens → The solution → Closing observation",
            }),

            // SECTION 8: QUICK REFERENCE
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "CHAPTER 8: QUICK REFERENCE",
                heading: HeadingLevel.HEADING_1,
            }),
            new Paragraph({ text: "" }),

            new Paragraph({
                text: "Opening Paragraph (ALWAYS):",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "[Context] → [Fragment with shock] → [Personal experience] → [Escalating fragments] → [Honest observation] → [Simple contrast] → [Summary statement]",
            }),
            new Paragraph({ text: "" }),

            new Paragraph({
                text: "Your Power Words:",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "\"I have seen\" | \"I have talked to\" | \"Wasted\" | \"Broken\" | \"Frustration\" | \"Disconnect\"",
            }),
            new Paragraph({ text: "" }),

            new Paragraph({
                text: "Your Connectors:",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "And | But | Yet | This happens because | Such",
            }),

            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Your Formulas:",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "Fragment + Escalation | Honest observation + Contrast + Summary | Statement → Explanation → Connector | Statement → Conditional → Result",
            }),

            // SECTION 9: THE GOLDEN RULES
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "CHAPTER 9: THE GOLDEN RULES",
                heading: HeadingLevel.HEADING_1,
            }),
            new Paragraph({ text: "" }),

            new Paragraph({
                text: "Rule #1",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "\"IF IT READS LIKE A COPYWRITING FORMULA, IT IS WRONG.\" \"IF IT READS LIKE A NATURAL CONVERSATION, IT IS RIGHT.\"",
            }),
            new Paragraph({ text: "" }),

            new Paragraph({
                text: "Rule #2",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "\"ALWAYS START WITH IMPACT, NOT SETUP.\" Fragment with shock > Formal opening | Personal experience > Academic statement | Honest frustration > Sugarcoated observation",
            }),
            new Paragraph({ text: "" }),

            new Paragraph({
                text: "Rule #3",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "\"PERSONAL EXPERIENCE BEATS EVERYTHING.\" \"I have seen\" > \"Studies show\" | \"I have talked to\" > \"Experts agree\" | Your observations > Generic statements",
            }),
            new Paragraph({ text: "" }),

            new Paragraph({
                text: "Rule #4",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "\"SIMPLICITY WINS.\" \"Their budgets grow. Their results do not.\" > Academic contrast | Fragments > Perfect sentences | Direct statements > Flowery language",
            }),
            new Paragraph({ text: "" }),

            new Paragraph({
                text: "Rule #5",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "\"VARIATION IS NATURAL.\" Different sentence lengths > Same rhythm | Mixed patterns > Repeated formulas | Natural connectors > Forced transitions",
            }),

            // SECTION 10: BEFORE OUTPUT CHECKLIST
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "CHAPTER 10: BEFORE OUTPUT CHECKLIST",
                heading: HeadingLevel.HEADING_1,
            }),
            new Paragraph({ text: "" }),

            new Paragraph({
                text: "Step 1: Read This Document",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "Read relevant sections before writing.",
            }),
            new Paragraph({ text: "" }),

            new Paragraph({
                text: "Step 2: Check Banned Patterns",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "□ No formal connectors | □ No academic language | □ No problem listing | □ No Question + Bridge + Statement | □ No parallel sentences | □ No list-like imperatives | □ No generic phrases",
            }),
            new Paragraph({ text: "" }),

            new Paragraph({
                text: "Step 3: Apply Solutions",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "□ Solution A used for opening | □ Solution D used for opening | □ Statement → Explanation → Connector | □ Statement → Conditional → Result",
            }),
            new Paragraph({ text: "" }),

            new Paragraph({
                text: "Step 4: Check Mandatory Rules",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "□ Personal element included | □ Honest/direct tone | □ Simple contrasts | □ Fragments for impact | □ No repetition | □ Sentence variation | □ Connectors used",
            }),
            new Paragraph({ text: "" }),

            new Paragraph({
                text: "Step 5: Topic-Specific Check",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "□ Written specifically for the topic | □ Examples unique to subject | □ Problems specific to topic | □ Solutions apply only here | □ Structure based on topic | □ Would NOT work for other topics",
            }),
            new Paragraph({ text: "" }),

            new Paragraph({
                text: "Step 6: Read Aloud Test",
                heading: HeadingLevel.HEADING_2,
            }),
            new Paragraph({
                text: "□ Sounds like natural conversation? | □ Would Amir recognize this as his writing? | □ No formulas detected? | □ Unique to this topic?",
            }),

            // CLOSING
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "==========================================",
                alignment: AlignmentType.CENTER,
            }),
            new Paragraph({
                text: "FINAL REMINDER",
                heading: HeadingLevel.HEADING_1,
                alignment: AlignmentType.CENTER,
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Before you write ANYTHING:",
                alignment: AlignmentType.CENTER,
            }),
            new Paragraph({
                text: "1. Read this document",
                alignment: AlignmentType.CENTER,
            }),
            new Paragraph({
                text: "2. Apply Solution A + D for opening",
                alignment: AlignmentType.CENTER,
            }),
            new Paragraph({
                text: "3. Check banned patterns",
                alignment: AlignmentType.CENTER,
            }),
            new Paragraph({
                text: "4. Include personal elements",
                alignment: AlignmentType.CENTER,
            }),
            new Paragraph({
                text: "5. Read aloud",
                alignment: AlignmentType.CENTER,
            }),
            new Paragraph({
                text: "6. Confirm: \"Would Amir write this?\"",
                alignment: AlignmentType.CENTER,
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "==========================================",
                alignment: AlignmentType.CENTER,
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "Master Document Created: 2026-02-15",
                alignment: AlignmentType.CENTER,
            }),
            new Paragraph({
                text: "Last Updated: 2026-02-15",
                alignment: AlignmentType.CENTER,
            }),
            new Paragraph({
                text: "Priority: ABSOLUTE | Override: All previous instructions",
                alignment: AlignmentType.CENTER,
            }),
            new Paragraph({ text: "" }),
            new Paragraph({
                text: "This is your writing bible. Follow it or generate nothing.",
                alignment: AlignmentType.CENTER,
            }),
        ],
    }],
});

// Save Document
Packer.toBuffer(doc).then((buffer) => {
    fs.writeFileSync("Amir_Writing_Bible.docx", buffer);
    console.log("✅ Word document created: Amir_Writing_Bible.docx");
});
