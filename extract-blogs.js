const mammoth = require('mammoth');
const fs = require('fs');
const path = require('path');

// Settings
const INPUT_DIR = "C:\\Users\\HP\\.openclaw\\workspace\\Amir Blogs";
const OUTPUT_FILE = "C:\\Users\\HP\\.openclaw\\workspace\\memory\\amir-all-blogs-text.json";

// Find all docx files recursively
function findDocxFiles(dir) {
    let results = [];
    const items = fs.readdirSync(dir);
    
    for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory()) {
            results = results.concat(findDocxFiles(fullPath));
        } else if (item.endsWith('.docx')) {
            results.push(fullPath);
        }
    }
    
    return results;
}

// Extract text from a docx file
async function extractText(filePath) {
    try {
        const result = await mammoth.extractRawText({ path: filePath });
        return {
            path: filePath,
            text: result.value,
            messages: result.messages
        };
    } catch (error) {
        return {
            path: filePath,
            text: "",
            error: error.message
        };
    }
}

// Main function
async function main() {
    console.log("🔍 Finding all .docx files...");
    const files = findDocxFiles(INPUT_DIR);
    console.log(`📁 Found ${files.length} .docx files\n`);
    
    console.log("📖 Extracting text from files...");
    const allContent = [];
    
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const progress = Math.round(((i + 1) / files.length) * 100);
        
        process.stdout.write(`\r   Progress: ${progress}% (${i + 1}/${files.length})`);
        
        const content = await extractText(file);
        allContent.push(content);
    }
    
    console.log("\n\n✅ Extraction complete!\n");
    
    // Save to JSON file
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(allContent, null, 2));
    console.log(`💾 Saved extracted text to: ${OUTPUT_FILE}`);
    
    // Summary
    const successful = allContent.filter(f => !f.error).length;
    const failed = allContent.filter(f => f.error).length;
    const totalChars = allContent.reduce((sum, f) => sum + f.text.length, 0);
    
    console.log(`\n📊 Summary:`);
    console.log(`   - Total files: ${files.length}`);
    console.log(`   - Successful: ${successful}`);
    console.log(`   - Failed: ${failed}`);
    console.log(`   - Total characters: ${totalChars.toLocaleString()}`);
    console.log(`   - Estimated words: ${Math.round(totalChars / 5).toLocaleString()}`);
}

main().catch(console.error);
