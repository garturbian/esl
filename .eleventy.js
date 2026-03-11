module.exports = function (eleventyConfig) {
    // Explicitly ignore Obsidian configuration
    eleventyConfig.ignores.add("src/lessons/.obsidian/");

    // Add a custom shortcode for the current year
    eleventyConfig.addShortcode("year", () => `${new Date().getFullYear()}`);

    // Add audio player shortcode
    eleventyConfig.addShortcode("audioPlayer", function (src) {
        // Use the built-in url filter if possible, otherwise just use the string
        // In .eleventy.js, this.page isn't available in standard addShortcode like this
        // so we just return the HTML and let it be processed or assume absolute path
        const url = eleventyConfig.getFilter("url");
        const resolvedSrc = url(src);
        return `<div class="audio-container">
    <audio controls>
        <source src="${resolvedSrc}" type="audio/mpeg">
        Your browser does not support the audio element.
    </audio>
</div>`;
    });

    // Pass through .nojekyll, CSS, audio, and images
    eleventyConfig.addPassthroughCopy("src/.nojekyll");
    eleventyConfig.addPassthroughCopy("src/css");
    eleventyConfig.addPassthroughCopy("src/audio");
    eleventyConfig.addPassthroughCopy("src/images");

    // Vocabulary Transform
    eleventyConfig.addTransform("vocab-transform", async function (content) {
        if (this.outputPath && this.outputPath.endsWith(".html") && this.inputPath.includes("/lessons/")) {
            const cheerio = require("cheerio");
            const fs = require("fs");
            const path = require("path");

            const $ = cheerio.load(content);
            const fileName = path.basename(this.inputPath, ".md").toLowerCase().replace(/\s+/g, '-').replace(/['’]/g, '');
            const vocabPath = path.join(__dirname, "src/_data/vocab", `${fileName}.json`);

            if (fs.existsSync(vocabPath)) {
                const vocabData = JSON.parse(fs.readFileSync(vocabPath, "utf-8"));

                // Process each vocab item
                const items = vocabData.vocab_items || vocabData.items;
                    $("p, li, h1, h2, h3").each(function () {
                        let html = $(this).html();
                        let text = $(this).text().toLowerCase().trim();
                        
                        // Process each item
                        items.forEach(item => {
                            const display = item.display;
                            const escapedDisplay = display.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                            const regex = new RegExp(`(?<!<[^>]*)\\b(${escapedDisplay})\\b(?![^<]*>)`, 'gi');
                            
                            // Context match: check if item's sentence (partially) appears in this element
                            const itemSentence = item.sentence.toLowerCase().trim();
                            const isContextMatch = text.includes(itemSentence.substring(0, 50)) || itemSentence.includes(text.substring(0, 40));

                            if (isContextMatch && !html.includes(`data-explanation="${item.explanation}"`)) {
                                html = html.replace(regex, `<span class="vocab-term" data-translation="${item.translation}" data-explanation="${item.explanation}">$1</span>`);
                            }
                        });
                        
                        $(this).html(html);
                    });
            }
            return $.html();
        }
        return content;
    });

    // Configuration
    return {
        dir: {
            input: "src",
            output: "_site",
            includes: "_includes"
        },
        templateFormats: ["md", "njk", "html"],
        markdownTemplateEngine: "njk",
        htmlTemplateEngine: "njk",
        pathPrefix: "/esl/"
    };
};
