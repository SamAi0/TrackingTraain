/**
 * TrackEase Authentication Interceptor
 * Automatically handles 401 Unauthorized errors by attempting to refresh the JWT access token.
 * If the refresh token is also expired or invalid, it redirects the user to the login page.
 */
(function() {
    const originalFetch = window.fetch;

    window.fetch = async function(...args) {
        let response = await originalFetch(...args);

        // If response is 401 Unauthorized
        if (response.status === 401) {
            const url = typeof args[0] === 'string' ? args[0] : (args[0].url || '');
            
            // Do not intercept login or refresh requests to avoid infinite loops
            if (url.includes('/api/auth/')) {
                return response;
            }

            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
                try {
                    // Attempt to refresh token
                    const refreshRes = await originalFetch('http://127.0.0.1:8000/api/auth/login/refresh/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ refresh: refreshToken })
                    });

                    if (refreshRes.ok) {
                        const data = await refreshRes.json();
                        // Save new access token
                        localStorage.setItem('access_token', data.access);
                        
                        // Update the authorization header for the original request
                        const originalRequest = args[1] || {};
                        if (!originalRequest.headers) {
                            originalRequest.headers = {};
                        }
                        
                        // Handle both Headers object and plain object
                        if (originalRequest.headers instanceof Headers) {
                            originalRequest.headers.set('Authorization', `Bearer ${data.access}`);
                        } else {
                            originalRequest.headers['Authorization'] = `Bearer ${data.access}`;
                        }
                        
                        args[1] = originalRequest;
                        
                        // Retry original request
                        return await originalFetch(...args);
                    } else {
                        // Refresh token failed (expired or invalid)
                        throw new Error('Session expired');
                    }
                } catch (e) {
                    forceLogout();
                    return response; // Return original 401 to fail gracefully
                }
            } else {
                forceLogout();
            }
        }
        
        return response;
    };

    function forceLogout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        // Redirect to login page based on current path depth
        const depth = window.location.pathname.split('/').length - 2;
        let prefix = depth > 0 ? '../'.repeat(depth - 1) : '';
        if (window.location.pathname.includes('/pages/')) {
            window.location.href = '/pages/auth/login.html';
        } else {
            window.location.href = 'pages/auth/login.html';
        }
    }
})();
