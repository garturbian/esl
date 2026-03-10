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
