module.exports = function(eleventyConfig) {
    // Add a custom shortcode for the current year
    eleventyConfig.addShortcode("year", () => `${new Date().getFullYear()}`);

    // Configuration
    return {
        dir: {
            input: "src",
            output: "docs",
            includes: "_includes"
        },
        templateFormats: ["md", "njk", "html"],
        markdownTemplateEngine: "njk",
        htmlTemplateEngine: "njk"
    };
};
