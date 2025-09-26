// ***** Imports *****
import * as fetches from './fetches'
import { setDragged } from "./main";

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

export async function addHousehold(data) {
    let form = document.getElementById(data["formId"]);
    let res = await fetches.submitHousehold(form)
    if (res.status === "error") {
        let parser = new DOMParser()
        let html = parser.parseFromString(res["html"], 'text/html');
        let formWithErrors = html.querySelector("form");
        // removing the submit button from the original layout
        formWithErrors.removeChild(formWithErrors.querySelector("#submitBtn"));
        data["modal"].querySelector(".modal-body").innerHTML = formWithErrors.outerHTML;
    } else {
        window.location.href = new URL(document.URL).origin + res.successUrl;
    }
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

export const dragStart = (ev) => {
    setDragged(ev);
}

export const getData = (targetEl, targetParent, innerEl, hiddenMembers, hohOptions, type) => {
    let data = {
        add: {
            element: {
                el: targetEl,
                classesToRemove: ["draggable", "customer"],
                classesToAdd: ["member"],
                attrsToRemove: ["draggable"],
                attrsToAdd: [],
                operations: {},
                innerElements: [
                    {
                        el: innerEl,
                        classesToRemove: ["add-customer", "btn-primary"],
                        classesToAdd: ["remove-customer", "btn-danger"],
                        operations: {
                            innerHTML: '<i class="fa-solid fa-minus"></i>',
                        }
                    }
                ]
            },
            targetParent: targetParent,
            hiddenMembers: hiddenMembers,
            hohOptions: hohOptions,
        },
        remove: {
            element: {
                el: targetEl,
                classesToRemove: ["member"],
                classesToAdd: ["draggable", "customer"],
                attrsToRemove: [],
                attrsToAdd: ["draggable"],
                operations: {},
                innerElements: [
                    {
                        el: innerEl,
                        classesToRemove: ["remove-customer", "btn-danger"],
                        classesToAdd: ["add-customer", "btn-primary"],
                        operations: {
                            innerHTML: '<i class="fa-solid fa-plus"></i>',
                        }
                    }
                ]
            },
            targetParent: targetParent,
            hiddenMembers: hiddenMembers,
            hohOptions: hohOptions,
        }
    }

    return data[type];
}

function applyChanges(ops={}, el) {
    for (const op in ops) {
        el[op] = ops[op];
    }
}

export const moveElement = (data={}, initial=false) => {
    let elementData = data.element;
    let element;
    let custId = elementData.el.dataset.customerId;
    let elementParent = elementData.el.parentNode;
    let innerElBtn;
    let options = data.hiddenMembers;
    let option = options.filter(opt => opt.value === custId)[0];
    let hohOption = data.hohOptions.find(opt => opt.value === option.value);
    if (!initial) {
        // changing the selected members
        option.selected = !option.selected;
    }
    // unhiding the household members
    hohOption.hidden = !hohOption.hidden;
    // determining the parent to determine if the element needs to be destroyed or hidden
    let destroy = elementParent.id === "membersDiv";
    if (!destroy) {
        // cloning the div
        element = elementData.el.cloneNode(true);
        elementData.innerElements[0].el = element.querySelector(".add-remove-button-div button");
        innerElBtn = elementData.innerElements[0].el;

        // hiding the original element
        elementData.el.hidden = true;
        elementData.el.classList.remove("d-flex");
        // adding element to new parent
        data.targetParent.appendChild(element);

        // removing classes from element
        element.classList.remove(...elementData.classesToRemove);
        // adding new classes
        element.classList.add(...elementData.classesToAdd);
        // removing attributes
        elementData.attrsToRemove?.forEach(attr => {
           if (element.hasAttribute(attr)) {
               element.removeAttribute(attr);
           }
        });
        // adding attributes
        elementData.attrsToAdd?.forEach(attr => {
           if (!!element.hasAttribute(attr)) {
               element.addAttribute(attr.name, attr.value);
           }
        });
        // checking any operations on element
        if (Object.keys(elementData.operations).length > 0) {
            applyChanges(elementData.operations, element);
        }

        // checking for inner elements
        if (elementData.innerElements.length > 0) {
            let innerElements = elementData.innerElements;
            for (const obj in innerElements) {
                let objData = innerElements[obj];
                let innerEl = objData.el;
                innerEl.classList.remove(...objData.classesToRemove); // removing classes
                innerEl.classList.add(...objData.classesToAdd); // adding classes

                if (Object.keys(objData.operations).length > 0) {
                    applyChanges(objData.operations, innerEl);
                }
            }
        }

        // adding the correct listeners
        let d;
        if (option.selected) {
            d = getData(element, elementParent, innerElBtn, data.hiddenMembers, data.hohOptions, "remove");
        }
        let moveHandler = () => moveElement(d);

        // adding general listeners back
        innerElBtn.addEventListener("click", moveHandler);
        element.addEventListener("dblclick", moveHandler);
    } else {
        element = elementData.el;
        elementParent.removeChild(element);
        let ogEl = data.targetParent.querySelector(`.customer[data-customer-id="${custId}"]`);
        ogEl.hidden = false;
        ogEl.classList.add("d-flex");
    }
}