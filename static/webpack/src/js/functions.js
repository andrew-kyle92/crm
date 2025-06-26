// ***** Getting the CSRF Token *****
export function getCookie(name) {
    let cookies = document.cookie.split(";");
    let c = null;
    cookies.forEach(cookie => {
       let [cookieName, value] = cookie.trim().split("=");
       if (cookieName === name ) {
           c = value
       }
    });
    return c
}

export function applyActivityFilter(data) {
    let url = new URL(document.URL) + "?" + new URLSearchParams(data);
    window.location.href = url;
}