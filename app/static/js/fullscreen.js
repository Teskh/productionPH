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

// Check full-screen state and enter fullscreen on page load
document.addEventListener('DOMContentLoaded', function() {
    enterFullScreen();
    
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

// Listen for changes in full-screen state and re-enter fullscreen if exited
document.addEventListener('fullscreenchange', function() {
    if (!document.fullscreenElement) {
        setTimeout(enterFullScreen, 100);
    }
});

// Re-enter fullscreen when the window gains focus
window.addEventListener('focus', function() {
    if (!document.fullscreenElement) {
        enterFullScreen();
    }
});
