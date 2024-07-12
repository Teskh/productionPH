// Full-screen functions
function enterFullScreen() {
    if (document.documentElement.requestFullscreen) {
        document.documentElement.requestFullscreen();
    } else if (document.documentElement.mozRequestFullScreen) {
        document.documentElement.mozRequestFullScreen();
    } else if (document.documentElement.webkitRequestFullscreen) {
        document.documentElement.webkitRequestFullscreen();
    } else if (document.documentElement.msRequestFullscreen) {
        document.documentElement.msRequestFullscreen();
    }
}

function exitFullScreen() {
    if (document.exitFullscreen) {
        document.exitFullscreen();
    } else if (document.mozCancelFullScreen) {
        document.mozCancelFullScreen();
    } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
    } else if (document.msExitFullscreen) {
        document.msExitFullscreen();
    }
}

function toggleFullScreen() {
    if (!document.fullscreenElement &&
        !document.mozFullScreenElement && 
        !document.webkitFullscreenElement && 
        !document.msFullscreenElement) {
        enterFullScreen();
    } else {
        exitFullScreen();
    }
}

// Check full-screen state on page load
document.addEventListener('DOMContentLoaded', function() {
    if (localStorage.getItem('fullscreen') === 'true') {
        enterFullScreen();
    }
    
    // Add full-screen toggle button
    const body = document.body;
    const fullscreenBtn = document.createElement('button');
    fullscreenBtn.innerHTML = '⤢';
    fullscreenBtn.style.position = 'fixed';
    fullscreenBtn.style.bottom = '20px';
    fullscreenBtn.style.right = '20px';
    fullscreenBtn.style.zIndex = '9999';
    fullscreenBtn.style.fontSize = '24px';
    fullscreenBtn.style.padding = '10px';
    fullscreenBtn.style.background = 'rgba(0,0,0,0.5)';
    fullscreenBtn.style.color = 'white';
    fullscreenBtn.style.border = 'none';
    fullscreenBtn.style.borderRadius = '5px';
    fullscreenBtn.style.cursor = 'pointer';
    fullscreenBtn.onclick = toggleFullScreen;
    body.appendChild(fullscreenBtn);
});

// Listen for changes in full-screen state
document.addEventListener('fullscreenchange', function() {
    if (document.fullscreenElement) {
        localStorage.setItem('fullscreen', 'true');
    } else {
        localStorage.setItem('fullscreen', 'false');
    }
});

// 2. Update app.py to serve the new JavaScript file
# Add this near the top of app.py, after creating the Flask app
app.static_folder = 'static'

// 3. Modify existing HTML files (index.html, dashboard.html, start_new_task.html, settings.html)
// Add this line just before the closing </body> tag in each file:
<script src="{{ url_for('static', filename='js/fullscreen.js') }}"></script>

// 4. Update the <head> section in each HTML file to include these meta tags:
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes"></meta>