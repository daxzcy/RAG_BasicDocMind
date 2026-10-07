// 对话 API
window.ChatAPI = {
    // 普通对话
    async chat(request) {
        return apiClient.post('/api/chat', request);
    },

    // 流式对话
    chatStream(request, onMessage, onError, onComplete) {
        const url = `${API_BASE_URL}/api/chat/stream`;
        const eventSource = new EventSource(
            `${url}?${new URLSearchParams({
                query: request.query,
                collection_name: request.collection_name,
                template_name: request.template_name || 'rag_qa',
                temperature: request.temperature || 0.7,
                max_tokens: request.max_tokens || 2000,
                search_top_k: request.search_top_k || 5,
                enable_search: request.enable_search !== false
            })}`
        );

        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'done') {
                    eventSource.close();
                    onComplete?.();
                } else {
                    onMessage(data);
                }
            } catch (e) {
                console.error('Parse error:', e);
            }
        };

        eventSource.onerror = (error) => {
            eventSource.close();
            onError?.(error);
        };

        return eventSource;
    }
};
