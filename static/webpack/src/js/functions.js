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
    let instanceId = data["instanceId"] ? data["instanceId"] : false;
    let res = await fetches.submitActivityNote(form, instanceId);
    if (res.status === "error") {
        let parser = new DOMParser()
        let html = parser.parseFromString(res["html"], 'text/html');
        let formWithErrors = html.querySelector("form");
        // removing the submit button from the original layout
        formWithErrors.removeChild(formWithErrors.querySelector("#submitBtn"));
        data["modal"].querySelector(".modal-body").innerHTML = formWithErrors.outerHTML;
    } else {
        // creating the new note card
        if (instanceId) {
            createCardElement(res["instance"], data["notesListId"], data["contentType"], true, instanceId);
        } else {
            createCardElement(res["instance"], data["notesListId"], data["contentType"]);
        }
        // hiding the modal
        data["modalInstance"].hide();
    }
}

export function createCardElement(data, listParentId, contentType, replace = false, elId) {
    let parent = document.getElementById(listParentId);
    if (parent) {
        // creating the card element
        let cardDiv = document.createElement("div");
        cardDiv.className = "card mb-3";
        let cardBody = document.createElement("div");
        cardBody.className = "card-body";
        cardBody.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h5 class="card-title mb-0">${data["formatted_date"]}</h5>
                <button class="modal-dyn-btn btn btn-outline-secondary btn-sm border-0" data-activity-id="${data["activity_id"]}" data-instance-id="${data["id"]}" data-bs-toggle="modal" data-content-type="${contentType}" data-bs-target="#activityModal"><i class="fa-solid fa-pen-to-square"></i></button>
            </div>
            <p class="card-text">${data["description"]}</p>
        `;
        cardDiv.appendChild(cardBody);

        if (replace) {
            let oldChild = document.getElementById(`card-${elId}`);
            let parentNode = oldChild.parentNode;
            parentNode.replaceChild(cardDiv, oldChild);
        } else {
            if (parent.childElementCount > 0) {
                parent.insertBefore(cardDiv, parent.firstElementChild);
            } else {
                parent.appendChild(cardDiv);
            }
        }
    }
}

export async function markActivityComplete(activityId, customerId) {
    if (activityId) {
        let res = await fetches.fetchMarkComplete(activityId);
        if (res.status === "error") {
            console.error("Error: ", res.message)
        } else {
            window.location.href = `/customers/view/${customerId}/`;
        }
    }
}

// ********** Modal Content Type functions **********
export function setNoteContentType() {

}