class VoiceChat {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.isDuplex = false;
        this.silenceTimeout = null;
        this.audioContext = null;
        this.silenceThreshold = 0.01; // Adjust as needed
        this.silenceDuration = 2000; // 2 seconds in ms
        this.stream = null;
        this.analyser = null;
        this.source = null;
        this.modal = document.querySelector('.voice-chat-modal');
        this.content = document.querySelector('.voice-chat-content');
        this.status = document.querySelector('.voice-chat-status');
        this.button = document.querySelector('.voice-chat-button');
        this.closeButton = document.querySelector('.close-voice-chat'); // Get the close button
        
        // Check if browser supports required APIs
        this.checkBrowserSupport();
        this.setupEventListeners();
        // Hide only the voice chat modal (dialog) by default
        this.modal.style.display = 'none';
    }

    checkBrowserSupport() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.button.disabled = true;
            this.button.title = 'Voice chat not supported in this browser';
            this.button.style.opacity = '0.5';
            this.addMessage('Voice chat is not supported in your browser. Please use Chrome, Firefox, or Edge.', 'assistant');
            console.error('MediaDevices API not supported');
        }
    }

    setupEventListeners() {
        this.button.addEventListener('click', () => this.toggleRecording());
        this.closeButton.addEventListener('click', () => this.hideModal()); // Add event listener for close button
    }

    async toggleRecording() {
        if (!this.isRecording) {
            this.isDuplex = true;
            await this.startRecording();
        } else {
            this.isDuplex = false;
            await this.stopRecording();
        }
    }

    async startRecording() {
        try {
            // Check if we're on HTTPS or localhost
            if (window.location.protocol !== 'https:' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
                throw new Error('Voice chat requires HTTPS or localhost');
            }

            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };
            
            this.mediaRecorder.onstop = () => {
                this.processAudio();
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            this.button.classList.add('recording');
            this.button.style.zIndex = '10001';
            this.status.textContent = 'Recording...';
            this.showModal();
            // Add shimmer effect to Flubber
            document.querySelector('.flubber-img-with-aura').classList.add('flubber-aura-shimmer');
            this.startSilenceDetection();
        } catch (error) {
            console.error('Error accessing microphone:', error);
            this.status.textContent = 'Error accessing microphone';
            
            // Show specific error message based on the error
            let errorMessage = 'Sorry, there was an error accessing your microphone. ';
            if (error.name === 'NotAllowedError') {
                errorMessage += 'Please allow microphone access in your browser settings.';
            } else if (error.name === 'NotFoundError') {
                errorMessage += 'No microphone found. Please connect a microphone and try again.';
            } else if (error.message.includes('HTTPS')) {
                errorMessage += 'Voice chat requires a secure HTTPS connection or localhost.';
            } else {
                errorMessage += 'Please try using a different browser (Chrome, Firefox, or Edge).';
            }
            
            this.addMessage(errorMessage, 'assistant');
        }
    }

    async stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.button.classList.remove('recording');
            this.button.style.zIndex = '10001';
            this.status.textContent = 'Stopped';
            // Remove shimmer effect from Flubber
            document.querySelector('.flubber-img-with-aura').classList.remove('flubber-aura-shimmer');
            
            // Stop all audio tracks
            if (this.stream) {
                this.stream.getTracks().forEach(track => track.stop());
            }
            this.stopSilenceDetection();
        }
    }

    startSilenceDetection() {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        this.source = this.audioContext.createMediaStreamSource(this.stream);
        this.analyser = this.audioContext.createAnalyser();
        this.source.connect(this.analyser);
        this.analyser.fftSize = 2048;
        const data = new Uint8Array(this.analyser.fftSize);

        let silenceStart = null;
        const checkSilence = () => {
            this.analyser.getByteTimeDomainData(data);
            let sum = 0;
            for (let i = 0; i < data.length; i++) {
                const val = (data[i] - 128) / 128;
                sum += val * val;
            }
            const rms = Math.sqrt(sum / data.length);

            if (rms < this.silenceThreshold) {
                if (!silenceStart) silenceStart = Date.now();
                if (Date.now() - silenceStart > this.silenceDuration) {
                    this.stopRecording();
                    return;
                }
            } else {
                silenceStart = null;
            }
            if (this.isRecording) {
                this.silenceTimeout = setTimeout(checkSilence, 100);
            }
        };
        checkSilence();
    }

    stopSilenceDetection() {
        if (this.silenceTimeout) clearTimeout(this.silenceTimeout);
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
        this.analyser = null;
        this.source = null;
    }

    async processAudio() {
        try {
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
            const formData = new FormData();
            formData.append('audio', audioBlob);

            const response = await fetch('/api/voice-chat', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            // Add user message
            this.addMessage(data.transcription, 'user');
            
            // Add assistant response
            this.addMessage(data.response, 'assistant');
            
            await this.playAssistantAudio(data.response);

            // If still in duplex mode, start recording again
            if (this.isDuplex) {
                await this.startRecording();
            } else {
                this.status.textContent = 'Ready';
                // Do NOT hide the modal here; keep it open until user closes it
            }
        } catch (error) {
            console.error('Error processing audio:', error);
            this.status.textContent = 'Error processing audio';
            this.addMessage('Sorry, there was an error processing your request.', 'assistant');
        }
    }

    playAssistantAudio(text) {
        return new Promise((resolve) => {
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'en-US';
                utterance.onend = resolve;
                window.speechSynthesis.speak(utterance);
            } else {
                resolve();
            }
        });
    }

    addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `voice-chat-message ${type}`;
        messageDiv.textContent = text;
        this.content.appendChild(messageDiv);
        // Auto-scroll to the latest message
        this.content.scrollTop = this.content.scrollHeight;
    }

    showModal() {
        this.modal.classList.add('active');
    }

    hideModal() {
        this.modal.classList.remove('active');
        // If we close the modal while recording, stop recording.
        if (this.isRecording) {
            this.stopRecording();
        }
        this.isDuplex = false; // Ensure duplex mode is off when closed manually
        // Clear chat content on close
        this.content.innerHTML = '';
        this.status.textContent = 'Ready';
    }

    hideKlausPermanently() {
        // Hide the modal and the button, and prevent them from being shown again
        this.hideModal();
        this.button.style.display = 'none';
        this.modal.style.display = 'none';
        // Optionally hide Flubber image too:
        const flubber = document.querySelector('.flubber-img-with-aura');
        if (flubber) flubber.style.display = 'none';
    }
}

// Initialize voice chat when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.voiceChat = new VoiceChat();
    // Expose a global function to hide Klaus dialog
    window.hideKlausDialog = function() {
        window.voiceChat.hideKlausPermanently();
    };
}); 