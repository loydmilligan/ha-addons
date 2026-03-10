/**
 * Lyric Scroll - Frontend Application
 */

class LyricScroll {
    constructor() {
        this.ws = null;
        this.lyrics = [];
        this.currentLineIndex = -1;
        this.state = 'idle'; // idle, playing, paused

        // DOM elements
        this.lyricsContent = document.getElementById('lyrics-content');
        this.statusMessage = document.getElementById('status-message');
        this.statusText = document.getElementById('status-text');
        this.trackTitle = document.getElementById('track-title');
        this.trackArtist = document.getElementById('track-artist');

        this.init();
    }

    init() {
        this.connect();
        this.setupEventListeners();
    }

    connect() {
        // Determine WebSocket URL based on current location
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        console.log('Connecting to WebSocket:', wsUrl);
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
        };

        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected, reconnecting in 3s...');
            setTimeout(() => this.connect(), 3000);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    handleMessage(message) {
        console.log('Received message:', message);

        switch (message.type) {
            case 'lyrics':
                this.handleLyrics(message.data);
                break;
            case 'position':
                this.handlePosition(message.data);
                break;
            case 'no_lyrics':
                this.handleNoLyrics(message.data);
                break;
            case 'idle':
                this.handleIdle();
                break;
        }
    }

    handleLyrics(data) {
        this.lyrics = data.lyrics || [];
        this.trackTitle.textContent = data.track?.title || '-';
        this.trackArtist.textContent = data.track?.artist || '-';

        this.statusMessage.classList.add('hidden');
        this.renderLyrics();
    }

    handlePosition(data) {
        const positionMs = data.position_ms;
        this.state = data.state;

        if (this.state === 'playing' && this.lyrics.length > 0) {
            this.updateCurrentLine(positionMs);
        }
    }

    handleNoLyrics(data) {
        this.lyrics = [];
        this.lyricsContent.innerHTML = '';
        this.statusMessage.classList.remove('hidden');
        this.statusText.textContent = 'No lyrics available';

        if (data.track) {
            this.trackTitle.textContent = data.track.title || '-';
            this.trackArtist.textContent = data.track.artist || '-';
        }
    }

    handleIdle() {
        this.state = 'idle';
        this.lyrics = [];
        this.currentLineIndex = -1;
        this.lyricsContent.innerHTML = '';
        this.statusMessage.classList.remove('hidden');
        this.statusText.textContent = 'Waiting for music...';
        this.trackTitle.textContent = '-';
        this.trackArtist.textContent = '-';
    }

    renderLyrics() {
        this.lyricsContent.innerHTML = this.lyrics.map((line, index) =>
            `<div class="lyric-line" data-index="${index}">${this.escapeHtml(line.text)}</div>`
        ).join('');
    }

    updateCurrentLine(positionMs) {
        // Find the current line based on position
        let newIndex = -1;
        for (let i = this.lyrics.length - 1; i >= 0; i--) {
            if (this.lyrics[i].timestamp_ms <= positionMs) {
                newIndex = i;
                break;
            }
        }

        if (newIndex !== this.currentLineIndex) {
            this.currentLineIndex = newIndex;
            this.highlightCurrentLine();
        }
    }

    highlightCurrentLine() {
        const lines = this.lyricsContent.querySelectorAll('.lyric-line');

        lines.forEach((line, index) => {
            line.classList.remove('current', 'past');

            if (index === this.currentLineIndex) {
                line.classList.add('current');
                // Scroll current line into view
                line.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else if (index < this.currentLineIndex) {
                line.classList.add('past');
            }
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    setupEventListeners() {
        // Settings button (placeholder for now)
        document.getElementById('settings-btn').addEventListener('click', () => {
            console.log('Settings clicked - not yet implemented');
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.lyricScroll = new LyricScroll();
});
