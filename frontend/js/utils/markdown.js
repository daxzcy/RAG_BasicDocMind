// Markdown 渲染工具
window.MarkdownUtils = {
    // 配置 marked
    init() {
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                highlight: function(code, lang) {
                    if (lang && hljs.getLanguage(lang)) {
                        try {
                            return hljs.highlight(code, { language: lang }).value;
                        } catch (e) {}
                    }
                    return hljs.highlightAuto(code).value;
                },
                breaks: true,
                gfm: true
            });
        }
    },

    // 渲染 Markdown
    render(markdown) {
        if (typeof marked !== 'undefined') {
            return marked.parse(markdown);
        }
        return markdown;
    }
};

// 初始化
MarkdownUtils.init();
