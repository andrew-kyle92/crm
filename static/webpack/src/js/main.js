// import the custom css
import "../scss/styles.scss";

// imports
import * as bootstrap from "bootstrap";

// ********** Start of main.js script **********
// imports
import * as functions from "./functions";
import * as fetches from "./fetches";
import { applyActivityFilter, moveElement, getData, dragStart } from "./functions";

// ***** Global Script Variables *****
const currentUrl = new URL(document.URL);
export let dragged;
let listenerRegistry = [];

// ***** Global Script Functions *****
export function setDragged(ev) {
    dragged = ev.target;
}

// on DOMContentLoaded
window.addEventListener("DOMContentLoaded", () => {
    if (currentUrl.href.includes("activities")) {
        // on click event for activities
        let activities = document.getElementsByClassName("activity");
        for (let i = 0; i < activities.length; i++) {
            let activity = activities[i];
            activity.addEventListener("click", async () => {
               let activityId = activity.dataset.activityId;
               let res = await fetches.fetchActivity(activityId);
               if (res.status === "errors") {
                    console.log(res.message);
               } else {
                   let noActivityDiv = document.getElementById("noActivityMsg");
                   let activityDiv = document.getElementById("activityDiv");
                   let activityData = res["activity"];
                   let parser = new DOMParser()
                   let activityHtml = parser.parseFromString(activityData, 'text/html');
                   let activityBody = activityHtml.getElementById(`mainContent`);

                   // checking to see if any children exist within the activityDiv
                   if (activityDiv.childElementCount > 0) {
                       activityDiv.removeChild(activityDiv.firstElementChild);
                   }
                   activityDiv.appendChild(activityBody);
                   // hiding the no activity div
                   noActivityDiv.hidden = true;
                   // un-hiding the activityDiv
                   activityDiv.hidden = false;
               }
            });
        }
    }

    if (currentUrl.href.includes("customers/add")) {
        // this will only allow digit characters to be entered and formats it on every input character
        let phoneInputs = document.getElementsByClassName("phone");
        for (let i = 0; i < phoneInputs.length; i++) {
            let phoneInput = phoneInputs[i];
            phoneInput.placeholder = "ex (555) 555-5555";
            phoneInput.addEventListener("input", (e) => {
                let x = e.target.value.replace(/\D/g, "").match(/(\d{0,3})(\d{0,3})(\d{0,4})/);
                e.target.value = !x[2] ? x[1] : "(" + x[1] + ") " + x[2] + (x[3] ? "-" + x[3] : "");
            });
        }
    }

    // ********** Startup functions ********** //
    let filterBtns = document.getElementsByClassName("applyFilterBtn");
    for (let i = 0; i < filterBtns.length; i++) {
        let filterBtn = filterBtns[i];
        filterBtn.addEventListener("click", () => {
            let valueSourceId = filterBtn.dataset.valueSource;
            let valueSource = document.getElementById(valueSourceId);
            let url = new URL(document.URL);
            let urlData = {}
            if (url.search !== '') {
                let urlParams = new URLSearchParams(url.search);
                urlParams.forEach((value, key) => {
                    urlData[key] = value;
                });
            }
            // adding/updating the filter to match the dropdown selection
            urlData["filter"] = valueSource.value;

            // applying the filters
            applyActivityFilter(urlData);
        });
    }

    // ********** Utility Functions ********** //
    // collapsible sections
    let collapseBtns = document.getElementsByClassName("collapse-btn");
    if (collapseBtns.length > 0) {
        for (let i = 0; i < collapseBtns.length; i++) {
            let collapseBtn = collapseBtns[i];

            collapseBtn.addEventListener("click", () => {
                let target = collapseBtn.dataset.target;
                let collapseType = collapseBtn.dataset.type;
            });
        }
    }

    // get the correct modal content
    let modalDynBtns = document.getElementsByClassName("modal-dyn-btn");
    if (modalDynBtns.length > 0) {
        let contentTypes = {
            note: {
                type: "note",
                title: "Add Note",
                endpoint: new URL(document.URL).pathname + "add-note/",
                activityId: null,
                submitBtnText: "Add Note",
                initEditor: true,
            },
            editNote: {
                type: "editNote",
                title: "Edit Note",
                endpoint: new URL(document.URL).pathname + "add-note/",
                activityId: null,
                submitBtnText: "Save Note",
                initEditor: true,
                instanceId: null,
            },
            household: {
                type: "household",
                title: "Edit Note",
                endpoint: new URL(document.URL).pathname + "add-household/",
                activityId: null,
                submitBtnText: "Add Household",
                initEditor: true,
                instanceId: null,
            }
        }
        for (let i = 0; i < modalDynBtns.length; i++) {
            let modalDynBtn = modalDynBtns[i];
            modalDynBtn.addEventListener("click", async  () => {
                let contentType = modalDynBtn.dataset.contentType;
                let modal = document.getElementById(modalDynBtn.dataset.bsTarget.replace("#", ""));
                let modalInstance = bootstrap.Modal.getOrCreateInstance(modal);
                let modalHeader = modal.querySelector(".modal-title");
                let modalBody = modal.querySelector(".modal-body");
                let modalSubmitBtn = modal.querySelector("#modalSubmitBtn");
                let modalData = contentTypes[contentType];
                modalData.activityId = modalDynBtn.dataset.activityId;
                if (contentType === "editNote") {
                    modalData["instanceId"] = modalDynBtn.dataset.instanceId;
                }
                // getting the html content
                let res = await fetches.fetchModalData(modalData);
                if (res.status === "error") {
                    console.log(res.message);
                } else {
                    // setting up the parser
                    let parser = new DOMParser();
                    // parsing the HTML
                    let html = parser.parseFromString(res.html, "text/html");
                    // getting the form element from the parsed HTML
                    let form = html.querySelector("form");
                    // removing the submit button from the original layout
                    form.removeChild(form.querySelector("#submitBtn"));
                    // changing the modal title and body
                    modalHeader.innerText = modalData.title;
                    modalBody.innerHTML = form.outerHTML;
                    modalSubmitBtn.innerText = modalData.submitBtnText;
                    // updating the modal
                    modalInstance.handleUpdate();

                    if (contentType.initEditor) {
                        // Re-initialize Prose editor
                        if (window.djangoProse && typeof window.djangoProse.init === 'function') {
                            window.djangoProse.init();
                        }
                    }

                    let data;
                    switch (contentType) {
                        case "note":
                            // adding and onclick function
                            data = {
                                notesListId: "notesList",
                                formId: form.id,
                                modalInstance: modalInstance,
                                modal: modal,
                                contentType: contentType,
                            }
                            modalSubmitBtn.addEventListener("click", async () => functions.addActivityNote(data));
                            break;
                        case "editNote":
                            // adding and onclick function
                            data = {
                                notesListId: "notesList",
                                formId: form.id,
                                modalInstance: modalInstance,
                                modal: modal,
                                contentType: contentType,
                                instanceId: modalData["instanceId"],
                            }
                            modalSubmitBtn.addEventListener("click", async () => functions.addActivityNote(data));
                            break;
                    }
                }
            });
        }
    }

    // tabs toggling logic
    let tabs = document.querySelectorAll(".tab-span");
    if (tabs.length > 0) {
        for (let i = 0; i < tabs.length; i++) {
            let tab = tabs[i];
            tab.addEventListener("click", () => {
                // tab vars
                let tabTarget = document.getElementById(tab.dataset.target);
                // un-hiding the tab if not already unhidden
                if (tabTarget.dataset.expanded !== "true") {
                    tab.classList.add("active");
                    tabTarget.classList.add("true");
                    tabTarget.hidden = false;
                }

                // hiding all other tabs
                let tabsList = Array.from(tabs);
                tabsList.forEach(t => {
                    if (t !== tab && t.classList.contains("active")) {
                        let tTarget = document.getElementById(t.dataset.target);
                        tTarget.dataset.expanded = "false";
                        tTarget.hidden = true;
                        t.classList.remove("active");
                    }
                });
            });
        }
    }

    // drag operations on households add/edit page
    let householdRegex = /households\/(add|edit)\/$/g;
    if (currentUrl.pathname.match(householdRegex)) {
        const customers = Array.from(document.getElementsByClassName("customer"));
        let hiddenMembers = document.getElementById("id_members");

        customers.forEach(customer => {
            customer.addEventListener("dragstart", dragStart);
        });

        // hiding all members withing the head of household input
        let headOfHouseholdSelect = document.getElementById("id_head_of_household");
        let headOfHouseholdOptions = Array.from(headOfHouseholdSelect.querySelectorAll("option")).filter(el => el.value !== "");
        headOfHouseholdOptions.forEach(option => {
            // if (option.value !== "") option.hidden = true;
            option.hidden = true;
        });

        // detecting any changes to the membersDiv
        const membersDiv = document.getElementById("membersDiv");
        let config = {
            childList: true
        }
        const mutationCallback = function(mutationList, observer) {
            for (const mutation of mutationList) {
                if (mutation.target.childElementCount > 0) {
                    mutation.target.classList.remove("add-space");
                } else {
                    if (!mutation.target.className.includes("add-space")) {
                        mutation.target.classList.add("add-space");
                    }
                }
            }
        }
        const observer = new MutationObserver(mutationCallback);
        observer.observe(membersDiv, config);

        membersDiv.addEventListener("dragover", (e) => {
            // removing the default behavior
            e.preventDefault();
            membersDiv.classList.add("dragover");
        });

        membersDiv.addEventListener("dragleave", (e) => {
            e.preventDefault();
            membersDiv.classList.remove("dragover");
        });

        membersDiv.addEventListener("drop", (e) => {
            e.preventDefault();

            let addRemoveBtn = dragged.querySelector(".add-remove-button-div button");
            let data = functions.getData(dragged, membersDiv, addRemoveBtn, hiddenMembers, headOfHouseholdOptions, "add")

            moveElement(data);
            membersDiv.classList.remove("dragover");
        });

        // add/remove button logic and dblclick handler for customer div
        let addRemoveBtns = Array.from(document.querySelectorAll(".add-remove-button-div button"));
        addRemoveBtns.forEach(btn => {
            let custNode = btn.parentNode.parentNode;
            let data;
            if(btn.classList.contains("add-customer")) {
                data = functions.getData(custNode, membersDiv, btn, hiddenMembers, headOfHouseholdOptions, "add");
            } else {
                data = functions.getData(custNode, membersDiv, btn, hiddenMembers, headOfHouseholdOptions, "remove");
            }

            let moveHandler = () => moveElement(data);
            btn.addEventListener("click", moveHandler);
            // listener for when you double-click the customer's div
            custNode.addEventListener("dblclick", moveHandler);
        });
    }
});