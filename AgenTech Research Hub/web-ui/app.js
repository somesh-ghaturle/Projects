// AgenTech Research Hub - Web UI JavaScript
class AgenTechUI {
    constructor() {
        // Try different API base URLs
        this.apiBase = 'http://localhost:8000';
        this.init();
    }

    async init() {
        await this.checkSystemHealth();
        this.setupEventListeners();
        this.setupExamples();
    }

    async checkSystemHealth() {
        try {
            // Try multiple endpoints to ensure connection
            const response = await fetch(`${this.apiBase}/health`, {
                method: 'GET',
                mode: 'cors',
                headers: {
                    'Accept': 'application/json',
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.status === 'healthy') {
                    this.updateStatusIndicator('online', 'System Online');
                    return;
                }
            }
            
            // If first attempt fails, try without CORS
            const fallbackResponse = await fetch(`${this.apiBase}/health`);
            if (fallbackResponse.ok) {
                const data = await fallbackResponse.json();
                if (data.status === 'healthy') {
                    this.updateStatusIndicator('online', 'System Online');
                    return;
                }
            }
            
            this.updateStatusIndicator('warning', 'System Issues');
        } catch (error) {
            console.warn('Primary API check failed, trying fallback...', error);
            
            // Try direct localhost connection
            try {
                const directResponse = await fetch('http://127.0.0.1:8000/health');
                if (directResponse.ok) {
                    const data = await directResponse.json();
                    this.apiBase = 'http://127.0.0.1:8000';
                    this.updateStatusIndicator('online', 'System Online');
                    return;
                }
            } catch (fallbackError) {
                console.error('All health checks failed:', fallbackError);
            }
            
            this.updateStatusIndicator('offline', 'API Server Offline');
        }
    }

    updateStatusIndicator(status, text) {
        const indicator = document.getElementById('status-indicator');
        const dot = indicator.querySelector('div');
        const span = indicator.querySelector('span');
        
        dot.className = 'w-3 h-3 rounded-full animate-pulse';
        
        switch (status) {
            case 'online':
                dot.classList.add('bg-green-400');
                break;
            case 'warning':
                dot.classList.add('bg-yellow-400');
                break;
            case 'offline':
                dot.classList.add('bg-red-400');
                break;
        }
        
        span.textContent = text;
    }

    setupEventListeners() {
        const form = document.getElementById('research-form');
        form.addEventListener('submit', (e) => this.handleResearch(e));
        
        // Auto-resize textarea if we had one
        const query = document.getElementById('research-query');
        query.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                form.dispatchEvent(new Event('submit'));
            }
        });
    }

    setupExamples() {
        // Examples are handled by onclick attributes in HTML
    }

    setQuery(query) {
        document.getElementById('research-query').value = query;
        document.getElementById('research-query').focus();
    }

    async handleResearch(event) {
        event.preventDefault();
        
        const query = document.getElementById('research-query').value.trim();
        const maxSources = parseInt(document.getElementById('max-sources').value);
        const researchType = document.getElementById('research-type').value;
        
        if (!query) {
            this.showNotification('Please enter a research query', 'warning');
            return;
        }

        this.showLoading();
        
        try {
            const response = await fetch(`${this.apiBase}/research`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    max_sources: maxSources,
                    research_type: researchType
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.displayResults(data);
            
        } catch (error) {
            console.error('Research failed:', error);
            this.showError('Research request failed. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    showLoading() {
        document.getElementById('loading-section').classList.remove('hidden');
        document.getElementById('results-section').classList.add('hidden');
        
        const loadingTexts = [
            'Initializing AI agents...',
            'Searching web sources...',
            'Analyzing academic papers...',
            'Processing real-time data...',
            'Generating insights...',
            'Validating information...',
            'Compiling results...'
        ];
        
        let index = 0;
        let progress = 0;
        
        const interval = setInterval(() => {
            document.getElementById('loading-text').textContent = loadingTexts[index];
            progress += Math.random() * 15 + 5; // Random progress increment
            document.getElementById('progress-bar').style.width = Math.min(progress, 90) + '%';
            
            index = (index + 1) % loadingTexts.length;
        }, 1000);
        
        // Store interval to clear it later
        this.loadingInterval = interval;
    }

    hideLoading() {
        document.getElementById('loading-section').classList.add('hidden');
        document.getElementById('progress-bar').style.width = '100%';
        
        if (this.loadingInterval) {
            clearInterval(this.loadingInterval);
            this.loadingInterval = null;
        }
    }

    displayResults(data) {
        document.getElementById('results-section').classList.remove('hidden');
        
        // Update summary
        this.updateSummary(data);
        
        // Update sources
        this.updateSources(data.sources || []);
        
        // Scroll to results
        document.getElementById('results-section').scrollIntoView({
            behavior: 'smooth'
        });
    }

    updateSummary(data) {
        const summaryContent = document.getElementById('summary-content');
        const sourcesCount = document.getElementById('sources-count');
        const qualityScore = document.getElementById('quality-score');
        
        // Create summary content
        let summaryHtml = `
            <div class="bg-gradient-to-r from-purple-50 to-blue-50 p-6 rounded-lg mb-4">
                <h4 class="text-lg font-semibold text-gray-800 mb-2">Query: "${data.query}"</h4>
                <p class="text-gray-700">${data.summary || 'Research completed successfully. Analysis of sources revealed comprehensive insights on the requested topic.'}</p>
            </div>
        `;
        
        if (data.success) {
            summaryHtml += `
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                    <div class="bg-green-50 p-4 rounded-lg">
                        <i class="fas fa-check-circle text-green-600 mr-2"></i>
                        <span class="font-semibold text-green-800">Research Successful</span>
                        <p class="text-sm text-green-700 mt-1">All agents completed their tasks successfully</p>
                    </div>
                    <div class="bg-blue-50 p-4 rounded-lg">
                        <i class="fas fa-brain text-blue-600 mr-2"></i>
                        <span class="font-semibold text-blue-800">AI Analysis Complete</span>
                        <p class="text-sm text-blue-700 mt-1">Multi-agent workflow processed your query</p>
                    </div>
                </div>
            `;
        }
        
        summaryContent.innerHTML = summaryHtml;
        sourcesCount.textContent = `Sources analyzed: ${data.sources_found || 0}`;
        qualityScore.textContent = `Quality score: ${Math.round((data.quality_score || 0) * 100)}%`;
    }

    updateSources(sources) {
        const sourcesGrid = document.getElementById('sources-grid');
        
        if (!sources || sources.length === 0) {
            sourcesGrid.innerHTML = `
                <div class="col-span-full text-center py-8 text-gray-500">
                    <i class="fas fa-search text-4xl mb-4"></i>
                    <p>No sources found for this query.</p>
                </div>
            `;
            return;
        }
        
        sourcesGrid.innerHTML = sources.map(source => `
            <div class="bg-white rounded-lg shadow-lg p-6 card-hover result-item">
                <div class="flex items-start justify-between mb-3">
                    <div class="flex items-center space-x-2">
                        <i class="fas fa-${this.getSourceIcon(source.source_type)} text-lg text-purple-600"></i>
                        <span class="text-sm font-medium text-purple-600 uppercase">${source.source_type}</span>
                    </div>
                    <div class="flex items-center space-x-1">
                        ${this.renderStars(source.relevance_score)}
                    </div>
                </div>
                
                <h4 class="font-bold text-gray-800 mb-2 line-clamp-2">${source.title}</h4>
                <p class="text-gray-600 text-sm mb-3 line-clamp-3">${source.snippet}</p>
                
                <div class="flex items-center justify-between">
                    <a href="${source.url}" target="_blank" rel="noopener noreferrer" 
                       class="text-blue-600 hover:text-blue-800 text-sm font-medium transition">
                        <i class="fas fa-external-link-alt mr-1"></i>
                        Read Source
                    </a>
                    <span class="text-xs text-gray-500">
                        <i class="fas fa-clock mr-1"></i>
                        ${source.last_updated || 'Recent'}
                    </span>
                </div>
            </div>
        `).join('');
    }

    getSourceIcon(sourceType) {
        const icons = {
            'TECH_NEWS': 'newspaper',
            'ACADEMIC_TECH': 'graduation-cap',
            'TECH_AUTHORITY': 'certificate',
            'ENCYCLOPEDIA': 'book',
            'RESEARCH_PAPER': 'file-alt',
            'BLOG': 'blog',
            'FORUM': 'comments',
            'default': 'link'
        };
        return icons[sourceType] || icons.default;
    }

    renderStars(score) {
        const stars = Math.round(score * 5);
        let html = '';
        for (let i = 0; i < 5; i++) {
            if (i < stars) {
                html += '<i class="fas fa-star text-yellow-400 text-xs"></i>';
            } else {
                html += '<i class="far fa-star text-gray-300 text-xs"></i>';
            }
        }
        return html;
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 max-w-md ${this.getNotificationClasses(type)}`;
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-${this.getNotificationIcon(type)} mr-3"></i>
                <span class="flex-1">${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-3">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    getNotificationClasses(type) {
        const classes = {
            'info': 'bg-blue-500 text-white',
            'success': 'bg-green-500 text-white',
            'warning': 'bg-yellow-500 text-white',
            'error': 'bg-red-500 text-white'
        };
        return classes[type] || classes.info;
    }

    getNotificationIcon(type) {
        const icons = {
            'info': 'info-circle',
            'success': 'check-circle',
            'warning': 'exclamation-triangle',
            'error': 'exclamation-circle'
        };
        return icons[type] || icons.info;
    }
}

// Global function for example buttons
function setQuery(query) {
    window.agenTechUI.setQuery(query);
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    window.agenTechUI = new AgenTechUI();
});

// Add some utility CSS classes
const style = document.createElement('style');
style.textContent = `
    .line-clamp-2 {
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    }
    .line-clamp-3 {
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
    }
`;
document.head.appendChild(style);
