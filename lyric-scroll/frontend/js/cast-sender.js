/**
 * Lyric Scroll Cast Sender
 * Handles Google Cast integration for casting lyrics to Chromecast devices
 */
class LyricScrollCastSender {
  constructor(appId) {
    this.appId = appId;
    this.namespace = 'urn:x-cast:com.lyricscroll.cast';
    this.session = null;
    this.isReady = false;
    this.onStatusChange = null;  // Callback for UI updates

    this._initializeCast();
  }

  _initializeCast() {
    // Wait for Cast API to be available
    window['__onGCastApiAvailable'] = (isAvailable) => {
      if (isAvailable) {
        this._setupCast();
      } else {
        console.error('Cast API not available');
        this._updateStatus('error', 'Cast not available');
      }
    };

    // If Cast API is already loaded, set it up
    if (typeof cast !== 'undefined' && cast.framework) {
      this._setupCast();
    }
  }

  _setupCast() {
    try {
      cast.framework.CastContext.getInstance().setOptions({
        receiverApplicationId: this.appId,
        autoJoinPolicy: chrome.cast.AutoJoinPolicy.ORIGIN_SCOPED
      });

      const context = cast.framework.CastContext.getInstance();

      context.addEventListener(
        cast.framework.CastContextEventType.SESSION_STATE_CHANGED,
        (event) => this._handleSessionStateChange(event)
      );

      context.addEventListener(
        cast.framework.CastContextEventType.CAST_STATE_CHANGED,
        (event) => this._handleCastStateChange(event)
      );

      this.isReady = true;
      this._updateStatus('ready', 'Cast ready');
      console.log('Cast SDK initialized with app ID:', this.appId);
    } catch (err) {
      console.error('Failed to initialize Cast:', err);
      this._updateStatus('error', 'Cast init failed');
    }
  }

  _handleSessionStateChange(event) {
    const state = event.sessionState;
    console.log('Cast session state:', state);

    if (state === cast.framework.SessionState.SESSION_STARTED ||
        state === cast.framework.SessionState.SESSION_RESUMED) {
      this.session = cast.framework.CastContext.getInstance().getCurrentSession();
      const deviceName = this.session.getCastDevice().friendlyName;
      this._updateStatus('connected', `Connected to ${deviceName}`);
    } else if (state === cast.framework.SessionState.SESSION_ENDED) {
      this.session = null;
      this._updateStatus('disconnected', 'Disconnected');
    }
  }

  _handleCastStateChange(event) {
    const state = event.castState;
    console.log('Cast state:', state);

    if (state === cast.framework.CastState.NO_DEVICES_AVAILABLE) {
      this._updateStatus('no_devices', 'No Cast devices found');
    } else if (state === cast.framework.CastState.NOT_CONNECTED) {
      if (this.isReady && !this.session) {
        this._updateStatus('ready', 'Cast ready');
      }
    }
  }

  _updateStatus(state, message) {
    if (this.onStatusChange) {
      this.onStatusChange(state, message);
    }
    console.log(`Cast status: ${state} - ${message}`);
  }

  // Public Methods

  /**
   * Start a cast session - opens Chrome's cast dialog
   */
  async startCasting() {
    if (!this.isReady) {
      throw new Error('Cast not ready');
    }

    try {
      await cast.framework.CastContext.getInstance().requestSession();
    } catch (err) {
      if (err === 'cancel') {
        console.log('User cancelled cast dialog');
      } else {
        console.error('Failed to start cast session:', err);
        throw err;
      }
    }
  }

  /**
   * Stop the current cast session
   */
  stopCasting() {
    if (this.session) {
      this.session.endSession(true);
      this.session = null;
    }
  }

  /**
   * Check if currently casting
   */
  isConnected() {
    return this.session !== null;
  }

  /**
   * Get the connected device name
   */
  getDeviceName() {
    if (this.session) {
      return this.session.getCastDevice().friendlyName;
    }
    return null;
  }

  /**
   * Cast a URL to the receiver
   * @param {string} url - The URL to display on the Chromecast
   */
  async castUrl(url) {
    if (!this.session) {
      throw new Error('Not connected to Chromecast');
    }

    await this.session.sendMessage(this.namespace, { loadUrl: url });
    console.log(`Cast URL sent: ${url}`);
  }

  /**
   * Clear content and show standby screen on receiver
   */
  async clearContent() {
    if (!this.session) {
      throw new Error('Not connected to Chromecast');
    }

    await this.session.sendMessage(this.namespace, { clearContent: true });
  }

  /**
   * Reload the current content on receiver
   */
  async reloadContent() {
    if (!this.session) {
      throw new Error('Not connected to Chromecast');
    }

    await this.session.sendMessage(this.namespace, { reload: true });
  }

  /**
   * Send a status message to display on receiver standby screen
   * @param {string} message - Status message to display
   */
  async sendStatusMessage(message) {
    if (!this.session) {
      throw new Error('Not connected to Chromecast');
    }

    await this.session.sendMessage(this.namespace, { statusMessage: message });
  }

  /**
   * Send a custom message to the receiver
   * @param {object} data - Any JSON-serializable data
   */
  async sendMessage(data) {
    if (!this.session) {
      throw new Error('Not connected to Chromecast');
    }

    await this.session.sendMessage(this.namespace, data);
  }
}

// Export for use in app.js
window.LyricScrollCastSender = LyricScrollCastSender;
