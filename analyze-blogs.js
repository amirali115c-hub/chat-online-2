const fs = require('fs');
const data = JSON.parse(fs.readFileSync('C:\\Users\\HP\\.openclaw\\workspace\\memory\\amir-all-blogs-text.json', 'utf8'));

// Combine all valid texts
let allText = data.filter(f => f.text && f.text.length > 100).map(f => f.text).join(' ');

console.log('🔍 ANALYZING Amir\'s WRITING STYLE...\n');

// Basic metrics
const words = allText.split(/\s+/);
const sentences = allText.split(/[.!?]+/).filter(s => s.trim().length > 10);
const paragraphs = allText.split(/\n\n+/).filter(p => p.trim().length > 50);

console.log(`📊 BASIC METRICS:`);
console.log(`   • Total words: ${words.length.toLocaleString()}`);
console.log(`   • Total sentences: ${sentences.length.toLocaleString()}`);
console.log(`   • Avg sentence length: ${(words.length / sentences.length).toFixed(1)} words`);
console.log(`   • Avg paragraph length: ${(sentences.length / paragraphs.length).toFixed(1)} sentences\n`);

// 1. Sentence starters analysis
console.log(`📝 SENTENCE STARTERS:`);
const sentenceStarters = {};
sentences.forEach(s => {
    const firstWord = s.trim().split(/\s+/)[0].toLowerCase().replace(/[^a-z]/g, '');
    if (firstWord.length > 2) {
        sentenceStarters[firstWord] = (sentenceStarters[firstWord] || 0) + 1;
    }
});
const sortedStarters = Object.entries(sentenceStarters)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 20);
sortedStarters.forEach(([word, count]) => {
    const pct = ((count / sentences.length) * 100).toFixed(1);
    console.log(`   ${word}: ${count} (${pct}%)`);
});

// 2. Common phrases (3-4 words)
console.log(`\n🔤 COMMON PHRASES (3-4 words):`);
const phrases = {};
for (let i = 0; i < words.length - 3; i++) {
    const phrase3 = words.slice(i, i + 3).join(' ').toLowerCase().replace(/[^a-z0-9 ]/g, '');
    const phrase4 = words.slice(i, i + 4).join(' ').toLowerCase().replace(/[^a-z0-9 ]/g, '');
    phrases[phrase3] = (phrases[phrase3] || 0) + 1;
    phrases[phrase4] = (phrases[phrase4] || 0) + 1;
}
const sortedPhrases = Object.entries(phrases)
    .filter(([phrase, count]) => count > 50 && phrase.split(' ').length >= 3)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 30);
sortedPhrases.forEach(([phrase, count]) => {
    console.log(`   "${phrase}": ${count}`);
});

// 3. Transition words
console.log(`\n🔄 TRANSITION WORDS:`);
const transitions = [
    'however', 'therefore', 'furthermore', 'moreover', 'additionally',
    'consequently', 'meanwhile', 'subsequently', 'additionally', 'alternatively',
    'in addition', 'on the other hand', 'for example', 'for instance',
    'this includes', 'this is', 'it is important', 'these are'
];
const transitionCounts = {};
transitions.forEach(t => {
    const regex = new RegExp(`\\b${t}\\b`, 'gi');
    const matches = allText.match(regex) || [];
    transitionCounts[t] = matches.length;
});
Object.entries(transitionCounts)
    .sort((a, b) => b[1] - a[1])
    .forEach(([word, count]) => {
        if (count > 10) console.log(`   ${word}: ${count}`);
    });

// 4. Vocabulary complexity
console.log(`\n📚 VOCABULARY ANALYSIS:`);
const uniqueWords = new Set(words.map(w => w.toLowerCase().replace(/[^a-z]/g, '')));
console.log(`   • Unique words: ${uniqueWords.size.toLocaleString()}`);
console.log(`   • Lexical diversity: ${(uniqueWords.size / words.length * 100).toFixed(1)}%`);

// 5. Passive vs Active voice indicators
console.log(`\n🎯 VOICE ANALYSIS:`);
const passiveIndicators = ['is', 'are', 'was', 'were', 'been', 'being', 'be'];
const activeIndicators = ['will', 'can', 'should', 'must', 'need', 'want', 'choose'];
const passiveCount = passiveIndicators.reduce((sum, w) => {
    const regex = new RegExp(`\\b${w}\\b`, 'gi');
    return sum + (allText.match(regex) || []).length;
}, 0);
const activeCount = activeIndicators.reduce((sum, w) => {
    const regex = new RegExp(`\\b${w}\\b`, 'gi');
    return sum + (allText.match(regex) || []).length;
}, 0);
console.log(`   • Passive markers: ${passiveCount}`);
console.log(`   • Active markers: ${activeCount}`);

// 6. Content themes/niches
console.log(`\n🎯 CONTENT THEMES:`);
const themes = {
    'SEO/Digital Marketing': ['seo', 'search engine', 'keyword', 'ranking', 'traffic', 'optimization'],
    'Real Estate': ['property', 'real estate', 'home', 'apartment', 'buyer', 'seller', 'listing'],
    'Jewelry': ['jewelry', 'diamond', 'gold', 'ring', 'necklace', 'bracelet', 'gemstone'],
    'Construction': ['construction', 'building', 'contractor', 'project', 'infrastructure'],
    'Automotive': ['car', 'vehicle', 'auto', 'auction', 'automotive', 'driving'],
    'Business': ['business', 'company', 'enterprise', 'organization', 'growth', 'strategy']
};
Object.entries(themes).forEach(([theme, keywords]) => {
    const count = keywords.reduce((sum, kw) => {
        const regex = new RegExp(`\\b${kw}\\b`, 'gi');
        return sum + (allText.match(regex) || []).length;
    }, 0);
    if (count > 50) console.log(`   ${theme}: ${count} mentions`);
});

// 7. Tone indicators
console.log(`\n🎨 TONE ANALYSIS:`);
const professionalWords = ['professional', 'quality', 'excellent', 'premium', 'expert', 'authority'];
const conversationalWords = ['you', 'your', 'we', 'our', 'feel', 'love', 'amazing'];
const formalWords = ['therefore', 'furthermore', 'consequently', 'moreover', 'thus'];

const profCount = professionalWords.reduce((sum, w) => {
    const regex = new RegExp(`\\b${w}\\b`, 'gi');
    return sum + (allText.match(regex) || []).length;
}, 0);
const convCount = conversationalWords.reduce((sum, w) => {
    const regex = new RegExp(`\\b${w}\\b`, 'gi');
    return sum + (allText.match(regex) || []).length;
}, 0);
console.log(`   • Professional markers: ${profCount}`);
console.log(`   • Conversational markers (you/your): ${convCount}`);
console.log(`   • You-to-total ratio: ${((convCount / sentences.length) * 100).toFixed(1)}%`);

console.log(`\n✅ ANALYSIS COMPLETE!`);
