// Full-screen function
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

// Enter fullscreen on page load
document.addEventListener('DOMContentLoaded', function() {
    enterFullScreen();
});

// Re-enter fullscreen when the window gains focus or when fullscreen is exited
document.addEventListener('fullscreenchange', function() {
    if (!document.fullscreenElement) {
        setTimeout(enterFullScreen, 100);
    }
});

window.addEventListener('focus', function() {
    if (!document.fullscreenElement) {
        enterFullScreen();
    }
});

// Attempt to re-enter fullscreen when switching pages
window.addEventListener('load', function() {
    if (!document.fullscreenElement) {
        enterFullScreen();
    }
});
