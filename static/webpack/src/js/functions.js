// ***** Imports *****
import * as fetches from './fetches'

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
    window.location.href = new URL(document.URL) + "?" + new URLSearchParams(data);
}

export async function addActivityNote(data) {
    let form = document.getElementById(data["formId"]);
    let res = await fetches.submitActivityNote(form);
    console.log(res);
}