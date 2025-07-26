// Security utilities for device fingerprinting and location tracking
// These are used for internal security and anti-abuse measures only

interface DeviceFingerprint {
  deviceId: string;
  userAgent: string;
  screenResolution: string;
  timezone: string;
  language: string;
  platform: string;
  cookieEnabled: boolean;
  doNotTrack: string | null;
  colorDepth: number;
  pixelRatio: number;
  touchSupport: boolean;
  webGLSupport: boolean;
}

interface LocationInfo {
  ip?: string;
  country?: string;
  city?: string;
  latitude?: number;
  longitude?: number;
  accuracy?: number;
  timestamp: number;
}

class SecurityService {
  private deviceId: string | null = null;
  private locationInfo: LocationInfo | null = null;

  // Generate or retrieve persistent device ID
  getDeviceId(): string {
    if (this.deviceId) {
      return this.deviceId;
    }

    // Try to get from localStorage first
    let deviceId = localStorage.getItem('bermuda_device_id');
    
    if (!deviceId) {
      // Generate new device ID based on browser fingerprint
      const fingerprint = this.generateFingerprint();
      deviceId = this.hashFingerprint(fingerprint);
      localStorage.setItem('bermuda_device_id', deviceId);
    }

    this.deviceId = deviceId;
    return deviceId;
  }

  // Generate browser fingerprint for device identification
  private generateFingerprint(): DeviceFingerprint {
    const screen = window.screen;
    const navigator = window.navigator;

    return {
      deviceId: this.getDeviceId() || 'unknown',
      userAgent: navigator.userAgent,
      screenResolution: `${screen.width}x${screen.height}`,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      language: navigator.language,
      platform: navigator.platform,
      cookieEnabled: navigator.cookieEnabled,
      doNotTrack: navigator.doNotTrack,
      colorDepth: screen.colorDepth,
      pixelRatio: window.devicePixelRatio,
      touchSupport: 'ontouchstart' in window,
      webGLSupport: this.checkWebGLSupport()
    };
  }

  // Check for WebGL support
  private checkWebGLSupport(): boolean {
    try {
      const canvas = document.createElement('canvas');
      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
      return !!gl;
    } catch (e) {
      return false;
    }
  }

  // Hash fingerprint to create device ID
  private hashFingerprint(fingerprint: DeviceFingerprint): string {
    const str = JSON.stringify(fingerprint);
    let hash = 0;
    
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    
    return Math.abs(hash).toString(36);
  }

  // Get location information (with user permission)
  async getLocationInfo(): Promise<LocationInfo | null> {
    if (this.locationInfo) {
      return this.locationInfo;
    }

    try {
      // Try to get IP-based location first (no permission required)
      const ipLocation = await this.getIPLocation();
      
      // Try to get GPS location (requires permission)
      const gpsLocation = await this.getGPSLocation();
      
      this.locationInfo = {
        ...ipLocation,
        ...gpsLocation,
        timestamp: Date.now()
      };

      return this.locationInfo;
    } catch (error) {
      console.warn('Failed to get location info:', error);
      return {
        timestamp: Date.now()
      };
    }
  }

  // Get approximate location from IP (using a free service)
  private async getIPLocation(): Promise<Partial<LocationInfo>> {
    try {
      const response = await fetch('https://ipapi.co/json/');
      if (!response.ok) throw new Error('IP location failed');
      
      const data = await response.json();
      return {
        ip: data.ip,
        country: data.country_name,
        city: data.city
      };
    } catch (error) {
      console.warn('IP location failed:', error);
      return {};
    }
  }

  // Get precise location from GPS (requires user permission)
  private async getGPSLocation(): Promise<Partial<LocationInfo>> {
    return new Promise((resolve) => {
      if (!navigator.geolocation) {
        resolve({});
        return;
      }

      const options = {
        enableHighAccuracy: false,
        timeout: 5000,
        maximumAge: 300000 // 5 minutes
      };

      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy
          });
        },
        (error) => {
          console.warn('GPS location failed:', error.message);
          resolve({});
        },
        options
      );
    });
  }

  // Get full security context for API calls
  async getSecurityContext() {
    const deviceId = this.getDeviceId();
    const fingerprint = this.generateFingerprint();
    const location = await this.getLocationInfo();

    return {
      device_id: deviceId,
      fingerprint,
      location,
      timestamp: Date.now(),
      session_start: performance.now()
    };
  }

  // Rate limiting check (simple client-side implementation)
  checkRateLimit(action: string, maxRequests: number = 10, timeWindow: number = 60000): boolean {
    const key = `rate_limit_${action}`;
    const now = Date.now();
    
    const requests = JSON.parse(localStorage.getItem(key) || '[]') as number[];
    
    // Remove old requests outside time window
    const validRequests = requests.filter(timestamp => now - timestamp < timeWindow);
    
    if (validRequests.length >= maxRequests) {
      return false; // Rate limit exceeded
    }
    
    // Add current request
    validRequests.push(now);
    localStorage.setItem(key, JSON.stringify(validRequests));
    
    return true;
  }

  // Clear stored security data (for privacy compliance)
  clearSecurityData(): void {
    localStorage.removeItem('bermuda_device_id');
    this.deviceId = null;
    this.locationInfo = null;
    
    // Clear rate limiting data
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
      if (key.startsWith('rate_limit_')) {
        localStorage.removeItem(key);
      }
    });
  }
}

export const securityService = new SecurityService();