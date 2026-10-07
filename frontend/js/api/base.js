// API 基础配置
window.API_BASE_URL = 'http://localhost:8000';

// 创建 Axios 实例
window.apiClient = axios.create({
    baseURL: window.API_BASE_URL,
    timeout: 60000,
    headers: {
        'Content-Type': 'application/json'
    }
});

// 请求拦截器
window.apiClient.interceptors.request.use(
    config => {
        const apiKey = localStorage.getItem('rag_api_key');
        if (apiKey) {
            config.headers['X-API-Key'] = apiKey;
        }
        return config;
    },
    error => Promise.reject(error)
);

// 响应拦截器
window.apiClient.interceptors.response.use(
    response => response.data,
    error => {
        console.error('API Error:', error);
        const message = error.response?.data?.detail || error.message || '请求失败';
        ElementPlus.ElMessage.error(message);
        return Promise.reject(error);
    }
);
